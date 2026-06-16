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

# Current Progress (Week 5)

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

### Week 4: Containerization & Orchestration 
- Containerizing the architecture using Docker (`Dockerfile.master`, `Dockerfile.worker`)
- Orchestrating the multi-container cluster using `docker-compose.yml`
- Configuring internal Docker DNS and optimizing gRPC network routing
- Managing Linux user permissions and persisting PyTorch model caches
- Implementing `.dockerignore` for strict environment isolation


### Week 5: Multiple Workers & Batch Splitting (Current)
- Scaled the architecture to support multiple worker node containers within the Docker Compose network.
- Implemented a batch-splitting scheduler to evenly distribute image payloads across available workers.
- Utilized Python `asyncio (asyncio.gather)` to fire master-to-worker gRPC network requests concurrently, significantly reducing batch inference latency.
- Created a result aggregator to collect asynchronous worker responses and reconstruct them into the original ordered format for the client.

---

# Current Architecture

```text
                                Client
                                  |
                                  v (HTTP POST /infer batch)
+--------------------------------------------------------------------------+
| Docker Compose Virtual Network                                           |
|                                                                          |
|   +-----------------------+               +-----------------------+      |
|   | ai_master_node        |               | worker-1              |      |
|   |                       |  gRPC         | [gRPC Server]         |      |
|   | [FastAPI Scheduler]   |=============> | [PyTorch ResNet-18]   |      |
|   | Port 8000             |               +-----------------------+      |
|   |                       |                                              |
|   | [Async Event Loop]    |  gRPC         +-----------------------+      |
|   |                       |=============> | worker-2              |      |
|   | [Result Aggregator]   |               | [gRPC Server]         |      |
|   |                       |               | [PyTorch ResNet-18]   |      |
|   +-----------------------+               +-----------------------+      |
|             ||                            |                              |
|             ||               gRPC         +-----------------------+      |
|             +===========================> | worker-n              |      |
|                                           | [gRPC Server]         |      |
|                                           | [PyTorch ResNet-18]   |      |
|                                           +-----------------------+      |
|                                                                          |
+--------------------------------------------------------------------------+

```