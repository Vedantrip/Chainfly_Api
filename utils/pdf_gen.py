from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import uuid
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from utils.generate_rooftop_layout import draw_rooftop_layout
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def fmt_currency(value):
    # Register a font that supports the ₹ symbol if needed
    try:
        pdfmetrics.registerFont(TTFont('ArialUnicode', 'arial-unicode-ms.ttf'))
        return f"₹{value:,.0f}"  # Using the Unicode ₹ symbol
    except:
        return f"Rs.{value:,.0f}"  # Fallback if font registration fails

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

    from datetime import datetime
    safe_name = data.get("customer_name", "user").replace(" ", "_").lower()
    timestamp = datetime.now().strftime("%Y%m%d")
    file_name = f"{safe_name}_proposal_{timestamp}.pdf"
    file_path = os.path.join(output_dir, file_name)

    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter
    y = height - 80

    # Set up the title font
    logo_path = "assets/chainfly_logo.png"
    logo_width = 150
    logo_height = 50 
    
    try:
        # Draw logo with adjusted positioning
        c.drawImage(logo_path, x=40, y=height-80, 
                   width=logo_width, height=logo_height,
                   preserveAspectRatio=True, mask='auto')

    except Exception as e:
        print(f"Error loading logo: {e}")
        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, height-60, "CHAINFLY")
        c.setFont("Helvetica", 12)
        c.drawString(40, height-80, "Solar Feasibility Proposal")

    # --- Title ---
    c.setFont("Helvetica-Bold", 18)
    c.drawString(200, height - 60, "Solar Feasibility Proposal")

    y -= 80
    c.setFont("Helvetica", 12)

    def draw_line(label, value):
        nonlocal y
        if y < 150:  # Ensure enough space for footer
            c.showPage()
            y = height - 100
        c.drawString(50, y, f"{label}: {value}")
        y -= 20

    # --- Section 1: Customer Details ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "1. Customer Details")
    y -= 10
    c.line(50, y, width - 50, y)
    y -= 20
    c.setFont("Helvetica", 12)
    draw_line("Location", f"{data.get('latitude')}, {data.get('longitude')}")
    draw_line("Rooftop Area", f"{data.get('rooftop_area_m2')} m²")
    draw_line("Monthly Bill", fmt_currency(data.get('monthly_bill', 0)))

    y -= 20
    # --- Section 2: System Design ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "2. System Design")
    y -= 10
    c.line(50, y, width - 50, y)
    y -= 20
    c.setFont("Helvetica", 12)
    draw_line("System Size", f"{data.get('system_size_kw')} kW")
    draw_line("Shadow Risk", data.get('shadow_risk', 'Unknown'))
    draw_line("Orientation OK", str(data.get('orientation_ok', False)))
    draw_line("Installation Suitable", str(data.get('suitable', False)))

    y -= 20
    # --- Section 3: Financial Summary ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "3. Financial Summary")
    y -= 10
    c.line(50, y, width - 50, y)
    y -= 20
    c.setFont("Helvetica", 12)
    draw_line("Monthly Generation", f"{savings.get('monthly_generation_kwh', 0)} kWh")
    draw_line("Monthly Savings", fmt_currency(savings.get('monthly_savings', 0)))
    draw_line("CAPEX", fmt_currency(savings.get('capex', 0)))
    draw_line("Subsidy", fmt_currency(savings.get('subsidy', 0)))
    draw_line("Net CAPEX", fmt_currency(savings.get('net_capex', 0)))
    draw_line("Annual O&M", fmt_currency(savings.get('o_and_m', 0)))
    payback = f"{int(savings.get('payback_years', 0) * 12)} months"
    draw_line("Payback Period", payback)
    draw_line("ROI (25 yrs)", f"{savings.get('roi_percent_25yr', 0)}%")

    y -= 20
    # --- Section 4: Rooftop Layout ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "4. Rooftop Layout Simulation")
    y -= 10
    c.line(50, y, width - 50, y)

    # Ensure we have enough space for the image and footer
    if y < 300:  # If not enough space, create new page
        c.showPage()
        y = height - 100

    y -= 180  # Adjust this value based on your image height needs
    layout_path = os.path.join(output_dir, "rooftop_layout.png")

    # --- Dynamic Rooftop Layout Estimation ---
    rooftop_area = data.get("rooftop_area_m2", 70)
    system_size = data.get("system_size_kw", 3)

    # Calculate shadow zone dynamically (20% from left, 10% from bottom, 25% width, 30% height)
    shadow_zone = (
        round(rooftop_area**0.5 * 0.2, 1),
        round(rooftop_area**0.5 * 0.1, 1),
        round(rooftop_area**0.5 * 0.25, 1),
        round(rooftop_area**0.5 * 0.3, 1)
    )

    draw_rooftop_layout(
        rooftop_area_m2=rooftop_area,
        system_size_kw=system_size,
        shadow_zone=shadow_zone,
        output_path=layout_path
    )

    try:
        c.drawImage(layout_path, x=50, y=y, width=500, height=180)
        y -= 40
    except Exception as e:
        print(f"Error drawing rooftop layout: {e}")
        draw_line("Note", "Could not load rooftop layout.")

    # --- Section 5: Savings Projection ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "5. 25-Year Savings Projection")
    y -= 10
    c.line(50, y, width - 50, y)

    # Ensure we have enough space for the chart and footer
    if y < 300:  # If not enough space, create new page
        c.showPage()
        y = height - 100

    y -= 180  # Adjust this value based on your chart height needs
    chart_path = os.path.join(output_dir, "savings_chart.png")
    create_savings_chart(savings, chart_path)
    try:
        c.drawImage(chart_path, x=50, y=y, width=500, height=180)
    except Exception as e:
        print(f"Error drawing savings chart: {e}")
        draw_line("Note", "Chart could not be rendered.")

    # --- Footer ---
    c.setFont("Helvetica", 10)
    # Ensure footer is on a new page if needed
    if y < 100:
        c.showPage()
        y = height - 100

    c.drawString(50, 60, "ChainFly Energy Pvt. Ltd.")
    c.drawString(50, 48, "📞 +91 70155 71891")
    c.drawString(200, 48, "🌐 www.chainfly.co")
    c.drawString(400, 48, "✉️ contact@chainfly.co")

    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(width / 2, 30, "This proposal is auto-generated by ChainFly's rooftop solar API platform.")

    c.save()
    return file_path