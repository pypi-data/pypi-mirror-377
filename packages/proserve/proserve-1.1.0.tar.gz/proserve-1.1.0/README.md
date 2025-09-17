# ProServe - Professional Service Framework

🚀 **Advanced manifest-based microservice framework with multi-environment isolation**

ProServe is a powerful Python library for building scalable microservices with declarative YAML manifests, supporting deployment across diverse environments from cloud containers to embedded devices like RP2040 and Arduino.

## ✨ Features

### 🎯 **Core Framework**
- **Manifest-Driven Architecture**: Declarative YAML-based service configuration
- **Multi-Environment Isolation**: Process, Docker, Kubernetes, MicroPython, Arduino, RP2040
- **Auto-Discovery & Migration**: Automatic service detection and seamless migration tools
- **Zero Vendor Lock-in**: Export generated code and run independently

### 🔧 **Advanced Capabilities**
- **Structured Logging**: Rich console output with JSON export and WebSocket broadcasting
- **Health & Metrics**: Built-in monitoring endpoints with Prometheus integration
- **Dynamic Handlers**: Hot-reload Python scripts with isolation sandboxing
- **Background Tasks**: Async periodic tasks with optional WebSocket broadcasting
- **CORS & Security**: Configurable CORS, authentication, and request validation

### 🌍 **Multi-Platform Support**
- **Cloud Native**: Docker, Kubernetes, Docker Compose orchestration
- **Embedded Systems**: MicroPython, CircuitPython, Arduino IDE integration
- **Hardware Platforms**: Raspberry Pi Pico (RP2040), ESP32, STM32, Arduino boards
- **Development Tools**: PlatformIO, Arduino CLI, esptool integration

### 🚀 **DevOps & Deployment**
- **Blue-Green Migration**: Gradual traffic shifting with automatic rollback
- **Service Discovery**: Automatic manifest generation from existing code
- **Monitoring Stack**: Grafana dashboards, Prometheus metrics, Alertmanager
- **CI/CD Ready**: GitHub Actions, Docker builds, PyPI publishing

## 📦 Installation

### Basic Installation
```bash
pip install proserve
```

### With All Features
```bash
pip install proserve[all]
```

### Specific Feature Sets
```bash
# Docker & Kubernetes support
pip install proserve[docker,kubernetes]

# MicroPython & Embedded development
pip install proserve[micropython,arduino,rp2040]

# Monitoring & observability
pip install proserve[monitoring]

# Development tools
pip install proserve[development,testing]
```

## 🚀 Quick Start

### 1. Create a Service Manifest

```yaml
# my-service.yaml
name: my-awesome-service
version: 1.0.0
type: http
port: 8080
host: 0.0.0.0

# Features
requires_edpmt: false
enable_cors: true
enable_health: true
enable_metrics: true

# Endpoints
endpoints:
  - path: /api/hello
    method: GET
    script: handlers/hello.py

# WebSocket handlers
websocket_handlers:
  - path: /ws
    script: handlers/websocket.py

# Background tasks
background_tasks:
  - script: handlers/background.py
    interval: 60
    broadcast: true

# Environment isolation
isolation:
  mode: process  # none, process, docker, kubernetes, micropython, arduino
  timeout: 30
  auto_environment: true

# Environment variables
env_vars:
  - API_KEY
  - DATABASE_URL
  - DEBUG

# Static file serving
static_dirs:
  "/static": "./static"
  "/assets": "./assets"
```

### 2. Create Handler Scripts

```python
# handlers/hello.py
async def handle_request(request, service):
    return {"message": "Hello from ProServe!", "service": service.manifest.name}

# handlers/websocket.py  
async def handle_websocket(ws, data, service):
    if data.get('action') == 'ping':
        return {'action': 'pong', 'timestamp': time.time()}

# handlers/background.py
async def background_task(service):
    service.logger.info("Background task executed")
    return {"status": "completed"}
```

### 3. Run Your Service

```bash
# Using CLI
proserve run --manifest my-service.yaml

# Using Python
python -c "
from proserve import ServiceRunner
runner = ServiceRunner('my-service.yaml')
runner.run()
"
```

## 🌍 Multi-Environment Deployment

### Cloud Native (Docker/Kubernetes)
```yaml
isolation:
  mode: docker
  image: python:3.11-slim
  resources:
    memory: "512Mi"
    cpu: "0.5"
```

