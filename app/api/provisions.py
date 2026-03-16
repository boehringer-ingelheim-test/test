import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.provision import Provision
from app.schemas.provision import ProvisionCreate, ProvisionResponse, ProvisionListResponse
from app.services import terraform

router = APIRouter()
logger = logging.getLogger(__name__)


def _run_provision(provision_id: str, workspace: str, tshirt_size: str):
    """Background task: run terraform and update DB status."""
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        record = db.query(Provision).filter(Provision.id == provision_id).first()
        if not record:
            return
        record.status = "provisioning"
        db.commit()

        outputs = terraform.provision(workspace, tshirt_size)

        record.status = "active"
        record.outputs = outputs
        db.commit()
    except Exception as e:
        logger.error("Provisioning failed for %s: %s", provision_id, e)
        record.status = "failed"
        record.error = str(e)
        db.commit()
    finally:
        db.close()


def _run_deprovision(provision_id: str, workspace: str):
    """Background task: run terraform destroy and update DB status."""
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        record = db.query(Provision).filter(Provision.id == provision_id).first()
        if not record:
            return
        terraform.deprovision(workspace)
        record.status = "destroyed"
        db.commit()
    except Exception as e:
        logger.error("Deprovisioning failed for %s: %s", provision_id, e)
        record.status = "failed"
        record.error = str(e)
        db.commit()
    finally:
        db.close()


@router.post("", response_model=ProvisionResponse, status_code=202)
def create_provision(
    body: ProvisionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Request provisioning of a new cloud environment for a user/group."""
    existing = db.query(Provision).filter(Provision.name == body.name).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Provision '{body.name}' already exists.")

    record = Provision(
        name=body.name,
        owner=body.owner,
        tshirt_size=body.tshirt_size,
        terraform_workspace=body.name,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    background_tasks.add_task(
        _run_provision, record.id, record.terraform_workspace, record.tshirt_size
    )
    return record


@router.get("", response_model=ProvisionListResponse)
def list_provisions(db: Session = Depends(get_db)):
    """List all provisioning records."""
    items = db.query(Provision).all()
    return {"total": len(items), "items": items}


@router.get("/{provision_id}", response_model=ProvisionResponse)
def get_provision(provision_id: str, db: Session = Depends(get_db)):
    """Get status and details of a specific provision."""
    record = db.query(Provision).filter(Provision.id == provision_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Provision not found.")
    return record


@router.delete("/{provision_id}", response_model=ProvisionResponse, status_code=202)
def delete_provision(
    provision_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Trigger deprovisioning (terraform destroy) for a provision."""
    record = db.query(Provision).filter(Provision.id == provision_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Provision not found.")
    if record.status not in ("active", "failed"):
        raise HTTPException(
            status_code=409,
            detail=f"Cannot deprovision from status '{record.status}'.",
        )

    background_tasks.add_task(
        _run_deprovision, record.id, record.terraform_workspace
    )
    return record
