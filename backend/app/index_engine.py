from sqlalchemy import func
from .models import FareObservation

BASE_INDEX = 100.0

def route_index(db, route):
    rows=db.query(FareObservation.observed_at,func.avg(FareObservation.price_inr).label("avg_price")).filter(
        FareObservation.route==route).group_by(FareObservation.observed_at).order_by(FareObservation.observed_at).all()
    if not rows: return 0.0
    prices=[float(x.avg_price) for x in rows]
    n=min(7,len(prices))
    base=sum(prices[:n])/n
    return round(BASE_INDEX*prices[-1]/base,2) if base else BASE_INDEX

def national_index(db):
    rows=db.query(FareObservation.route,FareObservation.observed_at,func.avg(FareObservation.price_inr).label("avg_price")).group_by(
        FareObservation.route,FareObservation.observed_at).order_by(FareObservation.observed_at).all()
    latest={}
    for x in rows: latest[x.route]=float(x.avg_price)
    if not latest: return 0.0
    return round(sum(latest.values())/len(latest)/50.0,2)
