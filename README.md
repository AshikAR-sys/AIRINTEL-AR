# AirIntel India — Full Stack MVP

project: Real-time Airfare Price Index for India.

## Fastest way to run
1. Install Docker Desktop.
2. Open a terminal inside this folder.
3. Run: `docker compose up --build`
4. Open http://localhost:5173
5. Backend API docs: http://localhost:8000/docs

The app seeds demo airfare data automatically, so the complete dashboard works immediately.

## Flow
Airfare data -> cleaning -> PostgreSQL -> APIx -> forecasting -> dashboard

## Stack
Frontend: React + Tailwind CSS + Chart.js
Backend: FastAPI (Python)
Database: PostgreSQL
Web Scraping: Playwright
Analytics: Airfare Price Index + lightweight forecasting

## Important
Real airline/travel websites can change their HTML and may have anti-bot restrictions. The included Playwright layer is a configurable prototype and uses a safe demo collector by default. For production, add site-specific adapters only for permitted sources and respect each site's terms, robots rules, and rate limits.

## Main API endpoints
GET /health
GET /api/summary
GET /api/routes
GET /api/fares?route=MAA-DEL
GET /api/index?route=MAA-DEL
GET /api/forecast?route=MAA-DEL
POST /api/scrape/run
GET /api/export/csv?route=MAA-DEL
