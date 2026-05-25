# Tech Spec: DRAM-Radar (dram-sentry)

## Stack
*   **Backend Runtime:** Python 3.11+ (FastAPI for high-performance async I/O).
*   **Data Processing:** Pandas (time-series analysis), Scikit-Learn (forecasting models), NumPy.
*   **Database:** PostgreSQL 15 (Primary data store with JSONB support for flexible schema evolution).
*   **Caching:** Redis 7 (Session management, rate limiting, real-time price cache).
*   **AI/ML:** LightGBM (Gradient boosting for price prediction) - lightweight and fast for time-series forecasting.
*   **Infrastructure as Code:** Docker (Containerization), Docker Compose (Local dev), Terraform (AWS/Render infra).

## Hosting Strategy
*   **MVP Phase (Free-tier-first):** **Render.com**.
    *   Web Service: Free tier (Docker container).
    *   Postgres: $7/mo Hobby plan (sufficient for initial user load).
    *   Redis: Render Redis ($7/mo Hobby plan).
*   **Scale Phase:** **AWS ECS Fargate** + **Amazon RDS**.
    *   Auto-scaling based on API request volume.
    *   Multi-AZ deployment for high availability.

## Data Model
*   **`users`**
    *   `id` (UUID, PK)
    *   `email` (String, Unique)
    *   `subscription_tier` (Enum: 'free', 'pro', 'enterprise')
    *   `api_key` (String, Unique)
    *   `created_at` (Timestamp)
*   **`price_history`**
    *   `id` (UUID, PK)
    *   `component_type` (String: 'DDR5-4800', 'LPDDR5X', etc.)
    *   `price_usd` (Decimal)
    *   `timestamp` (Timestamp)
    *   `source` (String: 'Micron', 'Samsung', 'MarketAverage')
*   **`forecasts`**
    *   `id` (UUID, PK)
    *   `component_type` (String)
    *   `predicted_price` (Decimal)
    *   `confidence_interval_low` (Decimal)
    *   `confidence_interval_high` (Decimal)
    *   `model_version` (String)
    *   `forecast_date` (Timestamp)
*   **`alerts`**
    *   `id` (UUID, PK)
    *   `user_id` (UUID, FK)
    *   `condition_type` (Enum: 'price_above', 'price_below', 'volatility_spike')
    *   `threshold_value` (Decimal)
    *   `is_active` (Boolean)
    *   `last_triggered_at` (Timestamp)

## API Surface
*   **POST /api/v1/auth/register** - Create new user account.
*   **POST /api/v1/auth/login** - Authenticate and return JWT token.
*   **GET /api/v1/market/overview** - Get current global DRAM price index and top 5 trending components.
*   **GET /api/v1/market/trends/{component_id}** - Fetch historical price chart data (JSON lines format for frontend rendering).
*   **POST /api/v1/alerts** - Create a new price monitoring alert (requires auth).
*   **GET /api/v1/alerts** - List user's active alerts.
*   **DELETE /api/v1/alerts/{alert_id}** - Disable an alert.
*   **POST /api/v1/forecast/simulate** - Run AI prediction for a specific component (returns 30-day projection).
*   **GET /api/v1/health** - Liveness probe for load balancers.

## Security Model
*   **Authentication:** **Auth0** (Managed SSO, MFA support, easy integration with Stripe for subscription management).
    *   *Rationale:* Reduces DevOps overhead on auth implementation, allows focus on core product logic.
*   **Authorization:** Role-Based Access Control (RBAC).
    *   `free`: Read-only access to public market data.
    *   `pro`: Access to historical data, custom alerts, and forecast simulation.
    *   `enterprise`: API access (Webhooks), bulk exports, priority support.
*   **Secrets Management:** Environment variables injected at runtime. For production, integration with **AWS Secrets Manager** or **HashiCorp Vault**.
*   **Data Protection:** TLS 1.3 enforced for all endpoints. PII (user emails) hashed and salted in the database.

## Observability
*   **Logs:** Structured JSON logs sent to **CloudWatch** (AWS) or **Logtail** (LogDNA). Log levels: DEBUG, INFO, WARN, ERROR.
*   **Metrics:** **Prometheus** (exposed via `/metrics` endpoint).
    *   *Key Metrics:* `api_requests_total`, `api_latency_seconds`, `price_update_queue_size`, `forecast_model_accuracy_score`.
*   **Tracing:** **OpenTelemetry** (Jaeger backend) to trace the flow from API request -> Data Fetching -> ML Inference -> Database Query.
*   **Error Tracking:** **Sentry** (integrated into FastAPI) to capture unhandled exceptions and provide stack traces to developers.

## Build & CI
*   **Version Control:** GitHub (Private repo).
*   **CI Pipeline (GitHub Actions):**
    1.  **Lint:** `ruff` (Python linter).
    2.  **Test:** `pytest` with coverage reporting (target > 80%).
    3.  **Security Scan:** `bandit` (Python security linter) and `snyk` (dependency scanning).
    4.  **Build:** `docker build -t dram-sentry .`
*   **CD Pipeline:** GitHub Actions -> Push to **Render** (Auto-deploy on push to `main`).
*   **Database Migrations:** **Alembic** (managed via GitHub Actions on deployment).