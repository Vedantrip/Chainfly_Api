from fastapi import APIRouter
from pydantic import BaseModel
from utils.solar_calc import calculate_system_size, estimate_savings_and_roi
from utils.pdf_gen import generate_proposal_pdf

router = APIRouter()

class FeasibilityRequest(BaseModel):
    latitude: float
    longitude: float
    rooftop_area_m2: float
    monthly_bill: float
    panel_type: str = "basic"  # 👈 Changed from is_premium
    customer_name: str

@router.post("/feasibility")
def check_feasibility(data: FeasibilityRequest):
    # Pass panel_type to the calculation function
    system_size = calculate_system_size(data.rooftop_area_m2, data.panel_type)

    # Trust-building placeholder logic
    shadow_risk = "Low" if data.latitude > 20 else "Moderate"
    orientation_ok = True
    suitable = system_size >= 1.5

    savings = estimate_savings_and_roi(system_size, data.monthly_bill)

    # PDF Report Generation payload
    payload = {
        "latitude": data.latitude,
        "longitude": data.longitude,
        "rooftop_area_m2": data.rooftop_area_m2,
        "monthly_bill": data.monthly_bill,
        "system_size_kw": system_size,
        "shadow_risk": shadow_risk,
        "orientation_ok": orientation_ok,
        "suitable": suitable,
    }

    pdf_path = generate_proposal_pdf(data.dict(), savings)

    return {
        "feasibility": payload,
        "savings": savings,
        "proposal_pdf": pdf_path
    }
