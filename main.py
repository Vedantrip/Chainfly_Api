from fastapi import FastAPI
from routes import feasibility
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Chainfly Rooftop Solar API")

# Enable CORS before including any routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include your router
app.include_router(feasibility.router)
