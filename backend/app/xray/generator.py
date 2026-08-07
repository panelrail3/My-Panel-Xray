import json, os, tempfile
from pathlib import Path
from ..models.user import User
from ..models.inbound import Inbound
from .transports import validate_combination

def build_stream(inbound: Inbound) -> dict:
    settings = json.loads(inbound.settings_json or "{}")
    stream = {"network": inbound.transport, "method": inbound.transport, "security": inbound.security}
    # Xray currently documents streamSettings.method; network is retained only for
    # compatibility with older client ecosystems and can be removed if desired.
    if inbound.transport == "raw":
        stream["rawSettings"] = settings.get("rawSettings", {})
    elif inbound.transport == "xhttp":
        stream["xhttpSettings"] = settings.get("xhttpSettings", {"path": inbound.path or "/xhttp"})
    elif inbound.transport == "websocket":
        stream["wsSettings"] = settings.get("wsSettings", {"path": inbound.path or "/ws"})
    elif inbound.transport == "grpc":
        stream["grpcSettings"] = settings.get("grpcSettings", {"serviceName": inbound.path or "grpc"})
    elif inbound.transport == "httpupgrade":
        stream["httpupgradeSettings"] = settings.get("httpupgradeSettings", {"path": inbound.path or "/upgrade"})
    if inbound.security == "tls":
        stream["tlsSettings"] = settings.get("tlsSettings", {})
    elif inbound.security == "reality":
        stream["realitySettings"] = settings.get("realitySettings", {})
    return stream

def build_inbound(inbound: Inbound, users: list[User]) -> dict:
    validate_combination(inbound.transport, inbound.security)
    vusers=[]
    for u in users:
        if not u.enabled:
            continue
        item={"id":u.uuid,"level":0,"email":u.username}
        if inbound.flow:
            item["flow"]=inbound.flow
        vusers.append(item)
    return {
        "tag": inbound.name,
        "listen": inbound.listen_host,
        "port": inbound.listen_port,
        "protocol": inbound.protocol,
        "settings": {"users": vusers, "decryption": "none"},
        "streamSettings": build_stream(inbound),
    }

def build_config(inbounds, users):
    return {
        "log": {"loglevel": "warning"},
        "api": {"tag": "api", "listen": "127.0.0.1:10085", "services": ["StatsService"]},
        "stats": {},
        "policy": {
            "levels": {"0": {
                "handshake": 4, "connIdle": 300, "uplinkOnly": 2, "downlinkOnly": 5,
                "statsUserUplink": True, "statsUserDownlink": True,
                "statsUserOnline": True, "bufferSize": 4
            }},
            "system": {
                "statsInboundUplink": True, "statsInboundDownlink": True,
                "statsOutboundUplink": True, "statsOutboundDownlink": True
            }
        },
        "inbounds": [build_inbound(i, users) for i in inbounds if i.enabled],
        "outbounds": [{"protocol": "freedom", "tag": "direct"}]
    }

def write_atomic(config: dict, target: str):
    target_path=Path(target); target_path.parent.mkdir(parents=True, exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=".xray-",suffix=".json",dir=target_path.parent)
    try:
        with os.fdopen(fd,"w") as f:
            json.dump(config,f,indent=2,ensure_ascii=False)
            f.flush(); os.fsync(f.fileno())
        os.replace(tmp,target)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
