# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 02:05:10 2021
Re-writing Strategy-1 (INDEX OPTION WRITING)
@author: lmahendran
"""
####
from datetime import datetime,date
from dateutil.relativedelta import relativedelta, TH
from XTConnect.Connect import XTSConnect
from pathlib import Path
import time
import json
import logging
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
# pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', -1)
import configparser
import timer
from threading import Thread
from openpyxl import load_workbook
from sys import exit

############## logging configs ##############

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

filename='../logs/Index_Option_Writing_log.txt'

file_handler = logging.FileHandler(filename)
# file_handler=logging.handlers.TimedRotatingFileHandler(filename, when='d', interval=1, backupCount=5)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

############## XTS Initialisation ##############

cfg = configparser.ConfigParser()
cfg.read('../../XTConnect/config.ini')
source = cfg['user']['source']
appKey = cfg.get('user', 'interactive_appkey')
secretKey = cfg.get('user', 'interactive_secretkey')
xt = XTSConnect(appKey, secretKey, source)

global cdate
cdate = datetime.strftime(datetime.now(), "%d-%m-%Y")
token_file=f'access_token_{cdate}.txt'
file = Path(token_file)
if file.exists() and (date.today() == date.fromtimestamp(file.stat().st_mtime)):
    logger.info('Token file exists and created today')
    in_file = open(token_file,'r').read().split()
    access_token = in_file[0]
    userID=in_file[1]
    isInvestorClient=in_file[2]
    logger.info('Initializing session with token..')
    xt._set_common_variables(access_token, userID, isInvestorClient)
else:
    logger.error('Wrong with token file. Generate separately.. Aborting script!..')
    exit()

############## Variable Declarations ##############

etr_inst = None
rpr_inst = None
ext_inst = None
tr_insts = None
ltp = {}
gl_pnl = None
idxs = ['NIFTY','BANKNIFTY']
orders=[{'refId':10001, 'setno':1, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"NIFTY", 'otype': "ce", 'status': "Idle", 'expiry': 'week', 'lot': 1, 'startTime':"09:58:00"},
		{'refId':10002, 'setno':2, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"NIFTY", 'otype': "pe", 'status': "Idle", 'expiry': 'week', 'lot': 1, 'startTime':"09:58:00"}]
universal = {'exit_status': 'Idle', 'minPrice': -12000, 'maxPrice': 24000, 'exitTime':'22:48:00', 'ext_txn_type':'buy'}

############## Functions ##############

def nextThu_and_lastThu_expiry_date():
    global weekly_exp, monthly_exp
    logger.info('Calculating weekly and monthly expiry dates..')
    todayte = datetime.today()
    cmon = todayte.month
    if_month_next=(todayte + relativedelta(weekday=TH(1))).month
    next_thursday_expiry=todayte + relativedelta(weekday=TH(1))
    if (if_month_next!=cmon):
        month_last_thu_expiry= todayte + relativedelta(weekday=TH(5))
        if (month_last_thu_expiry.month!=if_month_next):
            month_last_thu_expiry= todayte + relativedelta(weekday=TH(4))
    else:
        for i in range(1, 7):
            t = todayte + relativedelta(weekday=TH(i))
            if t.month != cmon:
                # since t is exceeded we need last one  which we can get by subtracting -2 since it is already a Thursday.
                t = t + relativedelta(weekday=TH(-2))
                month_last_thu_expiry=t
                break
    monthly_exp=str((month_last_thu_expiry.strftime("%d")))+month_last_thu_expiry.strftime("%b").capitalize()+month_last_thu_expiry.strftime("%Y")
    weekly_exp=str((next_thursday_expiry.strftime("%d")))+next_thursday_expiry.strftime("%b").capitalize()+next_thursday_expiry.strftime("%Y")
    logger.info(f'weekly expiry is : {weekly_exp}, monthly expiry is: {monthly_exp}')

def masterDump():
    global instrument_df
    filename=f'../ohlc/NSE_Instruments_{cdate}.csv'
    file = Path(filename)
    if file.exists() and (date.today() == date.fromtimestamp(file.stat().st_mtime)):
        logger.info('MasterDump already exists.. reading directly')
        instrument_df=pd.read_csv(filename,header='infer')
    else:
        logger.info('Creating MasterDump..')
        exchangesegments = [xt.EXCHANGE_NSEFO]
        mastr_resp = xt.get_master(exchangeSegmentList=exchangesegments)
        # print("Master: " + str(mastr_resp))
        master=mastr_resp['result']
        spl=master.split('\n')
        mstr_df = pd.DataFrame([sub.split("|") for sub in spl],columns=(['ExchangeSegment','ExchangeInstrumentID','InstrumentType','Name','Description','Series','NameWithSeries','InstrumentID','PriceBand.High','PriceBand.Low','FreezeQty','TickSize',' LotSize','UnderlyingInstrumentId','UnderlyingIndexName','ContractExpiration','StrikePrice','OptionType']))
        instrument_df = mstr_df[mstr_df.Series == 'OPTIDX']
        instrument_df.to_csv(f"../ohlc/NSE_Instruments_{cdate}.csv",index=False)        

def strikePrice(idx):
    if idx in idxs[0]:
        base = 50
        ids = 'NIFTY 50'
    elif idx in idxs[1]:
        base = 100
        ids = 'NIFTY BANK'
    # if idx in idxs:
        # base,ids = [50,'Nifty 50'] if idx == 'NIFTY' else [100,'NIFTY BANK']
    else:
        logger.info(f'Invalid Index name {idx} - Valid names are {idxs}')
    try:
        idx_instruments = [{'exchangeSegment': 1, 'exchangeInstrumentID': ids}]
        spot_resp = xt.get_quote(
                    Instruments=idx_instruments,
                    xtsMessageCode=1504,
                    publishFormat='JSON')
        if spot_resp['type'] !='error':
            listQuotes = json.loads(spot_resp['result']['listQuotes'][0])
            spot=listQuotes['IndexValue']
        else:
            logger.error(spot_resp['description'])
            raise Exception()
    except Exception:
        logger.exception(f'Unable to getSpot from index {ids}')
        exit()
    else:
        strikePrice = base * round(spot/base)
        logger.info(f'StrikePrice computed as : {strikePrice}')
        return strikePrice

def instrumentLookup(instrument_df,symbol):
    """Looks up instrument token for a given script from instrument dump"""
    try:
        return instrument_df[instrument_df.Description==symbol].ExchangeInstrumentID.values[0]
    except:
        return -1

def getOrderList():
    aa = 0
    logger.info('Checking OrderBook for order status..') 
    while aa < 5:
        try:
           oBook_resp = xt.get_order_book()
           if oBook_resp['type'] != "error":
               orderList =  oBook_resp['result']
               # logger.info('OrderBook result retreived success')
               return orderList
               break
           else:
               raise Exception("Unkonwn error in getOrderList func")           
        except Exception:
            logger.exception("Can't extract order data..retrying")
            # traceback.print_exc()
            time.sleep(2)
            aa+=1

def cancelOrder(OrderID):
    logger.info(f'Cancelling order: {OrderID} ')
    cancel_resp = xt.cancel_order(
        appOrderID=OrderID,
        orderUniqueIdentifier='FC_Cancel_Orders_1') 
    if cancel_resp['type'] != 'error':
        cancelled_SL_orderID = cancel_resp['result']['AppOrderID']
        logger.info(f'Cancelled SL order id : {cancelled_SL_orderID}')
    if cancel_resp['type'] == 'error':
        logger.error(f'Cancel order not processed for : {OrderID}')

def placeOrder(symbol,txn_type,qty):
    logger.info('Placing Orders..')
    # Place an intraday stop loss order on NSE
    if txn_type == "buy":
        t_type=xt.TRANSACTION_TYPE_BUY
    elif txn_type == "sell":
        t_type=xt.TRANSACTION_TYPE_SELL
    try:
        order_resp = xt.place_order(exchangeSegment=xt.EXCHANGE_NSEFO,
                         exchangeInstrumentID= symbol ,
                         productType=xt.PRODUCT_MIS, 
                         orderType=xt.ORDER_TYPE_MARKET,                   
                         orderSide=t_type,
                         timeInForce=xt.VALIDITY_DAY,
                         disclosedQuantity=0,
                         orderQuantity=qty,
                         limitPrice=0,
                         stopPrice=0,
                         orderUniqueIdentifier="FC_MarketOrder"
                         )
        if order_resp['type'] != 'error':
            orderID = order_resp['result']['AppOrderID']            #extracting the order id from response
            logger.info(f'Order ID for {t_type} {symbol} is: {orderID}')
            time.sleep(2)
            a=0
            while a<12:
                orderLists = getOrderList()
                if orderLists:
                    new_orders = [ol for ol in orderLists if ol['AppOrderID'] == orderID and ol['OrderStatus'] != 'Filled']  
                    if not new_orders:
                        tradedPrice = float(next((orderList['OrderAverageTradedPrice'] for orderList in orderLists if orderList['AppOrderID'] == orderID and orderList['OrderStatus'] == 'Filled'),None))
                        LastUpdateDateTime=datetime.fromisoformat(next((orderList['LastUpdateDateTime'] for orderList in orderLists if orderList['AppOrderID'] == orderID and orderList['OrderStatus'] == 'Filled'))[0:19])
                        dateTime = LastUpdateDateTime.strftime("%Y-%m-%d %H:%M:%S")
                        logger.info(f"traded price is: {tradedPrice} and ordered  time is: {dateTime}")
                        return orderID, tradedPrice, dateTime
                        break
                        # loop = False
                    else:
                        logger.info(f' Placed order {orderID} might be in Open or New Status, Hence retrying..{a}')
                        a+=1
                        time.sleep(2.5)
                        if a==11:
                            logger.info('Placed order is still in New or Open Status..Hence Cancelling the placed order')
                            cancelOrder(orderID)
                            return None, None, None
                            break
                else:
                    logger.info('\n  Unable to get OrderList inside place order function..')
                    logger.info('..Hence traded price will retun as Zero \n ')
        elif order_resp['type'] == 'error':
            logger.error(order_resp['description'])
            logger.info(f'Order not placed for - {symbol} ')
            raise Exception('Order not placed - ')
    except Exception():
        logger.exception('Unable to place order in placeOrder func...')
        time.sleep(1)

def placeSLOrder(symbol, txn_type, qty, slTrigger):
    logger.info('Placing SL Order..')
    # Place an intraday stop loss order on NSE
    if txn_type == "buy":
        t_type=xt.TRANSACTION_TYPE_BUY
    elif txn_type == "sell":
        t_type=xt.TRANSACTION_TYPE_SELL
    sl_order_resp = xt.place_order(exchangeSegment=xt.EXCHANGE_NSEFO,
                         exchangeInstrumentID= symbol ,
                         productType=xt.PRODUCT_MIS, 
                         orderType="StopMarket",                   
                         orderSide=t_type,
                         timeInForce=xt.VALIDITY_DAY,
                         disclosedQuantity=0,
                         orderQuantity=qty,
                         limitPrice=0,
                         stopPrice=slTrigger,
                         orderUniqueIdentifier="FC_SLOrder"
                         )
    if sl_order_resp['type'] != 'error':
        orderID = sl_order_resp['result']['AppOrderID']            #extracting the order id from response
        logger.info(f'\n  StopLoss Order ID for {t_type_sl} {symbol} is: {orderID} \n')
        return orderID
    else:
        logger.info(' \n TradedPice is not available, Hence not placing SL order, TRY MANUALLY.. \n')

    
def execute(orders):
    global tr_insts
    tr_insts = []
    etr_inst = {}
    rpr_inst = {}
    startTime = datetime.strptime((cdate+" "+orders['startTime']),"%d-%m-%Y %H:%M:%S")
    weekday = datetime.today().weekday()
    while True:
        if orders['status'] == 'Idle':
            #Entry condition check
            if (datetime.now() >= startTime):
                logger.info(f'Placing orders for {orders["setno"]} at {orders["startTime"]}..')
                etr_inst['set']=orders['setno']
                etr_inst['txn_type'] = orders['ent_txn_type']
                strikePrice = strikePrice(orders['idx'])
                
                if weekday != 3: #if not thursday, take straddle
                    etr_inst['strike'] = strikePrice + 50 if orders['otype'] == 'ce' else strikePrice - 50
                else:
                    etr_inst['strike'] = strikePrice
                
                etr_inst['qty'] = 75*orders['lot'] if orders['idx'] == 'NIFTY' else 25*orders['lot']
                etr_inst['tr_qty'] = -etr_inst['qty'] if orders['ent_txn_type'] == 'sell' else etr_inst['qty']
                
                if orders['expiry'] == 'week':
                    etr_inst['expiry'] = weekly_exp
                etr_inst['optionType'] = orders['otype'].upper()
                
                if weekly_exp == monthly_exp:
                    inst_name = orders['idx']+(datetime.strftime(datetime.strptime(etr_inst['expiry'], '%d%b%Y'),'%y%b')).upper()+str(etr_inst['strike'])+etr_inst['optionType']
                else:
                    inst_name = orders['idx']+(datetime.strftime(datetime.strptime(etr_inst['expiry'], '%d%b%Y'),'%y%#m%d'))+str(etr_inst['strike'])+etr_inst['optionType']
                
                etr_inst['name'] = inst_name
                etr_inst['symbol'] = int(instrumentLookup(instrument_df,inst_name))
                etr_inst['orderID'] = None
                etr_inst['tradedPrice'] = None
                # logger.info(f"orders before placing orders : {orders}")
                orderID, tradedPrice, dateTime = placeOrder(etr_inst['symbol'],etr_inst['txn_type'],etr_inst['qty'])
                etr_inst['orderID'] = orderID
                etr_inst['tradedPrice'] = tradedPrice
                etr_inst['dateTime'] = dateTime
                if orderID and tradedPrice:
                    etr_inst['set_type'] = 'Entry'
                    orders['status'] = 'Entered'
                logger.info(f'Entry order dtls: {etr_inst}')
                tr_insts.append(etr_inst)
                
            if orders['status'] == 'Entered':
                # ename = next(i['name'] for i in tr_insts if i['set_type']=='Entry' and i['set']==orders['setno'])
                esymbol = next(i['symbol'] for i in tr_insts if i['set_type']=='Entry' and i['set']==orders['setno'])
                etp = next(i['tradedPrice'] for i in tr_insts if i['set_type']=='Entry' and i['set']==orders['setno'])
                slt = round((etp + 15.25),2)
                eqty = next(i['qty'] for i in tr_insts if i['set_type']=='Entry' and i['set']==orders['setno'])
                rpr_txn_type = orders['rpr_txn_type']
                placeSLOrder(esymbol, rpr_txn_type, eqty, slt)
                
                
############## main ##############
if __name__ == '__main__':
    nextThu_and_lastThu_expiry_date()
    masterDump()
    execute(orders)
    