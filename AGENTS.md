# AGENTS.md

Instructions and guardrails for AI coding agents working in the **Distributed AI Model Serving Framework** (`distributed-ai-workload`) repository.

---

## 1. Project Context & Authoritative Docs

This is a hands-on distributed systems & ML infrastructure learning project built iteratively across a 10-week roadmap.

Before making non-trivial changes, read:
- **`docs/ARCHITECTURE.md`** — Current system architecture (Week 6), data contracts, deployment topology, ADRs, and planned evolution.
- **`context.md`** — Weekly milestone roadmap, learning objectives, and target deliverables.
- **`README.md`** — High-level overview and recorded benchmark results.

---

## 2. Collaboration Mode

Operate as a **collaborative builder**:
- You may write and edit code directly when asked, rather than only giving advice.
- **Explain trade-offs** behind non-trivial implementation choices (e.g., concurrency, serialization, failure handling, latency vs. throughput) so the project remains a strong learning experience.
- **Respect the current milestone.** Do not jump ahead to future roadmap weeks (e.g., adding RabbitMQ, Redis, Prometheus, or Kubernetes) unless explicitly requested.
- **Ask before changing contracts or infrastructure:**
  - Always ask before modifying `proto/inference.proto` or any breaking HTTP API schema.
  - Always ask before introducing new infrastructure services (message brokers, databases, monitoring stacks, etc.).

---

## 3. Repository Layout

```text
distributed-ai-workload/
├── AGENTS.md                 # This file
├── README.md                 # Project summary & benchmark findings
├── context.md                # 10-week learning roadmap & milestones
├── docs/
│   └── ARCHITECTURE.md       # System architecture, contracts & ADRs
├── pyproject.toml            # Python dependencies & project metadata (Python >=3.13)
├── uv.lock                   # Locked dependency graph (managed by uv)
├── docker-compose.yml        # Local multi-container cluster (master + 3 workers)
├── DockerFile.master         # Master container image (FastAPI + Uvicorn)
├── DockerFile.worker         # Worker container image (gRPC + PyTorch ResNet-18)
├── master/
│   ├── main.py               # FastAPI gateway (/, /health, /infer)
│   ├── scheduler.py          # Round-robin batch dispatcher (asyncio.gather)
│   ├── grpc_client.py        # Async gRPC client stub wrapper
│   └── aggregator.py         # Reorders worker results by image_id
├── worker/
│   ├── server.py             # gRPC server (ThreadPoolExecutor, port 50051)
│   └── ml_service.py         # ResNet-18 loading, preprocessing & inference
├── proto/
│   ├── inference.proto       # gRPC service & message definitions
│   ├── inference_pb2.py      # Generated protobuf classes (do not hand-edit)
│   └── inference_pb2_grpc.py # Generated gRPC stubs/servicers (do not hand-edit)
├── data/
│   └── labels/
│       └── imagenet-labels.json
└── scripts/
    ├── infer_local.py        # Standalone single-image inference script
    ├── benchmark.py          # Async httpx batch latency/throughput benchmark
    └── locust.py             # Locust load-testing user definition
```

---

## 4. Engineering Guardrails

### Dependency Management (`uv` only)
- **Always use `uv`** (`pyproject.toml` and `uv.lock`).
- **Never** use `pip install` to modify dependencies and **never** recreate `requirements.txt`.
- Common commands:
  ```bash
  uv add <package>            # Add a runtime dependency
  uv add --dev <package>      # Add a dev-only dependency
  uv sync                     # Sync local .venv with uv.lock
  uv run <command>            # Run scripts inside the uv environment
  ```
- Both Dockerfiles install dependencies via `uv sync --frozen --no-dev`, so `uv.lock` must stay in sync with `pyproject.toml`.

### Protocol Buffers & gRPC Contracts
- `proto/inference.proto` is the single source of truth for master-to-worker RPCs.
- **Never hand-edit** `proto/inference_pb2.py` or `proto/inference_pb2_grpc.py`.
- After approved edits to `proto/inference.proto`, regenerate stubs from the repo root:
  ```bash
  uv run python -m grpc_tools.protoc -I proto --python_out=proto --grpc_python_out=proto proto/inference.proto
  ```

### Code Style & Typing
- Use Python **type hints** on all new and modified function signatures (`params` and return types).
- Write clear, concise **docstrings** for modules, classes, and public functions.
- Follow standard Python formatting and linting conventions (PEP 8 / `ruff` compatible: clean imports, no unused variables, explicit exception handling).
- Keep master I/O non-blocking (`async`/`await` with `grpc.aio` and FastAPI async routes).

### Docker & Compose Synchronization
- Whenever you add/rename files, change ports, add environment variables, or modify startup commands, update **`DockerFile.master`**, **`DockerFile.worker`**, and **`docker-compose.yml`** in the same change.
- Preserve the exact filename casing (`DockerFile.master` and `DockerFile.worker` — capital `F`) unless performing a deliberate rename across `docker-compose.yml` and docs.
- Keep containers running as the non-root `appuser` and preserve `TORCH_HOME=/app/.cache/torch` permissions in `DockerFile.worker`.

---

## 5. Running & Verifying Changes

### Start the Cluster
```bash
docker compose up --build
```
- Master API: `http://localhost:8000` (HTML upload form at `/`, health at `/health`, inference at `POST /infer`).
- Workers: `worker-1`, `worker-2`, `worker-3` on internal port `50051`.

### Benchmarking & Load Testing
Run from the `scripts/` directory (scripts reference `../data/images/elephant.jpg`):
```bash
# Async batch benchmark (200 images x 5 iterations)
uv run python scripts/benchmark.py

# Locust load test (web UI on http://localhost:8089)
uv run locust -f scripts/locust.py
```

---

## 6. Known Codebase Quirks

Be aware of these existing details when modifying related files:
- **`WORKER_ADDRESSES` whitespace:** `docker-compose.yml` currently defines `worker-1:50051 ,worker-2:50051 ,worker-3:50051` and `master/scheduler.py` splits on `,` without `.strip()`. Be careful if modifying address parsing or env vars.
- **`sys.path` proto imports:** `master/grpc_client.py` and `worker/server.py` append the repo root and `proto/` to `sys.path` to resolve generated `inference_pb2` imports.
- **Hardcoded container label path:** `worker/ml_service.py` reads `/app/data/labels/imagenet-labels.json`, which assumes the container working directory (`/app`).
- **Placeholder health endpoint:** `GET /health` in `master/main.py` currently returns static `"active_workers": 0`.
