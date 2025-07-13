from fastapi import FastAPI
from routes import feasibility
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Chainfly Rooftop Solar API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://vedantrip.github.io/ChainflySolarApi/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(feasibility.router)

# ✅ Add this route
@app.get("/")
def home():
    return {"message": "ChainFly API is live 🚀"}
