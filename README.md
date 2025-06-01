# Interview Ace

An AI-powered web application that helps users prepare for job interviews by analyzing their resume and conducting personalized mock interviews.

## Features

- Resume Analysis
  - Upload and parse resumes (PDF/DOC)
  - Extract key information
  - Infer job role and experience level

- Mock Interviews
  - Text-based interview sessions
  - Personalized questions based on resume
  - Real-time evaluation of answers

- Feedback System
  - Detailed performance analysis
  - Strengths and weaknesses identification
  - Improvement suggestions

## Tech Stack

- Frontend: React.js, TailwindCSS/Material UI
- Backend: FastAPI
- Database: PostgreSQL
- AI/ML: Hugging Face LLMs, Groq, Gemini APIs
- Authentication: JWT

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory with:
   ```
   POSTGRES_SERVER=localhost
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=interview_ace
   SECRET_KEY=your-secret-key-here
   ```

5. Initialize the database:
   ```bash
   python -m app.db.init_db
   ```

6. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
.
├── .gitignore
├── README.md
├── requirements.txt
├── backend/
│   ├── main.py
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   └── v1/
│   │   │       ├── api.py
│   │   │       └── endpoints/
│   │   │           ├── auth/
│   │   │           │   ├── __init__.py
│   │   │           │   ├── change_password.py
│   │   │           │   ├── login.py
│   │   │           │   ├── logout.py
│   │   │           │   ├── me.py
│   │   │           │   ├── refresh.py
│   │   │           │   ├── register.py
|     |     |            |
│   │   │           ├── interview/
│   │   │           │   ├── __init__.py
│   │   │           │   ├── answer.py
│   │   │           │   ├── complete.py
│   │   │           │   ├── history.py
│   │   │           │   ├── next_question.py
│   │   │           │   ├── session.py
│   │   │           │   ├── start.py
│   │   │           │   └── summary.py
│   │   │           └── resume/
│   │   │               ├── __init__.py
│   │   │               ├── analysis.py
│   │   │               ├── export.py
│   │   │               ├── management.py
│   │   │               ├── sharing.py
│   │   │               ├── upload.py
│   │   │               └── version.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── middleware.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── init_db.py
│   │   │   └── session.py
│   │   ├── models/
│   │   │   ├── base.py
│   │   │   ├── interview.py
│   │   │   ├── resume.py
│   │   │   ├── security.py
│   │   │   └── user.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── base.py
│   │   │   ├── interview.py
│   │   │   ├── resume.py
│   │   │   ├── security.py
│   │   │   └── user.py
│   │   ├── services/
│   │   │   ├── interview_orchestrator.py
│   │   │   └── resume_parser.py
│   │   └── utils/
│   │       ├── file_handler.py
│   │       ├── file_utils.py
│   │       └── llm_client.py
└── uploads/
    └── ...
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License