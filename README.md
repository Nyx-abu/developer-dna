<div align="center">
  <img src="https://via.placeholder.com/150?text=Developer+DNA" alt="Developer DNA Logo" width="150"/>
  <h1>🧬 Developer DNA</h1>
  <p><strong>AI-powered developer telemetry platform that continuously analyzes your coding activity to generate insights on productivity, skill growth, debugging patterns, and career progression.</strong></p>
  <p><i>Think <strong>Spotify Wrapped for developers</strong> — powered by real telemetry from your IDE.</i></p>

  <p>
    <a href="https://github.com/Nyx-abu/developer-dna/stargazers"><img src="https://img.shields.io/github/stars/Nyx-abu/developer-dna?style=for-the-badge&color=yellow" alt="Stars Badge"/></a>
    <a href="https://github.com/Nyx-abu/developer-dna/network/members"><img src="https://img.shields.io/github/forks/Nyx-abu/developer-dna?style=for-the-badge&color=blue" alt="Forks Badge"/></a>
    <a href="https://github.com/Nyx-abu/developer-dna/issues"><img src="https://img.shields.io/github/issues/Nyx-abu/developer-dna?style=for-the-badge&color=red" alt="Issues Badge"/></a>
    <a href="https://github.com/Nyx-abu/developer-dna/pulls"><img src="https://img.shields.io/github/issues-pr/Nyx-abu/developer-dna?style=for-the-badge&color=brightgreen" alt="Pull Requests Badge"/></a>
    <img src="https://img.shields.io/badge/Open_Source-%E2%9D%A4-red?style=for-the-badge" alt="Open Source Love">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="License: MIT">
  </p>
  <p>
    <img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js">
    <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django">
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  </p>
</div>

---

## 📖 About Developer DNA

**Developer DNA** is an open-source initiative designed to help developers quantify their coding journey. By silently capturing IDE events—from file saves and terminal commands to debugging sessions—our platform leverages advanced AI (like Gemini and Qwen) to map out your skill progression, productivity peaks, and areas for improvement.

Our goal is to give every developer a personalized **"Spotify Wrapped"** experience, allowing you to reflect on your career trajectory, discover your unique coding patterns, and optimize your workflow.

---

## ⚡ Quick Start (5 minutes)

### Prerequisites

- [Docker Desktop](https://docs.docker.com/desktop/) (with Docker Compose v2+)
- [Node.js 22+](https://nodejs.org/) (for local frontend/extension dev)
- [Python 3.12+](https://python.org/) (for local backend dev)
- A free [Gemini API key](https://aistudio.google.com/apikey)

### 1. Clone & configure

```bash
git clone https://github.com/yourusername/developer-dna.git
cd developer-dna
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your-key-here
```

### 2. Start all services

```bash
docker compose up -d --build
```

This starts 5 services:
| Service    | Port  | Description                    |
|-----------|-------|--------------------------------|
| postgres  | 5432  | PostgreSQL 15 database         |
| kafka     | 9092  | Apache Kafka (KRaft mode)      |
| backend   | 8000  | Django REST API                |
| worker    | —     | Kafka consumer worker          |
| frontend  | 3000  | Next.js dashboard              |

### 3. Run migrations

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

### 4. Open the dashboard

Navigate to **http://localhost:3000** — you should see the Developer DNA dashboard.

Admin panel is at **http://localhost:8000/admin/**.

### 5. Install the VS Code extension

```bash
cd extension
npm install
npm run compile
```

Then press `F5` in VS Code to launch the Extension Development Host.

---

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  VS Code     │────▶│  Django API  │────▶│  PostgreSQL  │
│  Extension   │     │  (DRF)       │     │              │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                     ┌──────▼───────┐
                     │  Apache      │
                     │  Kafka       │
                     └──────┬───────┘
                            │
                     ┌──────▼───────┐     ┌──────────────┐
                     │  Worker      │────▶│  LangGraph   │
                     │  (Consumer)  │     │  Agents      │
                     └──────────────┘     │  + FAISS     │
                                          └──────┬───────┘
                                                 │
                     ┌──────────────┐            │
                     │  Next.js     │◀───────────┘
                     │  Dashboard   │  (reads insights)
                     └──────────────┘
```

### Event Flow

1. **VS Code Extension** captures coding activity (file saves, git ops, errors, terminal commands)
2. Events are **batch-POSTed** to the Django API
3. Django **publishes events to Kafka** topics
4. **Worker process** consumes events, stores in PostgreSQL
5. When analysis is triggered, **LangGraph agents** run a 5-stage pipeline:
   - Skill Agent → Productivity Agent → Debug Agent → Career Agent → Report Agent
6. Insights are stored and displayed on the **Next.js dashboard**

### AI Pipeline

The LangGraph workflow chains 5 specialized agents:

| Agent              | Purpose                                    |
|-------------------|--------------------------------------------|
| Skill Agent       | Assess language proficiency & growth       |
| Productivity Agent| Analyze flow states & time patterns        |
| Debug Agent       | Error patterns & resolution efficiency     |
| Career Agent      | Career trajectory & skill gap analysis     |
| Report Agent      | Generate Wrapped-style narrative reports   |

**Primary model**: Gemini 2.5 Flash (API, free tier)
**Fallback model**: Qwen3 1.7B (local, for offline use)

---

## 🛠️ Development

### Makefile commands

```bash
make up              # Start all services
make down            # Stop all services
make logs            # Follow all logs
make migrate         # Run Django migrations
make test            # Run backend tests
make test-frontend   # Run frontend tests
make seed            # Load sample data
make clean           # Stop & remove volumes
```

### Backend (Django)

```bash
cd backend
pip install -r requirements.txt
python manage.py runserver
```

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

### Extension

```bash
cd extension
npm install
npm run compile
# Press F5 in VS Code to launch Extension Development Host
```

---

## 📁 Project Structure

```
developer-dna/
├── backend/          Django 5 + DRF backend
│   ├── config/       Django settings, URLs
│   ├── telemetry/    Models, serializers, views
│   ├── events/       Kafka producer/consumer, Pydantic schemas
│   └── agents/       LangGraph agents, FAISS store
├── frontend/         Next.js 14 dashboard
│   └── src/
│       ├── app/      Pages (overview, skills, reports, etc.)
│       ├── components/  UI components
│       └── lib/      API client, types
├── extension/        VS Code extension
│   └── src/
│       ├── watchers/ File, Git, Error, Terminal watchers
│       └── buffer/   Event buffer with batch POST
├── docker-compose.yml
├── Makefile
└── .env.example
```

---

## 🔑 Environment Variables

| Variable                 | Required | Description                          |
|-------------------------|----------|--------------------------------------|
| `GEMINI_API_KEY`        | Yes*     | Google AI Studio API key             |
| `DJANGO_SECRET_KEY`     | Yes      | Django secret key (auto-generated)   |
| `DATABASE_URL`          | Yes      | PostgreSQL connection string         |
| `KAFKA_BOOTSTRAP_SERVERS`| Yes     | Kafka broker address                 |
| `NEXT_PUBLIC_API_URL`   | Yes      | Backend API URL for frontend         |

*If not set, falls back to Qwen3 1.7B offline model.

---

## 📜 License

MIT
