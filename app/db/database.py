from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = "sqlite:///data/data_redmane.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define ORM models
class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    status = Column(String)
    datasets = relationship("Dataset", back_populates="project")
    patients = relationship("Patient", back_populates="project")

class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String)
    project = relationship("Project", back_populates="datasets")
    metadata_entries = relationship("DatasetMetadata", back_populates="dataset")
    raw_files = relationship("RawFile", back_populates="dataset")

class DatasetMetadata(Base):
    __tablename__ = "datasets_metadata"
    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    key = Column(String, nullable=False)
    value = Column(Text, nullable=False)
    dataset = relationship("Dataset", back_populates="metadata_entries")

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    ext_patient_id = Column(String)
    ext_patient_url = Column(String)
    public_patient_id = Column(String)
    project = relationship("Project", back_populates="patients")
    metadata_entries = relationship("PatientMetadata", back_populates="patient")
    samples = relationship("Sample", back_populates="patient")

class PatientMetadata(Base):
    __tablename__ = "patients_metadata"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    key = Column(String)
    value = Column(Text)
    patient = relationship("Patient", back_populates="metadata_entries")

class Sample(Base):
    __tablename__ = "samples"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    ext_sample_id = Column(String)
    ext_sample_url = Column(String)
    patient = relationship("Patient", back_populates="samples")
    metadata_entries = relationship("SampleMetadata", back_populates="sample")

class SampleMetadata(Base):
    __tablename__ = "samples_metadata"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sample_id = Column(Integer, ForeignKey("samples.id"), nullable=False)
    key = Column(String)
    value = Column(Text)
    sample = relationship("Sample", back_populates="metadata_entries")

class RawFile(Base):
    __tablename__ = "raw_files"
    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    path = Column(Text)
    dataset = relationship("Dataset", back_populates="raw_files")
    metadata_entries = relationship("RawFileMetadata", back_populates="raw_file")

class RawFileMetadata(Base):
    __tablename__ = "raw_files_metadata"
    metadata_id = Column(Integer, primary_key=True, autoincrement=True)
    raw_file_id = Column(Integer, ForeignKey("raw_files.id"), nullable=True)
    metadata_key = Column(String, nullable=False)
    metadata_value = Column(Text, nullable=False)
    raw_file = relationship("RawFile", back_populates="metadata_entries")

# Function to initialize database
def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
