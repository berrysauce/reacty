import uvicorn
from fastapi import FastAPI, Response, Request, HTTPException, Form, status, Depends, Cookie, Header
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
import secure
from deta import Deta
from dotenv import load_dotenv
import os
from tools import hashing, dnsverify, htmlgen
from datetime import datetime, timedelta
import sentry_sdk
import requests
import json


"""
-----------------------------------------------------------------------------
                                SETUP
-----------------------------------------------------------------------------
"""

# INITIALIZE SENTRY ############################################

sentry_sdk.init(
    "https://945096747f3a40a68a51ed8d493be8d8@o309026.ingest.sentry.io/5955006",
    traces_sample_rate=1.0
)

# APPLICATION SETUP ############################################

load_dotenv()
app = FastAPI(
    docs_url=None,
    redoc_url=None
)
deta = Deta(os.getenv("DETA_TOKEN"))
sitesdb = deta.Base("reacty-sites")
templates = Jinja2Templates(directory="templates")

app.mount("/assets", StaticFiles(directory="templates/assets"), name="assets")
app.mount("/forgot/assets", StaticFiles(directory="templates/assets"), name="assets")

SECRET_KEY = str(os.getenv("AUTH_SECRET"))
ALGORITHM = "HS256"
# PRODUCTION EXPIRY: 720
ACCESS_TOKEN_EXPIRE_MINUTES = 720

# SECURE HEADERS & CONTENT SECURITY POLCIY #####################

#secure_csp = (
#    secure.ContentSecurityPolicy()
#    .font_src("'self'", "https://fonts.googleapis.com", "https://fonts.gstatic.com", "https://cdnjs.cloudflare.com")
#    .script_src("'self'", "https://*.hcaptcha.com", "https://*.cloudflareinsights.com", "https://*.cloudflare.com", "https://cdn.jsdelivr.net")
#)
# secure_headers = secure.Secure(csp=secure_csp)

secure_headers = secure.Secure()

# FUNCTION AND CLASS DECLARATION ###############################

