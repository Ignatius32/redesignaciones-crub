# CRUB Course Team Management System

A comprehensive system for detecting course teams and aggregating data from multiple sources at Centro Regional Universitario Bariloche (CRUB).

## Features

- **Data Integration**: Aggregates data from Google Sheets (materias_equipo, designaciones_docentes) and Huayca API
- **Course Team Detection**: Automatically detects unique courses and builds complete faculty teams
- **Data Enrichment**: Matches and enriches faculty assignments with personal details and academic information
- **Multiple Interfaces**: 
  - **FastAPI REST API** with web interface (recommended)
  - Modern web interface (Streamlit)
  - Command-line interface for terminal users
- **Advanced Filtering**: Filter courses by department, period, career, team size, and more
- **Authentication**: Built-in admin authentication for data management
- **API Documentation**: Interactive Swagger UI and ReDoc documentation
- **Comprehensive Statistics**: Detailed analytics and visualizations of course data

## Quick Start

### FastAPI Web Application (Recommended)

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Start the FastAPI server:**
```bash
uvicorn src.crub_courses.ui.fastapi_app:app --host 0.0.0.0 --port 8000 --reload
```

3. **Access the application:**
- **Dashboard**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Admin Panel**: http://localhost:8000/admin (credentials configured in .env file)

### Alternative Interfaces

**Streamlit Web Interface:**
```bash
python run_streamlit_app.py
```

**Console Application:**
```bash
python run_console_app.py
```

## Project Structure

```
redesignaciones-crub/
├── src/
│   └── crub_courses/
│       ├── __init__.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── clients.py      # API client implementations
│       │   └── factory.py      # Client factory functions
│       ├── models/
│       │   ├── __init__.py
│       │   ├── core.py         # Core data models
│       │   ├── summary.py      # Summary and status models
│       │   └── types.py        # Type aliases
│       ├── services/
│       │   ├── __init__.py
│       │   └── course_team_service.py  # Main business logic
│       └── ui/
│           ├── __init__.py
│           ├── console_app.py   # Command-line interface
│           ├── streamlit_app.py # Streamlit web interface
│           ├── fastapi_app.py   # FastAPI REST API + web interface
│           ├── templates/       # HTML templates for FastAPI
│           │   ├── base.html
│           │   ├── dashboard.html
│           │   ├── courses.html
│           │   ├── course_detail.html
│           │   └── admin.html
│           └── static/         # CSS and other static files
│               └── styles.css
├── tests/
│   ├── test_integration.py     # Integration tests
│   └── test_quick.py          # Quick unit tests
├── docs/
│   ├── api_1.md               # API documentation
│   ├── api_2.md
│   └── TEST_RESULTS.md        # Test results
├── scripts/
│   └── debug_apis.py          # Debug utilities
├── run_console_app.py         # Console app entry point
├── run_streamlit_app.py       # Streamlit app entry point
├── run_fastapi_app.py         # FastAPI app entry point
├── setup.py                   # Package setup
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## Installation

### Prerequisites
- Python 3.11 or higher
- Git (for version control)

### Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd redesignaciones-crub
```

2. **Create and activate virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env file with your actual credentials
```

**Required environment variables:**
- `GOOGLE_SHEETS_BASE_URL`: Your Google Sheets API endpoint
- `GOOGLE_SHEETS_SECRET`: Secret for Google Sheets access
- `HUAYCA_USERNAME`: Username for Huayca API
- `HUAYCA_PASSWORD`: Password for Huayca API
- `ADMIN_USERNAME`: Admin username for FastAPI (default: admin)
- `ADMIN_PASSWORD`: Admin password for FastAPI

5. **Start the application:**

## REST API Endpoints

The FastAPI application provides a comprehensive REST API:

### Public Endpoints
- `GET /api/health` - Health check
- `GET /api/courses` - List courses with optional filtering
- `GET /api/courses/{cod_siu}/{periodo}` - Get specific course details
- `GET /api/departments` - List available departments
- `GET /api/summary` - System summary and statistics
- `GET /api/data-status` - Data source status

### Admin Endpoints (Authentication Required)
- `POST /api/refresh-data` - Refresh data from all sources

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## Web Interface Features

### FastAPI Web Application
- **Modern Bootstrap UI**: Responsive design with professional styling
- **Dashboard**: Overview statistics and quick navigation
- **Course Catalog**: Filterable list with search capabilities
- **Course Details**: Comprehensive course and team information
- **Admin Panel**: Data management and system monitoring
- **Authentication**: Secure admin access for sensitive operations

### Legacy Streamlit Interface

### Legacy Streamlit Interface

Start the Streamlit web application:

```bash
python run_streamlit_app.py
```

Then open your browser to `http://localhost:8501`

**Features:**
- Interactive filtering by department, period, career
- Real-time statistics and visualizations
- Detailed course information with team member details
- Export capabilities

### Command-Line Interface

Start the console application:

```bash
python run_console_app.py
```

**Features:**
- Text-based menu system
- Department filtering
- Course search functionality
- Detailed course information display
- Statistics and summaries

## Technology Stack

- **Backend**: FastAPI, Python 3.11+
- **Frontend**: Bootstrap 5, Jinja2 templates
- **Data Models**: Pydantic for validation and serialization
- **APIs**: Google Sheets API, Huayca REST API
- **Documentation**: Automatic OpenAPI/Swagger generation
- **Authentication**: HTTP Basic Auth (expandable to JWT/OAuth)
- **Development**: Uvicorn ASGI server with hot reload

