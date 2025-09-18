# 🚀 ProServe - Modern Microservices Framework

[![PyPI version](https://badge.fury.io/py/proserve.svg)](https://badge.fury.io/py/proserve)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Build Status](https://travis-ci.com/tom-sapletta-com/proserve.svg?branch=main)](https://travis-ci.com/tom-sapletta-com/proserve)

**Build production-ready microservices with minimal code - Python decorators or YAML manifests!**

🎯 **98% Less Boilerplate • 5-Minute Start • Production Ready**

ProServe is a revolutionary microservices framework that combines the simplicity of Flask with the power of modern architecture. Create APIs, static sites, real-time chat, and more with just a few lines of code.

> 🚀 **Fully Modular Architecture**: All components are now modular, testable, and follow SOLID principles  
> 🧪 **Comprehensive E2E Testing**: 8+ test suites covering real-world scenarios, security, performance, and integrations

## ⚡ Quick Start (3 Lines of Code!)

```python
# app.py
from proserve import Service

app = Service("my-api")

@app.endpoint("/", method="GET")
async def hello(request):
    return {"message": "Hello World! 🚀"}

if __name__ == "__main__":
    app.run(port=8080)
```

```bash
python app.py
# Open: http://localhost:8080
```

**That's it!** You have a production-ready API running.

> 🎓 **New to microservices?** Check out our [Junior Quick Start Guide](./docs/JUNIOR_QUICK_START.md) - "ProServe in 5 minutes"


## 🏗️ Manifest-Driven Development

**Note:** Manifests are **not** outdated. They are a core feature of ProServe, providing a declarative way to define microservices using YAML. The newer decorator-based approach complements manifests, offering flexibility for developers who prefer coding over configuration. Both approaches are fully supported and production-ready.

With tools like [SELLM](https://github.com/tom-sapletta-com/sellm), you can even generate manifests using AI from simple text descriptions, making it incredibly easy to create complex services without manual configuration.

### Example 1: Basic Manifest

```yaml
# manifest.yml
name: my-service
port: 8080

endpoints:
  - path: /api/status
    method: GET
    response:
      status: "ok"
      version: "1.0.0"
  
  - path: /api/hello/{name}
    method: GET
    response:
      message: "Hello {{name}}!"

static:
  enabled: true
  path: ./public
```

```bash
proserve run
# Automatically creates API from manifest.yml
# Open: http://localhost:8080/api/status
# Try: http://localhost:8080/api/hello/World
```

### Example 2: Advanced Manifest with WebSocket

```yaml
# advanced_manifest.yml
name: chat-service
port: 8081

endpoints:
  - path: /api/chat/info
    method: GET
    response:
      status: "Chat Service Running"
      users: 0

websockets:
  - path: /ws/chat
    handler: chat_handler
    on_connect:
      message: "User connected"
    on_disconnect:
      message: "User disconnected"

static:
  enabled: true
  path: ./chat_ui
```

```bash
proserve run advanced_manifest.yml
# Starts a chat service with WebSocket support
# Open: http://localhost:8081/api/chat/info
# Connect WebSocket: ws://localhost:8081/ws/chat
```

## 📖 Documentation

All detailed documentation is available in the [docs](./docs/) folder:

- [Architecture Guide](./docs/ARCHITECTURE.md) - Understand the modular design of ProServe
- [API Documentation](./docs/API_DOCUMENTATION.md) - Complete API reference
- [Quick Start Guide](./docs/QUICK_START.md) - Get started in minutes
- [Junior Quick Start](./docs/JUNIOR_QUICK_START.md) - Beginner-friendly guide
- [Deployment Checklist](./docs/DEPLOYMENT_CHECKLIST.md) - Prepare for production
- [E2E Testing Guide](./docs/E2E_TESTING.md) - Comprehensive testing suite
- [Ecosystem Overview](./docs/ECOSYSTEM.md) - Integration with other tools
- [Modular Architecture](./docs/MODULAR_ARCHITECTURE.md) - Design principles
- [Future Roadmap](./docs/FUTURE_ROADMAP.md) - Upcoming features
- [Release Notes v2.0.0](./docs/RELEASE_NOTES_v2.0.0.md) - Latest updates
- [YAML Driven Showcase](./docs/YAML_DRIVEN_SHOWCASE.md) - Manifest examples

### Python Packages

Explore the ecosystem of Python packages related to ProServe:

- [ProServe](https://pypi.org/project/proserve/) - Core microservices framework
- [Servos](https://pypi.org/project/servos/) - Environment isolation and orchestration
- [wmlog](https://pypi.org/project/wmlog/) - Centralized structured logging
- [SELLM](https://pypi.org/project/sellm/) - AI-powered manifest generator
- [EDPMT](https://pypi.org/project/edpmt/) - Hardware control framework for IoT

## 💡 Why ProServe?

- **Zero-Config APIs**: Build REST endpoints in 3 lines of code
- **Manifest-Driven**: Define services in YAML, like docker-compose
- **Multi-Environment**: Run anywhere - local, Docker, Kubernetes, embedded
- **Full-Stack**: HTTP, WebSocket, background tasks, static hosting
- **Production-Ready**: Logging, monitoring, security built-in

## License

ProServe is released under the Apache Software License 2.0. See the [LICENSE](LICENSE) file for details.

Start building microservices today with ProServe!