def createtoken(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Creates JWT token
    """
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(access_token: Optional[str] = Cookie(None)):
    """
    Gets current user by JWT token
    """
    
    if access_token is None:
        #raise HTTPException(status_code=401, detail="Unauthorized. Authentication failed.")
        return None
    
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

def verifycaptcha(response: str):
    """
    Verifies that hCaptcha result is valid
    """
    
    data = {"secret": str(os.getenv("CAPTCHA_SECRET")), "response": response}
    r = requests.post("https://hcaptcha.com/siteverify", data=data)
    if r.status_code == 200 and json.loads(r.text)["success"] == True:
        return True
    else:
        return False

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

@app.get("/terms")
def terms(request: Request):
    return templates.TemplateResponse("terms.html", {"request": request})

@app.get("/privacy")
def privacy(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request})

@app.get("/login")
def login(request: Request, error: Optional[str] = None):
    if error == None:
        popup = ""
    elif error == "auth":
        popup = htmlgen.loginalert("Wrong domain/password.")
    elif error == "captcha":
        popup = htmlgen.loginalert("Captcha failed.")
    elif error == "locked":
        popup = htmlgen.loginalert("This account was locked. Contact support for further details.")
    else:
        popup = htmlgen.loginalert("Login error.")
        
    return templates.TemplateResponse("login.html", {"request": request, "login_alert": popup})

@app.get("/signup")
def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/forgot")
def forgot(request: Request):
    return templates.TemplateResponse("forgot-step1.html", {"request": request})

@app.get("/dashboard")
def dashboard(request: Request, key: str = Depends(get_current_user)):
    if key is None:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
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
                            SIGNUP / LOGIN
-----------------------------------------------------------------------------
"""
@app.post("/login/auth")
def loginauth(response: Response, username: str = Form(...), password: str = Form(...), captcha: str = Form(None, alias="h-captcha-response")):
    """
    Handles user authentication 
    """
    
    domain = username
    if captcha is None:
        return RedirectResponse(url=f"/login?error=captcha", status_code=status.HTTP_303_SEE_OTHER)
    else:
        if verifycaptcha(captcha) is False:
            return RedirectResponse(url=f"/login?error=captcha", status_code=status.HTTP_303_SEE_OTHER)
    
    try:
        site = sitesdb.fetch({"domain": domain}).items[0]
    except IndexError:
        return RedirectResponse(url=f"/login?error=auth", status_code=status.HTTP_303_SEE_OTHER)
    
    if hashing.verifypw(site["password"], password) is False:
        return RedirectResponse(url=f"/login?error=auth", status_code=status.HTTP_303_SEE_OTHER)
    
    if site["locked"] is True:
        return RedirectResponse(url=f"/login?error=locked", status_code=status.HTTP_303_SEE_OTHER)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = createtoken(
        data={"sub": site["key"]}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=access_token)
    return response

@app.get("/logout")
def logout(response: Response, key: str = Depends(get_current_user)):
    """
    Logs out user
    """
    
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    return response

@app.post("/login/create")
def create(username: str = Form(...), password: str = Form(...), captcha: str = Form(None, alias="h-captcha-response")):
    """
    Creates a new user
    """
    
    if captcha is None:
        raise HTTPException(status_code=401, detail="Unauthorized. Captcha failed.")
    else:
        if verifycaptcha(captcha) is False:
            raise HTTPException(status_code=401, detail="Unauthorized. Captcha failed.")
    
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


"""
-----------------------------------------------------------------------------
                            PASSWORD RESET
-----------------------------------------------------------------------------
"""

@app.post("/login/reset")
def loginreset(username: str = Form(...), captcha: str = Form(None, alias="h-captcha-response")):
    """
    Handles password resets
    """
    
    domain = username
    try:
        site = sitesdb.fetch({"domain": domain}).items[0]
    except IndexError:
        raise HTTPException(status_code=401, detail="Reset request failed. Domain is not registered.")
    
    if captcha is None:
        raise HTTPException(status_code=401, detail="Unauthorized. Captcha failed.")
    else:
        if verifycaptcha(captcha) is False:
            raise HTTPException(status_code=401, detail="Unauthorized. Captcha failed.")
    
    verification = dnsverify.start(domain)
    if verification is None:
        raise HTTPException(status_code=400, detail="Reset already in progress")
    key = verification["key"]
    return RedirectResponse(url=f"/forgot/2?key={key}", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/login/reset/check")
def loginresetcheck(key: str):
    """
    Checks if the correct TXT DNS record to reset the user's password is set
    """
    
    verification = dnsverify.verify(key)
    if verification is None:
        raise HTTPException(status_code=404, detail="Reset key not found")
    else:
        if dnsverify.get(key)["records"] is True:
            return {"records": True}
        else:
            return {"records": verification}

@app.post("/login/reset/set")
def loginset(key: str, password: str = Form(...)):
    """
    Sets a new account password
    """
    
    verification = dnsverify.get(key)
    if verification is None:
        raise HTTPException(status_code=404, detail="Reset key not found")
    elif verification["records"] is False:
        raise HTTPException(status_code=404, detail="Reset key not found")
    
    site = sitesdb.fetch({"domain": "http://"+verification["domain"]}).items
    if len(site) != 0:
        site = site[0]
    else:
        site = sitesdb.fetch({"domain": "https://"+verification["domain"]}).items[0]
    
    dnsverify.delete(key)
    sitesdb.update(key=site["key"], updates={"password": hashing.hashpw(password)})
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    
@app.get("/forgot/2")
def forgot2(request: Request, key: str):
    """
    Displays fogot (step 2) page
    """
    
    verification = dnsverify.get(key)
    if verification is None:
        raise HTTPException(status_code=404, detail="Reset key not found")
    
    return templates.TemplateResponse("forgot-step2.html", {
        "request": request, 
        "domain": verification["domain"], 
        "verify_key": verification["verifykey"]
    })

@app.get("/forgot/3")
def forgot3(request: Request, key: str):
    """
    Displays fogot (step 3) page
    """
    
    verification = dnsverify.get(key)
    dt = datetime.now()
    if verification is None:
        raise HTTPException(status_code=404, detail="Reset key not found")
    elif verification["records"] is False:
        raise HTTPException(status_code=404, detail="Reset key not found")
    elif dt.strftime("%d-%m-%Y") != verification["valid"]:
        dnsverify.delete(key)
        raise HTTPException(status_code=400, detail="Reset key invalid")
    
    return templates.TemplateResponse("forgot-step3.html", {
        "request": request, 
        "key": verification["key"]
    })



"""
-----------------------------------------------------------------------------
                               BACK END
-----------------------------------------------------------------------------
"""

@app.get("/api/{key}/widget.js")
def widgetjs(key: str):
    """
    Creates and serves widget for site
    """
    
    # add site key to widget code
    site = sitesdb.get(key)
    if site is False or site is None:
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
    """
    Receives and stores feedback reported from the widget
    """
    
    site = sitesdb.get(key)
    if not site:
        raise HTTPException(status_code=404, detail="Site key not found")
    
    if site["locked"] is True:
        raise HTTPException(status_code=401, detail="This account was locked. Contact support for further details.")
    
    if "http://" in site["domain"]:
        wwwsubstring = "http://"
    elif "https://" in site["domain"]:
        wwwsubstring = "https://"
        
    wwwcheck = site["domain"].replace(wwwsubstring, wwwsubstring + "www.")
    
    if origin is None:
        raise HTTPException(status_code=400, detail="Wrong or missing headers")
    elif origin != site["domain"] and origin != wwwcheck:
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
    """
    Changes account settings
    """
    
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
    """
    Clears the account's feedback
    """
    
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
    """
    Deletes the account
    """
    
    site = sitesdb.get(key)
    if site is False:
        raise HTTPException(status_code=404, detail="Site key not found")
    sitesdb.delete(key)
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


"""
-----------------------------------------------------------------------------
                             MIDDLEWARES
-----------------------------------------------------------------------------
"""

@app.middleware("http")
async def set_secure_headers(request, call_next):
    response = await call_next(request)
    secure_headers.framework.fastapi(response)
    return response
        
        
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