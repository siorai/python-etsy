from etsy import Etsy
import pickle 
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
    elif use_em == 'y':
      print('Using em!')
    else:
      print('What was what?')
      initialize()
  except IOError:
    print('Credentials file not found, would you like to create one?')
    create_it = raw_input('y/n')
    if create_it == 'y':
      f_cred = open(credentials, 'w')
      print('%s has been created, populating...') % credentials
      f_cred.close
      get_credentials()
    else: 
      print('Exiting...')
  
    #print('Cannot find %s, creating new') % credentials
  
  


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
    print('Writting: %s') % credentials_dict
    pickle.dump(credentials_dict, open(credentials, 'w'))
  elif correct_info == 'n':
    initialize()
  else:
    verify()



initialize()
