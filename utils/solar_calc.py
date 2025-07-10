def calculate_system_size(area_m2, is_premium=False):
    kw_per_m2 = 1 / (7.5 if is_premium else 10)
    return round(area_m2 * kw_per_m2, 2)

def capex_cost(system_size_kw):
    return round(system_size_kw * 60000, 2)  # As per govt. it is ₹60,000 per kW

def mnre_subsidy(system_size_kw):
    subsidy_rate = 0.3  # Which is actually like 30%
    if system_size_kw <= 3:
        return round(capex_cost(system_size_kw) * subsidy_rate, 2)
    elif system_size_kw <= 10:
        return round(capex_cost(system_size_kw) * 0.2, 2)
    return 0

def estimate_savings_and_roi(system_size_kw, bill, tariff=7.0, sun_hours=4.5):
    monthly_gen_kwh = system_size_kw * sun_hours * 30
    raw_savings = monthly_gen_kwh * tariff

    #---------- Input sanity cap-----
    monthly_savings = min(raw_savings, bill * 0.95)

    capex = capex_cost(system_size_kw)
    subsidy = mnre_subsidy(system_size_kw)
    net_capex = capex - subsidy

    o_and_m = 0.01 * capex
    annual_savings = monthly_savings * 12

    payback_years = round(net_capex / annual_savings, 2)
    roi_25yr = round(((annual_savings - o_and_m) * 25) / net_capex * 100, 2)

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
