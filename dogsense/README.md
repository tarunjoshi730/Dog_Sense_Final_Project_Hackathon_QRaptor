# DogSense - Smart AI-Enabled Pet Health & Safety Monitor

## Overview
DogSense is a comprehensive IoT and AI-powered pet monitoring system that tracks your dog's health, safety, and behavior in real-time.

## Features
- **Real-time vitals monitoring** (heart rate, temperature)
- **GPS tracking** with geofencing alerts
- **Behavior analysis** using computer vision
- **Environmental monitoring** (temperature, humidity, water level)
- **Mobile & web dashboard** for real-time monitoring
- **AI-powered anomaly detection**
- **Automated alerts** for health and safety issues

## Architecture

```
DogSense/
├── iot/                    # IoT device firmware
│   ├── esp32_collar/      # ESP32 collar firmware
│   └── raspberry_pi/      # Home monitoring station
├── backend/               # FastAPI backend
│   ├── api/              # REST API endpoints
│   ├── models/           # Database models
│   └── services/         # Business logic
├── frontend/             # Web dashboard
├── mobile/              # React Native mobile app
├── ai/                  # AI models and training
└── docs/               # Documentation
```

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- ESP32 development board
- Raspberry Pi 4
- MQTT broker (Mosquitto)

### Installation
1. Clone the repository
2. Install dependencies: `./scripts/install.sh`
3. Configure devices: `./scripts/setup_devices.sh`
4. Start services: `./scripts/start.sh`

## Documentation
- [Setup Guide](docs/setup/README.md)
- [API Documentation](docs/api/README.md)
- [Deployment Guide](docs/deployment/README.md)

## License
MIT License