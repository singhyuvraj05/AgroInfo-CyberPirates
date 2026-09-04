# AgroInfo Project Context

## 1. PROJECT OVERVIEW

### What AgroInfo is

AgroInfo is a cooperative digital agriculture network prototype for small and
marginal farmers across India. It combines farm information, soil health,
weather conditions, vegetation-health signals, and AI-assisted analysis to
provide localized and explainable agricultural guidance.

### Problem statement

Small and marginal farmers often lack access to data-driven agricultural
guidance. Dependence on traditional methods, without practical access to
satellite data, soil-health analytics, and climate forecasting, can lead to
crop failure and threaten food security. The lack of shared digital
infrastructure also limits collaboration between states on climate-resilient
farming.

### Core purpose of the MVP

The MVP will demonstrate one focused farmer journey: a farmer provides field
and crop information, AgroInfo obtains environmental context, and an advisory
engine produces an explainable recommendation. The MVP will also demonstrate
crop-disease screening and how agricultural intelligence can be shared and
reused across states.

This is a convincing hackathon prototype, not a complete national agriculture
platform.

## 2. CURRENT TEAM

- **Pawan** — AI/ML + Python + data + disease prediction / Team Leader
- **Shambhavi** — Presentation + documentation + demo flow + communication
- **Yuvraj Singh** — Frontend + application integration + general coding + Git/GitHub + debugging.                                                                

## 3. AGREED MVP

The team has agreed to prioritize the following features:

- Farmer dashboard
- Localized agricultural advisory
- Soil + weather intelligence
- Crop/regenerative recommendation
- Crop disease diagnosis
- NDVI / vegetation-health demonstration
- Cooperative state model/data sharing

The MVP should prioritize a small, coherent, working flow over broad national
coverage or a large number of incomplete features.

## 4. AGREED TECH STACK

- **Frontend:** Next.js / React / TypeScript
- **Backend:** FastAPI / Python
- **Database:** MySQL
- **ORM:** SQLAlchemy
- **Weather:** Open-Meteo
- **AI/ML:** Python-based services/models
- **NDVI:** Synthetic/demo data initially
- **Version control:** Git/GitHub

MySQL is the agreed database for this hackathon, and FastAPI is the agreed
backend framework.

## 5. ARCHITECTURE

The intended high-level architecture is:

```text
Frontend (Next.js / React / TypeScript)
        |
        v
FastAPI backend
        |
        +--> MySQL
        +--> Open-Meteo
        +--> Python AI/ML services
        +--> Synthetic NDVI/demo data
        |
        v
Response
        |
        v
Frontend
```

The frontend is responsible for the farmer-facing dashboard, forms, results,
visualizations, and interaction states. FastAPI exposes the application API,
validates requests, coordinates services, and returns structured responses.
MySQL stores farm and advisory data. External APIs and AI/ML services are
accessed through the backend rather than directly from the browser.

### Advisory data flow

The advisory engine combines:

- **Soil:** pH, nutrient values, soil type, and other available soil-health
  information
- **Weather:** current conditions and forecast information from Open-Meteo
- **NDVI:** synthetic vegetation-health values and trends for the initial demo
- **Crop information:** current or planned crop, crop requirements, and
  available farm context

The engine uses these inputs to produce a localized recommendation, explain the
main factors behind it, identify relevant risks, and suggest regenerative or
water-conscious practices. AI/ML outputs should be understandable and checked
against sensible agricultural rules rather than presented as unexplained
predictions.

## 6. PLANNED DATABASE TABLES

The following tables are proposed. Exact column types and relationships will
be finalized during implementation.

### `farms`

Important fields:

- `id`
- farmer or owner reference, if needed
- state
- district
- village or location details
- area
- soil type
- current crop
- planned crop
- irrigation availability
- `created_at`
- `updated_at`

### `soil_data`

Important fields:

- `id`
- `farm_id`
- nitrogen
- phosphorus
- potassium
- pH
- organic carbon, if available
- source or measurement method
- recorded date

### `weather_data`

Important fields:

- `id`
- `farm_id`
- location or coordinates
- observation/forecast date
- temperature
- rainfall
- humidity
- forecast summary
- data source
- fetched timestamp

### `vegetation_data`

Important fields:

- `id`
- `farm_id`
- observation date
- NDVI value
- vegetation-health status
- trend or comparison value
- source

The initial source will be synthetic/demo data.

### `advisories`

Important fields:

- `id`
- `farm_id`
- recommended crop or action
- advisory text
- explanation
- regenerative recommendation
- risk information
- confidence score
- input snapshot or source references
- created timestamp

### `disease_scans`

Important fields:

- `id`
- `farm_id`, if associated with a farm
- image reference or upload metadata
- crop
- predicted disease
- confidence score
- symptoms
- recommended next step
- created timestamp

