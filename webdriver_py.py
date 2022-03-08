from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import sys

from datetime import datetime as dt
#cur_dt = dt.now().strftime("%d/%m/%Y %H:%M:%S")
import win32com.client as win32

outlook = win32.Dispatch('outlook.application')

mail = outlook.CreateItem(0)

mail.To = 'lm8@ford.com'

mail.Subject = 'Today Altimetrik Login Information'

 

def prnt_send_mail(body):

                print(body)

                mail.Body = body

                mail.Send()

  

options = Options()
options.add_argument("--disable-notifications")
PATH = "C:\\Users\\imran\\Downloads\\chromedriver_win32.exe"
driver = webdriver.Chrome()

PATH = "C:/Users/imran/Downloads/chromedriver.exe"
driver = webdriver.Chrome('C:/Users/imran/Downloads/chromedriver.exe')
 

driver.get("https://ind01.safelinks.protection.outlook.com/?url=http%3A%2F%2Faltimetrik.myemploywise.com%2F&data=02%7C01%7C%7C2a762a87da5c472c069608d7e532910d%7Ce9cb3c8041564c39a7fe68fe427a3d46%7C0%7C0%7C637229878190332604&sdata=K3n9ZmyoSvKa2ma8VKDzIK5CGbhKxAcHRd63LQK%2BGHw%3D&reserved=0")

 

uname = driver.find_element_by_id("userNameInput")

uname.send_keys("lmahendran@altimetrik.com")

upwd = driver.find_element_by_id("passwordInput")

upwd.send_keys("password")

upwd.send_keys(Keys.RETURN)

 

try:

                markIn = WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.LINK_TEXT,'Mark In')));

                #markIn = driver.find_element_by_link_text('Mark In')

                #if markIn.is_displayed():

                markIn.click()

                time.sleep(5)

                #txtOut = driver.find_element_by_id("markin_links").text

                txtOut=WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.ID,'markin_links')));

                print(txtOut.text)

                #txtOut = driver.find_element_by_xpath("//*[contains(text(), 'You Marked In at ')]").text

                prnt_send_mail(txtOut.text)

 

except TimeoutException:

                try:

                                popUp = WebDriverWait(driver,8).until(EC.visibility_of_element_located((By.XPATH,"//img[contains(@src,'wizard_close.png')]")))

                                popUp.click()

                                markOut = WebDriverWait(driver,8).until(EC.visibility_of_element_located((By.LINK_TEXT,'Now')));

                                markOut.click()

                                msg = "Marked Out Successfully at: " + dt.now().strftime("%d/%m/%Y %H:%M:%S")

                                prnt_send_mail(msg)

                except TimeoutException:

                                markOut = WebDriverWait(driver,8).until(EC.visibility_of_element_located((By.LINK_TEXT,'Now')));

                                markOut.click()

                                msg = "Marked Out Successfully at: " + dt.now().strftime("%d/%m/%Y %H:%M:%S")

                                prnt_send_mail(msg)

except:

                msg = "Oops!" + sys.exc_info()[0] + "occurred."

                prnt_send_mail(msg)