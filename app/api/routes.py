from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import SQLAlchemyError

# Import database session and SQLAlchemy models
from app.db.database import (
    SessionLocal, init_db,  # Database session and initialization
    Project, Dataset, DatasetMetadata, Patient, PatientMetadata,
    Sample, SampleMetadata, RawFile, RawFileMetadata
)

# Import Pydantic schemas (to use in `response_model`)
from app.schemas.schemas import (
    Project as ProjectSchema,
    Dataset as DatasetSchema,
    Patient as PatientSchema,
    RawFileResponse,
    DatasetMetadata as DatasetMetadataSchema, DatasetWithMetadata,
    PatientWithSampleCount, PatientMetadata as PatientMetadataSchema, PatientWithMetadata,
    SampleMetadata as SampleMetadataSchema, Sample as SampleSchema, SampleWithoutPatient,
    PatientWithSamples, RawFileMetadataCreate, RawFileCreate, MetadataUpdate
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


####################################### PASS ############################################
# ✅ 7️⃣ Add Raw Files with Metadata
@router.post("/add_raw_files/")
async def add_raw_files(raw_files: List[RawFileCreate], db: Session = Depends(get_db)):
    try:
        for raw_file in raw_files:
            #  Use ORM Model (`RawFile`) instead of Pydantic Response Model
            new_file = RawFile(dataset_id=raw_file.dataset_id, path=raw_file.path)  
            db.add(new_file)
            db.commit()
            db.refresh(new_file)  # Fetch latest changes (including `id`)

            #  Insert Metadata Using ORM Model (`RawFileMetadata`)
            if raw_file.metadata:
                for metadata in raw_file.metadata:
                    new_metadata = RawFileMetadata(
                        raw_file_id=new_file.id,
                        key_name=metadata.metadata_key,  
                        value=metadata.metadata_value
                    )
                    db.add(new_metadata)
                
                db.commit()

        return {"status": "success", "message": "Raw files and metadata added successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
#################################################################################################


 ############################### PASS ###################################   
    # ✅ Root Redirect
@router.get("/")
async def root():
    return RedirectResponse(url="/projects")
############################################################################

################################# PASS ##################################################
@router.get("/patients_metadata/{patient_id}", response_model=List[PatientWithSamples])
async def get_patients_metadata(
    project_id: int,
    patient_id: int,
    db: Session = Depends(get_db)
):
    try:
        # Query Patients for the given project_id
        query = db.query(Patient).filter(Patient.project_id == project_id)

        if patient_id != 0:
            query = query.filter(Patient.id == patient_id)

        patients = query.all()

        if not patients:
            raise HTTPException(status_code=404, detail="No patients found.")

        # Attach Metadata and Samples
        for patient in patients:
            # Fetch Metadata (Fix column name)
            patient.metadata = db.query(PatientMetadata.id, 
                                        PatientMetadata.patient_id, 
                                        PatientMetadata.key.label("key"),  # Renaming key_name to key
                                        PatientMetadata.value
                                       ).filter(PatientMetadata.patient_id == patient.id).all()

            # Fetch Samples with Metadata
            samples = db.query(Sample).filter(Sample.patient_id == patient.id).all()
            for sample in samples:
                sample.metadata = db.query(SampleMetadata).filter(SampleMetadata.sample_id == sample.id).all()
            patient.samples = samples

        return patients

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
 #################################################################################################   


####################################### PASS #######################################################
# ✅ 6️⃣ Fetch Samples per patient
@router.get("/samples/{sample_id}", response_model=List[SampleSchema])
async def get_samples_per_patient(
    sample_id: int,
    project_id: int,
    db: Session = Depends(get_db)
):
    try:
        # ✅ Query samples that belong to patients under the given project_id
        query = db.query(Sample).join(Patient).filter(Patient.project_id == project_id)

        if sample_id != 0:
            query = query.filter(Sample.id == sample_id)

        samples = query.all()

        if not samples:
            raise HTTPException(status_code=404, detail="No samples found for the given project_id and sample_id.")

        # ✅ Attach Metadata and Patient Information
        for sample in samples:
            sample.metadata = db.query(SampleMetadata).filter(SampleMetadata.sample_id == sample.id).all()
            sample.patient = db.query(Patient).filter(Patient.id == sample.patient_id).first()

        return samples

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
#####################################################################################################################

##################################### PASS #######################################################
# ✅ 2️⃣ Fetch All Patients with Sample Counts
@router.get("/patients/", response_model=List[PatientWithSampleCount])
async def get_patients(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    db: Session = Depends(get_db)
):
    try:
        # ✅ Query Patients with optional filtering by project_id
        query = db.query(Patient)

        if project_id is not None:
            query = query.filter(Patient.project_id == project_id)

        patients = query.all()

        if not patients:
            raise HTTPException(status_code=404, detail="No patients found for the given project_id.")

        # ✅ Attach Sample Counts
        for patient in patients:
            patient.sample_count = db.query(Sample).filter(Sample.patient_id == patient.id).count()

        return patients

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
############################################################################################################

############################### PASS ####################################
@router.get("/projects/", response_model=List[ProjectSchema])
async def get_projects(db: Session = Depends(get_db)):
    try:
        # ✅ Query all projects
        projects = db.query(Project).all()

        if not projects:
            raise HTTPException(status_code=404, detail="No projects found.")

        return projects

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
###################################################################################

################################## PASS ############################################
# ✅ 4️⃣ Fetch All Datasets
@router.get("/datasets/", response_model=List[DatasetSchema])
async def get_datasets(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    dataset_id: Optional[int] = Query(None, description="Filter by dataset ID"),
    db: Session = Depends(get_db)
):
    try:
        # ✅ Query datasets with optional filtering
        query = db.query(Dataset)

        if project_id is not None:
            query = query.filter(Dataset.project_id == project_id)

        if dataset_id is not None:
            query = query.filter(Dataset.id == dataset_id)

        datasets = query.all()

        if not datasets:
            raise HTTPException(status_code=404, detail="No datasets found for the given filters.")

        return datasets

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
########################################################################################

################################## PASS #######################################################
# ✅ 5️⃣ Fetch Dataset with Metadata
@router.get("/datasets_with_metadata/{dataset_id}", response_model=DatasetWithMetadata)
async def get_dataset_with_metadata(
    dataset_id: int,
    project_id: int,
    db: Session = Depends(get_db)
):
    try:
        # ✅ Fetch dataset details
        dataset = db.query(Dataset).filter(
            Dataset.id == dataset_id, Dataset.project_id == project_id
        ).first()

        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        # ✅ Fetch dataset metadata
        metadata = db.query(DatasetMetadata).filter(DatasetMetadata.dataset_id == dataset_id).all()
        dataset.metadata = metadata  # Attach metadata to dataset

        return dataset

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
#####################################################################################

#################################### PASS ########################################################
# ✅ 8️⃣ Fetch Raw Files with Metadata
@router.get("/raw_files_with_metadata/{dataset_id}", response_model=List[RawFileResponse])
async def get_raw_files_with_metadata(
    dataset_id: int,
    db: Session = Depends(get_db)
):
    try:
        # ✅ Query raw files belonging to the dataset
        raw_files = (
            db.query(RawFile)
            .filter(RawFile.dataset_id == dataset_id)
            .all()
        )

        if not raw_files:
            raise HTTPException(status_code=404, detail="No raw files found for the given dataset_id.")

        # ✅ Attach metadata and sample information
        for raw_file in raw_files:
            raw_file.metadata = (
                db.query(RawFileMetadata)
                .filter(RawFileMetadata.raw_file_id == raw_file.id)
                .all()
            )

            # Fetch sample_id from metadata if available
            sample_id_metadata = next(
                (meta.metadata_value for meta in raw_file.metadata if meta.metadata_key == "sample_id"), None
            )

            if sample_id_metadata:
                sample = db.query(Sample).filter(Sample.id == int(sample_id_metadata)).first()
                raw_file.sample_id = str(sample.id) if sample else None
                raw_file.ext_sample_id = sample.ext_sample_id if sample else None

                # Fetch sample metadata
                raw_file.sample_metadata = (
                    db.query(SampleMetadata)
                    .filter(SampleMetadata.sample_id == raw_file.sample_id)
                    .all()
                    if raw_file.sample_id else []
                )
            else:
                raw_file.sample_id = None
                raw_file.ext_sample_id = None
                raw_file.sample_metadata = []

        return raw_files

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
######################################################################################

#################################### PASS ######################################
# ✅ 9️⃣ Update Metadata (Size Update)
@router.put("/datasets_metadata/size_update", response_model=MetadataUpdate)
def update_metadata(update: MetadataUpdate, db: Session = Depends(get_db)):
    try:
        # ✅ Update or Insert 'raw_file_extension_size_of_all_files' Metadata
        if update.raw_file_size:
            record = (
                db.query(DatasetMetadata)
                .filter(
                    DatasetMetadata.dataset_id == update.dataset_id,
                    DatasetMetadata.key == "raw_file_extension_size_of_all_files"
                )
                .first()
            )

            if record:
                record.value = update.raw_file_size  # Update existing record
            else:
                db.add(DatasetMetadata(
                    dataset_id=update.dataset_id,
                    key="raw_file_extension_size_of_all_files",
                    value=update.raw_file_size
                ))  # Insert new record

        # ✅ Update or Insert 'last_size_update' Metadata
        if update.last_size_update:
            record = (
                db.query(DatasetMetadata)
                .filter(
                    DatasetMetadata.dataset_id == update.dataset_id,
                    DatasetMetadata.key == "last_size_update"
                )
                .first()
            )

            if record:
                record.value = update.last_size_update  # Update existing record
            else:
                db.add(DatasetMetadata(
                    dataset_id=update.dataset_id,
                    key="last_size_update",
                    value=update.last_size_update
                ))  # Insert new record

        db.commit()  # Commit changes
        return update

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
###################################################################################

