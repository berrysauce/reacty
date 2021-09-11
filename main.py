import uvicorn
from fastapi import FastAPI, Response, Request, HTTPException, Form, status, Depends, Cookie, Header
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
from deta import Deta
from dotenv import load_dotenv
import os
from tools import hashing
from datetime import datetime, timedelta
import sentry_sdk


# Initialize Sentry
sentry_sdk.init(
    "https://945096747f3a40a68a51ed8d493be8d8@o309026.ingest.sentry.io/5955006",
    traces_sample_rate=1.0
)

load_dotenv()
app = FastAPI()
deta = Deta(os.getenv("DETA_TOKEN"))
sitesdb = deta.Base("reacty-sites")
templates = Jinja2Templates(directory="templates")

app.mount("/assets", StaticFiles(directory="templates/assets"), name="assets")

SECRET_KEY = str(os.getenv("AUTH_SECRET"))
ALGORITHM = "HS256"
# PRODUCTION EXPIRY: 720
ACCESS_TOKEN_EXPIRE_MINUTES = 2

def createtoken(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(access_token: Optional[str] = Cookie(None)):
    if access_token is None:
        raise HTTPException(status_code=401, detail="Unauthorized. Authentication failed.")
    
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        key: str = payload.get("sub")
        if key is None:
            raise HTTPException(status_code=401, detail="Unauthorized. Authentication failed.")
    except JWTError:
        raise HTTPException(status_code=401, detail="Unauthorized. Session expired.")
    site = sitesdb.get(key)
    if site is False:
        raise HTTPException(status_code=401, detail="Unauthorized. Authentication failed.")
    return site["key"]

class Site(BaseModel):
    key: str

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

@app.get("/pricing")
def root(request: Request):
    return templates.TemplateResponse("pricing.html", {"request": request})

@app.get("/login")
def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signup")
def root(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/dashboard")
def dashboard(request: Request, key: str = Depends(get_current_user)):
    site = sitesdb.get(key)
        
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "domain": site["domain"], 
        "positive_reactions": site["feedback"]["positive"], 
        "neutral_reactions": site["feedback"]["neutral"], 
        "negative_reactions": site["feedback"]["negative"], 
        "webkey": key,
        "widgettext": site["widget"]["text"]
    })
    

"""
-----------------------------------------------------------------------------
                              BACK END
-----------------------------------------------------------------------------
"""
@app.post("/login/auth")
def loginauth(response: Response, username: str = Form(...), password: str = Form(...)):
    domain = username
    try:
        site = sitesdb.fetch({"domain": domain}).items[0]
    except IndexError:
        raise HTTPException(status_code=401, detail="Unauthorized. Authentication failed.")
    
    if hashing.verifypw(site["password"], password) is False:
        raise HTTPException(status_code=401, detail="Unauthorized. Authentication failed.")
    
    if site["locked"] is True:
        raise HTTPException(status_code=401, detail="This account was locked. Contact support for further details.")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = createtoken(
        data={"sub": site["key"]}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=access_token)
    return response

@app.get("/logout")
def logout(response: Response, key: str = Depends(get_current_user)):
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    return response

@app.post("/api/create")
def create(username: str = Form(...), password: str = Form(...)):
    domain = username
    if len(sitesdb.fetch({"domain": domain}).items) != 0:
        raise HTTPException(status_code=409, detail="Domain is already registered.")
    result = sitesdb.insert({
        "domain": domain,
        "password": hashing.hashpw(password),
        "created_on": str(datetime.now()),
        "widget": {
            "text": f"Any feedback for {domain}?"
        },
        "feedback": {
            "positive": 0,
            "neutral": 0,
            "negative": 0
        },
        "locked": False
    })
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = createtoken(
        data={"sub": result["key"]}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=access_token)
    return response

@app.get("/api/{key}/widget.js")
def widgetjs(key: str):
    # add site key to widget code
    site = sitesdb.get(key)
    if site is False:
        raise HTTPException(status_code=404, detail="Site key not found")
    
    if site["locked"] is True:
        raise HTTPException(status_code=401, detail="This account was locked. Contact support for further details.")
    
    with open("tools/widget.js", "r") as f:
        widget = str(f.read())
        widget = widget.replace("[webkey]", key)
        widget = widget.replace("[widgettext]", site["widget"]["text"])
    return Response(content=widget, media_type="text/javascript")

@app.get("/api/{key}/report/{feedback}")
def getfeedback(key: str, feedback: str, origin: Optional[str] = Header(None)):
    site = sitesdb.get(key)
    if not site:
        raise HTTPException(status_code=404, detail="Site key not found")
    
    if site["locked"] is True:
        raise HTTPException(status_code=401, detail="This account was locked. Contact support for further details.")
    
    if origin is None:
        raise HTTPException(status_code=400, detail="Wrong or missing headers")
    elif origin != site["domain"]:
        raise HTTPException(status_code=400, detail="Wrong or missing headers")
    
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
        
@app.post("/api/settings")
def widgetsettings(key: str = Depends(get_current_user), text: str = Form(...)):
    site = sitesdb.get(key)
    if site is False:
        raise HTTPException(status_code=404, detail="Site key not found")
    sitesdb.update(key=key, updates={
        "widget": {
            "text": text}
    })
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/api/clear")
def clearwidget(key: str = Depends(get_current_user)):
    site = sitesdb.get(key)
    if site is False:
        raise HTTPException(status_code=404, detail="Site key not found")
    sitesdb.update(key=key, updates={
        "feedback": {
            "positive": 0,
            "neutral": 0,
            "negative": 0
        }
    })
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/api/delete")
def deletewidget(key: str = Depends(get_current_user)):
    site = sitesdb.get(key)
    if site is False:
        raise HTTPException(status_code=404, detail="Site key not found")
    sitesdb.delete(key)
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
        
"""
-----------------------------------------------------------------------------
                            EXCEPTION HANDLER
-----------------------------------------------------------------------------
"""

@app.exception_handler(StarletteHTTPException)
async def custom_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse("error.html", {"request": request, "code": "404", "detail": "Sorry, but the requested resource couldn't be found. Try again later or check your request."})
    else:
        return templates.TemplateResponse("error.html", {"request": request, "code": str(exc.status_code), "detail": exc.detail})




if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=80)