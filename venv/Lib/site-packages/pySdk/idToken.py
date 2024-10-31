import json
from jose import jwt

import requests


class idToken:
    def __init__(self,token):
        self.token=token;
       
       
    def decodePayload(self):
        
        res=requests.get("https://api.secuuth.io/tokens/jwks")

        data=res.json()

        try:
            payload = jwt.decode(self.token,data, algorithms='RS256', options= {'verify_exp':True,'verify_aud': False,})
            
            return payload
        except:
            print("not verified")
            return {}

    def getSub(self):
        payload=self.decodePayload();
        return payload.get('sub')
    def getAud(self):
        payload=self.decodePayload();
        return payload.get('aud')
    def getIss(self):
        payload=self.decodePayload();
        return payload.get('iss')
    def getExp(self):
        payload=self.decodePayload();
        return payload.get('exp')
    def getJti(self):
        payload=self.decodePayload();
        return payload.get('jti')
    def getTyp(self):
        payload=self.decodePayload();
        return payload.get('typ')
    def getSignInMode(self):
        payload=self.decodePayload();
        return payload.get('signInMode')
    def getUserId(self):
        payload=self.decodePayload();
        return payload.get('userId')
    def getauthTime(self):
        payload=self.decodePayload();
        return payload.get('auth_time')
    def getIat(self):
        payload=self.decodePayload();
        return payload.get('iat')
    
    
        
        
  

    