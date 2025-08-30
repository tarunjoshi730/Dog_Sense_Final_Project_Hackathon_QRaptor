from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Pet(Base):
    __tablename__ = "pets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    breed = Column(String(100))
    age = Column(Integer)
    weight = Column(Float)
    species = Column(String(50), default="dog")
    profile_image = Column(String(255))
    emergency_contact = Column(String(100))
    vet_contact = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    devices = relationship("Device", back_populates="pet")
    sensor_data = relationship("SensorData", back_populates="pet")
    alerts = relationship("Alert", back_populates="pet")
    behavior_analysis = relationship("BehaviorAnalysis", back_populates="pet")

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), unique=True, index=True)
    device_type = Column(String(50))  # collar, home_station, camera
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    battery_level = Column(Integer, default=100)
    last_seen = Column(DateTime)
    firmware_version = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    pet = relationship("Pet", back_populates="devices")
    sensor_data = relationship("SensorData", back_populates="device")

class SensorData(Base):
    __tablename__ = "sensor_data"
    
    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=True)
    device_id = Column(String(50), ForeignKey("devices.device_id"))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Vital signs
    heart_rate = Column(Float)
    temperature = Column(Float)
    respiratory_rate = Column(Float)
    
    # Activity
    activity_level = Column(Float)
    steps = Column(Integer)
    calories = Column(Float)
    
    # Location
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    speed = Column(Float)
    satellites = Column(Integer)
    
    # Environment
    ambient_temperature = Column(Float)
    humidity = Column(Float)
    water_level = Column(Float)
    
    # Raw sensor data
    raw_data = Column(JSON)
    
    # Relationships
    pet = relationship("Pet", back_populates="sensor_data")
    device = relationship("Device", back_populates="sensor_data")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"))
    device_id = Column(String(50))
    alert_type = Column(String(50))  # health, safety, behavior, environment
    severity = Column(String(20))  # low, medium, high, critical
    title = Column(String(200))
    description = Column(Text)
    data = Column(JSON)  # Additional alert data
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    pet = relationship("Pet", back_populates="alerts")

class BehaviorAnalysis(Base):
    __tablename__ = "behavior_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"))
    device_id = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Behavior classifications
    resting = Column(Float)
    active = Column(Float)
    alert = Column(Float)
    distressed = Column(Float)
    playing = Column(Float)
    eating = Column(Float)
    drinking = Column(Float)
    
    # Specific behaviors
    barking = Column(Float)
    whining = Column(Float)
    panting = Column(Float)
    limping = Column(Float)
    scratching = Column(Float)
    
    # Posture analysis
    posture = Column(String(50))
    confidence = Column(Float)
    
    # Image/video reference
    media_url = Column(String(255))
    
    # Relationships
    pet = relationship("Pet", back_populates="behavior_analysis")

class Geofence(Base):
    __tablename__ = "geofences"
    
    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"))
    name = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    radius = Column(Float)  # in meters
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class HealthRecord(Base):
    __tablename__ = "health_records"
    
    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"))
    record_type = Column(String(50))  # vet_visit, medication, vaccination, etc.
    title = Column(String(200))
    description = Column(Text)
    date = Column(DateTime)
    vet_name = Column(String(100))
    medications = Column(JSON)
    notes = Column(Text)
    attachments = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"))
    type = Column(String(50))  # push, email, sms
    title = Column(String(200))
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    sent_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(100))
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    pets = relationship("Pet", secondary="user_pets", back_populates="users")

class UserPet(Base):
    __tablename__ = "user_pets"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), primary_key=True)
    role = Column(String(50), default="owner")  # owner, viewer, caregiver