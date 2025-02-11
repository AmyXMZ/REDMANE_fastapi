from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
# SQLite Database URL
DATABASE_URL = "sqlite:///./data/data_redmane.db"
# Create the database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


# Define Database Models
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(String)

    datasets = relationship("Dataset", back_populates="project")
    patients = relationship("Patient", back_populates="project")

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String)

    project = relationship("Project", back_populates="datasets")
    metadata = relationship("DatasetMetadata", back_populates="dataset")
    raw_files = relationship("RawFile", back_populates="dataset")

class DatasetMetadata(Base):
    __tablename__ = "datasets_metadata"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)

    dataset = relationship("Dataset", back_populates="metadata")

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    ext_patient_id = Column(String)
    ext_patient_url = Column(String)
    public_patient_id = Column(String)

    project = relationship("Project", back_populates="patients")
    metadata = relationship("PatientMetadata", back_populates="patient")
    samples = relationship("Sample", back_populates="patient")

class PatientMetadata(Base):
    __tablename__ = "patients_metadata"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    key = Column(String)
    value = Column(String)

    patient = relationship("Patient", back_populates="metadata")

class Sample(Base):
    __tablename__ = "samples"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    ext_sample_id = Column(String)
    ext_sample_url = Column(String)

    patient = relationship("Patient", back_populates="samples")
    metadata = relationship("SampleMetadata", back_populates="sample")

class SampleMetadata(Base):
    __tablename__ = "samples_metadata"

    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(Integer, ForeignKey("samples.id"), nullable=False)
    key = Column(String)
    value = Column(String)

    sample = relationship("Sample", back_populates="metadata")

class RawFile(Base):
    __tablename__ = "raw_files"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    path = Column(Text)

    dataset = relationship("Dataset", back_populates="raw_files")
    metadata = relationship("RawFileMetadata", back_populates="raw_file")

class RawFileMetadata(Base):
    __tablename__ = "raw_files_metadata"

    metadata_id = Column(Integer, primary_key=True, index=True)
    raw_file_id = Column(Integer, ForeignKey("raw_files.id"))
    metadata_key = Column(String, nullable=False)
    metadata_value = Column(String, nullable=False)

    raw_file = relationship("RawFile", back_populates="metadata")

# Function to initialize the database
def init_db():
    Base.metadata.create_all(bind=engine)