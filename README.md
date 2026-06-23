<div align="center">
  <img src="docs/assets/hero_banner.png" alt="Developer DNA Hero" width="100%"/>

  <br />
  <br />

  <p>
    <b>AI-powered developer telemetry platform that continuously analyzes your coding activity to generate insights on productivity, skill growth, debugging patterns, and career progression.</b>
  </p>
  <p><i>Think <strong>Spotify Wrapped for developers</strong> — powered by real telemetry from your IDE.</i></p>

  <p>
    <a href="https://github.com/Nyx-abu/developer-dna/stargazers"><img src="https://img.shields.io/github/stars/Nyx-abu/developer-dna?style=for-the-badge&color=e2b93b&logo=github" alt="Stars Badge"/></a>
    <a href="https://github.com/Nyx-abu/developer-dna/network/members"><img src="https://img.shields.io/github/forks/Nyx-abu/developer-dna?style=for-the-badge&color=blue&logo=github" alt="Forks Badge"/></a>
    <a href="https://github.com/Nyx-abu/developer-dna/issues"><img src="https://img.shields.io/github/issues/Nyx-abu/developer-dna?style=for-the-badge&color=red&logo=github" alt="Issues Badge"/></a>
    <a href="https://github.com/Nyx-abu/developer-dna/pulls"><img src="https://img.shields.io/github/issues-pr/Nyx-abu/developer-dna?style=for-the-badge&color=brightgreen&logo=github" alt="Pull Requests Badge"/></a>
    <br />
    <img src="https://img.shields.io/badge/Open_Source-%E2%9D%A4-red?style=for-the-badge" alt="Open Source Love">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="License: MIT">
  </p>
  <p>
    <img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js">
    <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django">
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  </p>

  <h4>
    <a href="#-features">Features</a>
    <span> | </span>
    <a href="#-getting-started-5-minutes">Getting Started</a>
    <span> | </span>
    <a href="#%EF%B8%8F-architecture">Architecture</a>
    <span> | </span>
    <a href="#-contributing">Contributing</a>
  </h4>
</div>

---

## 📖 About Developer DNA

**Developer DNA** is an open-source initiative designed to help developers quantify their coding journey. By silently capturing IDE events—from file saves and terminal commands to debugging sessions—our platform leverages advanced AI (like Gemini and Qwen) to map out your skill progression, productivity peaks, and areas for improvement.

Our goal is to give every developer a personalized **"Spotify Wrapped"** experience, allowing you to reflect on your career trajectory, discover your unique coding patterns, and optimize your workflow.

---

## 📸 See It In Action

<div align="center">
  <img src="docs/assets/dashboard_mockup.png" alt="Developer DNA Dashboard" width="100%" style="border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.2);"/>
  <p><i>The intuitive, dark-mode Next.js dashboard providing real-time AI insights.</i></p>
</div>

---

## ✨ Features

- 🧠 **AI-Driven Insights:** Uses a 5-agent LangGraph pipeline (Skill, Productivity, Debug, Career, Report) to process your data.
- 📊 **Beautiful Dashboards:** A sleek Next.js interface displaying coding heatmaps, error distribution charts, and skill radars.
- 🔌 **Seamless IDE Integration:** A VS Code extension silently watches your typing, git operations, and terminal errors without impacting performance.
- 🚀 **Asynchronous & Scalable:** Powered by Apache Kafka for event streaming and PostgreSQL for robust storage.
- 🔒 **Privacy First:** Your code telemetry is processed locally or via secure API, never exposing sensitive secrets.

---

## ⚡ Getting Started (5 minutes)

### Prerequisites
- [Docker Desktop](https://docs.docker.com/desktop/) (with Docker Compose v2+)
- [Node.js 22+](https://nodejs.org/)
- [Python 3.12+](https://python.org/)
- A free [Gemini API key](https://aistudio.google.com/apikey)

### 1. Clone & Configure

```bash
git clone https://github.com/Nyx-abu/developer-dna.git
cd developer-dna
cp .env.example .env
```
Edit `.env` and add your Gemini API key:
```env
GEMINI_API_KEY=your-key-here
```

### 2. Start the Engines 🚀

```bash
make up
```
This single command spins up PostgreSQL, Kafka, the Django REST API, background workers, and the Next.js frontend!

### 3. Run Migrations & Seed Data

```bash
make migrate
make seed
```

### 4. Install the VS Code Extension

```bash
cd extension
npm install
npm run compile
```
Press `F5` in VS Code to launch the Extension Development Host and start tracking! 

Dashboard available at: **http://localhost:3000** 

---

## 🏗️ Architecture

```mermaid
graph TD;
    subgraph Client
        VSC[VS Code Extension]
    end
    subgraph Backend Core
        API[Django DRF API]
        Kafka[Apache Kafka]
        Worker[Kafka Consumer Worker]
        DB[(PostgreSQL)]
    end
    subgraph AI Pipeline
        LangGraph[LangGraph Agents]
        FAISS[(FAISS Vector Store)]
    end
    subgraph Frontend
        Next[Next.js Dashboard]
    end

    VSC -- Batch POST Events --> API
    API -- Publish --> Kafka
    Kafka -- Consume --> Worker
    Worker -- Store Raw Data --> DB
    Worker -- Trigger Analysis --> LangGraph
    LangGraph -- RAG Context --> FAISS
    LangGraph -- Store Insights --> DB
    Next -- Fetch Insights --> API
```

---

## 📁 Project Structure

```text
developer-dna/
├── backend/          # Django 5 + DRF + LangGraph agents
├── frontend/         # Next.js 14 dashboard (React, Tailwind)
├── extension/        # VS Code extension telemetry watchers
├── docs/             # Images and architecture documentation
├── docker-compose.yml
└── Makefile
```

---

## 🤝 Contributing

We welcome contributions from the community! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to report bugs, suggest features, and submit pull requests. Let's build the ultimate developer tool together!

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<div align="center">
  <br/>
  <sub>Built with ❤️ by the Developer DNA Open Source Community</sub>
</div>
