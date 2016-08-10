from flask import Flask
from flask import request
from dejavu import Dejavu
from dejavu.recognize import FileRecognizer
import urllib2
import os
import tempfile
import json

app = Flask(__name__)

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('requests.log')
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)

config = {
     "database": {
         "host": os.environ['DEJAVU_DB_HOST'],
         "user": os.environ['DEJAVU_DB_USER'],
         "passwd": os.environ['DEJAVU_DB_PASSWORD'], 
         "db": os.environ['DEJAVU_DB_NAME']
     }
}

djv = Dejavu(config)

@app.route("/fingerprint", methods=['POST'])
def add_fingerprint():
	if not request.form['url']:
		return 'You must provide a URL that contains an audio file', 400
	if not request.form['name']:
		return 'You must provide a name for your fingerprint', 400

	tmp = tempfile.NamedTemporaryFile(delete=True)
	audioFile = urllib2.urlopen(request.form['url'])
	tmp.write(audioFile.read())
	djv.fingerprint_file(tmp.name, request.form['name'])
	tmp.close()

	return "fingerprinted " + request.form['name']

@app.route("/fingerprints", methods=['GET'])
def list_fingerprints():
	if djv.get_fingerprinted_songs():
		return djv.get_fingerprinted_songs()
	else:
		return "No fingerprints available yet."


@app.route("/recognize", methods=['POST'])
def recognize():
	if not request.form['url']:
		return 'You must provide a URL that contains an audio file to recognize', 400

	tmp = tempfile.NamedTemporaryFile(delete=True)
	audioFile = urllib2.urlopen(request.form['url'])
	tmp.write(audioFile.read())
	result = djv.recognize(FileRecognizer, tmp.name)
	tmp.close()

	return json.dumps(result)
	
	

if __name__ == "__main__":
    app.run()
