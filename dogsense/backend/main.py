from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import asyncio
from datetime import datetime, timedelta

from database import get_db, engine
from models import Base, Pet, Device, SensorData, Alert, BehaviorAnalysis
from services.mqtt_service import MQTTService
from services.alert_service import AlertService
from services.ai_service import AIService
from services.websocket_service import WebSocketService
from schemas import (
    PetCreate, PetResponse, 
    SensorDataCreate, SensorDataResponse,
    AlertCreate, AlertResponse,
    BehaviorAnalysisResponse
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DogSense API",
    description="Smart Pet Health & Safety Monitor API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
mqtt_service = MQTTService()
alert_service = AlertService()
ai_service = AIService()
websocket_service = WebSocketService()

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await mqtt_service.start()
    await websocket_service.start()

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await mqtt_service.stop()
    await websocket_service.stop()

# WebSocket endpoint for real-time data
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket_service.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_service.handle_message(client_id, data)
    except WebSocketDisconnect:
        websocket_service.disconnect(client_id)

# Pet endpoints
@app.post("/pets", response_model=PetResponse)
async def create_pet(pet: PetCreate, db: Session = Depends(get_db)):
    """Create a new pet profile"""
    db_pet = Pet(**pet.dict())
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet

@app.get("/pets", response_model=List[PetResponse])
async def get_pets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all pets"""
    pets = db.query(Pet).offset(skip).limit(limit).all()
    return pets

@app.get("/pets/{pet_id}", response_model=PetResponse)
async def get_pet(pet_id: int, db: Session = Depends(get_db)):
    """Get a specific pet"""
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pet

# Sensor data endpoints
@app.post("/sensor-data", response_model=SensorDataResponse)
async def create_sensor_data(data: SensorDataCreate, db: Session = Depends(get_db)):
    """Create new sensor data entry"""
    db_data = SensorData(**data.dict())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    
    # Process data for alerts
    await alert_service.process_sensor_data(db_data, db)
    
    # Broadcast to WebSocket clients
    await websocket_service.broadcast("sensor_update", db_data.dict())
    
    return db_data

@app.get("/sensor-data", response_model=List[SensorDataResponse])
async def get_sensor_data(
    pet_id: Optional[int] = None,
    device_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get sensor data with filtering"""
    query = db.query(SensorData)
    
    if pet_id:
        query = query.filter(SensorData.pet_id == pet_id)
    if device_id:
        query = query.filter(SensorData.device_id == device_id)
    if start_date:
        query = query.filter(SensorData.timestamp >= start_date)
    if end_date:
        query = query.filter(SensorData.timestamp <= end_date)
    
    data = query.order_by(SensorData.timestamp.desc()).limit(limit).all()
    return data

# Alert endpoints
@app.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    pet_id: Optional[int] = None,
    severity: Optional[str] = None,
    resolved: Optional[bool] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get alerts with filtering"""
    query = db.query(Alert)
    
    if pet_id:
        query = query.filter(Alert.pet_id == pet_id)
    if severity:
        query = query.filter(Alert.severity == severity)
    if resolved is not None:
        query = query.filter(Alert.resolved == resolved)
    
    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
    return alerts

@app.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    """Resolve an alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.resolved = True
    alert.resolved_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Alert resolved"}

# Behavior analysis endpoints
@app.get("/behavior-analysis/{pet_id}", response_model=List[BehaviorAnalysisResponse])
async def get_behavior_analysis(
    pet_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get behavior analysis for a pet"""
    query = db.query(BehaviorAnalysis).filter(BehaviorAnalysis.pet_id == pet_id)
    
    if start_date:
        query = query.filter(BehaviorAnalysis.timestamp >= start_date)
    if end_date:
        query = query.filter(BehaviorAnalysis.timestamp <= end_date)
    
    analysis = query.order_by(BehaviorAnalysis.timestamp.desc()).all()
    return analysis

# Dashboard endpoints
@app.get("/dashboard/summary")
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get dashboard summary data"""
    total_pets = db.query(Pet).count()
    active_alerts = db.query(Alert).filter(Alert.resolved == False).count()
    recent_data = db.query(SensorData).order_by(SensorData.timestamp.desc()).limit(10).all()
    
    return {
        "total_pets": total_pets,
        "active_alerts": active_alerts,
        "recent_data": recent_data
    }

@app.get("/dashboard/pet/{pet_id}/health")
async def get_pet_health_summary(pet_id: int, db: Session = Depends(get_db)):
    """Get health summary for a specific pet"""
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    # Get latest sensor data
    latest_data = db.query(SensorData).filter(
        SensorData.pet_id == pet_id
    ).order_by(SensorData.timestamp.desc()).first()
    
    # Get recent alerts
    recent_alerts = db.query(Alert).filter(
        Alert.pet_id == pet_id,
        Alert.created_at >= datetime.utcnow() - timedelta(days=7)
    ).all()
    
    # Get behavior patterns
    behavior_data = db.query(BehaviorAnalysis).filter(
        BehaviorAnalysis.pet_id == pet_id,
        BehaviorAnalysis.timestamp >= datetime.utcnow() - timedelta(days=7)
    ).all()
    
    return {
        "pet": pet,
        "latest_data": latest_data,
        "recent_alerts": recent_alerts,
        "behavior_patterns": behavior_data
    }

# Device management endpoints
@app.post("/devices/register")
async def register_device(device_data: dict, db: Session = Depends(get_db)):
    """Register a new device"""
    device = Device(
        device_id=device_data.get('device_id'),
        device_type=device_data.get('device_type'),
        pet_id=device_data.get('pet_id'),
        is_active=True
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    
    return device

@app.get("/devices/{device_id}/status")
async def get_device_status(device_id: str, db: Session = Depends(get_db)):
    """Get device status"""
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Get latest data from device
    latest_data = db.query(SensorData).filter(
        SensorData.device_id == device_id
    ).order_by(SensorData.timestamp.desc()).first()
    
    return {
        "device": device,
        "last_seen": latest_data.timestamp if latest_data else None,
        "is_online": latest_data and (datetime.utcnow() - latest_data.timestamp).seconds < 300
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)