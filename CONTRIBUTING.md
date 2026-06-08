# Contributing to Developer DNA

First off, thank you for considering contributing to Developer DNA! It's people like you that make open-source software such a great community to learn, inspire, and create.

## 🤝 How Can I Contribute?

### Reporting Bugs
If you find a bug, please create an issue on GitHub. Include as much detail as possible:
* **Description** of the issue
* **Steps to reproduce** the bug
* **Expected behavior** vs **Actual behavior**
* Any relevant **logs or screenshots**

### Suggesting Enhancements
Have an idea for a new feature? We'd love to hear it! Please create an issue labeled `enhancement` and describe your idea, why it would be useful, and how you imagine it working.

### Pull Requests
1. Fork the repository and create your branch from `master` (or `main`).
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. If you've added code that should be tested, add tests.
3. Ensure the test suite passes.
4. Make sure your code lints properly.
5. Issue that pull request!

## 🛠️ Local Development Setup

Developer DNA is composed of several components: a Django backend, a Next.js frontend, a VS Code extension, and LangGraph AI agents. 

To set up the project locally:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Nyx-abu/developer-dna.git
   cd developer-dna
   ```

2. **Set up Environment Variables:**
   Copy `.env.example` to `.env` and fill in your Gemini API key:
   ```bash
   cp .env.example .env
   ```

3. **Start the services via Docker Compose:**
   ```bash
   make up
   ```
   Or manually: `docker compose up -d --build`

4. **Run Database Migrations:**
   ```bash
   make migrate
   ```

5. **Start Hacking!**
   * Frontend: Accessible at `http://localhost:3000`
   * Backend API: Accessible at `http://localhost:8000`
   * To work on the VS Code extension, navigate to the `extension` directory, run `npm install` and `npm run compile`, then press `F5` in VS Code.

## 📝 Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.
* `feat:` A new feature
* `fix:` A bug fix
* `docs:` Documentation only changes
* `style:` Changes that do not affect the meaning of the code
* `refactor:` A code change that neither fixes a bug nor adds a feature
* `perf:` A code change that improves performance
* `test:` Adding missing tests or correcting existing tests
* `chore:` Changes to the build process or auxiliary tools

## ⚖️ Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct (which is basically: be kind and respectful to everyone).

Thank you for your contributions! 🧬
