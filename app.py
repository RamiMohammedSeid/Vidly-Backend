# app.py
from flask import Flask, request, jsonify, abort
app = Flask(__name__)
from whitenoise import WhiteNoise

app.wsgi_app = WhiteNoise(app.wsgi_app, root='./static')
import urllib.request
import json
import pymongo
import random
import string
from tqdm import tqdm
import requests
import downloader
from bson.json_util import dumps
from bson.json_util import loads
import os
import wget
import ffmpeg
dirName = './static'
bashCommand = "bash apt-get install -y ffmpeg"
import subprocess
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
try:
    # Create target Directory
    os.mkdir(dirName)
    print("Directory " , dirName ,  " Created ") 
except FileExistsError:
    print("Directory " , dirName ,  " already exists")

def randomString(stringLength=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

client = pymongo.MongoClient("mongodb://rami:1234@vidly-cluster-shard-00-00-xhpaw.gcp.mongodb.net:27017,vidly-cluster-shard-00-01-xhpaw.gcp.mongodb.net:27017,vidly-cluster-shard-00-02-xhpaw.gcp.mongodb.net:27017/vidly-db?ssl=true&replicaSet=Vidly-cluster-shard-0&authSource=admin&retryWrites=true&w=majority")
database = client["vidly-db"]
series_collection = database["vidly-series"]
user_collection = database["vidly-users"]
episode_collection = database["vidly-episodes"]
def file_link(fileid):
    opener = urllib.request.build_opener()
    splitted_file_id = fileid.split("@")
    opener.addheaders = [('Authorization', 'Bearer '+splitted_file_id[1])]
    urllib.request.install_opener(opener)
    response = urllib.request.urlopen(f"https://api.pcloud.com/getfilelink?fileid={ splitted_file_id[0] }&contenttype=video/mp4&resolution=100/100")
    data = response.read().decode("utf-8")

    print(data)
    json_data = json.loads (str(data ))
    print(json_data)
    return "http://"+json_data["hosts"] [1]+json_data["path"]
    #return f"https://drive.google.com/uc?export=download&id={fileid}"


response = output
      
@app.route('/downloadvideo', methods=['GET'])
def downloadvideo():
    file_linked = file_link(request.args["id"])
    vidname = request.args["id"]+"."+file_linked.split(".")[-1]  
    if(os.path.isfile('./static/'+vidname)==False):
        print ("File doesn't exist")
        wget.download(file_linked,'./static/'+vidname)
        print("Done Downloading")

    return file_linked #"http://app-485da3dc-d460-43f7-906c-81aca17e1c2e.cleverapps.io/"+vidname
##    for i in episode_collection.find():
##    if(i["comming_soon"] == False):
##        print([i["episode_link"],file_link(i["episode_link"])])
##        wget.download(file_link(i["episode_link"]),"./static/"+i["episode_link"]+".mp4")
        
@app.route('/monitor', methods=['GET'])
def monitorv():

    return response


@app.route('/series', methods=['GET'])
def movies():
    handle = series_collection.find().limit(20)
    
    return (dumps(handle))

@app.route('/episodes', methods=['GET'])
def episodes():
    handle = episode_collection.find({"series_id":request.args["series_id"]}).sort("season_number",1).sort("episode_number",1)
    
    return (dumps(handle))


@app.route('/login', methods=['GET'])
def login():
    handle = user_collection.find_one({"email":request.args["email"], "passhash":request.args["passhash"]})
    if(handle != None):
        return jsonify({"info":"success","api":handle["api"]})

    
    return jsonify({"info":"200"})

@app.route('/search', methods=['GET'])
def search():
    list = series_collection.find({"series_name":{'$regex':"(?i)"+str(request.args["q"]).lower()}}).limit(20)
    
    return (dumps(list))



@app.route('/register', methods=['GET'])
def register():

    if(user_collection.find_one({"email":request.args["email"]}) != None):
        return jsonify({"info":"102"})
    if(user_collection.find_one({"name":request.args["name"]}) != None):
        return jsonify({"info":"190"})
    api_string = randomString(9)     
    user_collection.insert_one({"name":request.args["name"],"email":request.args["email"],"passhash":request.args["passhash"],"api":api_string})
    return jsonify({"info":"success","api":api_string})



@app.route('/', methods=['GET'])
def index(): 
    return "Hie it's Vidly"


@app.route('/getvideo', methods=['GET'])
def getvideo(): 
    opener = urllib.request.build_opener()
    opener.addheaders = [('Authorization', 'Bearer JYHF7Zl1uYf0p8mFSZfD3ia7ZydBK2Hf6cpLAy7uLjGp0pmrP9rCk')]
    urllib.request.install_opener(opener)
    response = urllib.request.urlopen(f"https://api.pcloud.com/getvideolink?path={ request.args['path'] }")

    json_data = json.loads (str(response.read().decode("utf-8") ))   
    return "http://"+json_data["hosts"] [0]+json_data["path"]



if __name__ == "__main__":
    app.run()