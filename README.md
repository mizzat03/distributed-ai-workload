# Distributed AI Model Serving Framework

A highly scalable, distributed image inference system built with Python, FastAPI, PyTorch, gRPC, and Docker.
This project demonstrates how resource-intensive machine learning workloads can be decoupled and scaled across multiple worker nodes, showcasing a modern microservice architecture designed for high throughput and fault tolerance.

---

## Project Overview

This system serves as a robust proof-of-concept for enterprise-grade AI model deployment.

Instead of bottlenecking inference directly inside a single monolithic API server, a **master node** receives client requests and asynchronously delegates the computational heavy lifting to dedicated **worker nodes** via high-speed gRPC channels.

This architecture provides a scalable foundation that bridges:
* High-Performance Machine Learning Inference
* Scalable Distributed Systems
* Asynchronous Backend APIs
* Low-Latency Service-to-Service Communication
* Containerization & Orchestration
* Fault Tolerance & High Availability

---

## Current Progress 

### Week 1: Core Inference
* Local PyTorch image inference
* Image preprocessing pipeline
* Pretrained CNN model inference
* Single image prediction

### Week 2: API Gateway
* FastAPI inference API
* `POST /infer` endpoint
* Multipart image uploads
* JSON prediction responses

### Week 3: Microservice Communication
* gRPC + Protocol Buffers integration
* Separating master and worker architecture
* Implementing high-speed gRPC communication channels
* Creating protobuf service definitions

### Week 4: Containerization & Orchestration
* Containerizing the architecture using Docker (`Dockerfile.master`, `Dockerfile.worker`)
* Orchestrating the multi-container cluster using `docker-compose.yml`
* Configuring internal Docker DNS and optimizing gRPC network routing
* Managing Linux user permissions and persisting PyTorch model caches
* Implementing `.dockerignore` for strict environment isolation

### Week 5: Multiple Workers & Batch Splitting
* Scaled the architecture to support multiple worker node containers within the Docker Compose network.
* Implemented a batch-splitting scheduler to evenly distribute image payloads across available workers.
* Utilized Python `asyncio (asyncio.gather)` to fire master-to-worker gRPC network requests concurrently, significantly reducing batch inference latency.
* Created a result aggregator to collect asynchronous worker responses and reconstruct them into the original ordered format for the client.

### Week 6: Benchmarking & Performance Testing (Current)
* Built a custom asynchronous Python benchmarking script using `httpx` to simulate high-volume batch requests.
* Measured end-to-end system latency and throughput (images/second) across different worker pool sizes.
* Identified and documented local hardware bottlenecks (CPU contention) in the distributed architecture.

---

## Performance Benchmarks

To validate the scalability of the distributed architecture, the system was benchmarked locally using a batch payload of **200 images**. The tests measured total round-trip latency and throughput as the number of active gRPC worker containers increased.

| Setup | Average Latency (200 images) | Average Throughput |
| :--- | :--- | :--- |
| **1 Worker** | 5.67 seconds | 35.32 images/sec |
| **2 Workers** | 4.55 seconds | 44.00 images/sec |
| **3 Workers** | 4.56 seconds | 43.90 images/sec |

### Engineering Findings & Bottleneck Analysis
* **Successful Distribution (1 to 2 Workers):** Scaling from one to two workers yielded a clear performance improvement. Average latency dropped by ~1.1 seconds, and throughput increased by ~24%, proving the `scheduler.py` and `aggregator.py` successfully distribute and merge concurrent payloads.
* **The Hardware Plateau (2 vs 3 Workers):** Adding a third worker yielded zero additional performance gains. This demonstrates textbook **CPU contention**. Because PyTorch inference aggressively utilizes CPU cores, running two workers on a local machine fully saturated the available physical hardware limits (such as those imposed by Docker Desktop). Adding a third worker forced containers to compete for the same maxed-out CPU cores, confirming that future linear scaling requires deploying the workers across discrete physical hardware or cloud instances.

---

## Current Architecture

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

```

```