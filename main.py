from flask import Flask, request, render_template
import requests, collections, urllib.parse
from typing import List

app = Flask(__name__)  # Get Flask ready
cache = {}  # Initialize the cache to nothing


def request_url(
    wikibaseurl: str = "https://en.wikipedia.org/w/api.php",
    pagetitle: str = "Python_(programming_language)",
    starttime: str = "2020-02-09T02:42:57.512Z",
    endtime: str = "2024-07-09T01:44:00.000Z",
):  # Get all the revisions (up to 10?) of a wikimedia page (by default Wikipedia)
    if pagetitle in cache.keys():
        return cache[
            pagetitle
        ]  # If the page title is in the cache, just return what we had there
    print(pagetitle, urllib.parse.unquote(pagetitle))
    resp = requests.get(
        wikibaseurl,
        params={  # Otherwise, do the GET request!
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "titles": urllib.parse.unquote(pagetitle),
            "formatversion": 2,
            "rvprop": "content",
            "rvslots": "*",
            "rvstart": endtime,
            "rvend": starttime,
            "rvdir": "older",
            "rvlimit": 50,
        },
    )
    if resp.status_code != 200:
        return ["Oops! Something went wrong."] * 10
    rev = resp.json()["query"]["pages"][0][
        "revisions"
    ]  # Go through the JSON 'till we get here
    if not pagetitle in cache.keys():
        cache[pagetitle] = rev  # If it's not in the cache, add it
    return rev  # Return the revisions


def compare(
    dataarg: List[str], start: int = 0, end: int = 3, minimum_prevalence: int = 1
) -> List[str]:
    curr = dataarg[start].split("\n")
    for i in range(start + 1, end):
        curr.extend(dataarg[i].split("\n"))  # Add every revision text to one list
    dupes = [
        item
        for item, count in collections.Counter(curr).items()
        if count > int(minimum_prevalence)
    ]  # If text is seen more than minimum_prevalence times, then add it into dupes
    dupes = list(set(dupes))  # Get unique names
    dupes.sort()
    return dupes


def controversialness(dataarg: str, dupes: List[str]) -> float:
    return max(0, int((1 - len(dupes) / len(dataarg.split("\n"))) * 1000) / 10)


select_info = lambda txt: txt["slots"]["main"][
    "content"
]  # Used for getting even deeper into each revision's JSON (from request_url[i] to actual text)


def fullparse(
    pagetitle: str, minimum_prevalence: int = 1, maxarticles: int = 3
) -> List[str]:  # Bring it all together!
    data = request_url(pagetitle=pagetitle)
    data = [select_info(i) for i in data]
    return compare(data, end=maxarticles, minimum_prevalence=minimum_prevalence)


@app.route("/")  # https://example.com
def index_page():
    return render_template("index.html")  # templates/index.html

@app.route("/render")  # https://example.com/render?article=... (generally)
def render():
    return render_template("render.html")  # templates/render.html

@app.route("/api")
def api():
    if(request.args.get("query")=="controversialness" or request.args.get("q")=="controversialness"): # https://example.com/api?query=controversialness&article=...&minprev=...&articleno=...
        if (
            request.args.get("minprev") in ["", None]
            or request.args.get("articleno") in ["", None]
            or request.args.get("article") in ["", None]
        ):
            return "0%"
        data = fullparse(
            request.args.get("article"),
            minimum_prevalence=float(request.args.get("minprev")),
            maxarticles=int(request.args.get("articleno")),
        )
        return (
            str(
                controversialness(
                    select_info(request_url(pagetitle=request.args.get("article"))[-1]),
                    data,
                )
            )
            + "%"
        )
    elif(request.args.get("query")=="text" or request.args.get("q")=="text"): # https://example.com/api?query=text&article=...&minprev=...&articleno=...
        return "\n".join(
            fullparse(
                request.args.get("article"),
                minimum_prevalence=float(request.args.get("minprev")),
                maxarticles=int(request.args.get("articleno")),
            )
        )
    else:
        return ""
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Run it!
