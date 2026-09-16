from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from .database import Base

class FareObservation(Base):
    __tablename__ = "fare_observations"
    id = Column(Integer, primary_key=True)
    observed_at = Column(DateTime, nullable=False, index=True)
    route = Column(String(20), nullable=False, index=True)
    origin = Column(String(8), nullable=False)
    destination = Column(String(8), nullable=False)
    airline = Column(String(80), nullable=False)
    flight_code = Column(String(30), nullable=False)
    price_inr = Column(Float, nullable=False)
    source = Column(String(120), nullable=False)
    cabin = Column(String(30), default="Economy")
    duration_minutes = Column(Integer, default=140)

Index("ix_fare_route_time", FareObservation.route, FareObservation.observed_at)
