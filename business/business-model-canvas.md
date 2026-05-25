## Business Model Canvas – dram‑sentry (DRAM‑Radar)

### 1. Customer Segments
- **Cloud service providers** (e.g., AWS, Azure, GCP) that purchase DDR4/DDR5 modules at scale and need to protect margin volatility.  
- **Hardware OEMs & contract manufacturers** (e.g., Samsung, Micron, Foxconn) that source DRAM for servers, laptops, and edge devices.  
- **Large‑scale data‑center operators & hyperscalers** that plan capacity years ahead and require price forecasts for CAPEX budgeting.  
- **Financial analysts & commodity traders** specializing in semiconductor components who need real‑time market intelligence.  

### 2. Value Propositions
- **AI‑driven price forecasts** with ≤ 5 % mean‑absolute‑percentage‑error (MAPE) for 3‑month horizon, reducing surprise cost spikes.  
- **Real‑time alert engine** (≤ 30 s latency) that pushes Slack, Teams, or webhook notifications when price deviation > 3 % YoY.  
- **Historical price database** (10 yr granularity) for back‑testing procurement strategies and CAPEX models.  
- **Scenario planning tool** that simulates “what‑if” supply‑chain disruptions (e.g., fab shutdowns) on DRAM spend.  
- **Compliance‑ready audit logs** (ISO 27001, SOC 2) for internal finance & procurement audit trails.  

### 3. Channels
- **Self‑serve SaaS portal** (website → free 14‑day trial → instant onboarding).  
- **Enterprise sales team** (direct outreach, demos, PoC support).  
- **Channel partners** – major cloud consulting firms (e.g., Accenture, Deloitte) that bundle dram‑sentry into their cost‑optimization services.  
- **API marketplace** (RapidAPI, AWS Marketplace) for integration into existing procurement platforms.  
- **Industry webinars & conferences** (Hot Chips, IEEE SC) to generate pipeline leads.  

### 4. Customer Relationships
- **Automated onboarding** with guided wizard, data‑connector templates (SAP Ariba, Coupa).  
- **Dedicated Customer Success Manager** for Professional & Enterprise tiers (quarterly business reviews, custom model tuning).  
- **Community forum & knowledge base** (public docs, best‑practice playbooks).  
- **SLA‑backed support** – 99.9 % uptime, 1‑hour response for Enterprise tier.  
- **Feedback loop** – quarterly product‑roadmap voting for paying customers.  

### 5. Revenue Streams *(mirrors pricing tiers from revenue‑model.md)*
| Tier | Price (USD) | Price (THB) | Seats Included | Core Features |
|------|-------------|-------------|----------------|---------------|
| **Starter** | **$199 / month** | **≈ THB 6,567** | 1 seat | Basic price feed, 2 alerts/month, email notifications |
| **Professional** | **$499 / month** | **≈ THB 16,467** | Up to 5 seats | Full AI forecasts, 20 alerts/month, Slack/Teams webhook, API access |
| **Enterprise** | **$1,299 / month** | **≈ THB 42,867** | Unlimited seats | Unlimited alerts, custom model training, on‑prem data‑ingest, SLA 1‑hour, dedicated CSM |
| **Pay‑per‑Alert Add‑on** | **$0.05 / alert** (beyond tier limit) | **≈ THB 1.65 / alert** | – | Scalable alert volume for burst usage |

*All plans include a 14‑day free trial with full feature access. Annual contracts receive a 15 % discount (e.g., Professional annual = $5,089 / yr).*

### 6. Key Resources
- **Proprietary AI forecasting engine** (time‑series + transformer models) trained on 10 yr of global DRAM price data.  
- **Data acquisition pipelines** (scrapers, API feeds from DRAM manufacturers, market analysts).  
- **Cloud infrastructure** (AWS/GCP – Kinesis, Redshift, SageMaker) for real‑time processing.  
- **Domain experts** (semiconductor economists, supply‑chain analysts).  
- **Compliance certifications** (ISO 27001, SOC 2 Type II).  

### 7. Key Activities
- **Continuous data ingestion & cleansing** (daily price updates, macro‑economic indicators).  
- **Model training & validation** (quarterly retraining, drift detection).  
- **Alert rule engine development** (threshold management, multi‑channel delivery).  
- **Customer onboarding & integration** (API SDKs, connector libraries).  
- **Regulatory & security audits** (maintaining certifications).  

### 8. Key Partners
- **DRAM manufacturers & market research firms** (e.g., DRAMeXchange, TrendForce) for premium price feeds.  
- **Cloud providers** (AWS, Azure) for preferential compute pricing & marketplace distribution.  
- **Enterprise resource planning (ERP) vendors** (SAP, Oracle) for seamless procurement integration.  
- **Consulting & systems‑integrator partners** (Accenture, Capgemini) to co‑sell cost‑optimization bundles.  
- **Alert delivery platforms** (Slack, Microsoft Teams, PagerDuty) for webhook integration.  

### 9. Cost Structure
- **Cloud compute & storage** – $30k / yr (AWS SageMaker, Redshift, Kinesis).  
- **Data licensing fees** – $120k / yr (premium DRAM price feeds).  
- **Engineering & R&D salaries** – $800k / yr (ML engineers, domain experts).  
- **Sales & marketing** – $250k / yr (content, events, partner commissions).  
- **Compliance & security** – $60k / yr (audit, certifications).  
- **Customer support & CSM** – $150k / yr (support staff, tools).  

*Total annual burn ≈ $1.41 M, with break‑even projected at 1,200 Enterprise seats or equivalent ARR of $2.5 M.*