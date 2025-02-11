from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse

# Import database session and models
from app.db.database import SessionLocal, init_db
from app.db.database import (
    Project, Dataset, DatasetMetadata, Patient, PatientMetadata,
    Sample, SampleMetadata, RawFile, RawFileMetadata
)

router = APIRouter()

# ✅ Ensure database is initialized
init_db()

# ✅ Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ Fetch All Projects
@router.get("/projects/", response_model=List[Project])
async def get_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()


# ✅ Fetch All Patients with Sample Count
@router.get("/patients/", response_model=List[Patient])
async def get_patients(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    db: Session = Depends(get_db)
):
    query = db.query(Patient)
    if project_id:
        query = query.filter(Patient.project_id == project_id)

    return query.all()


# ✅ Fetch All Datasets
@router.get("/datasets/", response_model=List[Dataset])
async def get_datasets(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    dataset_id: Optional[int] = Query(None, description="Filter by dataset ID"),
    db: Session = Depends(get_db),
):
    query = db.query(Dataset)
    if project_id:
        query = query.filter(Dataset.project_id == project_id)
    if dataset_id:
        query = query.filter(Dataset.id == dataset_id)

    return query.all()


# ✅ Add Raw Files with Metadata
@router.post("/add_raw_files/")
async def add_raw_files(raw_files: List[RawFile], db: Session = Depends(get_db)):
    try:
        for raw_file in raw_files:
            db.add(raw_file)
        db.commit()
        return {"status": "success", "message": "Raw files added successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ✅ Fetch Raw Files with Metadata
@router.get("/raw_files_with_metadata/{dataset_id}", response_model=List[RawFile])
async def get_raw_files_with_metadata(dataset_id: int, db: Session = Depends(get_db)):
    return db.query(RawFile).filter(RawFile.dataset_id == dataset_id).all()
