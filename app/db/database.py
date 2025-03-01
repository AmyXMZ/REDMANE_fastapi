from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# DATABASE_URL = "postgresql+psycopg2://postgres:password@127.0.0.1:5433/redmane" #for local connection on VSCode
DATABASE_URL = "postgresql+psycopg2://psqladmin:12345@115.146.86.241:5432/redmane"


engine = create_engine(DATABASE_URL)  
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)  
    status = Column(String)

    datasets = relationship("Dataset", back_populates="project", cascade="all, delete-orphan")
    patients = relationship("Patient", back_populates="project", cascade="all, delete-orphan")

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(Text)

    project = relationship("Project", back_populates="datasets")
    meta_data = relationship("DatasetMetadata", back_populates="dataset", cascade="all, delete-orphan")
    raw_files = relationship("RawFile", back_populates="dataset", cascade="all, delete-orphan")

class DatasetMetadata(Base):
    __tablename__ = "datasets_metadata"

    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    key = Column(Text, nullable=False)
    value = Column(Text, nullable=False)

    dataset = relationship("Dataset", back_populates="meta_data")

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    ext_patient_id = Column(String, unique=True)  
    ext_patient_url = Column(Text)
    public_patient_id = Column(String)

    project = relationship("Project", back_populates="patients")
    meta_data = relationship("PatientMetadata", back_populates="patient", cascade="all, delete-orphan")
    samples = relationship("Sample", back_populates="patient", cascade="all, delete-orphan")

class PatientMetadata(Base):
    __tablename__ = "patients_metadata"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    key = Column(Text)
    value = Column(Text)

    patient = relationship("Patient", back_populates="meta_data")

class Sample(Base):
    __tablename__ = "samples"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    ext_sample_id = Column(String, unique=True)
    ext_sample_url = Column(Text)

    patient = relationship("Patient", back_populates="samples")
    meta_data = relationship("SampleMetadata", back_populates="sample", cascade="all, delete-orphan")

class SampleMetadata(Base):
    __tablename__ = "samples_metadata"

    id = Column(Integer, primary_key=True)
    sample_id = Column(Integer, ForeignKey("samples.id", ondelete="CASCADE"), nullable=False, index=True)
    key = Column(Text)
    value = Column(Text)

    sample = relationship("Sample", back_populates="meta_data")

class RawFile(Base):
    __tablename__ = "raw_files"

    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    path = Column(Text, nullable=False)

    dataset = relationship("Dataset", back_populates="raw_files")
    meta_data = relationship("RawFileMetadata", back_populates="raw_file", cascade="all, delete-orphan")

class RawFileMetadata(Base):
    __tablename__ = "raw_files_metadata"

    metadata_id = Column(Integer, primary_key=True)
    raw_file_id = Column(Integer, ForeignKey("raw_files.id", ondelete="CASCADE"), nullable=False, index=True)
    metadata_key = Column(Text, nullable=False)
    metadata_value = Column(Text, nullable=False)

    raw_file = relationship("RawFile", back_populates="meta_data")