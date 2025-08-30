import cv2
import numpy as np
import tensorflow as tf
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class BehaviorDetector:
    """AI model for detecting dog behaviors from video frames"""
    
    def __init__(self, model_path: str = None):
        self.model = None
        self.class_names = [
            'resting', 'active', 'alert', 'distressed', 
            'playing', 'eating', 'drinking', 'walking',
            'running', 'barking', 'whining', 'panting',
            'limping', 'scratching', 'sleeping'
        ]
        
        if model_path:
            self.load_model(model_path)
        else:
            self.load_default_model()
            
    def load_model(self, model_path: str):
        """Load TensorFlow Lite model"""
        try:
            self.interpreter = tf.lite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            
            # Get input and output tensors
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            logger.info(f"Loaded model from {model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.load_default_model()
            
    def load_default_model(self):
        """Load default behavior detection model"""
        # This would load a pre-trained model
        # For now, we'll use a simple placeholder
        logger.info("Using default behavior detection")
        
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """Preprocess frame for model input"""
        # Resize to model input size
        input_shape = self.input_details[0]['shape']
        height, width = input_shape[1], input_shape[2]
        
        frame_resized = cv2.resize(frame, (width, height))
        
        # Normalize pixel values
        frame_normalized = frame_resized.astype(np.float32) / 255.0
        
        # Add batch dimension
        frame_batch = np.expand_dims(frame_normalized, axis=0)
        
        return frame_batch
        
    def detect_behavior(self, frame: np.ndarray) -> Dict[str, float]:
        """Detect behavior from a single frame"""
        if self.interpreter is None:
            return self.get_placeholder_behavior()
            
        try:
            # Preprocess frame
            input_data = self.preprocess_frame(frame)
            
            # Set input tensor
            self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
            
            # Run inference
            self.interpreter.invoke()
            
            # Get output
            output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
            
            # Convert to dictionary
            behavior_scores = {
                class_name: float(score) 
                for class_name, score in zip(self.class_names, output_data[0])
            }
            
            return behavior_scores
            
        except Exception as e:
            logger.error(f"Error detecting behavior: {e}")
            return self.get_placeholder_behavior()
            
    def get_placeholder_behavior(self) -> Dict[str, float]:
        """Return placeholder behavior detection"""
        import random
        
        # Simulate realistic behavior scores
        behaviors = {
            'resting': random.uniform(0.0, 0.8),
            'active': random.uniform(0.0, 0.7),
            'alert': random.uniform(0.0, 0.6),
            'distressed': random.uniform(0.0, 0.3),
            'playing': random.uniform(0.0, 0.5),
            'eating': random.uniform(0.0, 0.4),
            'drinking': random.uniform(0.0, 0.3),
            'walking': random.uniform(0.0, 0.6),
            'running': random.uniform(0.0, 0.4),
            'barking': random.uniform(0.0, 0.5),
            'whining': random.uniform(0.0, 0.2),
            'panting': random.uniform(0.0, 0.4),
            'limping': random.uniform(0.0, 0.1),
            'scratching': random.uniform(0.0, 0.3),
            'sleeping': random.uniform(0.0, 0.9)
        }
        
        # Normalize to sum to 1.0
        total = sum(behaviors.values())
        if total > 0:
            behaviors = {k: v/total for k, v in behaviors.items()}
            
        return behaviors
        
    def detect_posture(self, frame: np.ndarray) -> Dict[str, any]:
        """Detect dog posture from frame"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Use OpenCV pose detection
            # This is a simplified version - production would use more sophisticated methods
            
            # Detect keypoints (simplified)
            height, width = frame.shape[:2]
            
            # Simulate posture detection
            posture = {
                'sitting': 0.3,
                'standing': 0.4,
                'lying_down': 0.2,
                'walking': 0.1
            }
            
            # Detect body orientation
            orientation = self.detect_orientation(frame)
            
            return {
                'posture': posture,
                'orientation': orientation,
                'confidence': 0.75
            }
            
        except Exception as e:
            logger.error(f"Error detecting posture: {e}")
            return {
                'posture': {'unknown': 1.0},
                'orientation': 0.0,
                'confidence': 0.0
            }
            
    def detect_orientation(self, frame: np.ndarray) -> float:
        """Detect body orientation in degrees"""
        # Simplified orientation detection
        # In production, use pose estimation models
        
        height, width = frame.shape[:2]
        center_x = width // 2
        
        # Simulate orientation based on frame analysis
        return 0.0  # Placeholder
        
    def detect_anomaly(self, current_behavior: Dict[str, float], 
                      historical_behaviors: List[Dict[str, float]]) -> Dict[str, float]:
        """Detect anomalous behavior patterns"""
        if not historical_behaviors:
            return {'anomaly_score': 0.0, 'is_anomaly': False}
            
        try:
            # Calculate average historical behavior
            avg_behavior = {}
            for behavior in self.class_names:
                values = [hb.get(behavior, 0) for hb in historical_behaviors]
                avg_behavior[behavior] = np.mean(values) if values else 0
                
            # Calculate deviation
            deviations = {}
            for behavior in self.class_names:
                current = current_behavior.get(behavior, 0)
                avg = avg_behavior.get(behavior, 0)
                deviations[behavior] = abs(current - avg)
                
            # Calculate anomaly score
            anomaly_score = np.mean(list(deviations.values()))
            
            # Determine if it's an anomaly
            threshold = 0.3  # Adjust based on requirements
            is_anomaly = anomaly_score > threshold
            
            return {
                'anomaly_score': float(anomaly_score),
                'is_anomaly': bool(is_anomaly),
                'deviations': deviations,
                'threshold': threshold
            }
            
        except Exception as e:
            logger.error(f"Error detecting anomaly: {e}")
            return {'anomaly_score': 0.0, 'is_anomaly': False}
            
    def track_activity(self, frames: List[np.ndarray]) -> Dict[str, float]:
        """Track activity level over multiple frames"""
        if not frames:
            return {'activity_level': 0.0, 'movement_score': 0.0}
            
        try:
            # Calculate optical flow for movement detection
            if len(frames) < 2:
                return {'activity_level': 0.0, 'movement_score': 0.0}
                
            # Convert frames to grayscale
            gray_frames = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames]
            
            # Calculate optical flow
            flow = cv2.calcOpticalFlowPyrLK(
                gray_frames[0], gray_frames[-1], None, None
            )
            
            if flow[0] is not None:
                # Calculate movement magnitude
                movement = np.mean(np.abs(flow[0]))
                activity_level = min(movement / 100.0, 1.0)
            else:
                activity_level = 0.0
                
            return {
                'activity_level': float(activity_level),
                'movement_score': float(movement) if 'movement' in locals() else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error tracking activity: {e}")
            return {'activity_level': 0.0, 'movement_score': 0.0}

class HealthAnalyzer:
    """Analyze health metrics and detect issues"""
    
    def __init__(self):
        self.normal_ranges = {
            'heart_rate': {'min': 60, 'max': 120},
            'temperature': {'min': 37.5, 'max': 39.5},
            'respiratory_rate': {'min': 10, 'max': 30}
        }
        
    def analyze_vitals(self, vitals: Dict[str, float]) -> Dict[str, any]:
        """Analyze vital signs for health issues"""
        analysis = {
            'is_normal': True,
            'alerts': [],
            'recommendations': []
        }
        
        for metric, value in vitals.items():
            if metric in self.normal_ranges:
                normal_range = self.normal_ranges[metric]
                
                if value < normal_range['min']:
                    analysis['alerts'].append({
                        'type': f'low_{metric}',
                        'value': value,
                        'threshold': normal_range['min']
                    })
                    analysis['is_normal'] = False
                    
                elif value > normal_range['max']:
                    analysis['alerts'].append({
                        'type': f'high_{metric}',
                        'value': value,
                        'threshold': normal_range['max']
                    })
                    analysis['is_normal'] = False
                    
        # Add recommendations based on alerts
        for alert in analysis['alerts']:
            if alert['type'] == 'high_temperature':
                analysis['recommendations'].append(
                    "Check for overheating - ensure pet has access to water and shade"
                )
            elif alert['type'] == 'low_heart_rate':
                analysis['recommendations'].append(
                    "Monitor closely - low heart rate may indicate distress"
                )
                
        return analysis
        
    def predict_health_risk(self, data: Dict[str, any]) -> Dict[str, float]:
        """Predict health risk based on multiple factors"""
        # Simplified risk prediction
        risk_factors = {
            'temperature_deviation': 0.0,
            'heart_rate_deviation': 0.0,
            'behavior_anomaly': 0.0,
            'activity_decline': 0.0
        }
        
        # Calculate risk scores
        total_risk = sum(risk_factors.values()) / len(risk_factors)
        
        return {
            'overall_risk': total_risk,
            'risk_factors': risk_factors,
            'risk_level': 'low' if total_risk < 0.3 else 'medium' if total_risk < 0.7 else 'high'
        }