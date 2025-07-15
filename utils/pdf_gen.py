from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import uuid
import os
from datetime import datetime
from utils.generate_rooftop_layout import draw_rooftop_layout

def fmt_currency(value):
    try:
        pdfmetrics.registerFont(TTFont('ArialUnicode', 'arial-unicode-ms.ttf'))
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
    logo_path = "assets/chainfly_logo.png"
    try:
        c.drawImage(logo_path, x=40, y=height-80, width=150, height=50, preserveAspectRatio=True, mask='auto')
    except:
        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, height-60, "CHAINFLY")
    c.setFont("Helvetica-Bold", 18)
    c.drawString(200, height - 60, "Solar Feasibility Proposal")

    # --- KPI Strip ---
    c.setFont("Helvetica-Bold", 11)
    c.setFillColorRGB(0.90, 0.95, 1.0)
    c.rect(40, y - 30, width - 80, 40, fill=True, stroke=False)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(50, y - 18, f"📏 {data.get('system_size_kw')} kW   💰 CAPEX: {fmt_currency(savings.get('capex'))}   💸 Net: {fmt_currency(savings.get('net_capex'))}   ⚡ Savings: {fmt_currency(savings.get('monthly_savings'))}/mo   📈 ROI: {savings.get('roi_percent_25yr')}%   ⏳ Payback: {int(savings.get('payback_years')*12)} mo")
    y -= 90

    def draw_section(title):
        nonlocal y
        if y < 150:
            c.showPage()
            y = height - 100
        c.setFont("Helvetica-Bold", 14)
        c.setFillColorRGB(0.2, 0.4, 0.6)
        c.drawString(50, y, title)
        y -= 10
        c.setFillColorRGB(0, 0, 0)
        c.line(50, y, width - 50, y)
        y -= 20

    def draw_line(label, value):
        nonlocal y
        if y < 100:
            c.showPage()
            y = height - 100
        c.setFont("Helvetica", 12)
        c.drawString(50, y, f"{label}: {value}")
        y -= 18

    # --- Sections ---
    draw_section("1. 📍 Customer Details")
    draw_line("Customer", data.get("customer_name", "N/A"))
    draw_line("Location", f"{data.get('latitude')}, {data.get('longitude')}")
    draw_line("Rooftop Area", f"{data.get('rooftop_area_m2')} m²")
    draw_line("Monthly Bill", fmt_currency(data.get('monthly_bill', 0)))

    draw_section("2. 🏗️ System Design")
    draw_line("System Size", f"{data.get('system_size_kw')} kW")
    draw_line("Shadow Risk", data.get('shadow_risk', 'Unknown'))
    draw_line("Orientation OK", str(data.get('orientation_ok', False)))
    draw_line("Installation Suitable", str(data.get('suitable', False)))

    draw_section("3. 💡 Financial Summary")
    draw_line("Monthly Generation", f"{savings.get('monthly_generation_kwh', 0)} kWh")
    draw_line("Monthly Savings", fmt_currency(savings.get('monthly_savings', 0)))
    draw_line("CAPEX", fmt_currency(savings.get('capex', 0)))
    draw_line("Subsidy", fmt_currency(savings.get('subsidy', 0)))
    draw_line("Net CAPEX", fmt_currency(savings.get('net_capex', 0)))
    draw_line("Annual O&M", fmt_currency(savings.get('o_and_m', 0)))
    draw_line("Payback Period", f"{int(savings.get('payback_years', 0) * 12)} months")
    draw_line("ROI (25 yrs)", f"{savings.get('roi_percent_25yr')}%")

    draw_section("4. 🧱 Rooftop Layout")
    layout_path = os.path.join(output_dir, "rooftop_layout.png")
    shadow_zone = (
        round(0.2 * data.get("rooftop_area_m2", 70)**0.5, 1),
        round(0.1 * data.get("rooftop_area_m2", 70)**0.5, 1),
        round(0.25 * data.get("rooftop_area_m2", 70)**0.5, 1),
        round(0.3 * data.get("rooftop_area_m2", 70)**0.5, 1)
    )
    draw_rooftop_layout(
        rooftop_area_m2=data.get("rooftop_area_m2", 70),
        system_size_kw=data.get("system_size_kw", 3),
        shadow_zone=shadow_zone,
        output_path=layout_path
    )
    try:
        c.drawImage(layout_path, x=50, y=y - 200, width=500, height=180)
        y -= 220
    except:
        draw_line("Note", "Could not render rooftop layout.")

    draw_section("5. 📈 25-Year Savings Projection")
    chart_path = os.path.join(output_dir, "savings_chart.png")
    create_savings_chart(savings, chart_path)
    try:
        c.drawImage(chart_path, x=50, y=y - 200, width=500, height=180)
    except:
        draw_line("Note", "Could not render savings chart.")

    # ------==Footer=======-----------
    c.setFont("Helvetica", 10)
    c.drawString(50, 60, "ChainFly Energy Pvt. Ltd.")
    c.drawString(50, 48, "📞 +91 70155 71891")
    c.drawString(200, 48, "🌐 www.chainfly.co")
    c.drawString(400, 48, "✉️ contact@chainfly.co")
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(width / 2, 30, "This proposal is auto-generated by ChainFly's rooftop solar API platform.")

    c.save()
    return file_path
