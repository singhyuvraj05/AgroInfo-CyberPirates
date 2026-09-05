# AgroInfo

AgroInfo is a small hackathon MVP connecting a Next.js frontend to a FastAPI
backend and a MySQL database.

## Project structure

```text
frontend/  Next.js, React, and TypeScript application
backend/   FastAPI application and SQLAlchemy database code
database/  MySQL setup notes
ai/        Reserved for future Python AI/ML work
```

The current milestone implements only a health check and a database-backed
demo farm lookup. Weather, AI/ML, disease detection, NDVI, recommendations,
cooperative sharing, and authentication are intentionally not included yet.

## Requirements

- Node.js 18.18 or newer and npm
- Python 3.11 or newer
- MySQL 8.x

## MySQL setup

Create the database and a local user, or use an existing MySQL user:

```sql
CREATE DATABASE agroinfo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'agroinfo'@'localhost' IDENTIFIED BY 'change-this-password';
GRANT ALL PRIVILEGES ON agroinfo.* TO 'agroinfo'@'localhost';
FLUSH PRIVILEGES;
```

See [database/README.md](database/README.md) for more details.

## Backend setup

From `backend/`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` with the local MySQL connection details. Then start FastAPI:

```powershell
uvicorn app.main:app --reload --port 8000
```

The backend creates the `farms` table and inserts the demo farm on startup if
they do not already exist.

Useful endpoints:

- `GET http://localhost:8000/api/health`
- `GET http://localhost:8000/api/farms/1`
- `GET http://localhost:8000/api/weather/1`

## Frontend setup

From `frontend/`:

```powershell
npm install
Copy-Item .env.example .env.local
npm run dev
```

Open <http://localhost:3000>. The page requests the health endpoint and then
loads the demo farm through FastAPI. The browser never connects directly to
MySQL.

The weather endpoint reads the farm coordinates from MySQL and retrieves
current and three-day precipitation data from Open-Meteo. Open-Meteo does not
require an API key for this demo.

## Configuration

Backend configuration is in [backend/.env.example](backend/.env.example):

```env
DATABASE_URL=mysql+pymysql://agroinfo:change-this-password@localhost:3306/agroinfo
FRONTEND_ORIGIN=http://localhost:3000
```

Frontend configuration is in [frontend/.env.example](frontend/.env.example):

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Do not commit `.env` or `.env.local` files.
