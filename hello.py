from flask import Flask, request, render_template
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()
from ConfigParser import SafeConfigParser
import os
import urllib3, certifi
from instagram import client

from clarifai.client import ClarifaiApi

import json
import ssl

from nltk.corpus import wordnet

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

os.environ["CLARIFAI_APP_ID"] = parser.get('clarifai', 'app_id')
os.environ["CLARIFAI_APP_SECRET"] = parser.get('clarifai', 'app_secret')

unauthenticated_api = client.InstagramAPI(**CONFIG)
clarifai_api = ClarifaiApi()

gryffindor = ["brave", "daring", "nerve", "chivalry", "lion"]
hufflepuff = ["hard_work", "dedication", "patience", "loyalty", "fair", "badger"]
ravenclaw = ["intelligence", "knowledge", "wit", "wisdom", "eagle"]
slytherin = ["ambition", "cunning", "resourcefulness", "serpent"]

@app.route("/")
def authorize_instagram():
    try:
      url = unauthenticated_api.get_authorize_url(scope=["basic"])
      return render_template('index.html', url=url)
    except Exception as e:
      return "authorized"

@app.route('/oauth_callback')
def on_callback():
    code = request.args.get('code')
    response = None
    tagging = []
    images = []
    if not code:
        return "Missing code"
    try:

        print CONFIG['client_id']
        encoded_body = "client_id={}&client_secret={}&redirect_uri={}&grant_type=authorization_code&code={}".format(CONFIG['client_id'], CONFIG['client_secret'], CONFIG['redirect_uri'], code)

        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        r = http.request('POST', 'https://api.instagram.com/oauth/access_token', body=encoded_body)
        something = json.loads(r.data)
        boop = something['access_token']
        print something['user']['username']

        req = 'https://api.instagram.com/v1/users/self/media/recent/?access_token={}&count={}'.format(str(boop), "10")
        #print req
        b = http.request('GET', req)
        boo = json.loads(b.data)
        #print boo

        for i in boo['data']:
            print i['images']['standard_resolution']['url']
            images.append(str(i['images']['standard_resolution']['url'])) 

        #print os.environ.get('CLARIFAI_APP_ID', None)

        for j in images:
            result = clarifai_api.tag_image_urls(j)
            res = json.dumps(result)
            parsed_json = json.loads(res)
            imgtag = json.dumps(parsed_json['results'][0])
            parsed_json = json.loads(imgtag)
            imgtag2 = parsed_json['result']['tag']['classes']
            #imgtag = res['result']['tag']['classes']
            for x in imgtag2:
                tagging.append(str(x).replace(" ", "_"))
                #print x

        tagging = list(set(tagging))
        gTotal = 0
        hTotal = 0
        rTotal = 0
        sTotal = 0
        items = len(tagging)
        house = ""
        for i in tagging:
            imgWord = wordnet.synsets(i)
            for word in gryffindor:
                wordWord = wordnet.synsets(word)
                if imgWord and wordWord:
                    sim = imgWord[0].wup_similarity(wordWord[0])
                    if sim:
                        gTotal += sim
            for word in hufflepuff:
                wordWord = wordnet.synsets(word)
                if imgWord and wordWord:
                    sim = imgWord[0].wup_similarity(wordWord[0])
                    if sim:
                        hTotal += sim
            for word in ravenclaw:
                wordWord = wordnet.synsets(word)
                if imgWord and wordWord:
                    sim = imgWord[0].wup_similarity(wordWord[0])
                    if sim:
                        rTotal += sim
            for word in slytherin:
                wordWord = wordnet.synsets(word)
                if imgWord and wordWord:
                    sim = imgWord[0].wup_similarity(wordWord[0])
                    if sim:
                        sTotal += sim
        
        gyr = gTotal/items
        huf = hTotal/items
        rav = rTotal/items
        sly = sTotal/items
        
        max = gyr
        house = "Gryffindor"
        if max < huf:
            max = huf
            house = "Hufflepuff"
        if max < rav:
            max = rav
            house = "Ravenclaw"
        if max < sly:
            max = sly
            house = "Slytherin"

    except Exception as e:
        print e
    
    return render_template("results.html", house=house)

if __name__ == "__main__":
    app.run()
