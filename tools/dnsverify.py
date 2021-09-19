import dns.resolver
from deta import Deta
from dotenv import load_dotenv
import os
from datetime import datetime


load_dotenv()
deta = Deta(os.getenv("DETA_TOKEN"))
verifydb = deta.Base("reacty-siteverify")

def start(domain: str):
    verification = verifydb.fetch({"domain": domain}).items
    if len(verification) == 0:
        dt = datetime.now()
        verifykey = str(os.urandom(16).hex())
        res = verifydb.insert({
            "domain": domain.replace("http://", "").replace("https://", ""),
            "valid": dt.strftime("%d-%m-%Y"),
            "records": False,
            "verifykey": verifykey
        })
        return res
    else:
        return None
 
def get(key: str):
    verification = verifydb.get(key)
    if verification is None:
        return None
    else:
        return verification

def verify(key: str):
    verification = verifydb.get(key)
    if verification is None:
        return None
    else:
        verifykey = verification["verifykey"]
    
    try:
        answers = dns.resolver.query(verification["domain"], "TXT")
    except dns.resolver.NoAnswer:
        return False
    
    if len(answers) == 0:
        return False
    
    for rdata in answers:
        for txt_string in rdata.strings:
            txt_string = txt_string.decode("utf-8")
            if txt_string == f"reacty-verify={verifykey}":
                verifydb.update(key=verification["key"], updates={
                    "records": True
                })
                return True
        return False
    
def delete(key: str):
    try:
        verifydb.delete(key)
        return True
    except:
        return False
    
    