# MARKETLENS


A comprehensive, production-grade intelligence platform that empowers e-commerce sellers with real-time tracking, automated competitor discovery, vector-similarity classification, customer sentiment analysis, gap finding, and an AI copilot chat interface.

---

## 🏗️ Core Architecture Overview

The system is designed in a three-tier architecture with modular, decoupled services:

```mermaid
graph TD
    subgraph Data Pipeline
        SC[Scheduler / APScheduler] -->|Triggers| SP[Scraper Pipeline]
        SP -->|Real-time Data| AMZ[Amazon Scrapers]
        SP -->|Auto-discover| DIS[Keyword Search Discovery]
        AMZ -->|Text Data| EMB[Sentence Transformers Embedding Service]
    end

    subgraph Database
        DB[(Postgres + pgvector)]
        REDIS[(Redis Cache)]
    end

    subgraph Backend APIs
        FA[FastAPI Server]
        PA[Pricing Agent]
        SA[Sentiment Agent]
        GF[Gap Finder Agent]
        LW[Listing Writer Agent]
        CA[Chat Agent]
        OR[Orchestrator]
    end

    subgraph Frontend Client
        FE[React + Vite SPA]
    end

    EMB -->|384d Vectors| DB
    SP -->|Saves Raw Data| DB
    DB -->|Read Data / Vector Matches| FA
    FA -->|Leverages| PA & SA & GF & LW & CA & OR
    FA -->|Response| FE
    OR -->|Combines Insights| FA
```

---

## 🛠️ System Components

### 1. 🔄 Data Pipeline & Scraper (`/pipeline`)
*   **APScheduler Engine:** Runs a recurring background pipeline (default every 3 hours) that handles schema synchronization, seller data collection, competitor scraping, embedding generation, and similarity matchmaking.
*   **Targeted Scraping:** Captures product listings, prices, ratings, and detailed customer reviews from Amazon.
*   **Keyword Discovery:** Dynamically discovers new competitors by searching target keywords (e.g., `"tws earbuds under 2000"`) and scanning organic search results up to configured caps.
*   **Resiliency:** Handled scraping fallbacks and simulation logic for seller performance metrics (such as units sold, conversion rate, sessions, and revenue).

### 2. 🧮 Vector Embedding & Similarity Classifier (`/pipeline/competitors`)
*   **Sentence Transformers:** Generates 384-dimensional dense vectors using the `all-MiniLM-L6-v2` model locally from the combined metadata of each product (`title + brand + bullet_points`).
*   **pgvector Similarity:** Leverages the `pgvector` database extension inside PostgreSQL to execute high-performance cosine similarity searches (`1 - (embedding <=> :target_embedding)`).
*   **Heuristic Matcher:** Classifies competitors into:
    *   `same_product`: Exact SKU matches across channels or extremely high-similarity listings.
    *   `similar_product`: Directly competing products in the same category.
    *   `None`: Non-competing products filtered out by the similarity threshold.

### 3. 🧠 Multi-Agent Architecture (`/agents`)
The platform orchestrates several specialized LLM agents to deliver intelligence:
*   **Unified AI Client (`ai_client.py`):** A robust LLM client featuring fallback strategies (primary: Groq Llama-3.3, secondary: OpenRouter Claude-3.5, tertiary: OpenAI GPT-4o).
*   **Pricing Agent (`pricing.py`):** Monitors price fluctuations, detects sudden competitor drops, and logs alerts.
*   **Sentiment Agent (`sentiment.py`):** Groups customer reviews into tags and categorizes common issues or praise (e.g., sound quality, battery life, connectivity, comfort).
*   **Gap Finder Agent (`gap_finder.py`):** Analyzes competitor weak spots (low rating/complaints) compared to your own product's strengths to identify market entry gaps.
*   **Listing Writer Agent (`listing_writer.py`):** Suggests optimized product titles and bullet points using the discovered gap data to target competitor weaknesses.
*   **Chat Agent (`chat_agent.py`):** An interactive assistant responding to user queries about metrics, prices, and strategic advice.
*   **Orchestrator (`orchestrator.py`):** Combines findings from the Pricing, Sentiment, and Gap Finder agents to output structured **Strategy Cards** with action points.

### 4. ⚡ FastAPI Backend (`/backend`)
*   Provides RESTful routes for agent processing (`/api/pricing`, `/api/sentiment`, `/api/gaps`, `/api/strategy`, `/api/listing/rewrite`, `/api/chat`).
*   Handles JWT authentication (`auth.py`) for secure platform registration and login.
*   Interacts with the database via SQLAlchemy ORM.

### 5. 💻 React Frontend (`/frontend`)
*   **Modern Dashboard:** Full-featured UI showing unit sales, revenue, session statistics, and real-time conversion rates.
*   **Competitor Workspace:** Deep comparison panels displaying pricing dynamics and similarity coefficients.
*   **AI Copilot Sandbox:** Dynamic interface for chat interaction, listing rewrites, and strategic decision support.

---

## 🗄️ Database Schema Details

The application uses PostgreSQL with a set of core tables:
*   `products`: Stores ASIN, platform, title, brand, rank, bullets, description, and the `embedding` (type: `Vector(384)`).
*   `price_snapshots`: Historic price points over time to track discount strategies.
*   `rating_snapshots`: Cumulative rating scores and review counts.
*   `reviews`: Raw customer reviews used for LLM sentiment parsing.
*   `seller_metrics`: Performance statistics (units sold, sessions, conversion rates).
*   `competitors`: Maps relationships between products along with classification types and similarity scores.

---

## 🚀 Getting Started

Follow these steps to configure, run, and explore the project locally.

### 1. Configure the Environment
Create a `.env` file in the root workspace directory with the following variables:
```env
# Database Configuration
DATABASE_URL=postgresql://datathon_user:datathon_pass@localhost:5433/datathon_db

# API Credentials (Fill in the ones you have; LLM client has fallbacks)
GROQ_API_KEY=your_groq_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
OPENAI_API_KEY=your_openai_api_key

# Scraper & Similarity Settings
SCRAPE_INTERVAL_HOURS=3
SIMILARITY_TOP_K=5
```

### 2. Start Services (PostgreSQL + Redis)
Start the preconfigured databases using Docker Compose:
```bash
docker compose up -d
```
Check that the containers `datathon_postgres` and `datathon_redis` are healthy.

### 3. Bootstrap and Seed the Database
Initialize the schema and inject 30 days of historical mock data:
```bash
# Set up virtual environment and install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the seeding script
python seed_mock_data.py
```

### 4. Run the Data Pipeline
To test a one-shot ingestion run or start the periodic scheduler:
```bash
python -m pipeline.scheduler
```

### 5. Start the FastAPI Backend
```bash
uvicorn backend.main:app --reload --port 8000
```

### 6. Start the Frontend Dev Server
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser. Register an account (or login) to explore the dashboard.
