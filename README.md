# Seismic Analysis

AI Powered Seismic Activity Dataset Analysis.

## Project Overview

This is a web application designed for analyzing seismic activity datasets using Generative AI.

### Core Technologies
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Data Analysis:** [Pandas](https://pandas.pydata.org/)
- **AI Integration:** [Google Gen AI SDK](https://ai.google.dev/gemini-api/docs/text-generation)
- **Frontend:** Vanilla HTML, CSS, and JavaScript.
- **Web Server:** [Uvicorn](https://www.uvicorn.org/)
- **Language:** Python 3.x
- **Environment Management:** `python-dotenv`

### Architecture
- `app/`: Main source code directory.
    - `main.py`: Entry point for the FastAPI application.
    - `api/`: Contains API route definitions using `APIRouter`.
        - `home.py`: Serves the primary entry point (home page) at `/home`.
    - `services/`: Contains the business logic, data processing, and AI integrations.
        - `dataset.py`: Handles data loading and cleaning logic using Pandas.
        - `graph.py`: Manages graph generation and visualization logic.
        - `llm.py`: Integrates Generative AI models using `async/await`.
    - `core/`: Application configuration and shared dependencies.
        - `config.py`: Environment configuration loader.
    - `static/`: Contains static assets (CSS, JS, images).
        - `css/`:
            - `base.css`: Standard base styles, variables, and resets.
            - `pages/`: Page-specific CSS files (e.g., `home.css`).
        - `js/`:
            - `modules/`: Shared logic and helper functions (ES Modules).
            - `pages/`: Page-specific entry points (e.g., `home.js`).
    - `pages/`: Contains HTML files for each route (e.g., `home.html`).
- `data/`: Contains datasets.
    - `earthquake_data_tsunami.csv`: [Global Earthquake & Tsunami Risk Assessment Dataset](https://www.kaggle.com/datasets/ahmeduzaki/global-earthquake-tsunami-risk-assessment-dataset)

## Getting Started

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)
- `GEMINI_API_KEY` environment variable.

### Installation
1.  **Clone the repository.**
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # On Windows
    source venv/bin/activate  # On Unix/macOS
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application
To start the development server with auto-reload enabled:
```bash
uvicorn app.main:app --reload
```
The application will be accessible at `http://127.0.0.1:8000`. You can access the generated endpoint documentation at `http://127.0.0.1:8000/docs`.

## Development Conventions

- **Path Handling:** Use `pathlib.Path` for all file and directory path operations to ensure cross-platform compatibility.
- **API Routes:** All routes should be defined in `app/api/` using `APIRouter` and included in `app/main.py`.
- **Logic Separation:** Business logic and data processing should reside in the `app/services/` directory.
- **Data Handling:** Use the `data/` directory for all dataset files. Load data using the helper functions in `app/services/dataset.py`.
- **Frontend Assets:**
    - Page-specific logic should live in `static/js/pages/`.
    - Shared logic should live in `static/js/modules/`.
    - Page-specific styles should live in `static/css/pages/`.
    - Base styles and variables should live in `static/css/base.css`.
- **HTML Layout:** HTML files for each page should reside in the `app/pages/` directory.
- **Environment Variables:** Configuration should be managed through `app/core/config.py` using `load_env()`.
- **AI Integration:** Use `app/services/llm.py` for AI logic. All LLM calls should be asynchronous.
