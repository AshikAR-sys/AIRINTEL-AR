from datetime import datetime, timedelta
from random import Random
from .models import FareObservation

ROUTES = [
    ("MAA-DEL","MAA","DEL"),("BOM-DEL","BOM","DEL"),
    ("BLR-DEL","BLR","DEL"),("MAA-BOM","MAA","BOM"),
    ("HYD-DEL","HYD","DEL"),("CCU-DEL","CCU","DEL")
]
AIRLINES = ["IndiGo","Air India","Akasa Air","SpiceJet"]

def seed_if_empty(db):
    if db.query(FareObservation).count():
        return
    rnd = Random(26056)
    now = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
    base = {"MAA-DEL":5600,"BOM-DEL":5100,"BLR-DEL":5300,"MAA-BOM":3900,"HYD-DEL":4700,"CCU-DEL":5200}
    rows=[]
    for day in range(60):
        dt=now-timedelta(days=59-day)
        for route,origin,dest in ROUTES:
            for j in range(4):
                airline=AIRLINES[(day+j)%len(AIRLINES)]
                weekend=350 if dt.weekday()>=5 else 0
                price=max(1800,base[route]+day*6+weekend+rnd.randint(-260,260)+j*120)
                rows.append(FareObservation(
                    observed_at=dt, route=route, origin=origin, destination=dest,
                    airline=airline, flight_code=f"{airline[:2].upper()}{100+((day+j)*7)%800}",
                    price_inr=float(price), source="Demo Public Fare Feed",
                    cabin="Economy", duration_minutes=130+j*15
                ))
    db.bulk_save_objects(rows)
    db.commit()
