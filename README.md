# Chainfly_Api
Here's a polished and professional `README.md` for your **ChainFly Rooftop Solar Quote Generator** project, including both frontend and backend details, deployment flow, and setup instructions.

---
# ☀️ ChainFly Rooftop Solar Quote Generator

A lightweight, full-stack web application to help rooftop solar panel sellers quickly assess site feasibility and generate professional proposals — complete with savings estimates, ROI, and downloadable PDF reports.

---

## 🚀 Live Demo

**Frontend (GitHub Pages):**  
🔗 [https://vedantrip.github.io/Chainfly_Api](https://vedantrip.github.io/Chainfly_Api)

**Backend (Railway/Deta):**  
🔗 Example: `https://chainflyapi-production.up.railway.app/feasibility`  
_or your live Deta backend URL_

---

## 📦 Features

- 📍 Takes inputs: Location, rooftop size, electricity bill
- 🧠 Calculates: system size, savings, ROI, subsidy
- 🧾 Generates: downloadable PDF proposals with layout, charts, financials
- 🧮 Includes 25-year cashflow, MNRE subsidy impact
- 🔄 API-based: Backend powered by FastAPI
- 🌐 Frontend hosted via GitHub Pages (Firebase optional)
- 🧠 Smart input sanity checks (e.g., premium panel use, shadow risks)

---

## 🖼️ Screenshots

| User Input Form | PDF Output |
|-----------------|------------|
| ![UI](./assets/chainfly_logo.png) | ![PDF](./generated_pdfs/rajeev_proposal_20250705.pdf) |

---

## 🧰 Tech Stack

### 🔹 Frontend

- HTML5 + CSS3 + Vanilla JS
- Hosted on GitHub Pages (Firebase optional)

### 🔹 Backend

- Python + FastAPI
- PDF generation via `reportlab`
- Charting via `matplotlib`
- Hosted on Railway or Deta Space

---