### MicroPython (RP2040/ESP32)
```yaml  
isolation:
  mode: micropython
  platform: rp2040  # or esp32, esp8266
  firmware_version: "1.19.1"
  memory_limit: 256KB
```

### Arduino
```yaml
isolation:
  mode: arduino
  board: esp32dev  # or nano33iot, uno_r4_wifi
  libraries:
    - WiFi
    - ArduinoJson
    - PubSubClient
```

## 🔧 Service Discovery & Migration

### Discover Existing Services
```bash
# Automatic service discovery
proserve-discover --project-root . --output manifests/

# Generate manifests from existing code
proserve convert legacy-service.py --output service.yaml
```

### Migrate to Manifest-Based
```bash
# Start migration with blue-green deployment  
proserve-migrate migrate --service my-service --strategy blue-green

# Monitor migration progress
proserve-migrate status --service my-service

# Complete migration
proserve-migrate complete --service my-service
```

## 🐳 Docker & Orchestration

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  my-service:
    image: proserve:latest
    environment:
      - PROSERVE_MANIFEST=/app/my-service.yaml
    ports:
      - "8080:8080"
    volumes:
      - ./manifests:/app/manifests:ro
```

### Multiple Architectures
```bash
# Build for different platforms
make build-docker  # Builds arm64, x86_64, micropython, arduino

# Deploy to specific environment
proserve-deploy --environment production --platform kubernetes
```

## 📊 Monitoring & Observability

### Built-in Endpoints
- `GET /health` - Health check with service status
- `GET /metrics` - Prometheus metrics endpoint
- `GET /status` - Detailed service information
- `WS /logs` - Real-time log streaming

### Prometheus Integration
```yaml
# Automatic metrics collection
monitoring:
  prometheus: true
  metrics_port: 9090
  custom_metrics:
    - request_duration_seconds
    - background_task_duration
    - websocket_connections_total
```

### Grafana Dashboards
```bash
# Setup monitoring stack
docker-compose -f docker-compose.manifest.yml --profile monitoring up
# Access Grafana at http://localhost:3000 (admin/admin123)
```

## 🧪 Testing & Development

### Run Tests
```bash
make test              # All tests
make test-unit         # Unit tests only  
make test-integration  # Integration tests
make test-environments # Multi-environment tests
```

### Development Setup
```bash
make dev-setup         # Complete dev environment
make format           # Code formatting
make lint             # Code linting
make check            # All quality checks
```

## 📚 Examples

### Simple HTTP Service
```python
from proserve import ProServeService, Manifest

manifest = Manifest.from_yaml("service.yaml")
service = ProServeService(manifest)

@service.endpoint("/api/users", methods=["GET"])
async def get_users(request):
    return {"users": ["alice", "bob"]}

service.run()
```

### MicroPython IoT Service
```python
# For RP2040/ESP32
from proserve.embedded import MicroPythonService

service = MicroPythonService("iot-sensor.yaml")

@service.background_task(interval=30)
async def read_sensors():
    temperature = sensor.read_temperature()
    service.broadcast({"temperature": temperature})

service.run()
```

## 📖 Documentation

- **[User Guide](https://proserve.readthedocs.io/guide/)** - Complete usage documentation
- **[API Reference](https://proserve.readthedocs.io/api/)** - Detailed API documentation  
- **[Examples](https://github.com/proserve/proserve/tree/main/examples)** - Sample applications
- **[Migration Guide](https://proserve.readthedocs.io/migration/)** - Legacy service migration
- **[Deployment Guide](https://proserve.readthedocs.io/deployment/)** - Production deployment

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
```bash
git clone https://github.com/proserve/proserve.git
cd proserve
make dev-setup
make test
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🏆 Credits

ProServe is built on top of excellent open-source libraries:
- [aiohttp](https://github.com/aio-libs/aiohttp) - Async HTTP framework
- [structlog](https://github.com/hynek/structlog) - Structured logging
- [rich](https://github.com/Textualize/rich) - Beautiful terminal output
- [docker-py](https://github.com/docker/docker-py) - Docker Python SDK
- [PyYAML](https://github.com/yaml/pyyaml) - YAML processing

---

**Made with ❤️ by the ProServe Team**
