AI Plugin Analytics Backend

Introduction

This Python backend powers the analytics engine for the AI plugin, enabling you to capture, store, and analyze user interactions and conversion events on your website. Built with FastAPI, this service exposes REST endpoints for logging chat messages, tracking CTA clicks, retrieving analytics data, and exporting reports.

Features

Message Logging: Record every chat message sent by users, tied to their session or user ID.

CTA Conversion Tracking: Track when users click on custom CTA buttons within the chat.

User Chat History: Save and retrieve full chat transcripts per user.

Analytics Endpoints: Aggregate data endpoints to fetch metrics like total messages, active users, and conversion rates.

CSV Exports: Export raw event logs or summarized analytics as CSV for further analysis.

Weekly Email Reports: Schedule and send summary reports via email (SMTP).

Modular & Extensible: Easily plug in new analytics modules or integrate additional AI backends (OpenAI, LLaMA).

Tech Stack

Python 3.10+

FastAPI for API routing

Uvicorn as the ASGI server

SQLModel / SQLAlchemy for ORM and database interactions

Alembic for database migrations

Pydantic for data validation

python-dotenv for environment variable management

Installation

Clone the repository

git clone https://github.com/your-org/ai-plugin-analytics-backend.git
cd ai-plugin-analytics-backend

Create a virtual environment

python -m venv venv
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate     # Windows

Install dependencies

pip install --upgrade pip
pip install -r requirements.txt

Configure environment variables
Copy .env.example to .env and update values:

DATABASE_URL=sqlite:///./analytics.db
OPENAI_API_KEY=sk-...
EMAIL_HOST=smtp.mailtrap.io
EMAIL_PORT=587
EMAIL_USER=user
EMAIL_PASSWORD=pass

Database Migrations

Use Alembic to manage schema:

alembic upgrade head

(Optional) To generate a new migration after changing models:

alembic revision --autogenerate -m "Add new field to Event model"

Running the Server

Start the API with Uvicorn:

uvicorn main:app --reload --host 0.0.0.0 --port 8000

Your endpoints will be available at http://localhost:8000 and the interactive docs at http://localhost:8000/docs.

API Endpoints

POST /client/update

Log a chat message or CTA event.

Request Body (JSON):

{
  "user_id": "string",
  "session_id": "string",
  "message": "Hello, world!",
  "event_type": "message"       // or "cta_click"
}

Response:

{ "status": "success" }

GET /analytics/summary

Retrieve aggregated analytics.

Query Params:

start_date (YYYY-MM-DD)

end_date (YYYY-MM-DD)

Response:

{
  "total_messages": 1234,
  "unique_users": 56,
  "cta_clicks": 78
}

GET /analytics/export

Download raw event logs as CSV.

Response:

CSV file download of event_id,user_id,session_id,event_type,timestamp,message

POST /reports/weekly

Trigger manual weekly report (used by scheduler).

Response:

{ "status": "report_sent" }

Scheduled Tasks

Weekly reports are sent via an internal scheduler (e.g., cron or APScheduler). Ensure your scheduler calls:

curl -X POST http://localhost:8000/reports/weekly

Configuration

Variable

Description

Default

DATABASE_URL

SQL connection string

sqlite:///./analytics.db

OPENAI_API_KEY

API key for AI backend integrations

(none)

EMAIL_HOST

SMTP server hostname

(none)

EMAIL_PORT

SMTP server port

587

EMAIL_USER

SMTP username

(none)

EMAIL_PASSWORD

SMTP password

(none)

Contributing

Fork the repo

Create a feature branch (git checkout -b feature/YourFeature)

Commit your changes (git commit -m "Add new analytics endpoint")

Push (git push origin feature/YourFeature)

Open a Pull Request
