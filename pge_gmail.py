from __future__ import print_function
import httplib2
import os
import base64, email
import re
from bs4 import BeautifulSoup

from apiclient import discovery
from apiclient import errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# how to pages for this code:
# https://developers.google.com/gmail/api/quickstart/python?authuser=1

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Farallonian'
historyIDFile = "static/pge_historyid.txt"


def readFile(filename):
    fobj = open(filename)
    content = fobj.read()
    fobj.close()
    return content


def writeFile(content, filename):
    with open(filename, 'w') as op:
        op.write(content)
        op.close()


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('.')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials



def ListMessagesWithLabels(service, user_id, label_ids=[], query=''):
  """List all Messages of the user's mailbox with label_ids applied.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    label_ids: Only return Messages with these labelIds applied.

  Returns:
    List of Messages that have all required Labels applied. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate id to get the details of a Message.
  """
  try:
    response = service.users().messages().list(userId=user_id,
                                               labelIds=label_ids, q=query).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id,
                                                 labelIds=label_ids,
                                                 q=query,
                                                 pageToken=page_token).execute()
      messages.extend(response['messages'])

    return messages
  except errors.HttpError, error:
    print ('An error occurred: %s' % error)



def getLatestHistoryId(service, http, queryList, currentId):
    latest = 0
    msgid = 0

    if len(queryList) > 0:
      for q in queryList:
        msg =  GetMessage(service, 'me', q['id'])
        currentHistoryId = msg['historyId']
        print("historyid ", currentHistoryId, "- latest:", latest)
        if int(currentHistoryId) > int(latest):
            latest = int(currentHistoryId)
            msgid = q['id']

      print("latest history id:", latest, "msg id", msgid)
#      print("message", msg)

      # only process if the prevoius id  is not the same as latest
      if latest > int(currentId):

          mime_msg = GetMimeMessage(service, 'me', msgid)
          date = mime_msg['date']
          frm = mime_msg['from']
          subj = mime_msg['subject']

          rawtext = ""
          rawtext = rawtext + " ------ ------ EMAIL Header info ------ ------ <br>" + "From: " + frm + "<br>" +  "Date: " + date + "<br>" +  "Subject: " + subj +"<br>" +  "Msg ID: " + msgid + "<br>"

          print("------ ------ EMAIL Header info ------ ------ ") 
          print("MIME From: ", frm)
          print("MIME Date: ", date)
          print("MIME Subject: ", subj)
#          print ("message ID" , msgid)
          

          for part in mime_msg.walk():
#              print(part.get_content_type())
              if part.get_content_type() == 'text/html':
                  rawtext = rawtext + part.get_payload()
                  writeFile(rawtext, "static/pge_email.html")

                  soup = BeautifulSoup(rawtext, "html.parser")
                  para = soup.findAll('p')
                  for eachp in para:
                      billAmt =  re.search(r"The amount of(.*)", eachp.text)
                      if billAmt:
                          billLine = billAmt.group(0)
                          billContent = eachp.text.encode('utf-8').strip()
                          bc = billContent.replace("=", "")
                          bc = bc.replace("<", "")
                          bc = bc.replace("/p>", "")
                          print("REGEX match:", bc)
                          writeFile(bc, "static/pge.html")
              else:
                  print("other multipart-mime - skipping")
          print("-------- Parsing message out --------\n\n")

    return latest



"""Get Message with given ID.
"""
def GetMessage(service, user_id, msg_id):
  """Get a Message with given ID.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A Message.
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()

    return message
  except errors.HttpError, error:
    print ('An error occurred: %s' % error)


def GetMimeMessage(service, user_id, msg_id):
  """Get a Message and use it to create a MIME Message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A MIME Message, consisting of data from Message.
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id,
                                             format='raw').execute()

    msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
    mime_msg = email.message_from_string(msg_str)

    return mime_msg
  except errors.HttpError, error:
    print ('An error occurred: %s' % error)


def getMail():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    currentHistoryId = readFile("static/pge_historyid.txt")
    print("currentHistoryId:", currentHistoryId)

    queryList = ListMessagesWithLabels(service, 'me', ['Label_1'], 'is:unread') # label 1 is PGEUtilities, custom label
    if queryList > 0:
        print ('Unread messages: ', len(queryList), "\n")
        latestHistoryId = getLatestHistoryId(service, http, queryList, int(currentHistoryId))

        print("latest history id: " , latestHistoryId)            
        if (int(latestHistoryId) > int(currentHistoryId)): # cast to int
            writeFile(str(latestHistoryId), "static/pge_historyid.txt")


        
def main():
    getMail()

if __name__ == '__main__':
    main()
