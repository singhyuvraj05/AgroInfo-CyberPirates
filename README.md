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
- `GET http://localhost:8000/api/advisory/1`
- `GET http://localhost:8000/api/recommendations/1`
- `GET http://localhost:8000/api/vegetation/1`
- `POST http://localhost:8000/api/disease-screening`
- `POST http://localhost:8000/api/cooperative/insights`
- `GET http://localhost:8000/api/cooperative/insights`
- `POST http://localhost:8000/api/cooperative/insights/{id}/reuse`

The cooperative feature is a prototype cooperative knowledge/model registry.
It stores fictional demo records and linked reuse/adaptation records. It is not
real inter-state federation, distributed synchronization, blockchain,
authentication, institutional verification, model-weight transfer, or
scientifically validated knowledge transfer. Registry metrics may come from
heuristic, synthetic, or constrained-demo features.

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

The advisory endpoint applies transparent V1 rules to the farm crop, demo soil
measurements, current weather, and three-day forecast rainfall. Nutrient
thresholds are demo assumptions in mg/kg, not a substitute for a local soil
test or agronomist.

The recommendation endpoint ranks only Soybean, Pearl millet, Chickpea, and
Sorghum using a deterministic 100-point MVP heuristic:

```text
soil suitability:          45 points
weather suitability:       50 points
regenerative suitability:   5 points
total:                    100 points
```

The score is always the exact sum of the score breakdown. It is a suitability
comparison, not a probability, yield prediction, or success guarantee. Water
availability is unknown and is not scored. Location is contextual only, and no
planting season is inferred. Crop thresholds, weights, and regenerative
descriptions are prototype assumptions requiring agronomic validation.

The vegetation endpoint uses deterministic synthetic NDVI values for the demo:
current NDVI `0.56` and previous NDVI `0.48` for farm 1. It does not use
satellite imagery, remote-sensing APIs, or field measurements.

Prototype NDVI assumptions:

```text
NDVI < 0.30          stressed
0.30 <= NDVI <= 0.55 moderate
NDVI > 0.55          healthy
```

Prototype trend assumptions compare current and previous synthetic values:

```text
change > 0.03  improving
change < -0.03 declining
otherwise      stable
```

These thresholds are demonstration heuristics, not universal scientific
standards or crop-health diagnosis.

The disease-screening endpoint is a constrained image-screening prototype. It
accepts JPEG and PNG uploads up to 5 MB, validates and decodes them in memory,
and does not save images or store them in MySQL. V1 does not identify real
diseases and does not use an AI model. A valid sufficiently sized image returns
an observation that no disease classification was performed; an ambiguous
image returns an uncertainty result. The certainty indicator is a prototype
workflow label, not a scientific disease probability or diagnostic confidence.
All responses include a non-diagnostic disclaimer.

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
