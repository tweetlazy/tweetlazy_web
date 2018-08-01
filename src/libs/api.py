import json
import uuid

# third-party imports
import tweepy
from flask import Flask, redirect, request, send_from_directory, session
from flask_session import Session

from tweeli.core import TwitterCore

app = Flask(__name__)

objectStorage = {}

def isLoggedIn():
    app.logger.debug("login state : %s",str('twt_user' in session))
    if 'twt_user' in session:
        return True
    else:
        return False
@app.before_request
def before_request():
    app.logger.debug('before request %s',request.endpoint)
    if isLoggedIn():
        if request.endpoint == 'send_login':
            return redirect("/html/index.html",code=302)
        if request.endpoint == 'login':
            return redirect("/html/index.html",code=302)
        else:
            return
    else:
        if request.endpoint == 'send_login':
            return 
        if request.endpoint == 'login':
            return 
    return redirect("/html/login.html",code=302)
@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect("/html/login.html",code=302)
@app.route("/login", methods=['POST'])
def login():
    session['twt_user']=request.form.to_dict()
    if isLoggedIn():
        return redirect("/html/index.html",code=302)
    return '';
@app.route('/html/login.html')
def send_login():
    return send_from_directory('templates', "login.html")
@app.route('/html/<path:path>')
def send_webs(path):
    return send_from_directory('templates', path)
    
def fetch_and_store():
    datas = [
        {'x':[1,2,3],'y':[3,4,6],'name':'test1'},
        {'x':[1,2,3],'y':[3,4,6],'name':'test2'},
        {'x':[1,2,3],'y':[3,4,6],'name':'test3'},

    ]
    return [json.dumps(x) for x in datas]
@app.route("/data/chart", methods=['GET'])
def chart_data():
    data = fetch_and_store()
    data_str=",".join([str(x) for x in data ])
    return "var data = [%s];"%(data_str)
@app.route("/layout/chart", methods=['GET'])
def chart_layout():
    return """var layout = {
              title: 'Changes during last week',
              xaxis: {
                title: 'Days of the Week',
                showgrid: false,
                zeroline: false
              },
              yaxis: {
                title: 'Numbers',
                showline: false
              }
            };
    """
@app.route("/", methods=['GET', 'POST'])
def index():
    return redirect("/html/index.html",code=302)

@app.route("/api", methods=['GET', 'POST'])
def api():
    if 'action' in request.form:
        params = request.form.to_dict()
        action = params["action"]
        if action == "login":
            return login(params)
        else:
            if isLoggedIn():
                sessionID = session['sessionID']
                twitterCore = objectStorage[sessionID]
            else:
                errorMsg = {'status_code':'4401', 'description':'First you must log in!'}
                return json.dumps(errorMsg)
        if action in dir(twitterCore):
            method = getattr(twitterCore, action)
            try:
                result = method(**params)
            except Exception as e:
                errorMsg = {'status_code':'4400', 'description':str(e)}
                return json.dumps(errorMsg)
            if type(result) == tweepy.cursor.ItemIterator:
                results = []
                for res in result:
                    results.append(res._json)
                finalRes = {"status_code":"2200", "response":results}
                return json.dumps(finalRes)
            if "_json" in dir(result):
                finalRes = {"status_code":"2200", "response":result._json}
            else:
                finalRes = {"status_code":"2200", "response":result}
            return json.dumps(finalRes)
        else:
            errorMsg = {'status_code':'4401', 'description':'Action %s is not defined!'%action}
            return json.dumps(errorMsg) 
    else:
        errorMsg = {'status_code':'4400', 'description':'Param action is not exist!'}
        return json.dumps(errorMsg)

def runServer():
    # import logging
    # log = logging.getLogger('werkzeug')
    # log.disabled = True
    # Session(app)
    app.secret_key = 'lvkjlfLJLJEIOFs;ffiojsfjelsk'
    app.config['SESSION_TYPE']='filesystem'
    Session(app)
    app.run(host='0.0.0.0',debug=True)

if __name__ == "__main__":
    runServer()
