import os
import csv
import io
from flask import Flask
from flask import render_template
from flask import request
from flask import send_file
from flask import Response
from flask import jsonify
from flask_bootstrap import Bootstrap
from twitterscraper import query_tweets

def create_app():
  app = Flask(__name__)
  Bootstrap(app)
  return app

try:
	app = create_app()    
except BaseException as error:
	print('An exception occurred : {}'.format(error))

@app.route("/")
def hello():
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
		
		print(date_start)
		print(date_end)

		query = query + '%20since%3A' + date_start + '%20until%3A' + date_end

	# infinite scrolling or sized buckets
	if infinite == 'enabled':
		for tweet in query_tweets(query):
			bucket_data.append(vars(tweet))
	else:
		for tweet in query_tweets(query, size):
			bucket_data.append(vars(tweet))

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
	# request.form.get('date_end')

	


##########################################################################
# Start
##########################################################################
if __name__ == '__main__':
	app.secret_key = os.urandom(24)
	app.jinja_env.auto_reload = True
	app.config['TEMPLATES_AUTO_RELOAD']=True
	app.run(debug=True, host='0.0.0.0', port=8080, threaded=True)

