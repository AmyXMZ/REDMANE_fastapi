from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from alembic import command
from alembic.config import Config
from app.api.routes import router as api_router

app = FastAPI()

# CORS Middleware (Restrict origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Run Alembic Migrations on Startup (Database Initialization)
@app.on_event("startup")
def startup_event():
    print("Running Alembic Migrations...")
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print("Database is up-to-date!")

# Register API routes
app.include_router(api_router)

# Run the app using Uvicorn (ONLY if running this file directly)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888, reload=True)
