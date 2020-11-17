from cloudant import Cloudant
from flask import Flask, render_template, request, jsonify
import atexit, os, json, requests

app = Flask(__name__, static_url_path='')

db_name = 'mydb'
client = None
db = None

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'cloudantNoSQLDB' in vcap:
        creds = vcap['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)
elif "CLOUDANT_URL" in os.environ:
    client = Cloudant(os.environ['CLOUDANT_USERNAME'], os.environ['CLOUDANT_PASSWORD'], url=os.environ['CLOUDANT_URL'], connect=True)
    db = client.create_database(db_name, throw_on_exists=False)
elif os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)

# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))

@app.route('/')
def root():
    with open('static/pass.txt') as p:
        password = p.read().strip()
    return render_template('index.html', password=password)

@app.route('/nlp')
def nlpurl():
    with open('static/pass.txt') as p:
        apikey = p.read().strip()
    if 'url' in request.args:
        url = request.args['url']
        data = {"url": url,"features": {"sentiment": {},"categories": {},"concepts": {},"entities": {},"keywords": {}}}
    if 'text' in request.args:
        text = request.args['text']
        data = {"text": text,"features": {"sentiment": {},"categories": {},"concepts": {},"entities": {},"keywords": {}}}
    headers = {'Content-Type': 'application/json',}
    res = requests.post('https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/4586da57-0316-4d69-b120-8fdfb17acf5a/v1/analyze?version=2019-07-12', headers=headers, json=data, auth=('apikey', apikey))
    out  = res.json()
    return out

@atexit.register
def shutdown():
    if client:
        client.disconnect()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
