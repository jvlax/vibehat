# VibeHat - AI Dependency Exploit Scanner

A security research tool to identify and demonstrate dependency confusion vulnerabilities in AI-generated code. VibeHat scans GitHub repositories for missing dependencies that AI tools might hallucinate, helping developers understand potential security risks.

## 🚨 Security Research Purpose

This tool is designed for educational and security research purposes to demonstrate:
- How AI code generators can create dependencies that don't exist
- The security implications of dependency confusion attacks
- Best practices for validating AI-generated code

**Use responsibly and ethically!**

## 🏗️ Architecture

- **Backend**: Python FastAPI with PostgreSQL
- **Frontend**: Next.js with TypeScript and Tailwind CSS
- **Scanner**: GitHub API integration for repository analysis
- **Checker**: Multi-registry package verification (npm, PyPI, crates.io, etc.)

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- GitHub Personal Access Token

### Setup

1. **Clone and setup**:
   ```bash
   git clone <your-repo-url>
   cd vibehat
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your GitHub token
   ```

3. **Start services**:
   ```bash
   chmod +x test-local
   ./test-local
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Database: localhost:5432

## 🔍 How It Works

1. **Repository Scanning**: Analyzes dependency files (package.json, requirements.txt, Cargo.toml, etc.)
2. **Package Verification**: Checks if packages exist in their respective registries
3. **Vulnerability Detection**: Identifies missing packages that could be exploited
4. **Risk Assessment**: Reports potential dependency confusion vulnerabilities

## 📊 Supported Ecosystems

- **npm** (Node.js)
- **PyPI** (Python)
- **Crates.io** (Rust)
- **Go Modules**
- **Packagist** (PHP)
- **RubyGems** (Ruby)

## 🛡️ Ethical Use Guidelines

- Only scan repositories you own or have permission to analyze
- Use findings for defensive security purposes
- Do not publish or exploit vulnerable packages maliciously
- Report findings responsibly to repository owners

## 🔧 Development

### Local Development
```bash
# Backend only
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend only
cd frontend
npm install
npm run dev
```

### API Endpoints
- `POST /scan/repository` - Scan a GitHub repository
- `GET /scans` - Get scan results
- `POST /exploit/generate` - Generate proof-of-concept packages

## 📝 License

This project is for educational and security research purposes. Use responsibly.

## 🤝 Contributing

Contributions welcome! Please ensure all contributions align with ethical security research practices.

## ⚠️ Disclaimer

This tool is intended for security research and educational purposes only. Users are responsible for ensuring their use complies with applicable laws and ethical guidelines. 