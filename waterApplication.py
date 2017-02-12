import mechanicalsoup, re
from sys import argv
import os, time
import aes

loginInfo = { 'LOGIN':"login", 
              'PASSWORD':"password",
              'USER_NAME': "username"}

configFile = ".credentials/login-decrypt"
encryptfile = ".credentials/login-encrypt"

URL = "https://www.midpeninsulawater.org/billpay/"
now = time.strftime("%c")

def readConfigFile():
    aes.decrypt_file(aes.key, encryptfile, configFile, 64*1024)
    with open(configFile) as fp:
        for line in fp:
            entry = line.split(":")
            key = entry[0].strip()
            val = entry[1].strip()
            loginInfo[key] = val 
    print("this is logininfo", loginInfo)
    os.remove(configFile)
    ## remove login-decrypt file here
    
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
    acctStatus = ""
    acctInfo = response.soup
    if acctInfo:
        allTables =  response.soup.find_all('table')
        # print("length of all tables:", len(allTables))

    ## this gets only the account status section amount owed and write it to file
        for eachTable in allTables:
            if re.search(r"Account Status", eachTable.text):
                acctStatus = eachTable
      # print(acctStatus)
        writeFile(str(acctStatus), "./static/waterCurrent.html")

    ## this will write the entire page to file
        acctText = "Script Update: " + now + str(acctInfo)
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
                    historyString = "Script Update:" + now + str(history_page.soup)
                    writeFile(historyString, "./static/waterHistory.html")
#                    writeFile(str(history_page.soup), "./static/waterHistory.html")
    return historyPage



def waterProcess():
    readConfigFile()
    response , browser =  handleWaterLogin()
    acctInfo =  getWaterAccountMain(response)
    historyPage = getWaterBillHistory(response, browser)


#def main():    
#    waterProcess()


#if __name__ == "__main__":
#    main()




#  print " ================================"
