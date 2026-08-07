import base64, os, secrets
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.subscription import Subscription
from ..models.user import User
from ..security import require_admin

router=APIRouter(tags=["subscriptions"])

def endpoint():
    if os.getenv("RAILWAY_TCP_PROXY_DOMAIN") and os.getenv("RAILWAY_TCP_PROXY_PORT"):
        return os.getenv("RAILWAY_TCP_PROXY_DOMAIN"), int(os.getenv("RAILWAY_TCP_PROXY_PORT")), "tcp"
    host=os.getenv("RAILWAY_PUBLIC_DOMAIN")
    return host, 443, "public"

def make_uri(user:User):
    host,port,mode=endpoint()
    params="type=xhttp&path=%2Fxhttp"
    # Public Networking terminates HTTPS at Railway; do not falsely claim end-to-end TLS.
    if mode=="tcp": params+="&security=tls"
    return f"vless://{user.uuid}@{host}:{port}?{params}#{user.username}"

@router.post("/api/subscriptions/{user_id}")
def create_subscription(user_id:int,db:Session=Depends(get_db),_=Depends(require_admin)):
    user=db.get(User,user_id)
    if not user: raise HTTPException(404,"User not found")
    token=secrets.token_urlsafe(32); sub=Subscription(user_id=user.id,token=token)
    db.add(sub); db.commit()
    return {"token":token,"url":f"/sub/{token}","uri":make_uri(user)}

@router.get("/sub/{token}",response_class=PlainTextResponse)
def subscription(token:str,db:Session=Depends(get_db)):
    sub=db.query(Subscription).filter(Subscription.token==token,Subscription.enabled.is_(True)).first()
    if not sub: raise HTTPException(404,"Subscription not found")
    user=db.get(User,sub.user_id)
    if not user or not user.enabled: raise HTTPException(404,"User disabled")
    return base64.b64encode((make_uri(user)+"\n").encode()).decode()
