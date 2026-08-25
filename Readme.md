# ScribeXAgent Production Specification & Deployment Blueprint
This document outlines the first-principles architectural shift, local development setup, and production cloud infrastructure required to deploy a stateful, monitored, and horizontally scalable multi-agent system on AWS EKS.



## 1. Base Agent & LangGraph Orchestration (Python Implementation)

To transition from a fragile, linear script to a fault-tolerant state machine, we define the orchestrator as a declarative **LangGraph State Graph**. Each step represents a specialized, contract-bound node executing in isolation, persisting its transitional changes to a database checkpointer.




## 2. Multi-Layer Observability (OpenTelemetry & Arize Phoenix)

To debug non-deterministic agent loops and comply with strict HIPAA audit guidelines, ScribeX deploys a **dual-instrumentation protocol**.

```
                     ┌────────────────────────────────────────┐
                     │          OTLP Trace Collector          │
                     │          (Local Port 6006 / 4317)      │
                     └───────────────────▲────────────────────┘
                                         │ OpenTelemetry Spans
                 ┌───────────────────────┴───────────────────────┐
                 │            FastAPI Host App Container         │
                 │                                               │
                 │  ┌─────────────────────────────────────────┐  │
                 │  │      LangChain / LangGraph Spans        │  │ (Instrumented via LangChainInstrumentor)
                 │  │       (Tracks Graph Node Transitions)   │  │
                 │  └─────────────────────────────────────────┘  │
                 │  ┌─────────────────────────────────────────┐  │
                 │  │            OpenAI Client Spans          │  │ (Instrumented via OpenAIInstrumentor)
                 │  │       (Tracks prompt text, token cost)  │  │
                 │  └─────────────────────────────────────────┘  │
                 └───────────────────────────────────────────────┘
```

### Telemetry Handshake (`src/observability.py`)

---

## 3. Local Orchestrated Environment (`docker-compose.yml`)

The local setup matches production boundaries. It encapsulates your **FastAPI Orchestrator gateway**, a local **PostgreSQL/ParadeDB** relational datastore, **Ollama** model-serving, and a self-hosted **Arize Phoenix** instance.


---

## 4. Cloud Infrastructure & AWS Architecture

When shifting ScribeXAgent to a production environment on **AWS EKS**, we apply strict **Zero-Trust** security, **Least-Privilege** scoping, and **Elastic Scaling**.

```
               NGINX / AWS Load Balancer Controller (Ingress)
                                   │
                                   ▼
                      (Private VPC Subnets)
     ┌───────────────────────────────────────────────────────────┐
     │                     AWS EKS Cluster                       │
     │                                                           │
     │  Orchestrator Pods (m7i CPU Nodes - Autoscaling)    │
     │   ┌───────────────────────────────────────────────────┐   │
     │   │ FastAPI App Container                             │   │
     │   │   - Input Injection Guardrails               │   │
     │   │   - LangGraph State Machine Loop           │   │
     │   │   - IRSA Scoped IAM Credentials       │   │
     │   └───────────────┬───────────────────────┬───────────┘   │
     │                   │                       │               │
     │                   │ mTLS                  │ HTTPS (STS)   │
     │                   ▼                       ▼               │
     │  Inference Pods (vLLM / GPU Nodes)    AWS STS Endpoint    │
     │   ┌──────────────────────────────┐     (Rotates temporary │
     │   │ local-vLLM / Whisper Pods    │      boto3 tokens)     │
     │   └──────────────────────────────┘              │
     └───────────────────┬───────────────────────────────────────┘
                         │ (DynamoDBSaver Checkpoints)
                         ▼
     ┌───────────────────────────────────────────────────────────┐
     │                      AWS Cloud Core                       │
     │                                                           │
     │  Amazon DynamoDB Tables        Amazon S3 Buckets          │
     │  - PK / SK checkpoint schema   - Large State Offloads     │
     │  - Time-To-Live auto eviction    (compressed raw JSONs)   │
     │                    │
     └───────────────────────────────────────────────────────────┘
```






