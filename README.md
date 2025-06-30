# CRUB Course Team Management System

FastAPI web application for managing faculty designations and course assignments at Centro Regional Universitario Bariloche (CRUB).

## Features

This system combines data from multiple APIs to provide a comprehensive view of faculty designations and course assignments:

- **Google Sheets API**: Faculty designations (`designaciones_docentes`) and course assignments (`materias_equipo`)
- **Huayca API**: Detailed course information from the academic system
- **Data Integration**: Links designations with course assignments and enriches with detailed course information

### Key Data Relationships

1. **D Desig** (from `designaciones_docentes`) ↔ **Desig** (from `materias_equipo`)
   - Links faculty designations with their course assignments

2. **Cod SIU** (from `materias_equipo`) ↔ **cod_guarani** (from Huayca)
   - Links course assignments with detailed academic information

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Make sure your `.env` file contains the correct API credentials:

```env
# Google Sheets API Configuration
GOOGLE_SHEETS_BASE_URL=https://script.google.com/macros/s/.../exec
GOOGLE_SHEETS_SECRET=1250

# Huayca API Configuration  
HUAYCA_BASE_URL=https://huayca.crub.uncoma.edu.ar/catedras/1.0/rest/materias
HUAYCA_USERNAME=usuario1
HUAYCA_PASSWORD=pdf

# FastAPI Configuration
ADMIN_USERNAME=admin
ADMIN_PASSWORD=crub2025
DEBUG=true
HOST=127.0.0.1
PORT=8000
```

### 3. Test the System

Run the test script to verify all APIs are working:

```bash
python test_system.py
```

### 4. Start the Server

#### Option A: Using the startup script
```bash
python run_server.py
```

#### Option B: Using uvicorn directly
```bash
# From the project root
python -m uvicorn src.crub_courses.main:app --reload --host 127.0.0.1 --port 8000
```

### 5. Access the Application

- **Home page**: http://localhost:8000/
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

## API Endpoints

### Public Endpoints

- `GET /` - Home page with API information
- `GET /health` - Health check and service status
- `GET /designaciones` - Get all faculty designations with related course assignments
- `GET /designaciones/{d_desig}` - Get specific designation by D Desig number
- `GET /designaciones/docente/{docente_name}` - Get all designations for a faculty member

### Admin Endpoints (require authentication)

- `POST /admin/cache/clear` - Clear the Huayca data cache
- `GET /admin/stats` - Get system statistics

## Data Structure

### Designaciones Response

Each designation includes:

```json
{
  "id_redesignacion": 123,
  "d_desig": "12345",
  "apellido_y_nombre": "DOE, JOHN",
  "legajo": "67890",
  "departamento": "MATEMÁTICA",
  "area": "ALGEBRA",
  "materias": [
    {
      "id_redesignacion_materia": 456,
      "materia_nombre": "ALGEBRA LINEAL",
      "cod_siu": "MA101",
      "rol": "Resp",
      "periodo": "1CUAT",
      "materia_detalle": {
        "nombre_materia": "ALGEBRA LINEAL",
        "ano_plan": 1,
        "horas_totales": "120",
        "correlativas_para_cursar": "MATEMATICA BASICA aprobada",
        "optativa": "NO"
      }
    }
  ]
}
```

## Development

### Project Structure

```
src/
├── crub_courses/
│   ├── api/           # API clients for external services
│   ├── models/        # Data models and type definitions
│   ├── services/      # Business logic and data processing
│   └── main.py        # FastAPI application
docs/                  # API documentation
scripts/               # Utility scripts
tests/                 # Test files (future)
```

### Adding New Features

1. **New API clients**: Add to `src/crub_courses/api/clients.py`
2. **New data models**: Add to `src/crub_courses/models/types.py`
3. **New business logic**: Add to `src/crub_courses/services/`
4. **New endpoints**: Add to `src/crub_courses/main.py`

### Error Handling

The application includes comprehensive error handling:

- API connection failures
- Data parsing errors
- Authentication failures
- Missing data relationships

### Logging

The application logs important events and errors. Set `LOG_LEVEL=DEBUG` in your `.env` file for detailed logging.

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you're running from the project root and all dependencies are installed
2. **API connection failures**: Check your `.env` file and network connectivity
3. **Data relationship mismatches**: Run the test script to analyze data relationships

### Testing API Connections

```bash
# Test individual APIs
python -c "
from src.crub_courses.api.factory import create_google_sheets_client
client = create_google_sheets_client()
print(client.get_available_sheets())
"
```

### Checking Data Relationships

The test script (`test_system.py`) provides detailed analysis of data relationships and will help identify any data consistency issues.

## License

This project is for internal use at CRUB (Centro Regional Universitario Bariloche).
