import urllib
import json
import os
from flask import Flask
from flask import request
from flask import make_response
from cloudant.client import Cloudant
import requests
from PIL import Image
from PIL import ImageFilter
from io import BytesIO
from boto.s3.connection import S3Connection
import tinys3
from urllib.request import urlopen, Request
import xml.etree.ElementTree as ET

app = Flask(__name__)
 
USERNAME = "897fdf82-b8b6-46a4-9470-9d03b35b33c7-bluemix"
PASSWORD = "9d73b33828bb57c816434eda6f6f4da5d57abc81c449e524b9790728deb59813"
URL = "https://897fdf82-b8b6-46a4-9470-9d03b35b33c7-bluemix:9d73b33828bb57c816434eda6f6f4da5d57abc81c449e524b9790728deb59813@897fdf82-b8b6-46a4-9470-9d03b35b33c7-bluemix.cloudant.com"
global db_client
db_client = Cloudant(USERNAME, PASSWORD, url=URL)
db_client.connect()
DB = "bi"
my_db = db_client[DB]
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    print("Request:")
    #global data1
    global system
    global params
    system = req["result"]["action"]
    params = req["result"]["parameters"]["Time-period"]
    print("params:",params)
    print(json.dumps(req, indent=4))
    res = makeWebhookResult(req)
    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r
def makeWebhookResult(req):
    query1 =  {"Action": {"$eq":system},"keyword":{"$eq":params}}
    docs1 = my_db.get_query_result(query1)  
    print("doc",docs1)
    for doc in docs1:
        aa = doc
        print("data",aa)
        data1= aa["link"]
        print ("data",data1)
        url = data1 
        headers = {'X-Tableau-Auth': 'pbcqWL5cTrSzy_I4p7PEBg|mKSk8G9GaX05BuR3doEwzOTft6tnqVdc'}
        auth = ('smanasa597@gmail.com','Miracle@123')
        a = requests.get(url,headers=headers,auth=auth)
        print(type(BytesIO(a.content)))
        print("a",a)
        bb = Image.open(BytesIO(a.content))
        bb.save("bb.png")
        conn = tinys3.Connection('AKIAIEUNKAEFU3RU3ZUA','lWzDUxiEbq+Rj4m7bDp4/hJa1yipPOEcqUBzZIth',tls=True)
        f = open('bb.png','rb')
        conn.upload('bb.png',f,'cognitive12345')
        print("uploaded")
        connection = S3Connection(
            aws_access_key_id='AKIAIEUNKAEFU3RU3ZUA',
            aws_secret_access_key='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')
        link = connection.generate_url(
            60,
            'GET',
            'cognitive12345',
            'bb.png',
            response_headers={
            'response-content-type': 'application/octet-stream'
            })  
        
        return{
		"messages": [
        {
          "type": 0,
          "platform": "slack",
          "speech": "Here is the result for the requested query,"
        },
        {
          "type": 3,
          "platform": "slack",    
          "imageUrl": link
        }
        ]
        }
    else:
            return{
            "speech": "Sorry! failed to show the query results",
            "messages": [
            {
              "type": 0,
              "platform": "slack",
              "speech": "Sorry! failed to show the query results"
            }
            ]
            }
    
if __name__ == '__main__':
    port = int(os.getenv('port',5001))
    print("server is running at %d" %(port))
    app.run(debug=True, port = port)