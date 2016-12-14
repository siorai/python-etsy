from etsy import Etsy

__author__ = 'siorai@gmail.com (Paul Waldorf)'




def initialize():
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
  elif correct_info == 'n':
    initialize()
  else:
    verify()



initialize()
