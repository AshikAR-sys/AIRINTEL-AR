from dotenv import load_dotenv
load_dotenv()
from io import StringIO
import csv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import FareObservation
from .seed import seed_if_empty
from .index_engine import route_index, national_index
from .forecast import moving_average_forecast
from .scraper import scrape_configured_page

app=FastAPI(title="AirIntel India API",version="1.0.0")
origins=[x.strip() for x in __import__("os").getenv("CORS_ORIGINS","http://localhost:5173").split(",")]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db=next(get_db())
    try: seed_if_empty(db)
    finally: db.close()

@app.get("/health")
def health(): return {"status":"ok","service":"AirIntel India"}

@app.get("/api/summary")
def summary(db:Session=Depends(get_db)):
    return {
        "observations":db.query(FareObservation).count(),
        "routes":db.query(FareObservation.route).distinct().count(),
        "airlines":db.query(FareObservation.airline).distinct().count(),
        "national_index":national_index(db),
        "avg_fare":round(float(db.query(func.avg(FareObservation.price_inr)).scalar() or 0),2),
        "last_updated":db.query(func.max(FareObservation.observed_at)).scalar()
    }

@app.get("/api/routes")
def routes(db:Session=Depends(get_db)):
    rows=db.query(FareObservation.route,FareObservation.origin,FareObservation.destination,
        func.count(FareObservation.id).label("observations"),func.avg(FareObservation.price_inr).label("avg_fare")
    ).group_by(FareObservation.route,FareObservation.origin,FareObservation.destination).order_by(FareObservation.route).all()
    return [{"route":x.route,"origin":x.origin,"destination":x.destination,"observations":x.observations,
             "avg_fare":round(float(x.avg_fare),2),"index":route_index(db,x.route)} for x in rows]

@app.get("/api/fares")
def fares(route:str|None=None,limit:int=100,db:Session=Depends(get_db)):
    q=db.query(FareObservation)
    if route: q=q.filter(FareObservation.route==route)
    rows=q.order_by(FareObservation.observed_at.desc()).limit(min(limit,500)).all()
    return [{"observed_at":x.observed_at,"route":x.route,"airline":x.airline,"flight_code":x.flight_code,
             "price_inr":x.price_inr,"source":x.source} for x in rows]

@app.get("/api/index")
def index(route:str|None=None,db:Session=Depends(get_db)):
    return {"route":route or "NATIONAL","index":route_index(db,route) if route else national_index(db),"base":100.0}

@app.get("/api/forecast")
def forecast(route:str,db:Session=Depends(get_db)):
    rows=db.query(FareObservation.observed_at,func.avg(FareObservation.price_inr).label("avg_price")).filter(
        FareObservation.route==route).group_by(FareObservation.observed_at).order_by(FareObservation.observed_at).all()
    if not rows: raise HTTPException(404,"Route not found")
    points=[(x.observed_at,float(x.avg_price)) for x in rows]
    fc=moving_average_forecast(points,7)
    return {"route":route,
            "history":[{"date":d.date().isoformat(),"value":round(v,2)} for d,v in points[-30:]],
            "forecast":[{"date":d.date().isoformat(),"value":v} for d,v in fc]}

@app.post("/api/scrape/run")
async def run_scrape(db:Session=Depends(get_db)):
    data=await scrape_configured_page()
    for item in data: db.add(FareObservation(**item))
    db.commit()
    return {"inserted":len(data),"message":"Collection completed."}

@app.get("/api/export/csv")
def export_csv(route:str|None=None,db:Session=Depends(get_db)):
    q=db.query(FareObservation)
    if route: q=q.filter(FareObservation.route==route)
    rows=q.order_by(FareObservation.observed_at.desc()).all()
    out=StringIO(); w=csv.writer(out)
    w.writerow(["observed_at","route","origin","destination","airline","flight_code","price_inr","source","cabin","duration_minutes"])
    for x in rows:
        w.writerow([x.observed_at.isoformat(),x.route,x.origin,x.destination,x.airline,x.flight_code,x.price_inr,x.source,x.cabin,x.duration_minutes])
    return {"filename":f"airintel_{route or 'national'}.csv","content":out.getvalue()}
