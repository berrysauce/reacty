import uvicorn
from fastapi import FastAPI, Response, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
from deta import Deta
from dotenv import load_dotenv
import os
from tools import hashing
from datetime import datetime


load_dotenv()
app = FastAPI()
deta = Deta(os.getenv("DETA_TOKEN"))
sitesdb = deta.Base("feeed-sites")
templates = Jinja2Templates(directory="templates")

app.mount("/assets", StaticFiles(directory="templates/assets"), name="assets")
class LoginSite(BaseModel):
    domain: str
    password: str


"""
-----------------------------------------------------------------------------
                              FRONT END
-----------------------------------------------------------------------------
"""

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard")
def dashboard(request: Request):
    site = sitesdb.fetch({"domain": "example.com"}).items[0]
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "domain": site["domain"], 
        "positive_reactions": site["feedback"]["positive"], 
        "neutral_reactions": site["feedback"]["neutral"], 
        "negative_reactions": site["feedback"]["negative"], 
        "webkey": site["key"]
    })

"""
-----------------------------------------------------------------------------
                              BACK END
-----------------------------------------------------------------------------
"""

@app.post("/api/create")
def create(site: LoginSite):
    if len(sitesdb.fetch({"domain": site.domain}).items) != 0:
        # ---------------------------------------------------------- CHANGE LATER
        return {"msg": "Action failed, domain already exists!"}
    sitesdb.insert({
        "domain": site.domain,
        "password": hashing.hashpw(site.password),
        "created_on": str(datetime.now()),
        "feedback": {
            "positive": 0,
            "neutral": 0,
            "negative": 0
        },
        "locked": False
    })
    # ---------------------------------------------------------- CHANGE LATER
    return {"msg": "Action successfull!"}

@app.get("/api/{key}/widget.js")
def widgetjs(key: str):
    # add site key to widget code
    with open("tools/widget.js", "r") as f:
        widget = str(f.read())
        widget = widget.replace("[webkey]", key)
    return Response(content=widget, media_type="text/javascript")

@app.get("/api/{key}/report/{feedback}")
def getfeedback(key: str, feedback: str):
    site = sitesdb.get(key)
    if not site:
        return {"msg": "Site key doesn't exist."}
    if feedback == "1":
        newamount = site["feedback"]["positive"] + 1
        sitesdb.update(key=key, updates={
            "feedback": {
                "positive": newamount,
                "neutral": site["feedback"]["neutral"],
                "negative": site["feedback"]["negative"]
            }
        })
    elif feedback == "2":
        newamount = site["feedback"]["neutral"] + 1
        sitesdb.update(key=key, updates={
            "feedback": {
                "positive": site["feedback"]["positive"],
                "neutral": newamount,
                "negative": site["feedback"]["negative"]
            }
        })
    elif feedback == "3":
        newamount = site["feedback"]["negative"] + 1
        sitesdb.update(key=key, updates={
            "feedback": {
                "positive": site["feedback"]["positive"],
                "neutral": site["feedback"]["neutral"],
                "negative": newamount
            }
        })


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=80)