import os
from flask import Flask
from flask import render_template
from flask import Response
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

def dbset():
  redis.set(app.config['REDIS_DB'] + ':xxx', 42)

def dbget():
  return redis.get(app.config['REDIS_DB'] +':xxx')

@app.route('/')
def main():
  return 'main'

@app.route('/artwork', methods=['GET'])
def get():
  result = dbget()
  return Response(json.dumps(result), mimetype='application/json')

@app.route('/artwork', methods=['POST'])
def set():
  dbset()
  return 'OK'

@app.route('/images')
def images():
  return Response(json.dumps(getlinks()), mimetype='application/json')

@app.route('/random-image')
def randomimage():
  n = random.randint(0, len(getlinks()))
  #return Response(json.dumps({'image':getlinks()[n]}), mimetype='application/json')
  return render_template('random-image.html', url=getlinks()[n])

if __name__ == '__main__':
  app.run(debug=True)

