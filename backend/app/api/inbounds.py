import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.inbound import Inbound
from ..schemas.inbound import InboundCreate, InboundResponse
from ..security import require_admin
from ..xray.transports import validate_combination

router = APIRouter(prefix="/api/inbounds", tags=["inbounds"])

@router.get("", response_model=list[InboundResponse])
def list_inbounds(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(Inbound).order_by(Inbound.id.desc()).all()

@router.post("", response_model=InboundResponse)
def create_inbound(data: InboundCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    try:
        validate_combination(data.transport, data.security)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    i = Inbound(name=data.name, protocol=data.protocol, transport=data.transport,
                security=data.security, listen_port=data.listen_port, path=data.path,
                flow=data.flow, settings_json=json.dumps(data.settings))
    db.add(i); db.commit(); db.refresh(i)
    return i
