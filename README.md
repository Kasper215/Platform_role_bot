# Role Bot

A sophisticated role-playing chatbot application with NSFW capabilities, featuring a Python/FastAPI backend and a React/Vite frontend.

## ✨ Features

- **Role-playing Characters**: Interact with various AI characters, each with unique personalities and backstories
- **NSFW Support**: Optional mature content handling with specialized models
- **Multi-model Support**: Seamlessly switches between different LLM providers (OpenRouter, DeepSeek, Venice, Gemini)
- **Failover Mechanism**: Automatic model switching when primary models fail
- **Chat History**: Persistent storage of conversations
- **User Authentication**: Secure login and registration system
- **Responsive Design**: Modern UI that works on desktop and mobile devices
- **Multilingual Support**: Capable of handling conversations in multiple languages

## 🛠️ Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI** - High-performance web framework
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation and settings management
- **HTTPX** - Asynchronous HTTP client for LLM API calls
- **Python-dotenv** - Environment variable management

### Frontend
- **React 18** - JavaScript library for building user interfaces
- **Vite** - Fast build tool and development server
- **TypeScript** - Typed superset of JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - Promise-based HTTP client

### Database
- **SQLite** (development) - Lightweight relational database
- **PostgreSQL** (production ready) - Robust open-source database

### LLM Providers
- **OpenRouter** - Access to various open-source and proprietary models
- **DeepSeek** - Specialized coding and reasoning models
- **Venice** - Uncensored inference API
- **Google Gemini** - Multimodal AI models

## 📋 Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- Git
- API keys for at least one LLM provider (OpenRouter recommended for free tier)

## 🔧 Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd role_bot
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv
# Activate virtual environment
# On Windows:
.venv\Scripts\Activate.ps1
# On Unix or MacOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file from example
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Initialize Database
```bash
# From the backend directory
cd ../backend
python -c "from database import init_db; init_db()"
```

### 5. Run the Application
```bash
# Start backend server (from backend directory)
uvicorn main:app --reload

# Start frontend development server (from frontend directory)
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🔐 Environment Variables

Create a `.env` file in the backend directory based on `.env.example`:

```env
# LLM API Keys (at least one required)
OPENROUTER_API_KEY=your_openrouter_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here
VENICE_API_KEY=your_venice_key_here
GEMINI_API_KEY=your_gemini_key_here

# Optional: Default models
OPENROUTER_MODEL=google/gemini-2.0-flash-exp:free
```

## 📁 Project Structure

```
role_bot/
├── backend/                 # Python/FastAPI backend
│   ├── main.py              # Application entry point
│   ├── llm_client.py        # LLM provider integrations
│   ├── auth.py              # Authentication utilities
│   ├── database.py          # Database setup and models
│   ├── models.py            # Pydantic and SQLAlchemy models
│   ├── schemas.py           # API request/response schemas
│   ├── routers/             # API route modules
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── bots.py          # Character/bot management
│   │   └── chats.py         # Chat message handling
│   ├── .env                 # Environment variables (gitignored)
│   ├── .env.example         # Template for environment variables
│   └── requirements.txt     # Python dependencies
├── frontend/                # React/Vite frontend
│   ├── src/                 # Source code
│   │   ├── App.tsx          # Main application component
│   │   ├── main.tsx         # Entry point
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API service functions
│   │   ├── utils/           # Utility functions
│   │   ├── assets/          # Static assets (images, icons)
│   │   └── styles/          # CSS and styling
│   ├── public/              # Static public files
│   ├── index.html           # HTML template
│   ├── package.json         # Node.js dependencies and scripts
│   ├── vite.config.ts       # Vite configuration
│   ├── tsconfig.json        # TypeScript configuration
│   └── eslint.config.js     # ESLint configuration
├── .gitignore               # Git ignore rules
├── .env.example             # Environment variables template
└── README.md                # This file
```

## 🚀 Usage

1. Register a new account or log in with existing credentials
2. Create or select a character to chat with
3. Toggle NSFW mode if desired (requires appropriate API keys)
4. Start conversations and enjoy immersive role-playing experiences

## 🔒 Security Notes

- Never commit your `.env` file to version control
- The `.gitignore` file is configured to exclude sensitive files
- API keys should be kept secret and rotated periodically
- The application uses HTTPS in production environments

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the high-performance backend framework
- [React](https://reactjs.org/) and [Vite](https://vitejs.dev/) for the modern frontend stack
- [OpenRouter](https://openrouter.ai/) for providing access to diverse LLM models
- All contributors and testers who helped improve this project

---

*Last updated: June 5, 2026*