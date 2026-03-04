# 🎨 Art Buddy - AI-Powered Art Learning Platform

A comprehensive full-stack learning platform featuring AI tutoring, RAG-powered Q&A, n8n workflow automation, and Duolingo-style progressive learning.

## 🚀 Quick Start

### Option 1: One-Click Startup (Windows)
```powershell
.\start.ps1
```

This script will:
- ✅ Clean up any existing processes
- ✅ Start backend server on port 8000
- ✅ Start frontend server on port 3000
- ✅ Verify both servers are running
- ✅ Open the app in your browser

### Option 2: Manual Startup

**Backend:**
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```powershell
cd frontend
npm run dev
```

## 🔑 Test Credentials
- **Email:** test@example.com
- **Password:** testpass123

## 📍 URLs
- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## ✨ Features

### 📚 Lessons
- **Duolingo-style UI** with circular lesson nodes
- **6 categories**: Drawing, Painting, Color Theory, Digital Art, Design, Character Art
- **Progressive unlocking** - complete lessons to unlock the next
- **14 lessons** with varying difficulty levels
- **30 quiz questions** for comprehensive assessment

### 🤖 AI Tutor
- **RAG-powered Q&A** using knowledge base
- **Real-time chat interface**
- **Source attribution** for answers
- **Sample prompts** to get started
- Knowledge base statistics display

### 📊 Progress Tracking
- **Stats dashboard** with completion rate, streak, time invested, average score
- **Skill progress bars** for each category
- **Weekly activity charts**
- **n8n workflow testing** for automation
- **MCP tool integration** for AI interactions

### 🔧 Technology Stack

**Frontend:**
- React 18 + TypeScript
- Vite for blazing-fast dev server
- TanStack Query for data fetching
- React Router for navigation
- Tailwind CSS for styling
- Heroicons for icons

**Backend:**
- FastAPI (Python)
- SQLite database
- JWT authentication
- RAG system for AI tutoring
- n8n webhook integration
- MCP protocol support

## 📁 Project Structure
```
art_buddy/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── entities/        # Database models
│   │   ├── routers/         # API endpoints
│   │   └── services/        # Business logic
│   ├── art_buddy.db         # SQLite database
│   └── .venv/               # Python virtual environment
├── frontend/
│   ├── src/
│   │   ├── pages/           # React pages
│   │   ├── components/      # Reusable components
│   │   ├── services/        # API clients
│   │   └── stores/          # State management
│   └── package.json
├── start.ps1                # One-click startup script
└── README.md                # This file
```

## 🎯 Key Components

### Lessons Page (Duolingo-style)
- Circular lesson nodes with 4 states: locked, unlocked, in-progress, completed
- Color-coded categories with gradient borders
- Progress bars for each category
- Overall progress tracker
- Category filtering

### AI Tutor Page
- Chat interface with message history
- Sample prompts for quick start
- RAG system status display
- Source attribution
- Error handling

### Progress Page
- 4 stat cards: Completion Rate, Streak, Time Invested, Average Score
- Skill progress visualization
- Weekly activity chart (placeholder)
- n8n workflow testing buttons
- MCP tool testing buttons

## 🐛 Troubleshooting

### "Coming Soon" Messages
If you see "coming soon" instead of actual content:
1. Check you're accessing **http://localhost:3000** (not 3001 or 3003)
2. Kill all node processes: `Get-Process node | Stop-Process -Force`
3. Restart using `.\start.ps1`
4. Hard refresh browser: `Ctrl + Shift + R`

### Port Already in Use
```powershell
# Kill process on port 3000
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess | Stop-Process -Force

# Kill process on port 8000
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
```

### Backend Not Running
1. Ensure Python virtual environment is activated
2. Check backend terminal for errors
3. Verify database exists: `backend/art_buddy.db`
4. Test endpoint: `curl http://localhost:8000`

### Frontend Not Loading
1. Ensure `npm install` was run in frontend directory
2. Check frontend terminal for TypeScript errors
3. Clear browser cache
4. Check browser console for errors (F12)

## 📝 Database

**14 Lessons** across 6 categories:
- Drawing (5 lessons)
- Painting (3 lessons)  
- Color Theory (2 lessons)
- Digital Art (2 lessons)
- Design (1 lesson)
- Character Art (1 lesson)

**30 Quiz Questions** - 100% lesson coverage

## 🔄 Recent Fixes
- ✅ Fixed TypeScript compilation errors
- ✅ Corrected API method names
- ✅ Added proper type definitions
- ✅ Fixed Progress type mismatches
- ✅ Ensured single server per port
- ✅ Verified all pages export correctly

## 📚 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/me` - Get current user

### Lessons
- `GET /lessons` - List all lessons
- `GET /lessons/{id}` - Get lesson details
- `GET /lessons/{id}/quiz` - Get lesson quiz

### Progress
- `GET /progress` - Get user progress
- `POST /progress/start` - Start a lesson
- `POST /progress/update` - Update progress
- `POST /progress/complete` - Complete a lesson

### AI & RAG
- `POST /ai/ask` - Ask AI a question
- `GET /ai/knowledge-stats` - Get knowledge base stats

Full API documentation: http://localhost:8000/docs

## 🎨 Design Philosophy
- **Progressive Learning**: Lessons unlock as you progress
- **Gamification**: Streaks, scores, and visual progress
- **AI-Powered**: Intelligent tutoring with RAG
- **Automation**: n8n workflows for scheduling and notifications
- **Modern UI**: Duolingo-inspired, clean, responsive

## 📄 License
Educational project - not for commercial use

## 🤝 Support
- Check browser console for errors (F12)
- Verify both servers are running
- Ensure you're on the correct port (3000)
- Use test credentials for login
