from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import uuid
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from utils.generate_rooftop_layout import draw_rooftop_layout
from datetime import datetime

def fmt_currency(value):
    try:
        return f"₹{value:,.0f}"
    except:
        return f"Rs.{value:,.0f}"

def create_savings_chart(savings, output_path="generated_pdfs/savings_chart.png"):
    months = list(range(1, 26 * 12 + 1, 12))
    monthly_savings = savings.get('monthly_savings', 0)
    cumulative = [monthly_savings * m for m in months]
    plt.figure(figsize=(6, 3))
    plt.plot(months, cumulative, marker='o', color='green')
    plt.title("Estimated Savings Over 25 Years")
    plt.xlabel("Months")
    plt.ylabel("Cumulative Savings (₹)")
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
    y = height - 80

    # --- Logo ---
    try:
        c.drawImage("assets/chainfly_logo.png", x=40, y=height - 80, width=130, height=40)
    except:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, height - 60, "CHAINFLY SOLAR")

    # --- Title ---
    c.setFont("Helvetica-Bold", 18)
    c.drawString(200, height - 60, "Solar Feasibility Proposal")

    # --- Hero KPI Strip ---
    kpi_text = f"⚡ {data.get('system_size_kw', 'N/A')} kW   ■ CAPEX: {fmt_currency(savings.get('capex', 0))}   ■ Net: {fmt_currency(savings.get('net_capex', 0))}   ■ Savings: {fmt_currency(savings.get('monthly_savings', 0))}/mo   ■ ROI: {savings.get('roi_percent_25yr', 0)}%   ■ Payback: {int(savings.get('payback_years', 0) * 12)} months"
    c.setFillColorRGB(0.92, 0.96, 1)
    c.rect(30, y - 20, width - 60, 30, fill=True, stroke=False)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 11)
    c.drawString(40, y - 8, kpi_text)
    y -= 60

    def draw_line(label, value):
        nonlocal y
        if y < 120:
            c.showPage()
            y = height - 80
        c.drawString(50, y, f"{label}: {value}")
        y -= 18

    # --- Customer Section ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "1. 📍 Customer Details")
    y -= 10
    c.line(50, y, width - 50, y)
    y -= 20
    c.setFont("Helvetica", 12)
    draw_line("Customer", data.get("customer_name", "N/A"))
    draw_line("Location", f"{data.get('latitude')}, {data.get('longitude')}")
    draw_line("Rooftop Area", f"{data.get('rooftop_area_m2')} m²")
    draw_line("Monthly Bill", fmt_currency(data.get('monthly_bill', 0)))

    # --- System Section ---
    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "2. ⚙️ System Design")
    y -= 10
    c.line(50, y, width - 50, y)
    y -= 20
    c.setFont("Helvetica", 12)
    draw_line("System Size", f"{data.get('system_size_kw')} kW")
    draw_line("Shadow Risk", data.get('shadow_risk', 'Unknown'))
    draw_line("Orientation OK", str(data.get('orientation_ok', False)))
    draw_line("Installation Suitable", str(data.get('suitable', False)))

    # --- Finance Section ---
    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "3. 💰 Financial Summary")
    y -= 10
    c.line(50, y, width - 50, y)
    y -= 20
    draw_line("Monthly Generation", f"{savings.get('monthly_generation_kwh', 0)} kWh")
    draw_line("Monthly Savings", fmt_currency(savings.get('monthly_savings', 0)))
    draw_line("CAPEX", fmt_currency(savings.get('capex', 0)))
    draw_line("Subsidy", fmt_currency(savings.get('subsidy', 0)))
    draw_line("Net CAPEX", fmt_currency(savings.get('net_capex', 0)))
    draw_line("Annual O&M", fmt_currency(savings.get('o_and_m', 0)))
    draw_line("Payback Period", f"{int(savings.get('payback_years', 0) * 12)} months")
    draw_line("ROI (25 yrs)", f"{savings.get('roi_percent_25yr', 0)}%")

    # --- Rooftop layout ---
    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "4. 🏠 Rooftop Layout Simulation")
    y -= 10
    c.line(50, y, width - 50, y)
    y -= 200

    layout_path = os.path.join(output_dir, "rooftop_layout.png")
    draw_rooftop_layout(
        rooftop_area_m2=data.get("rooftop_area_m2", 70),
        system_size_kw=data.get("system_size_kw", 3),
        shadow_zone=(2, 2, 2.5, 3),
        output_path=layout_path
    )
    try:
        c.drawImage(layout_path, x=50, y=y, width=500, height=180)
        y -= 40
    except:
        draw_line("Note", "Could not load layout image.")

    # --- Savings Chart ---
    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "5. 📈 25-Year Savings Projection")
    y -= 10
    c.line(50, y, width - 50, y)
    y -= 200
    chart_path = os.path.join(output_dir, "savings_chart.png")
    create_savings_chart(savings, chart_path)
    try:
        c.drawImage(chart_path, x=50, y=y, width=500, height=180)
    except:
        draw_line("Note", "Could not load chart image.")

    # --- Footer ---
    c.setFont("Helvetica", 10)
    c.drawString(50, 50, "ChainFly Energy Pvt. Ltd. | 📞 +91 70155 71891 | 🌐 www.chainfly.co | ✉️ contact@chainfly.co")
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width / 2, 30, "This proposal is auto-generated by ChainFly's rooftop solar API platform.")
    c.save()

    return file_path

