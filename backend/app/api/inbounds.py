import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.inbound import Inbound
from ..schemas.inbound import InboundCreate, InboundResponse
from ..security import require_admin
from ..xray.transports import validate_combination
from ..xray.runtime import rebuild_and_restart

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
    i = Inbound(
        name=data.name,
        protocol=data.protocol,
        transport=data.transport,
        security=data.security,
        listen_port=data.listen_port,
        path=data.path,
        flow=data.flow,
        settings_json=json.dumps(data.settings),
    )
    db.add(i)
    db.commit()
    db.refresh(i)
    try:
        result = rebuild_and_restart(db)
        if result.get("status") == "error":
            db.delete(i)
            db.commit()
            rebuild_and_restart(db)
            raise HTTPException(status_code=422, detail=result.get("error"))
    except HTTPException:
        raise
    except Exception as e:
        db.delete(i)
        db.commit()
        rebuild_and_restart(db)
        raise HTTPException(status_code=500, detail=str(e))
    return i

@router.delete("/{inbound_id}")
def delete_inbound(inbound_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    i = db.get(Inbound, inbound_id)
    if not i:
        raise HTTPException(404, "Inbound not found")
    db.delete(i)
    db.commit()
    result = rebuild_and_restart(db)
    return {"deleted": True, "xray": result}
