from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import database initialization
from app.db.database import init_db
from app.api.routes import router as api_router

app = FastAPI()

# ✅ CORS Middleware (Restrict origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# ✅ Initialize the database on FastAPI startup
@app.on_event("startup")
def startup_event():
    init_db()

# ✅ Register API routes
app.include_router(api_router)

# ✅ Run the app using Uvicorn (ONLY if running this file directly)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888, reload=True)
