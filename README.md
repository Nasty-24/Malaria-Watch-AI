# Malaria WatchAI

### Intelligent Malaria Surveillance and Geospatial Analytics

Malaria WatchAI is an evidence-based malaria surveillance
platform for Kenya, Tanzania and Ethiopia.

## Core Objectives

- Map malaria prevalence geographically.
- Predict prevalence at unsurveyed locations.
- Visualize prediction uncertainty.
- Analyse Plasmodium species patterns.
- Examine antimalarial drug efficacy and resistance.
- Monitor environmental and weather conditions.
- Generate evidence-grounded AI surveillance briefings.

# Selected SDGs

- SDG 3: Good Health and Well-being.Targeting malaria interventions and drug policy reviews.
- SDG 10: Reduced Inequalities. Mapping uncertainty and rural burden to ensure fair resource allocation.
- SDG 17: Partnerships for the Goals. Fusing open-access datasets.

## Technology Stack

- Frontend: React + Tailwind CSS
- Backend: Django REST Framework
- Database: PostgreSQL + PostGIS
- Machine Learning: Python, Scikit-learn, LightGBM
- Geospatial: GeoPandas, Rasterio
- Maps: MapLibre
- AI: Google Gemini API (via the backend; summaries only, number-checked against evidence)

## Geographic Scope

- Kenya
- Tanzania
- Ethiopia

## Intended Users

- Malaria programme planners, surveillance officers and public health researchers.

## Important Notice

- This platform supports research and programme planning. It is not a diagnostic or treatment recommendation system.

## Repository Structure & Documentation

- DATA.md: Complete inventory of data sources, access dates, and licenses.
- ASSUMPTIONS.md: Documentation of known sampling biases and modeling assumptions.
- MODEL_CARD.md :Model performance metrics and limitations note.

## Getting Started & Quickstart

### Run locally (Windows, no admin rights)

One-time setup used for the verified run (PostgreSQL 18.6 + PostGIS 3.7, GDAL from conda-forge):

```bash
# GDAL/GEOS/PROJ for GeoDjango (PostGIS is not packaged on conda-forge for Windows)
conda create -p %USERPROFILE%\.conda\envs\mwgis -c conda-forge gdal geos proj
# PostgreSQL: EDB "binaries" zip extracted to %USERPROFILE%\pgsql, then the PostGIS
# bundle (download.osgeo.org/postgis/windows/pg18/) copied over bin/, lib/ and share/
initdb -D %USERPROFILE%\pgdata -U postgres -A trust -E UTF8
```

In `.env` set `OSGEO4W_ROOT` to the conda env's `Library` folder (OSGeo4W and conda layouts
both work), e.g. `OSGEO4W_ROOT=C:/Users/<you>/.conda/envs/mwgis/Library`. Create the role and
database from `DB_*` in `.env`, and run `CREATE EXTENSION postgis` in that database and in
`template1` (so the test database gets it too).

Every session:

```bash
pg_ctl -D %USERPROFILE%\pgdata -l %USERPROFILE%\pgdata\server.log start
cd backend && python manage.py runserver          # http://localhost:8000/api/v1/docs/
cd frontend && npm run dev                        # http://localhost:5173
```

Loading data into a fresh database (about 1 minute):

```bash
cd backend
python manage.py migrate
# ADM1 before ADM2, for each of KEN, TZA, ETH:
python manage.py import_boundaries ../data/raw/boundaries/geoBoundaries-KEN-ADM1.geojson --country KEN --level ADM1 --id-field shapeID --repair
python manage.py import_ml_outputs
python manage.py seed_weather_source
python manage.py createsuperuser && python manage.py add_reviewer <username>
```

Tests: `python -m pytest` (repo root: data + ML), `cd backend && python -m pytest`,
`python -m ml.src.smoke`, `cd frontend && npm test`.
