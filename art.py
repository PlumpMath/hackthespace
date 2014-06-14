import os
from flask import Flask
from flask import Response
import json

app = Flask(__name__)

links = []

def getlinks():
  global links
  if not links:
    with open('images.txt') as f:
      links = f.readlines()
      print '[%s]' % ', '.join(map(str, links))
  return links

@app.route('/')
def main():
  return 'main'

@app.route('/images')
def images():
  return Response(json.dumps(getlinks()),  mimetype='application/json')

if __name__ == '__main__':
  app.run(debug=True)

