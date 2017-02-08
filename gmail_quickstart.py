from __future__ import print_function
import httplib2
import os
import base64, email

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



def getLatestHistoryId(service, http, queryList):
    latesthistoryId = 0
    if len(queryList) > 0:
      for q in queryList:
        msg =  GetMessage(service, 'me', q['id'])
        currentHistoryId = msg['historyId']
        print("historyid ",currentHistoryId)
        if currentHistoryId > latesthistoryId:
          latesthistoryId = currentHistoryId

      print("------ ------ EMAIL Header info ------ ------ ")

      mime_msg = GetMimeMessage(service, 'me', q['id'])
      date = mime_msg['date']
      frm = mime_msg['from']
      subj = mime_msg['subject']

      print("MIME Date: ", date)
      print("MIME From: ", frm)
      print("MIME Subject: ", subj)
      print ("message ID" , mime_msg['historyId'], q['id'])

    return latesthistoryId

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

#    print("\n ****** MIME BODY ****** \n", mime_msg)

    return mime_msg
  except errors.HttpError, error:
    print ('An error occurred: %s' % error)


def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
      print('Labels:')
      for label in labels:
        print(label['name'])
      
    print(" ------ ------ ------ ------ \n")
    queryList = ListMessagesWithLabels(service, 'me', ['Label_1'], 'is:unread') # label 1 is PGEUtilities, custom label
    if queryList > 0:
        print ('Unread messages: ', len(queryList), "\n")
        latestHistoryId = getLatestHistoryId(service, http, queryList) 
        print("latest history id: " , latestHistoryId)
        
    print(" ------ ------ ------ ------ \n")


if __name__ == '__main__':
    main()
