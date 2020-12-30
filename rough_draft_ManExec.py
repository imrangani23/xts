# -*- coding: utf-8 -*-
"""
Created on Wed Dec 30 11:02:52 2020
BASE TEST
@author: Welcome
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta, TH
from XTConnect.Connect import XTSConnect
import time
import datetime
import pandas as pd
from sys import exit
from nsetools import Nse
nse = Nse()


# Trading Interactive Creds
API_KEY = "ebaa4a8cf2de358e53c942"
API_SECRET = "Ojre664@S9"

# MarketData Creds
# API_KEY = "ebaa4a8cf2de358e53c942"
# API_SECRET = "Ojre664@S9"

XTS_API_BASE_URL = "https://xts-api.trading"
source = "WEBAPI"
xt = XTSConnect(API_KEY, API_SECRET, source)
login_resp = xt.interactive_login()

def nextThu_and_lastThu_expiry_date ():

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
    str_month_last_thu_expiry=str(int(month_last_thu_expiry.strftime("%d")))+month_last_thu_expiry.strftime("%b").capitalize()+month_last_thu_expiry.strftime("%Y")
    str_next_thursday_expiry=str(int(next_thursday_expiry.strftime("%d")))+next_thursday_expiry.strftime("%b").capitalize()+next_thursday_expiry.strftime("%Y")
    return (str_next_thursday_expiry,str_month_last_thu_expiry)


def strkPrcCalc(ltp,base):    
    return base * round(ltp/base)


def get_eID(symbol,ce_pe,expiry,strikePrice):
    # print("Current nifty price is:", nfty_ltp)
    # print("Current BankNifty price is:", bnknfty_ltp)
    if ce_pe == "ce":
        oType="CE"
    elif ce_pe == "pe":
        oType="PE"
    # print("expiry date caluclated as :", expiry)
    eID_resp = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol=symbol,
                expiryDate=expiry,
                optionType=oType,
                strikePrice=strikePrice)
    #print('Option Symbol:', str(response))
    # print("ExchangeInstrumentID is:",eID_resp)# (int(response["result"][0]["ExchangeInstrumentID"])))
    return int(eID_resp["result"][0]["ExchangeInstrumentID"])


def placeOrderWithSL(symbol,buy_sell,quantity):  
    # Place an intraday stop loss order on NSE
    if buy_sell == "buy":
        t_type=xt.TRANSACTION_TYPE_BUY
        t_type_sl=xt.TRANSACTION_TYPE_SELL
        slPoints = -15
    elif buy_sell == "sell":
        t_type=xt.TRANSACTION_TYPE_SELL
        t_type_sl=xt.TRANSACTION_TYPE_BUY
        slPoints = +15
    tradedPrice = 0
    # quantity = mul*nifty_lot_size
    print('placing order for --', symbol)
    order_resp = xt.place_order(exchangeSegment=xt.EXCHANGE_NSEFO,
                    exchangeInstrumentID= symbol ,
                    productType=xt.PRODUCT_MIS, 
                    orderType=xt.ORDER_TYPE_MARKET,                   
                    orderSide=t_type,
                    timeInForce=xt.VALIDITY_DAY,
                    disclosedQuantity=0,
                    orderQuantity=quantity,
                    limitPrice=0,
                    stopPrice=0,
                    orderUniqueIdentifier="FirstChoice0"
                    )
    # print(f'''placing Market  Order = xt.place_order(exchangeSegment=xt.EXCHANGE_NSEFO,
    #                 exchangeInstrumentID= {symbol} ,
    #                 productType=xt.PRODUCT_MIS, 
    #                 orderType=xt.ORDER_TYPE_MARKET,                   
    #                 orderSide={t_type},
    #                 timeInForce=xt.VALIDITY_DAY,
    #                 disclosedQuantity=0,
    #                 orderQuantity={quantity},
    #                 limitPrice=0,
    #                 stopPrice=0,
    #                 orderUniqueIdentifier="1test1"
    #                 )''')
    # print("Place Order: ", oder_resp)
    # return oder_resp
    # order_resp = {'type': 'success', 'code': 's-orders-0001', 'description': 'Request sent', 'result': {'AppOrderID': 10026325, 'OrderUniqueIdentifier': '123777', 'ClientID': 'IIFL24'}}
    # # extracting the order id from response
    if order_resp['type'] != 'error':
         orderID = order_resp['result']['AppOrderID']
         print(f''' Order ID for {t_type} {symbol} is: ", {orderID}''')
    elif order_resp['type'] == 'error':
            print("Error placing Order.. Exiting...")
            exit()
    time.sleep(3)
    # stopPrice = 0
    orderBook = xt.get_order_book()
    orderList =  orderBook['result'] #
    # orderList =  [{'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10026325, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31389582', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 39992, 'OrderSide': 'Buy', 'OrderType': 'StopMarket', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 269.3, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '77.77', 'LeavesQuantity': 75, 'CumulativeQuantity': 0, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-29T13:13:54.0517821', 'ExchangeTransactTime': '2020-12-29T15:05:57+05:30', 'LastUpdateDateTime': '2020-12-29T15:05:57.3474221', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'dec29_sl_1', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 313939350474164}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 20030735, 'OrderReferenceID': '', 'GeneratedBy': 'TWS', 'ExchangeOrderID': 'X_31389805', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 39992, 'OrderSide': 'Buy', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '208.75', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-29T14:56:31.871326', 'ExchangeTransactTime': '2020-12-29T14:56:32+05:30', 'LastUpdateDateTime': '2020-12-29T14:56:32.1253445', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': '', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 313939350474163}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10026385, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31389601', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41379, 'OrderSide': 'Buy', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 93.35, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '95.45', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-29T13:28:09.5274879', 'ExchangeTransactTime': '2020-12-29T13:50:59+05:30', 'LastUpdateDateTime': '2020-12-29T13:50:59.2861998', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'dec29_sl_2', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 313939350474162}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10026383, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31389599', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41379, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '78.35', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-29T13:26:41.0961354', 'ExchangeTransactTime': '2020-12-29T13:26:41+05:30', 'LastUpdateDateTime': '2020-12-29T13:26:41.9091972', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'dec29_2', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 313939350474161}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10026364, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31389580', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 39992, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '219.30', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-29T13:12:36.8657664', 'ExchangeTransactTime': '2020-12-29T13:12:37+05:30', 'LastUpdateDateTime': '2020-12-29T13:12:37.5668251', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'dec29_1', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 313939350474160}]
    # orderID = 10026325
    for i in orderList:
        if orderID == i["AppOrderID"] and i["OrderStatus"] == 'Filled':
            tradedPrice = float(( i["OrderAverageTradedPrice"]))
            print('traded price is: ', tradedPrice)
    print('placing SL order for --', symbol)
    placed_SL_order = xt.place_order(exchangeSegment=xt.EXCHANGE_NSEFO,
                    exchangeInstrumentID= symbol ,
                    productType=xt.PRODUCT_MIS, 
                    orderType="StopMarket",                   
                    orderSide=t_type_sl,
                    timeInForce=xt.VALIDITY_DAY,
                    disclosedQuantity=0,
                    orderQuantity=quantity,
                    limitPrice=0,
                    stopPrice=round((tradedPrice+slPoints),2),
                    orderUniqueIdentifier="FirstChoice1"
                    )
    # print(f'''placed_SL_order = xt.place_order(exchangeSegment=xt.EXCHANGE_NSEFO,
    #                exchangeInstrumentID= {symbol} ,
    #                productType=xt.PRODUCT_MIS, 
    #                orderType="StopMarket",                   
    #                orderSide={t_type_sl},
    #                timeInForce=xt.VALIDITY_DAY,
    #                disclosedQuantity=0,
    #                orderQuantity={quantity},
    #                limitPrice=0,
    #                stopPrice=round(({tradedPrice}+{slPoints}),2),
    #                orderUniqueIdentifier="FirstChoice1"
    #                )''')
    # placed_SL_order = {'type': 'success', 'code': 's-orders-0001', 'description': 'Request sent', 'result': {'AppOrderID': 10066666, 'OrderUniqueIdentifier': '123777', 'ClientID': 'IIFL24'}}
    if placed_SL_order['type'] != 'error':
        placed_SL_orderID = placed_SL_order['result']['AppOrderID']
        print("order id for StopLoss :", placed_SL_orderID)
    else:
        print("Error placing SL Order.. try again manually...")
        
        
def get_global_PnL():
    totalMTMdf = 0.0
    positionList=xt.get_position_daywise()['result']['positionList']
    posDf = pd.DataFrame(positionList)
    # posDf['MTM'].replace({',':''},regex=True).apply(pd.to_numeric,1).sum()
    totalMTMdf = posDf['MTM'].replace({',':''},regex=True).apply(pd.to_numeric,1).sum()
    return totalMTMdf

def squareOff(eid):
    sq_off_resp = xt.squareoff_position(
                exchangeSegment=xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=eid,
                productType=xt.PRODUCT_MIS,
                squareoffMode=xt.SQUAREOFF_DAYWISE,
                positionSquareOffQuantityType=xt.SQUAREOFFQUANTITY_PERCENTAGE,
                squareOffQtyValue=100,
                blockOrderSending=True,
                cancelOrders=True)
    if sq_off_resp['type'] == 'success':
        print(f"Squared-off for symbol {symbol} | {eid}")
        
def cancelOrder(OrderID):
    cancel_resp = xt.cancel_order(
        appOrderID=OrderID,
        orderUniqueIdentifier='FC_Cancel_Orders_1') 
    print(cancel_resp)
    
    
    
    
tickers = ["NIFTY"] 
for ticker in tickers:
    for oType in "ce","pe":
        weekly_exp,monthly_exp = nextThu_and_lastThu_expiry_date()
        #expiry = get_expiry_from_option_chain(ticker)
        # weekly_exp,monthly_exp=(expiry[:2])
        if ticker == "NIFTY":
             quantity = 75
             nfty_ltp = nse.get_index_quote("nifty 50")['lastPrice']
             strikePrice = strkPrcCalc(nfty_ltp,50)
        if ticker == "BANKNIFTY":
            quantity = 25
            bnknfty_ltp = nse.get_index_quote("nifty bank")['lastPrice']
            strikePrice = strkPrcCalc(bnknfty_ltp,100)
        print(f"symbol = {ticker}  expiry = {weekly_exp}  Otype = {oType}  strikePrice = {strikePrice } ")#.format(ticker,expiry,Otype,strikePrice,eID))
        eID = get_eID(ticker,oType,weekly_exp,strikePrice)
        print("EID is :", eID)
        placeOrderWithSL(eID,'sell',quantity)
    

print('#################--CODE ENDS HERE#--###################')

get_global_PnL()

cdate = datetime.datetime.strftime(datetime.datetime.now(), "%d-%m-%Y")
check=True
while check:
    if (get_global_PnL() < -1500) or (datetime.datetime.now() >= datetime.datetime.strptime(cdate + " 15:29:00", "%d-%m-%Y %H:%M:%S")):
        #closing all open positions
        positionList=xt.get_position_daywise()['result']['positionList']
        pos_df = pd.DataFrame(positionList)
        for i in range(len(pos_df)):
            if int(pos_df["Quantity"].values[i]) != 0:
                symbol=pos_df['TradingSymbol'].values[i]
                eid = pos_df["ExchangeInstrumentId"].values[i]
                squareOff(eid)
        print("Position Squareoff COmpleted ")
        
        #closing all pending orders
        orderList=xt.get_order_book()['result']
        ord_df = pd.DataFrame(orderList)
        pending = ord_df[ord_df['OrderStatus'].isin(["New","Open","Partially Filled"])]["AppOrderID"].tolist()
        drop = []
        attempt = 0
        while len(pending)>0 and attempt<5:
            pending = [j for j in pending if j not in drop]
            for order in pending:
                try:
                    cancelOrder(order)
                    drop.append(order)
                except:
                    print("unable to delete order id : ",order)
                    attempt+=1
        else:
            print("No Open orders to Cancel")
                
        check=False #exit the main loop
    else:
        print(time.strftime("%d-%m-%Y %H:%M:%S"),"|",get_global_PnL())
        time.sleep(30)

        
# print(time.strftime("%d-%m-%Y %H:%M:%S"),"|",get_global_PnL())            
# xt.get_position_daywise()['result']['positionList']        
# if get_global_PnL() > -200:
#     print(time.strftime("%d-%m-%Y %H:%M:%S"),"|",get_global_PnL())

# -1400 < -1500

orderList=xt.get_order_book()['result']
ord_df = pd.DataFrame(orderList)
pending = ord_df[ord_df['OrderStatus'].isin(["New","Open","Partially Filled"])]["AppOrderID"].tolist()
drop = []
attempt = 0
while len(pending)>0 and attempt<5:
    pending = [j for j in pending if j not in drop]
    for order in pending:
        try:
            cancelOrder(order)
            drop.append(order)
        except:
            print("unable to delete order id : ",order)
            attempt+=1

orderList=xt.get_order_book()['result']
orderDf = pd.DataFrame(orderList)

tradeList=xt.get_trade()['result']
tradeDf = pd.DataFrame(tradeList)

positionList=xt.get_position_daywise()['result']['positionList']
posDf = pd.DataFrame(positionList)
