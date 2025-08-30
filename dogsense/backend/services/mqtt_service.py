import json
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime
import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session
from database import SessionLocal
from models import SensorData, Alert, BehaviorAnalysis, Pet, Device

logger = logging.getLogger(__name__)

class MQTTService:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.is_running = False
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback for when the client receives a CONNACK response from the server."""
        logger.info(f"Connected with result code {rc}")
        
        # Subscribe to all relevant topics
        client.subscribe("dogsense/data/+")
        client.subscribe("dogsense/alerts/+")
        client.subscribe("dogsense/behavior/+")
        client.subscribe("dogsense/home/+")
        
    def on_message(self, client, userdata, msg):
        """Callback for when a PUBLISH message is received from the server."""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            logger.info(f"Received message on topic {topic}: {payload}")
            
            # Route message based on topic
            if topic.startswith("dogsense/data/"):
                self.handle_sensor_data(payload)
            elif topic.startswith("dogsense/alerts/"):
                self.handle_alert(payload)
            elif topic.startswith("dogsense/behavior/"):
                self.handle_behavior_data(payload)
            elif topic.startswith("dogsense/home/"):
                self.handle_home_data(payload)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            
    def handle_sensor_data(self, data: Dict[str, Any]):
        """Process sensor data from devices"""
        try:
            db = SessionLocal()
            
            # Find pet by device_id
            device = db.query(Device).filter(
                Device.device_id == data.get('device_id')
            ).first()
            
            if not device:
                logger.warning(f"Device {data.get('device_id')} not found")
                return
                
            # Create sensor data record
            sensor_data = SensorData(
                pet_id=device.pet_id,
                device_id=data.get('device_id'),
                heart_rate=data.get('heart_rate'),
                temperature=data.get('temperature'),
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                speed=data.get('speed'),
                satellites=data.get('satellites'),
                activity_level=data.get('activity_level'),
                ambient_temperature=data.get('ambient_temperature'),
                humidity=data.get('humidity'),
                water_level=data.get('water_level'),
                raw_data=data
            )
            
            db.add(sensor_data)
            db.commit()
            
            # Check for geofence violations
            self.check_geofence_violation(device.pet_id, data)
            
            db.close()
            
        except Exception as e:
            logger.error(f"Error handling sensor data: {e}")
            
    def handle_alert(self, alert_data: Dict[str, Any]):
        """Process alert data"""
        try:
            db = SessionLocal()
            
            # Find pet by device_id
            device = db.query(Device).filter(
                Device.device_id == alert_data.get('device_id')
            ).first()
            
            if not device:
                logger.warning(f"Device {alert_data.get('device_id')} not found")
                return
                
            # Create alert record
            alert = Alert(
                pet_id=device.pet_id,
                device_id=alert_data.get('device_id'),
                alert_type=alert_data.get('alert_type'),
                severity=self.determine_severity(alert_data),
                title=f"{alert_data.get('alert_type', 'Unknown')} Alert",
                description=json.dumps(alert_data),
                data=alert_data
            )
            
            db.add(alert)
            db.commit()
            
            # Send notifications
            self.send_notification(device.pet_id, alert)
            
            db.close()
            
        except Exception as e:
            logger.error(f"Error handling alert: {e}")
            
    def handle_behavior_data(self, behavior_data: Dict[str, Any]):
        """Process behavior analysis data"""
        try:
            db = SessionLocal()
            
            # Find pet by device_id
            device = db.query(Device).filter(
                Device.device_id == behavior_data.get('device_id')
            ).first()
            
            if not device:
                logger.warning(f"Device {behavior_data.get('device_id')} not found")
                return
                
            # Create behavior analysis record
            behavior = BehaviorAnalysis(
                pet_id=device.pet_id,
                device_id=behavior_data.get('device_id'),
                resting=behavior_data.get('behavior', {}).get('resting'),
                active=behavior_data.get('behavior', {}).get('active'),
                alert=behavior_data.get('behavior', {}).get('alert'),
                distressed=behavior_data.get('behavior', {}).get('distressed'),
                playing=behavior_data.get('behavior', {}).get('playing'),
                eating=behavior_data.get('behavior', {}).get('eating'),
                drinking=behavior_data.get('behavior', {}).get('drinking'),
                barking=behavior_data.get('behavior', {}).get('barking'),
                whining=behavior_data.get('behavior', {}).get('whining'),
                panting=behavior_data.get('behavior', {}).get('panting'),
                limping=behavior_data.get('behavior', {}).get('limping'),
                scratching=behavior_data.get('behavior', {}).get('scratching')
            )
            
            db.add(behavior)
            db.commit()
            
            # Check for concerning behaviors
            self.check_concerning_behaviors(device.pet_id, behavior_data)
            
            db.close()
            
        except Exception as e:
            logger.error(f"Error handling behavior data: {e}")
            
    def handle_home_data(self, data: Dict[str, Any]):
        """Process home monitoring data"""
        try:
            db = SessionLocal()
            
            # Create sensor data record for home station
            sensor_data = SensorData(
                device_id=data.get('device_id'),
                ambient_temperature=data.get('temperature'),
                humidity=data.get('humidity'),
                water_level=data.get('water_level'),
                raw_data=data
            )
            
            db.add(sensor_data)
            db.commit()
            
            db.close()
            
        except Exception as e:
            logger.error(f"Error handling home data: {e}")
            
    def check_geofence_violation(self, pet_id: int, data: Dict[str, Any]):
        """Check if pet has left geofenced area"""
        try:
            db = SessionLocal()
            
            # Get geofences for pet
            geofences = db.query(Geofence).filter(
                Geofence.pet_id == pet_id,
                Geofence.is_active == True
            ).all()
            
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            
            if latitude and longitude:
                for geofence in geofences:
                    distance = self.calculate_distance(
                        latitude, longitude,
                        geofence.latitude, geofence.longitude
                    )
                    
                    if distance > geofence.radius:
                        # Create geofence violation alert
                        alert = Alert(
                            pet_id=pet_id,
                            device_id=data.get('device_id'),
                            alert_type='geofence_violation',
                            severity='high',
                            title='Geofence Violation',
                            description=f'Pet left safe zone: {geofence.name}',
                            data={
                                'geofence_name': geofence.name,
                                'distance': distance,
                                'current_location': {'lat': latitude, 'lng': longitude}
                            }
                        )
                        
                        db.add(alert)
                        db.commit()
                        
                        self.send_notification(pet_id, alert)
                        
            db.close()
            
        except Exception as e:
            logger.error(f"Error checking geofence: {e}")
            
    def check_concerning_behaviors(self, pet_id: int, behavior_data: Dict[str, Any]):
        """Check for concerning behavior patterns"""
        try:
            db = SessionLocal()
            
            behaviors = behavior_data.get('behavior', {})
            concerning_thresholds = {
                'distressed': 0.7,
                'limping': 0.5,
                'scratching': 0.6
            }
            
            for behavior, threshold in concerning_thresholds.items():
                if behaviors.get(behavior, 0) > threshold:
                    alert = Alert(
                        pet_id=pet_id,
                        device_id=behavior_data.get('device_id'),
                        alert_type='behavior_concern',
                        severity='medium',
                        title=f'Concerning Behavior: {behavior}',
                        description=f'Detected high {behavior} behavior',
                        data={'behavior': behavior, 'confidence': behaviors.get(behavior)}
                    )
                    
                    db.add(alert)
                    db.commit()
                    
                    self.send_notification(pet_id, alert)
                    
            db.close()
            
        except Exception as e:
            logger.error(f"Error checking behaviors: {e}")
            
    def determine_severity(self, alert_data: Dict[str, Any]) -> str:
        """Determine alert severity based on data"""
        alert_type = alert_data.get('alert_type')
        value = alert_data.get('value')
        
        if alert_type == 'heart_rate':
            if value < 50 or value > 150:
                return 'critical'
            elif value < 60 or value > 120:
                return 'high'
            else:
                return 'medium'
                
        elif alert_type == 'temperature':
            if value < 37 or value > 40:
                return 'critical'
            elif value < 37.5 or value > 39.5:
                return 'high'
            else:
                return 'medium'
                
        return 'medium'
        
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two GPS coordinates in meters"""
        from math import radians, cos, sin, asin, sqrt
        
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Radius of earth in meters
        r = 6371000
        return c * r
        
    def send_notification(self, pet_id: int, alert):
        """Send notification to pet owners"""
        # This would integrate with push notification services
        logger.info(f"Sending notification for pet {pet_id}: {alert.title}")
        
    async def start(self):
        """Start the MQTT service"""
        if self.is_running:
            return
            
        self.client.connect("localhost", 1883, 60)
        self.client.loop_start()
        self.is_running = True
        logger.info("MQTT service started")
        
    async def stop(self):
        """Stop the MQTT service"""
        if not self.is_running:
            return
            
        self.client.loop_stop()
        self.client.disconnect()
        self.is_running = False
        logger.info("MQTT service stopped")