# Distributed AI Model Serving Framework

A distributed image inference system built with Python, FastAPI, PyTorch, and gRPC.  
This project explores how machine learning inference systems can be scaled across multiple worker nodes while introducing concepts from distributed systems, networking, backend engineering, and fault tolerance.

---

# Project Overview

This project aims to simulate a simplified production-style distributed AI inference system.

Instead of running inference directly inside a single API server, a **master node** receives inference requests and delegates the work to dedicated **worker nodes** using gRPC.

The project is designed primarily as a learning exercise to bridge:
- Machine Learning Inference
- Distributed Systems
- Backend APIs
- Service-to-Service Communication
- Fault Tolerance
- System Performance Measurement

---

# Current Progress (Week 3)

## Completed

### Week 1
- Local PyTorch image inference
- Image preprocessing pipeline
- Pretrained CNN model inference
- Single image prediction

### Week 2
- FastAPI inference API
- `POST /infer` endpoint
- Multipart image uploads
- JSON prediction responses

### Week 3 (Current)
- Learning gRPC + Protocol Buffers
- Separating master and worker architecture
- Implementing gRPC communication
- Creating protobuf service definitions

---

# Current Architecture

```text
Client
   |
   v
FastAPI Master API
   |
   v
gRPC Client
   |
   v
gRPC Worker Server
   |
   v
PyTorch Inference