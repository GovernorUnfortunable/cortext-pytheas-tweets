import os
import csv
import io
from flask import Flask
from flask import render_template
from flask import request
from flask import send_file
from flask import Response
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

	hashtag = str(request.form.get('hashtag'))
	account = str(request.form.get('account'))
	query = str(request.form.get('query'))
	size = int(request.form.get('size'))
	date_start = request.form.get('date_start')
	date_end = request.form.get('date_end')

	if query:
		query = query
	elif hashtag:
		query = hashtag
	elif account:
		query = account

	# CHUNK_FILE = 10
	output_file = str(query.replace(" ","_"))
	bucket_data = []

	for tweet in query_tweets(query, size):
		bucket_data.append(vars(tweet))
		
	info = {
		"QUERY" : query,
		"SIZE" : size,
		"TWEETS" : bucket_data
	}

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


##########################################################################
# Start
##########################################################################
if __name__ == '__main__':
	app.secret_key = os.urandom(24)
	app.jinja_env.auto_reload = True
	app.config['TEMPLATES_AUTO_RELOAD']=True
	app.run(debug=True, host='0.0.0.0', port=8080, threaded=True)