### `shared_models`

Important fields:

- `id`
- state
- district or region, if applicable
- crop
- climate or soil context
- observed problem
- recommended practice
- evidence/source
- outcome or notes
- model/version metadata
- created timestamp

This table represents reusable agricultural intelligence shared between states.

## 7. PLANNED API ENDPOINTS

The currently planned endpoints include:

```text
GET  /farms/{id}
POST /advisory
GET  /weather/{farm_id}
GET  /vegetation/{farm_id}
POST /disease/predict
GET  /models
POST /models
GET  /models/{id}
```

These endpoints are provisional and may be refined during implementation.
Request and response schemas should be kept small, explicit, and easy for the
frontend team to consume.

## 8. CURRENT IMPLEMENTATION STATUS

The current workspace was inspected before creating this file.

### Files currently present

Before this context file was created, the project root contained no files or
subfolders. The only file now intentionally present is:

- `PROJECT_CONTEXT.md` — this project memory/reference document

### Already implemented

- No application functionality has been implemented.
- No frontend, backend, database schema, AI/ML model, or API integration exists
  yet.

### Partially implemented

- Nothing is partially implemented.

### Not implemented yet

- Next.js frontend
- FastAPI backend
- MySQL database and SQLAlchemy models
- Farm, soil, weather, vegetation, advisory, disease, and shared-model tables
- Frontend-to-backend connection
- FastAPI-to-MySQL connection
- Open-Meteo integration
- Advisory engine
- AI/ML services or models
- Disease diagnosis
- NDVI demonstration
- Cooperative state model/data sharing
- Testing, deployment, and UI polish

Do not assume a feature is implemented merely because it appears in this
document or was discussed in planning.

## 9. NEXT BUILD ORDER

Build the MVP in this order:

1. **Project skeleton** — initialize the Next.js frontend and FastAPI backend,
   establish configuration, environment variables, and a clear repository
   structure.
2. **Frontend ↔ FastAPI connection** — add a health check and one simple
   request from the dashboard to verify end-to-end communication.
3. **FastAPI ↔ MySQL connection** — configure SQLAlchemy, connect to MySQL, and
   verify a database query.
4. **Farmer/farm data** — create the initial farm and soil models, API flow,
   and farmer dashboard form.
5. **Weather integration** — connect Open-Meteo, normalize the response, and
   provide a fallback/demo path if the external service is unavailable.
6. **Advisory engine** — combine soil, weather, NDVI demo values, and crop
   information into an explainable crop/regenerative recommendation.
7. **Disease diagnosis** — add image upload or a constrained screening flow
   with confidence and a clear non-diagnostic disclaimer.
8. **NDVI** — add synthetic vegetation-health data, status indicators, and a
   simple trend visualization.
9. **Cooperative model sharing** — add shared state models/advisories and show
   how one state's agricultural intelligence can be reused by another.
10. **UI polish/testing** — improve the farmer journey, responsive layout,
    loading/error states, demo data, validation, and critical-path testing.

## 10. IMPORTANT DEVELOPMENT PRINCIPLES

- This is a 24-hour hackathon MVP, not a production nationwide system.
- Prioritize a smaller working system over many unfinished features.
- Use AI as an accelerator, but understand and verify generated code.
- Do not blindly copy code.
- Keep the architecture simple enough for a 24-hour build.
- Advanced production ideas such as real satellite ingestion,
  authentication, multilingual voice, and similar capabilities are future
  scope unless already implemented.
- Prefer transparent, explainable outputs over impressive but unverifiable
  claims.
- Use synthetic or seeded data honestly and label it clearly in the demo.
- Keep external integrations replaceable with fallback data so the main demo
  remains reliable.

## 11. HACKATHON DEMO STORY

The intended demonstration flow is:

1. A farmer enters field, location, soil, and crop information.
2. AgroInfo obtains environmental information, including weather and
   vegetation-health context.
3. The advisory engine combines the inputs and produces an explainable
   crop/regenerative recommendation.
4. The farmer uploads a crop image for disease screening.
5. AgroInfo returns a likely issue, confidence, symptoms, and a safe next step.
6. The cooperative network demonstrates sharing and reuse of agricultural
   intelligence between states through the shared model/data structure.

The presentation should emphasize the practical farmer benefit and the
cooperation model, while clearly describing the prototype's simulated data and
limited scope.

## 12. HOW TO CONTINUE

Future AI sessions should first read `PROJECT_CONTEXT.md` and inspect the
current workspace before making architectural changes or writing code. They
should treat this document as the current project reference, verify the actual
implementation state from the files, and avoid assuming that planned features
already exist.

Any future change to the stack, MVP scope, architecture, or build order should
be discussed with the team and then reflected in this document when agreed.
