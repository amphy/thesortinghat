from flask import Flask, request
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()
from ConfigParser import SafeConfigParser

import urllib3, certifi
from instagram import client
#from instagram.bind import InstagramAPIError
import json
import ssl
#from urllib.request import urlopen
app = Flask(__name__)

parser = SafeConfigParser()

CONFIG = {}

try:
    parser.read('/var/www/sekrit/config.ini')

    CONFIG = {
        'client_id': parser.get('instagram', 'client_id'),
        'client_secret': parser.get('instagram', 'client_secret'),
        'redirect_uri': parser.get('instagram', 'redirect_uri')
    }
except:
    print "Error"


unauthenticated_api = client.InstagramAPI(**CONFIG)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/authorize-instagram/")
def authorize_instagram():
    try:
      url = unauthenticated_api.get_authorize_url(scope=["basic"])
      return '<a href="%s">Connect With Instagram</a>' % url
    except Exception as e:
      return "authorized"

@app.route('/oauth_callback')
def on_callback():
    code = request.args.get('code')
    #access_token = ""
    response = None
    if not code:
        return "Missing code"
    try:
        #access_token, user_info = unauthenticated_api.exchange_code_for_access_token(code)
        #if not access_token:
            #return "Could not get access token"

        #api = client.InstagramAPI(access_token=access_token, client_secret=CONFIG['client_secret'])

        print CONFIG['client_id']
        encoded_body = "client_id={}&client_secret={}&redirect_uri={}&grant_type=authorization_code&code={}".format(CONFIG['client_id'], CONFIG['client_secret'], CONFIG['redirect_uri'], code)

        #print encoded_body

        #request = "https://api.instagram.com/v1/users/self/?access_token={0}".format(access_token)
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        r = http.request('POST', 'https://api.instagram.com/oauth/access_token', body=encoded_body)
        #html = r.read()
        something = json.loads(r.data)
        #print "hi"
        #print r.data
        boop = something['access_token']
        print something['user']['username']
        

        req = 'https://api.instagram.com/v1/users/self/media/recent/?access_token={}'.format(str(boop))
        print req
        b = http.request('GET', req)
        boo = json.loads(b.data)
        print boo

        for i in boo['data']:
            print i['images']['standard_resolution']['url'] 

    except Exception as e:
        print "Unknown error "
    
    return "handled code: " + code + "<br /> hey"

if __name__ == "__main__":
    app.run()
