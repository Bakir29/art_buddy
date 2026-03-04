# Art Buddy Backend

FastAPI-based backend for the Art Buddy AI-powered art learning platform.

## Features

- **Layered Architecture**: Clean separation of entities, repositories, services, and controllers
- **PostgreSQL + pgvector**: Database with vector search capabilities for RAG
- **JWT Authentication**: Secure user authentication and authorization
- **Alembic Migrations**: Database schema management
- **Docker Support**: Containerized development environment
- **OpenAPI Documentation**: Auto-generated API docs

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (if running locally)

### Using Docker (Recommended)

1. **Setup environment**:
   ```bash
   # Windows
   setup-dev.bat
   
   # Linux/Mac
   chmod +x setup-dev.sh
   ./setup-dev.sh
   ```

2. **Access the application**:
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - n8n: http://localhost:5678 (admin/password)

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run PostgreSQL**:
   ```bash
   docker-compose up -d postgres
   ```

4. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

5. **Start the API**:
   ```bash
   uvicorn main:app --reload
   ```

## Project Structure

```
backend/
├── app/
│   ├── auth/                 # Authentication utilities
│   │   ├── security.py       # JWT and password handling
│   │   └── dependencies.py   # FastAPI auth dependencies
│   ├── entities/             # Data models and schemas
│   │   ├── models.py         # SQLAlchemy models
│   │   └── schemas.py        # Pydantic schemas
│   ├── repositories/         # Data access layer
│   │   └── user_repository.py
│   ├── services/             # Business logic (to be added)
│   ├── controllers/          # API endpoints (to be added)
│   ├── config.py            # Configuration settings
│   └── database.py          # Database connection
├── alembic/                  # Database migrations
├── docker-compose.yml       # Docker services
├── Dockerfile               # Backend container
├── main.py                  # FastAPI application
└── requirements.txt         # Python dependencies
```

## Database Models

- **User**: User accounts with authentication
- **Lesson**: Art learning content
- **Progress**: User learning progress tracking  
- **QuizQuestion/QuizResponse**: Quiz system
- **Reminder**: Automated notifications
- **KnowledgeChunk**: RAG knowledge base with vector embeddings

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key
- `OPENAI_API_KEY`: For embeddings and AI responses
- `N8N_WEBHOOK_URL`: n8n integration endpoint

## Commands

```bash
# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head

# Run tests (when added)
pytest

# Format code
black .
isort .

# Type checking
mypy app/
```

## API Endpoints

### Phase 1 (Current)
- `GET /` - Root endpoint
- `GET /health` - Health check

### Phase 2 (Planned)
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /lessons` - List lessons
- `POST /progress` - Update progress
- `GET /recommendations` - Get recommendations

## Development Phases

This backend is being developed in phases:

1. **Phase 1** ✅: Core structure, database, auth system
2. **Phase 2**: Core learning APIs  
3. **Phase 3**: RAG knowledge system
4. **Phase 4**: MCP tool integration
5. **Phase 5**: n8n workflow automation

## Contributing

1. Follow the layered architecture pattern
2. Add tests for new functionality
3. Update database migrations for schema changes
4. Document API endpoints with proper schemas