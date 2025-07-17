from fastapi import APIRouter
from pydantic import BaseModel
from utils.solar_calc import calculate_system_size, estimate_savings_and_roi
from utils.pdf_gen import generate_proposal_pdf

router = APIRouter()

# --- Pydantic Models ---

class FeasibilityRequest(BaseModel):
    latitude: float
    longitude: float
    rooftop_area_m2: float
    monthly_bill: float
    panel_type: str = "basic"
    customer_name: str

class Lead(BaseModel):
    customer_name: str
    contact_info: str 
    system_size_kw: float

# --- API Endpoints ---

@router.post("/feasibility")
def check_feasibility(data: FeasibilityRequest):
    # 1. Calculate system size and savings
    system_size = calculate_system_size(data.rooftop_area_m2, data.panel_type)
    savings = estimate_savings_and_roi(system_size, data.monthly_bill)

    # 2. Determine feasibility parameters
    shadow_risk = "Low" if data.latitude > 20 else "Moderate"
    orientation_ok = True
    suitable = system_size >= 1.5

    # 3. Create one complete payload with all data
    payload = {
        **data.dict(),  # Includes original data like name, location, etc.
        "system_size_kw": system_size,
        "shadow_risk": shadow_risk,
        "orientation_ok": orientation_ok,
        "suitable": suitable,
    }

    # 4. Generate the PDF with the complete payload
    pdf_path = generate_proposal_pdf(payload, savings)

    # 5. Return the final response
    return {
        "feasibility": payload,
        "savings": savings,
        "proposal_pdf": pdf_path
    }

@router.post("/capture-lead")
def capture_lead(lead: Lead):
    # In a real application, you would save this to a database.
    # For now, this will print the lead to your Railway server logs.
    print(f"--- New Lead Captured ---")
    print(f"Name: {lead.customer_name}")
    print(f"Contact: {lead.contact_info}")
    print(f"System Size: {lead.system_size_kw} kW")
    print(f"--------------------------")
    return {"status": "success", "message": "Lead captured"}
