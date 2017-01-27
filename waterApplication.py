import mechanicalsoup, re
from sys import argv
import os, time


loginInfo = { 'LOGIN':"login", 
              'PASSWORD':"password",
              'USER_NAME': "username"}

configFile = "login.config.me"
URL = "https://www.midpeninsulawater.org/billpay/"

now = time.strftime("%c")

def readConfigFile():
    with open(configFile) as fp:
        for line in fp:
            entry = line.split(":")
            key = entry[0].strip()
            val = entry[1].strip()
            loginInfo[key] = val 
 #   print("this is logininfo", loginInfo)
    
def writeFile(content, filename):
    with open(filename, 'w') as op:
        op.write(content)
        op.close()


def getLoginInfo(browser):
    login_page = browser.get(URL)
    login_form = login_page.soup.find("form", {"class":"ywploginform"})

    login_form.find("input", {"name": "login[username]"})["value"]= loginInfo['LOGIN']
    login_form.find("input", {"name": "login[password]"})["value"] = loginInfo['PASSWORD']
    response = browser.submit(login_form, login_page.url)
    return response

def handleWaterLogin():
    # create a browser object
    browser = mechanicalsoup.Browser()
    response = getLoginInfo(browser)
    if response:
        print("Your're connected as " + loginInfo['USER_NAME'])
       # print response
    else:
        print("Not connected")
    return response, browser


def getWaterAccountMain(response):
    acctText = ""
    acctInfo = response.soup
    if acctInfo:
#        acctText = acctInfo.get_text() # get text only
        acctText = "Last Updated: " + now + str(acctInfo)
#    print ("Got acct info")
   # print(acctInfo)
    writeFile(str(acctText), "./static/acctInfo.html")
    return acctText
 

def getWaterBillHistory(response, browser):
    historyPage = ""
    for link in response.soup.find_all('a'):
        availUrls = str(link.get('href'))
        if re.search(r"history", availUrls):
            print "link found for history, following...."
            print(link.get('href'))
            history_page = browser.get(availUrls)
            if history_page:
                    print ("Got history page")
                    historyPage =  history_page.soup.get_text()
                    #print(historyPage)
                    historyString = "Last Updated:" + now + str(history_page.soup)
                    writeFile(historyString, "./static/waterHistory.html")
#                    writeFile(str(history_page.soup), "./static/waterHistory.html")
    return historyPage



def waterProcess():
    readConfigFile()
    response , browser =  handleWaterLogin()
    acctInfo =  getWaterAccountMain(response)
    historyPage = getWaterBillHistory(response, browser)

def main():
    waterProcess()


if __name__ == "__main__":
    main()




#  print " ================================"
