import os
from flask import Flask
from flask import render_template
from flask import request
from flask import Response
from flask_negotiate import consumes, produces
import json
import random
from redis import Redis

app = Flask(__name__)
app.config['REDIS_DB'] = 'art'
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis = Redis.from_url(redis_url)
links = []

def getlinks():
  global links
  if not links:
    with open('images.txt') as f:
      links = [line.rstrip() for line in f]
  return links

def dbset(form):
  print 'Received form input'
  print form['thing1']
  print form['thing2']
  print form['thing3']
  redis.set(app.config['REDIS_DB'] + ':xxx', 42)

def dbget():
  return redis.get(app.config['REDIS_DB'] +':xxx')

@app.route('/')
def main():
  return 'main'

# tell

@app.route('/tell', methods=['GET'])
def get():
  result = dbget()
  #return Response(json.dumps(result), mimetype='application/json')
  return render_template('tell.html', url=_showimage())

@app.route('/tell', methods=['POST'])
def set():
  dbset(request.form)
  return 'Thank you.'

@app.route('/images')
def images():
  return Response(json.dumps(getlinks()), mimetype='application/json')

# show

def _showimage():
  n = random.randint(0, len(getlinks()))
  return getlinks()[n]

@app.route('/show')
@produces('text/html', '*/*')
def showimage_html():
  return render_template('show.html', url=_showimage())

@app.route('/show')
@produces('application/json')
def showimage_json():
  return Response(json.dumps({'image':_showimage()}), mimetype='application/json')

if __name__ == '__main__':
  app.run(debug=True)