## Data Sources and Coverage

### Current Data Status (as of June 2025)
- **📊 1,240 materias_equipo records** from Google Sheets
- **👥 591 designaciones_docentes records** from Google Sheets  
- **📚 546 materias from Huayca API**
- **🎯 341 unique courses detected**
- **✅ 100% faculty detail matching**
- **🔗 94.7% Huayca academic data enrichment**

### Data Flow
1. **Google Sheets**: Raw assignment and faculty data
2. **Course Detection**: Algorithm groups assignments into unique courses
3. **Faculty Enrichment**: Personal and professional details added
4. **Huayca Integration**: Academic course information from university system
5. **API Serving**: REST endpoints and web interface

## Data Model

### Core Entities

- **Course**: Unique course identified by (Cod SIU + Período)
- **TeamMember**: Faculty member assigned to a course
- **FacultyDetails**: Personal and professional information
- **HuaycaCourseDetails**: Academic course information

### Key Features

- **Automatic Team Detection**: Groups assignments by course code and period
- **Data Enrichment**: 100% faculty matching, 95%+ academic data coverage
- **Flexible Filtering**: Multiple criteria for course discovery
- **Rich Properties**: Computed properties for easy access to derived data

## Testing

### Run Integration Tests

```bash
python -m pytest tests/test_integration.py -v
```

### Run Quick Tests

```bash
python tests/test_quick.py
```

### Test Results

The system has been thoroughly tested with real API data:
- ✅ 341 unique courses detected from 1,240 assignments
- ✅ 100% faculty detail enrichment
- ✅ 94.7% Huayca data enrichment
- ✅ All 13 integration tests passing

See `docs/TEST_RESULTS.md` for detailed test results.

## Development

### Local Development Setup

1. **Clone and setup environment:**
```bash
git clone <repository-url>
cd redesignaciones-crub
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. **Start development server:**
```bash
uvicorn src.crub_courses.ui.fastapi_app:app --reload --host 0.0.0.0 --port 8000
```

3. **Access development tools:**
- **Application**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Admin Panel**: http://localhost:8000/admin

### Code Organization

- **`src/crub_courses/models/`**: Pydantic data models with validation
- **`src/crub_courses/api/`**: External API clients and factories
- **`src/crub_courses/services/`**: Business logic and algorithms
- **`src/crub_courses/ui/`**: User interface applications

### Key Design Principles

1. **Separation of Concerns**: Clear separation between data, business logic, and UI
2. **Type Safety**: Full type hints and Pydantic validation
3. **Error Handling**: Comprehensive error handling and logging
4. **Testability**: Modular design enables easy testing
5. **Extensibility**: Plugin-style architecture for new data sources

### Adding New Features

1. **New API Endpoint**: Add route to `fastapi_app.py`
2. **New Data Source**: Add client in `api/`, update models if needed
3. **New UI Page**: Create template in `templates/`, add route
4. **New Analysis**: Extend `CourseTeamService` with new methods
5. **New Filters**: Add to UI applications and service layer

### Production Deployment

**Environment Variables:**
```bash
# Set these for production
FASTAPI_SECRET_KEY=your-secret-key
ADMIN_USERNAME=your-admin-user
ADMIN_PASSWORD=your-secure-password
```

**Docker Deployment:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "src.crub_courses.ui.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

The system uses environment variables for secure configuration. Copy `.env.example` to `.env` and update with your credentials:

```bash
cp .env.example .env
```

**Required variables:**
- `GOOGLE_SHEETS_BASE_URL`: Google Apps Script deployment URL
- `GOOGLE_SHEETS_SECRET`: Authentication secret for Google Sheets
- `HUAYCA_BASE_URL`: Huayca API endpoint (usually default is fine)
- `HUAYCA_USERNAME`: Your Huayca API username
- `HUAYCA_PASSWORD`: Your Huayca API password
- `ADMIN_USERNAME`: FastAPI admin username (default: admin)
- `ADMIN_PASSWORD`: FastAPI admin password (change in production!)

**Optional variables:**
- `FASTAPI_SECRET_KEY`: Secret key for FastAPI sessions
- `DEBUG`: Enable debug mode (true/false)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)

## Performance

- **Data Loading**: ~60 seconds for full refresh from all APIs
- **Memory Usage**: Efficient caching and lookup structures
- **Scalability**: O(n) algorithms for most operations
- **Caching**: Built-in caching for improved response times

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run the test suite: `pytest`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues, please contact:
- Email: dev@crub.uncoma.edu.ar
- GitHub Issues: [Create an issue](https://github.com/crub/redesignaciones-crub/issues)

## Changelog

### Version 1.1.0 (2025-06-29)
- **NEW**: FastAPI REST API with comprehensive endpoints
- **NEW**: Modern web interface with Bootstrap 5 styling
- **NEW**: Admin panel with authentication and data management
- **NEW**: Interactive API documentation (Swagger UI + ReDoc)
- **NEW**: Production-ready authentication system
- **IMPROVED**: Enhanced filtering with period enum support
- **IMPROVED**: Better error handling and logging
- **IMPROVED**: Responsive design for mobile devices

### Version 1.0.0 (2025-06-29)
- Initial release
- Complete data integration from Google Sheets and Huayca APIs
- Streamlit and console interfaces
- Comprehensive test suite
- Full documentation
