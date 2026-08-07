import base64, os, secrets
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from urllib.parse import quote
from ..database import get_db
from ..models.subscription import Subscription
from ..models.user import User
from ..models.inbound import Inbound
from ..security import require_admin

router = APIRouter(tags=["subscriptions"])

def endpoint():
    tcp_domain = os.getenv("RAILWAY_TCP_PROXY_DOMAIN")
    tcp_port = os.getenv("RAILWAY_TCP_PROXY_PORT")
    if tcp_domain and tcp_port:
        return tcp_domain, int(tcp_port), "tcp"
    host = os.getenv("RAILWAY_PUBLIC_DOMAIN")
    return host, 443, "http"

def make_uri(user: User, inbound: Inbound | None = None):
    host, port, mode = endpoint()
    if not host:
        host = os.getenv("PUBLIC_HOST", "YOUR-DOMAIN")

    inbound = inbound or Inbound(
        name="xhttp",
        protocol="vless",
        transport="xhttp",
        security="reality",
        listen_port=443,
        path="/xhttp"
    )

    params = {
        "encryption": "none",
        "type": inbound.transport,
    }

    if inbound.transport == "grpc":
        params["serviceName"] = inbound.path or "grpc"
    else:
        params["path"] = inbound.path or "/xhttp"

    custom = {}
    try:
        custom = __import__("json").loads(inbound.settings_json or "{}")
    except Exception:
        custom = {}

    if inbound.security == "reality":
        from ..xray.reality import reality_parameters
        rp = custom.get("realitySettings") or reality_parameters()
        params.update({
            "security": "reality",
            "sni": (rp.get("serverNames") or [rp.get("serverName", "www.microsoft.com")])[0],
            "fp": "chrome",
            "pbk": rp.get("password") or rp.get("publicKey", ""),
            "sid": (rp.get("shortIds") or [rp.get("shortId", "")])[0],
        })
    elif inbound.security == "tls":
        params["security"] = "tls"
        params["sni"] = os.getenv("PUBLIC_HOST") or host
        params["fp"] = "chrome"
    else:
        params["security"] = "none"

    if inbound.transport == "xhttp":
        params["mode"] = "auto"

    query = "&".join(f"{k}={quote(str(v), safe='')}" for k, v in params.items() if v is not None)
    return f"vless://{user.uuid}@{host}:{port}?{query}#{quote(user.username)}"

@router.post("/api/subscriptions/{user_id}")
def create_subscription(user_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    token = secrets.token_urlsafe(32)
    sub = Subscription(user_id=user.id, token=token)
    db.add(sub)
    db.commit()
    return {"token": token, "url": f"/sub/{token}", "uri": make_uri(user)}

@router.get("/api/users/{user_id}/links")
def user_links(user_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    inbounds = db.query(Inbound).filter(Inbound.enabled.is_(True)).all()
    return {
        "user": {"id": user.id, "username": user.username, "uuid": user.uuid},
        "links": [
            {
                "inbound_id": i.id,
                "name": i.name,
                "uri": make_uri(user, i),
            }
            for i in inbounds
        ]
    }

@router.get("/sub/{token}", response_class=PlainTextResponse)
def subscription(token: str, db: Session = Depends(get_db)):
    sub = db.query(Subscription).filter(
        Subscription.token == token,
        Subscription.enabled.is_(True)
    ).first()
    if not sub:
        raise HTTPException(404, "Subscription not found")
    user = db.get(User, sub.user_id)
    if not user or not user.enabled:
        raise HTTPException(404, "User disabled")
    return base64.b64encode((make_uri(user) + "\n").encode()).decode()
