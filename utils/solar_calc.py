def calculate_system_size(area_m2, is_premium=False):
    """Calculate recommended system size in kW"""
    if area_m2 < 20:  # Minimum area requirement
        return 0
    kw_per_m2 = 1 / (7.5 if is_premium else 10)  # Premium panels are more efficient
    return round(area_m2 * kw_per_m2, 2)

def capex_cost(system_size_kw):
    """Calculate capital expenditure"""
    if system_size_kw <= 0:
        return 0
    return round(system_size_kw * 60000, 2)  # ₹60,000 per kW

def mnre_subsidy(system_size_kw):
    """Calculate government subsidy"""
    if system_size_kw <= 0:
        return 0
    if system_size_kw <= 3:
        return round(capex_cost(system_size_kw) * 0.3, 2)  # 30% subsidy
    elif system_size_kw <= 10:
        return round(capex_cost(system_size_kw) * 0.2, 2)  # 20% subsidy
    return 0  # No subsidy for >10kW

def estimate_savings_and_roi(system_size_kw, bill, tariff=7.0, sun_hours=4.5):
    """Calculate financial metrics"""
    if system_size_kw <= 0:
        return {
            "monthly_generation_kwh": 0,
            "monthly_savings": 0,
            "capex": 0,
            "subsidy": 0,
            "net_capex": 0,
            "o_and_m": 0,
            "payback_years": 0,
            "roi_percent_25yr": 0
        }

    monthly_gen_kwh = system_size_kw * sun_hours * 30
    raw_savings = monthly_gen_kwh * tariff
    monthly_savings = min(raw_savings, bill * 0.95)  # Cap at 95% of bill

    capex = capex_cost(system_size_kw)
    subsidy = mnre_subsidy(system_size_kw)
    net_capex = capex - subsidy
    o_and_m = 0.01 * capex  # 1% of CAPEX for annual maintenance
    annual_savings = monthly_savings * 12

    payback_years = round(net_capex / annual_savings, 2) if annual_savings > 0 else 0
    roi_25yr = round(((annual_savings - o_and_m) * 25) / net_capex * 100, 2) if net_capex > 0 else 0

    return {
        "monthly_generation_kwh": round(monthly_gen_kwh, 2),
        "monthly_savings": round(monthly_savings, 2),
        "capex": capex,
        "subsidy": subsidy,
        "net_capex": net_capex,
        "o_and_m": round(o_and_m, 2),
        "payback_years": payback_years,
        "roi_percent_25yr": roi_25yr
    }

def validate_solar_suitability(data):
    """Check if solar installation is viable"""
    required_fields = ['latitude', 'longitude', 'rooftop_area_m2', 'monthly_bill']
    if not all(field in data for field in required_fields):
        return False
    if data['rooftop_area_m2'] < 20 or data['monthly_bill'] < 3000:
        return False
    return True

def prepare_proposal_data(data):
    """Prepare complete dataset for PDF generation"""
    if not validate_solar_suitability(data):
        return None
        
    data['system_size_kw'] = calculate_system_size(
        data['rooftop_area_m2'],
        data.get('is_premium', False)
    )
    
    # Set defaults if not provided
    if 'orientation_ok' not in data:
        data['orientation_ok'] = True  # Should use proper orientation check
    
    if 'shadow_risk' not in data:
        data['shadow_risk'] = "Low"  # Should use proper shadow analysis
    
    data['suitable'] = (
        data['system_size_kw'] >= 1 and
        data['orientation_ok'] and
        data['shadow_risk'] in ["Low", "None"]
    )
    
    if data['suitable']:
        savings = estimate_savings_and_roi(
            data['system_size_kw'],
            data['monthly_bill']
        )
    else:
        savings = {
            "monthly_generation_kwh": 0,
            "monthly_savings": 0,
            "capex": 0,
            "subsidy": 0,
            "net_capex": 0,
            "o_and_m": 0,
            "payback_years": 0,
            "roi_percent_25yr": 0
        }
    
    return data, savings
