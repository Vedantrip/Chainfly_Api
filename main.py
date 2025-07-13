from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes import feasibility

app = FastAPI(title="Chainfly Rooftop Solar API")

# ✅ Allow frontend GitHub Pages access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://vedantrip.github.io"],  # No trailing slash
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Serve PDF files
app.mount("/generated_pdfs", StaticFiles(directory="generated_pdfs"), name="pdfs")

# ✅ Include routes
app.include_router(feasibility.router)

# ✅ Root test route
@app.get("/")
def home():
    return {"message": "ChainFly API is live 🚀"}
