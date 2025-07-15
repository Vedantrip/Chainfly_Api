from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib.units import inch
from utils.generate_rooftop_layout import draw_rooftop_layout
import uuid, os
from datetime import datetime


def fmt_currency(value):
    """Format currency with fallback for ₹ symbol compatibility"""
    try:
        return f"Rs.{value:,.0f}"
    except:
        return f"{value}"


def create_savings_chart(savings, output_path="generated_pdfs/savings_chart.png"):
    months = list(range(1, 26 * 12 + 1, 12))  # yearly points
    monthly_savings = savings.get('monthly_savings', 0)
    cumulative = [monthly_savings * m for m in months]

    plt.figure(figsize=(6, 3))
    plt.plot(months, cumulative, marker='o', color='green')
    plt.title("Estimated Savings Over 25 Years")
    plt.xlabel("Months")
    plt.ylabel("Cumulative Savings (Rs.)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def generate_proposal_pdf(data: dict, savings: dict, output_dir="generated_pdfs"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    safe_name = data.get("customer_name", "user").replace(" ", "_").lower()
    timestamp = datetime.now().strftime("%Y%m%d")
    file_name = f"{safe_name}_proposal_{timestamp}.pdf"
    file_path = os.path.join(output_dir, file_name)

    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter
    y = height - 60

    # Header & logo
    try:
        c.drawImage("assets/chainfly_logo.png", 40, y, width=120, height=40, preserveAspectRatio=True, mask='auto')
    except:
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, "CHAINFLY")

    c.setFont("Helvetica-Bold", 18)
    c.drawString(200, height - 50, "Solar Feasibility Proposal")
    y -= 70

    # KPI Strip
    system_size = data.get("system_size_kw", "N/A")
    capex = fmt_currency(savings.get("capex", 0))
    net = fmt_currency(savings.get("net_capex", 0))
    savings_m = fmt_currency(savings.get("monthly_savings", 0))
    roi = f"{savings.get('roi_percent_25yr', 0)}%"
    payback = f"{int(savings.get('payback_years', 0) * 12)} mo"

    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.9, 0.95, 1)
    c.rect(30, y, width - 60, 30, fill=True, stroke=False)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y + 10, f"◼ {system_size} kW   ◼ CAPEX: {capex}   ◼ Net: {net}   ◼ Savings: {savings_m}/mo   ◼ ROI: {roi}   ◼ Payback: {payback}")
    y -= 50

    def draw_heading(text):
        nonlocal y
        if y < 100:
            c.showPage()
            y = height - 100
        c.setFont("Helvetica-Bold", 14)
        c.setFillColorRGB(0.1, 0.3, 0.6)
        c.drawString(40, y, f"{text}")
        c.setFillColorRGB(0, 0, 0)
        y -= 8
        c.line(40, y, width - 40, y)
        y -= 20

    def draw_line(label, value):
        nonlocal y
        if y < 80:
            c.showPage()
            y = height - 100
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"{label}:")
        c.setFont("Helvetica", 12)
        c.drawString(180, y, str(value))
        y -= 20

    # 1. Customer Details
    draw_heading("1. Customer Details")
    draw_line("Customer", data.get("customer_name", "N/A"))
    draw_line("Location", f"{data.get('latitude', 'N/A')}, {data.get('longitude', 'N/A')}")
    draw_line("Rooftop Area", f"{data.get('rooftop_area_m2', 0)} m²")
    draw_line("Monthly Bill", fmt_currency(data.get("monthly_bill", 0)))

    # 2. System Design
    draw_heading("2. System Design")
    draw_line("System Size", f"{system_size} kW")
    draw_line("Shadow Risk", data.get("shadow_risk", "Unknown"))
    draw_line("Orientation OK", str(data.get("orientation_ok", False)))
    draw_line("Installation Suitable", str(data.get("suitable", False)))

    # 3. Financial Summary
    draw_heading("3. Financial Summary")
    draw_line("Monthly Generation", f"{savings.get('monthly_generation_kwh', 0)} kWh")
    draw_line("Monthly Savings", fmt_currency(savings.get("monthly_savings", 0)))
    draw_line("CAPEX", fmt_currency(savings.get("capex", 0)))
    draw_line("Subsidy", fmt_currency(savings.get("subsidy", 0)))
    draw_line("Net CAPEX", fmt_currency(savings.get("net_capex", 0)))
    draw_line("Annual O&M", fmt_currency(savings.get("o_and_m", 0)))
    draw_line("Payback Period", payback)
    draw_line("ROI (25 yrs)", roi)

    # 4. Rooftop Layout
    draw_heading("4. Rooftop Layout Simulation")
    layout_path = os.path.join(output_dir, "rooftop_layout.png")
    shadow_zone = (
        round(data.get('rooftop_area_m2', 70)**0.5 * 0.2, 1),
        round(data.get('rooftop_area_m2', 70)**0.5 * 0.1, 1),
        round(data.get('rooftop_area_m2', 70)**0.5 * 0.25, 1),
        round(data.get('rooftop_area_m2', 70)**0.5 * 0.3, 1)
    )

    draw_rooftop_layout(
        rooftop_area_m2=data.get("rooftop_area_m2", 70),
        system_size_kw=data.get("system_size_kw", 3),
        shadow_zone=shadow_zone,
        output_path=layout_path
    )

    try:
        c.drawImage(layout_path, 50, y - 180, width=500, height=180)
        y -= 200
    except Exception as e:
        draw_line("Note", "Rooftop layout unavailable.")

    # 5. 25-Year Savings
    draw_heading("5. 25-Year Savings Projection")
    chart_path = os.path.join(output_dir, "savings_chart.png")
    create_savings_chart(savings, chart_path)
    try:
        c.drawImage(chart_path, 50, y - 180, width=500, height=180)
        y -= 200
    except:
        draw_line("Note", "Savings chart unavailable.")

    # Footer
    c.setFont("Helvetica", 10)
    c.drawString(50, 50, "ChainFly Energy Pvt. Ltd.  |  📞 +91 70155 71891  |  🌐 www.chainfly.co  |  ✉️ contact@chainfly.co")
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(width / 2, 30, "This proposal is auto-generated by ChainFly's rooftop solar API platform.")
    c.save()
    return file_path
