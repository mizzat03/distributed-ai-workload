# Distributed AI Model Serving Framework

A highly scalable, distributed image inference system built with Python, FastAPI, PyTorch, gRPC, and Docker.  
This project demonstrates how resource-intensive machine learning workloads can be decoupled and scaled across multiple worker nodes, showcasing a modern microservice architecture designed for high throughput and fault tolerance.

---

# Project Overview

This system serves as a robust proof-of-concept for enterprise-grade AI model deployment. 

Instead of bottlenecking inference directly inside a single monolithic API server, a **master node** receives client requests and asynchronously delegates the computational heavy lifting to dedicated **worker nodes** via high-speed gRPC channels. 

This architecture provides a scalable foundation that bridges:
- High-Performance Machine Learning Inference
- Scalable Distributed Systems
- Asynchronous Backend APIs
- Low-Latency Service-to-Service Communication
- Containerization & Orchestration
- Fault Tolerance & High Availability

---

# Current Progress (Week 4)

## Completed

### Week 1: Core Inference
- Local PyTorch image inference
- Image preprocessing pipeline
- Pretrained CNN model inference
- Single image prediction

### Week 2: API Gateway
- FastAPI inference API
- `POST /infer` endpoint
- Multipart image uploads
- JSON prediction responses

### Week 3: Microservice Communication
- gRPC + Protocol Buffers integration
- Separating master and worker architecture
- Implementing high-speed gRPC communication channels
- Creating protobuf service definitions

### Week 4: Containerization & Orchestration (Current)
- Containerizing the architecture using Docker (`Dockerfile.master`, `Dockerfile.worker`)
- Orchestrating the multi-container cluster using `docker-compose.yml`
- Configuring internal Docker DNS and optimizing gRPC network routing
- Managing Linux user permissions and persisting PyTorch model caches
- Implementing `.dockerignore` for strict environment isolation

---

# Current Architecture

```text
                                Client
                                  |
                                  v (HTTP POST /infer)
+-----------------------------------------------------------------+
| Docker Compose Virtual Network                                  |
|                                                                 |
|   +-----------------------+          +-----------------------+  |
|   | ai_master_node        |          | worker                |  |
|   |                       |          |                       |  |
|   | [FastAPI]             |  gRPC    | [gRPC Server]         |  |
|   | Port 8000             |=======>  | Port 50051            |  |
|   |                       |          | [PyTorch ResNet-18]   |  |
|   +-----------------------+          +-----------------------+  |
|                                                                 |
+-----------------------------------------------------------------+