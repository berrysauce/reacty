import dns.resolver
from deta import Deta
from dotenv import load_dotenv
import os


load_dotenv()
deta = Deta(os.getenv("DETA_TOKEN"))
verifydb = deta.Base("reacty-siteverify")
 
def verify(domain: str):
    verification = verifydb.fetch({"domain": domain}).items
    if len(verification) == 0:
        verifykey = str(os.urandom(24).hex())
        verifydb.insert({
            "domain": domain,
            "verifykey": verifykey
        })
        return verifykey
    else:
        verification = verification[0]
        verifykey = verification["verifykey"]
    
    try:
        answers = dns.resolver.query(domain, "TXT")
    except dns.resolver.NoAnswer:
        return False
    
    if len(answers) == 0:
        return False
    
    for rdata in answers:
        for txt_string in rdata.strings:
            txt_string = txt_string.decode("utf-8")
            if txt_string == f"reacty-verification={verifykey}":
                verifydb.delete(verification["key"])
                return True
        return False
    
    