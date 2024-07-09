from flask import Flask, request, render_template
from difflib import Differ 
import requests
import collections
import datetime

differ=Differ()
app = Flask(__name__)
cache = {}
# https://en.wikipedia.org/w/api.php?action=query&format=json&prop=revisions&titles=Pet_door&formatversion=2&rvprop=content&rvslots=*&rvstart=2023-06-02T01%3A44%3A00.000Z&rvend=2024-07-09T01%3A44%3A00.000Z&rvdir=newer
def request_url(wikibaseurl="https://en.wikipedia.org/w/api.php", pagetitle="Donald_Trump", starttime="2020-02-09T02:42:57.512Z", endtime="2024-07-09T01:44:00.000Z"):
    if(pagetitle in cache.keys()):
        return cache[pagetitle]
    resp = requests.get(wikibaseurl, params={
        'action': 'query',
        'format': 'json',
        'prop': 'revisions',
        'titles': pagetitle,
        'formatversion': 2,
        'rvprop': 'content',
        'rvslots': '*',
        'rvstart': endtime,
        'rvend': starttime,
        'rvdir': 'older',
        'rvlimit': 50
    })
    rev = resp.json()["query"]["pages"][0]["revisions"]
    if not pagetitle in cache.keys():
        cache[pagetitle] = rev
    return rev
def compare(dataarg, start=0, end=3, minimum_prevalence=1):
    curr=dataarg[start].split("\n")
    for i in range(start+1,end):
        curr.extend(dataarg[i].split("\n"))
    dupes = [item for item, count in collections.Counter(curr).items() if count > int(minimum_prevalence)]
    dupes=list(set(dupes))
    dupes.sort()
    return dupes
def controversialness(dataarg, dupes):
    return max(0,int((1-len(dupes)/len(dataarg.split("\n")))*1000)/10)
select_info = lambda txt: txt["slots"]["main"]["content"]
def fullparse(pagetitle,minimum_prevalence=0.25, endtime=datetime.datetime.now().isoformat(), maxarticles=3):
    data = request_url(pagetitle=pagetitle)
    data = [select_info(i) for i in data]
    return compare(data,end=maxarticles,minimum_prevalence=minimum_prevalence)


@app.route('/')
def index():
    return render_template("index.html")
    
@app.route('/w')
def article_minprev_articleno():
    return "\n".join(fullparse(request.args.get("article"), minimum_prevalence=float(request.args.get("minprev")), maxarticles=int(request.args.get("articleno"))))

@app.route('/controversialness')
def controversialness_page():
    data=fullparse(request.args.get("article"), minimum_prevalence=float(request.args.get("minprev")), maxarticles=int(request.args.get("articleno")))
    return str(controversialness(
        select_info(request_url(pagetitle=request.args.get("article"))[-1]),
        data
    ))+"%"
@app.route('/render')
def render():
    return render_template("render.html")
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
