# Data Commons: FastAPI Backend

## Overview

Data Commons is a web application using a fastAPI backend.

## Features

- **Authentication**: Users can log in and log out. Unauthorized access to specific routes is prevented.
- **Dataset Management**: Manage datasets with options to view all datasets or a single dataset.
- **Patient Management**: View and manage patient information.
- **Project Management**: View all projects or a single project, with a dashboard overview.
- **Responsive Design**: The application is designed to be responsive, providing a good user experience across different devices.


## Project Structure
```plaintext
REDMANE_fastapi/
├── app/
│   │   ├── __init__.py             # Initializes the API package
│   │   └── routes.py               # Defines API endpoints
│   ├── db/
│   │   ├── __init__.py             # Initializes the database package
│   │   └── database.py             # Sets up and initializes the SQLite database
│   ├── schemas/
│   │   ├── __init__.py             # Initializes the schemas package
│   │   └── schemas.py              # Defines Pydantic models for data validation
│   └── main.py                     # Entry point for the FastAPI application
├── data/
│   ├── sample_data/                # Sample datasets and scripts for testing
│   │   ├── clear_patients_and_samples.sh  # Script to clear sample data
│   │   ├── import_onj_patients.py  # Script to import ONJ patients
│   │   ├── import_onj_samples.py   # Script to import ONJ samples
│   │   ├── import_rmh_patients.py  # Script to import RMH patients
│   │   ├── redcap_onj.csv          # Sample ONJ patient data
│   │   ├── redcap_onj_samples.csv  # Sample ONJ sample data
│   │   └── redcap_rmh.csv          # Sample RMH patient data
│   └── sample_files/               # Sample files for raw data tracking
│       └── tracker/                # Folder for tracking scripts and raw data
│           ├── scrnaseq/raw/       # scRNA-seq raw data files
│           │   └── random_file_2.fastq   # Example FASTQ file
│           └── westn/raw/          # WES raw data files
│               ├── *.fastq         # Example FASTQ files for testing
│               ├── create_counts_file_big.py  # Script for processing large count files
│               ├── create_counts_file_size.py # Script for calculating file size
│               ├── create_fastq_size.py       # Script for FASTQ size processing
│               └── file_report.py  # Script for generating file reports
├── data_redmane.db                 # SQLite database file
├── LICENSE                         # Project license
├── README.md                       # Project documentation
├── .gitignore                      # Git ignore file
└── .DS_Store
```

## Installation

### Setup Instructions

1. **Create a python virtual environment:**

   ```bash
   python3 -m venv env
   ```

2. **Install Libraries:**

   Using npm:
   ```bash
   pip install fastapi uvicorn
   ```

3. **Run server:**

   Connect to venv
   ```bash
   source env/bin/activate
   ```

   ```bash
   uvicorn app.main:app --reload --port 8888
   ```
