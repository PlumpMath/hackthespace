import os
from flask import Flask
from flask import render_template
from flask import request
from flask import Response
from flask_negotiate import consumes, produces
import hashlib
import json
import random
from redis import Redis

app = Flask(__name__)
app.config['REDIS_NS'] = 'art:'
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis = Redis.from_url(redis_url)
md5 = hashlib.md5()

links = []

def hash(s):
  md5.update(s)
  return md5.hexdigest()

def getlinks():
  global links
  if not links:
    with open('images.txt') as f:
      links = [line.rstrip() for line in f]
  return links

def dbset(form):
  if form['url']:
    #urlh = hash(form['url'])
    urlh = form['url']

    redis.sadd(app.config['REDIS_NS'] + "links", urlh)

    # bump all time interactions
    redis.incr(app.config['REDIS_NS'] + "hits")

    # bump this artwork seen count
    redis.incr(app.config['REDIS_NS'] + "hits:" + urlh)

    for it in ['thing1', 'thing2', 'thing3']:
      if form[it]:
        thing = ''.join(form[it].split()).lower()

        # bump thing usage all-time
        redis.zincrby(app.config['REDIS_NS'] + "things", thing, amount=1)

        # bump thing usage in this artwork
        key = app.config['REDIS_NS'] + urlh
        redis.zincrby(key, thing, amount=1)

# get all information pertaining to an image
def dbget(url, topN=10):
  hits = redis.get(app.config['REDIS_NS'] + "hits")
  hitsArtwork = redis.get(app.config['REDIS_NS'] + "hits:" + url)
  # get top N things
  things = redis.zrevrange(app.config['REDIS_NS'] + "things", 0, topN, withscores=True)
  thingsArtwork = redis.zrevrange(app.config['REDIS_NS'] + url, 0, topN, withscores=True)
  data = {'url':url, 'hits':hits, 'hits_artwork':hitsArtwork, 'things':things, 'things_artwork': thingsArtwork }
  return data 

@app.route('/')
def main():
  return render_template('main.html')

# tell

@app.route('/tell', methods=['GET'])
def get():
  return render_template('tell.html', url=_randomimagelink())

@app.route('/tell', methods=['POST'])
def set():
  dbset(request.form)
  return 'Thank you. View other contributions <a href="/show">here</a>.'

@app.route('/images')
def images():
  return Response(json.dumps(getlinks()), mimetype='application/json')

# show

def _randomimagelink():
  n = random.randint(0, len(getlinks()))
  return getlinks()[n]


@app.route('/show')
@produces('text/html', '*/*')
def showimage_html():
  # get a random image link from rated images
  url = redis.srandmember(app.config['REDIS_NS'] + "links")
  if url:
    # get all data for this link
    data = dbget(url)
    return render_template('show.html', data=data)
  else:
    return "Nothing yet"

@app.route('/show')
@produces('application/json')
def showimage_json():
  return Response(json.dumps({'image':_randomimagelink()}), mimetype='application/json')

if __name__ == '__main__':
  app.run(debug=True)

