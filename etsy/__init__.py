import six
import json
import logging
import requests
from requests_oauthlib import OAuth1

if six.PY3:
    from urllib.parse import parse_qs
    from urllib.parse import urlencode
else:
    from urlparse import parse_qs
    from urllib import urlencode

log = logging.getLogger(__name__)

class EtsyError(Exception):
    def __init__(self, message, response):
        super(EtsyError, self).__init__(message)
        self.response = response

class Etsy(object):
    """
    Represents the etsy API
    """
    url_base = "https://openapi.etsy.com/v2"
    
    def __init__(self, consumer_key, consumer_secret, oauth_token=None, oauth_token_secret=None, sandbox=False):
        self.params = {'api_key': consumer_key}
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        
        if sandbox:
            self.url_base = "http://sandbox.openapi.etsy.com/v2"
        
        # generic authenticated oauth hook
        self.simple_oauth = OAuth1(consumer_key, client_secret=consumer_secret)
        
        if oauth_token and oauth_token_secret:
            # full oauth hook for an authenticated user
            self.full_oauth = OAuth1(consumer_key, client_secret=consumer_secret,
                resource_owner_key=oauth_token, resource_owner_secret=oauth_token_secret)
    
    def show_listings(self, color=None, color_wiggle=5):
        """
        Show all listings on the site.
        color should be a RGB ('#00FF00') or a HSV ('360;100;100')
        """
        endpoint = '/listings/active'
        params = {}
        if color:
            params['color'] = color
            params['color_accuracy'] = color_wiggle
    
        response = self.execute(endpoint, params=params)
        return response


    def get_transactions(self, user, shop_id, number_of_transactions):
        """
        Get all of the transactions from user with shopid
        """    

        endpoint = '/shops/%s/transactions' % shop_id
        params = {'shop_id': shop_id,'limit': number_of_transactions}  
        if user == '__SELF__':
            auth = {'oauth': self.full_oauth}
        
        response = self.execute(endpoint, params=params, **auth)
        return response


    def get_user_info(self, user):
        """
        Get basic info about a user, pass in a username or a user_id
        """
        endpoint = '/users/%s' % user
        
        auth = {}
        if user == '__SELF__':
            auth = {'oauth': self.full_oauth}
            
        response = self.execute(endpoint, **auth)
        return response
    
    def find_user(self, keywords):
        """
        Search for a user given the 
        """
        endpoint = '/users'
        params = {'keywords': keywords}
        response = self.execute(endpoint, params=params)
        return response
    
    def get_auth_url(self, permissions=[]):
        """
        Returns a url that a user is redirected to in order to authenticate with
        the etsy API. This is step one in the authentication process.
        oauth_token and oauth_token_secret need to be saved for step two.
        """
        endpoint = '/oauth/request_token'
        params = {}
        if permissions:
            params = {'scope': " ".join(permissions)}
        self.oauth = self.simple_oauth
        response = self.execute(endpoint, oauth=self.oauth, params=params)
        parsed = parse_qs(response)
        url = parsed['login_url'][0]
        token = parsed['oauth_token'][0]
        secret = parsed['oauth_token_secret'][0]
        return {'oauth_token': token, 'url': url, 'oauth_token_secret': secret}
    
    def get_auth_token(self, verifier, oauth_token, oauth_token_secret):
        """
        Step two in the authentication process. oauth_token and oauth_token_secret
        are the same that came from the get_auth_url function call. Returned is
        the permanent oauth_token and oauth_token_secret that will be used in
        every subsiquent api request that requires authentication.
        """
        endpoint = '/oauth/access_token'
        oauth = OAuth1(self.consumer_key, client_secret=self.consumer_secret,
                resource_owner_key=oauth_token, 
                resource_owner_secret=oauth_token_secret,
                verifier=verifier)
        response = requests.post(url="%s%s" % (self.url_base, endpoint), auth=oauth)
        parsed = parse_qs(response.text)
        return {'oauth_token': parsed['oauth_token'][0], 'oauth_token_secret': parsed['oauth_token_secret'][0]}
        
    def execute(self, endpoint, method='get', oauth=None, params=None, files=None):
        """
        Actually do the request, and raise exception if an error comes back.
        """
        hooks = {}
        if oauth:
            # making an authenticated request, add the oauth hook to the request
            hooks = {'auth': oauth}
            if params is None:
                params = {}
        else:
            if params is None:
                params = self.params
            else:
                params.update(self.params)

        querystring = urlencode(params)
        url = "%s%s" % (self.url_base, endpoint)
        if querystring:
            url = "%s?%s" % (url, querystring)
        
        response = getattr(requests, method)(url, files=files, **hooks)
        
        if response.status_code > 201:
            e = response.text
            code = response.status_code
            raise EtsyError('API returned %s response: %s' % (code, e), response)

        try:
            return json.loads(response.text)
        except (TypeError, ValueError):
            return response.text

    def execute_authed(self, endpoint, method='get', params=None):
        return self.execute(endpoint, method, oauth=self.full_oauth, params=params)

    def iterate_pages(self, f, *p, **d):
        '''
        Iterates through pages in a response.
        Use this method when the response is valid json and has pagination
        Example:
            pages = e.iterate_pages('execute_authed', '/shops/GreenTurtleTshirts/receipts', 
                params={'was_paid': True, 'was_shipped': False})
            for page in pages:
                print page
        '''
        f = getattr(self, f)
        r = f(*p, **d)
        yield r
        while r['pagination']['next_page'] is not None:
            if not d:
                d = {}
            if 'params' not in d:
                d['params'] = {}
            d['params']['page'] = r['pagination']['next_page']
            r = f(*p, **d)
            yield r
