import json
import os
import csv
import io
import requests
from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import send_file
from flask import Response
from flask import jsonify
from flask import redirect
from flask import url_for
from uuid import uuid4
from flask_bootstrap import Bootstrap
from twitterscraper import query_tweets

## package app
def create_app():
	app = Flask(__name__)
	Bootstrap(app)
	with open('conf/conf.json') as f:
		conf = json.load(f)
		app.config['PORT'] = conf['PORT']
		app.config['DEBUG_LEVEL'] = conf['DEBUG_LEVEL']
	return app

try:
	app = create_app()
except BaseException as error:
	print('An exception occurred : {}'.format(error))

## before rendering app
@app.before_request
def before_request():
    try:
        # session['api_key'] = app.config['api_key']
        if 'access_token' not in session and request.endpoint != 'login':
            if 'auth' in request.endpoint:
                return auth()
            elif 'grant' in request.endpoint:
                return grant()            
            return redirect(url_for('login'))
    except BaseException as e:
        print(e)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', error=error)

## starting rendering app.html
@app.route("/")
def home():
	print("hello")
	return render_template('home.html')

@app.route("/processing", methods=['POST', 'GET'])
def processing():
	# type of query
	hashtag = str(request.form.get('hashtag'))
	account = str(request.form.get('account'))
	query = str(request.form.get('query'))
	
	# select query by
	infinite = request.form.get('infinite')
	size = int(request.form.get('size'))
	date = request.form.get('date')
	
	# prepare query
	if query:
		query = query
	elif hashtag:
		query = hashtag
	elif account:
		query = account

	# CHUNK_FILE = 10
	output_file = str(query.replace(" ","_"))
	bucket_data = []

	# if date
	if date == 'enabled':
		date_start = request.form.get('date_start')
		date_end = request.form.get('date_end')
		query = query + '%20since%3A' + date_start + '%20until%3A' + date_end

	# infinite scrolling or sized buckets
	if infinite == 'enabled':
		for tweet in query_tweets(query):
			bucket_data.append(vars(tweet))
	else:
		for tweet in query_tweets(query, size):
			bucket_data.append(vars(tweet))

	#special for date as cortext readable date
	for tweet in bucket_data:
		tweet['timestamp'] = tweet['timestamp'].strftime("%Y-%m-%d %H:%M:%S")

	# package everything 
	info = {
		"QUERY" : query,
		"SIZE" : size,
		"TWEETS" : bucket_data
	}	

	# choose between CSV or JSON
	datatype = request.form.get('datatype')
	
	if datatype == 'json':
		return jsonify(info)

	elif datatype == 'csv':
		keys = bucket_data[0].keys()
		output = io.StringIO()
		dict_writer = csv.DictWriter(output, keys)
		dict_writer.writeheader()
		dict_writer.writerows(bucket_data)
		csvdata = output.getvalue()
		return Response(
			csvdata,
			mimetype="text/csv",
			headers={"Content-disposition":
					 "attachment; filename="+query+".csv"})
	
	else:
		return render_template('home.html')

##########################################################################
# OAuth
##########################################################################
@app.route('/login')
def login():   
    return render_template('login.html')

@app.route('/grant', methods=['GET'])
def grant():
    with open('conf/conf.json') as conf_file:
        conf_data = json.load(conf_file)
        grant_host_url = conf_data['grant_host_url']
        redirect_uri_conf = conf_data['redirect_uri']

    grant_url = grant_host_url + "/auth/authorize" + \
                "?response_type=code" + \
                "&state=" + str(uuid4().hex) + \
                "&client_id=pytheas" + \
                "&redirect_uri=" + redirect_uri_conf

    headers = {
        'Location': grant_url
    }

    return Response(grant_url, status=302, headers=headers)

@app.route('/auth', methods=['GET'])
def auth():
    code = str(request.args['code']) 
    state = str(request.args['state']) 

    with open('conf/conf.json') as conf_file:
        conf_data = json.load(conf_file)
        redirect_uri_conf = conf_data['redirect_uri']
        grant_host_url = conf_data['grant_host_url']

    payload = {
      'code': code,
      'state': state,
      'client_id': 'pytheas',
      'client_secret': 'mys3cr3t',
      'redirect_uri': redirect_uri_conf,
      'grant_type': 'authorization_code'
    }

    r_grant = requests.post(grant_host_url + '/auth/grant', data=payload)
    data = r_grant.json()
    print()
    print(data)
    print()
    r_access = requests.get(grant_host_url + '/auth/access?access_token=' + str(data['access_token']))
    
    session['access_token'] = data['access_token']
    session['profil'] = r_access.json()

    return redirect(url_for('home'))

##########################################################################
# Start
##########################################################################
if __name__ == '__main__':
	app.secret_key = os.urandom(24)
	app.jinja_env.auto_reload = True
	app.config['TEMPLATES_AUTO_RELOAD']=True
	app.run(debug=True, host='0.0.0.0', port=8080, threaded=True)
