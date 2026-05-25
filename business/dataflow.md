# dram‑sentry Dataflow Architecture

```
┌───────────────────────┐
│  External Data Sources │
│  (Market feeds, APIs,   │
│   Web‑scrapers, CSVs)   │
└──────────────┬────────┘
               │
               ▼
┌───────────────────────┐
│   Ingestion Layer      │
│  • Kafka / Kinesis      │
│  • Auth: OAuth2 / API  │
│     Keys                │
│  • TLS‑encrypted        │
│    transport            │
└──────────────┬────────┘
               │
               ▼
┌───────────────────────┐
│ Processing / Transform │
│  • Spark Structured     │
│    Streaming (Python)   │
│  • AI Forecast Engine   │
│    (PyTorch, ONNX)      │
│  • Alert Engine (Rule‑│
│    based + ML)          │
│  • Auth: Service‑to‑    │
│    Service (JWT)        │
└──────────────┬────────┘
               │
               ▼
┌───────────────────────┐
│   Storage Tier         │
│  • Cold Storage: S3    │
│    (raw feeds, logs)   │
│  • Hot Storage: DynamoDB │
│    (price history,    │
│    forecasts, alerts) │
│  • Auth: IAM roles     │
└──────────────┬────────┘
               │
               ▼
┌───────────────────────┐
│ Query / Serving Layer │
│  • API Gateway (REST/ │
│    GraphQL)            │
│  • Lambda / Fargate    │
│    (serverless compute)│
│  • Auth: Cognito +    │
│    API Keys            │
│  • Rate‑limit, CORS   │
└──────────────┬────────┘
               │
               ▼
┌───────────────────────┐
│  Egress to User        │
│  • Web Dashboard (React) │
│  • Mobile SDK (iOS/Android) │
│  • Email / Slack Webhook │
│  • Auth: JWT, OAuth2   │
└───────────────────────┘
```

## Tier‑by‑Tier Component Breakdown

### 1. External Data Sources
| Source | Data Type | Frequency | Auth |
|--------|-----------|-----------|------|
| **DRAM Market API** | JSON price feeds | 1 min | API Key |
| **Manufacturer RSS** | XML inventory | 5 min | OAuth2 |
| **Web Scraper** | HTML tables | 30 min | None (public) |
| **CSV Dumps** | Historical prices | Daily | S3 Signed URL |

### 2. Ingestion Layer
- **Kafka / Kinesis Streams** – buffer all raw events, enable replay.
- **Kafka Connect / Kinesis Data Firehose** – pull from APIs, push to stream.
- **TLS 1.3** – encrypt transport.
- **OAuth2 / API Keys** – validate source identity.

### 3. Processing / Transform Layer
- **Spark Structured Streaming** – aggregate per‑minute price, compute moving averages.
- **AI Forecast Engine** – LSTM model (PyTorch) ingested via ONNX runtime; outputs 1‑hour, 24‑hour, 7‑day forecasts.
- **Alert Engine** – rule engine (Drools) + ML classifier (XGBoost) to flag anomalous spikes (> +30 % in 15 min).
- **Service‑to‑Service Auth** – JWT signed by Auth0, verified by downstream services.

### 4. Storage Tier
- **S3 (Cold)** – immutable raw feeds, audit logs, model checkpoints.
- **DynamoDB (Hot)** – 100 GB table for price history, 10 GB for forecasts, 5 GB for alerts.
- **IAM Policies** – least‑privilege: ingestion only writes to S3, processing reads from S3 & writes to DynamoDB, serving layer reads from DynamoDB.

### 5. Query / Serving Layer
- **API Gateway** – exposes `/prices`, `/forecasts`, `/alerts`. Supports REST and GraphQL.
- **Lambda / Fargate** – stateless compute for query logic, uses DynamoDB Streams for cache invalidation.
- **Cognito** – user pools for web/mobile, JWT tokens for API auth.
- **Rate‑limit** – 1000 RPS per user, 10 000 RPS global.

### 6. Egress to User
- **Web Dashboard** – React SPA, consumes API Gateway, shows live charts, forecast heatmaps, alert inbox.
- **Mobile SDK** – Swift/Kotlin, push notifications for critical alerts.
- **Email / Slack Webhook** – optional outbound channels for alert delivery.
- **Auth** – JWT refreshed every 15 min, OAuth2 for third‑party integrations.

---

**Security Boundaries**

| Boundary | Enforcement |
|----------|-------------|
| Source → Ingestion | TLS + API Key |
| Ingestion → Processing | Kafka ACLs, JWT |
| Processing → Storage | IAM roles, encryption at rest |
| Storage → Serving | IAM read‑only, VPC endpoints |
| Serving → User | Cognito JWT, HTTPS, CORS |

This architecture delivers low‑latency, real‑time DRAM price insights while ensuring data integrity, scalability, and robust security for a subscription‑based SaaS.