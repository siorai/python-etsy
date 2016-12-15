from etsy import Etsy

__author__ = 'siorai@gmail.com (Paul Waldorf)'


credentials_dict = {'client_key': '', 
               'client_secret':'',
              }

credentials = './credentials'

def initialize():
  try:
    f = open(credentials, 'r')
    print('Found your credentials. Verifying.')
    f.read()
    print('Use these settings?')
    use_em = raw_input('y/n')
    if use_em == 'n':
      get_credentials()
    else:
      print('Using em!')
  except IOError:
    print('Cannot find %s, creating new') % credentials
    get_credentials()
  


def get_credentials():
  print('Credentials file creation initialized, please input client key:')
  client_key = raw_input('Client Key : ')
  print('Please provide client secret:')
  client_secret = raw_input('Client Secret : ')
  verify(client_key, client_secret)  

def verify(client_key, client_secret):
  print('Verify information:')
  print("client key = '%s'") % client_key
  print("client secret = '%s'") % client_secret
  print('Double check this information, is it correct?')
  correct_info = raw_input('y/n:')

  if correct_info == 'y':
    print("Client key is %s and client secret is %s") % (client_key, client_secret)
    credentials_dict['client_key'] = client_key
    credentials_dict['client_secret'] = client_secret
    print("From credentials dict:")
    print(credentials_dict)
  elif correct_info == 'n':
    initialize()
  else:
    verify()



initialize()
