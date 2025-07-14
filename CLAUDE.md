# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based portfolio website that showcases projects, skills, and timeline information. The application uses a template-based architecture with data stored in JSON files.

## Common Commands

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py

# Run production server (Heroku deployment)
gunicorn app:app
```

### Frontend Dependencies
```bash
# Install frontend dependencies (Bootstrap 3.3.6, React 15.1.0)
bower install
```

## Architecture

### Application Structure
- **app.py**: Main Flask application with route handlers and error handlers
- **templates/**: Jinja2 HTML templates organized by type
  - **base.html**: Main base template with common layout
  - **components/**: Reusable template components (navbar, etc.)
  - **pages/**: Individual page templates
  - **errors/**: Error page templates
- **static/**: Static assets (CSS, JS, images, data files)
- **static/data/**: JSON data files for dynamic content

### Key Components

#### Data Management
- **projects.json**: Array of project objects with title, description, technologies, github, and demo links
- **skills.json**: Nested object with skill categories and proficiency levels (1-5 scale)
- **timeline.json**: Timeline/experience data structure

#### Route Structure
- `/`: Home page with skills display
- `/timeline`: Timeline/experience page
- `/projects`: Projects showcase page
- `/skills`: Skills visualization page
- `/blog`: Redirects to external WordPress blog
- `/project/<project_id>`: Project detail API endpoint (placeholder)

#### Error Handling
Comprehensive error handlers for 400, 403, 404, and 500 status codes, all rendering through `error.html` template.

### Data File Structure

#### Skills Data Format
```json
{
  "skills": [
    {
      "category": "Category Name",
      "items": [
        {"name": "Skill Name", "proficiency": 1-5}
      ]
    }
  ]
}
```

#### Projects Data Format
```json
[
  {
    "title": "Project Title",
    "description": "Project description",
    "technologies": ["Tech1", "Tech2"],
    "github": "github_url",
    "demo": "demo_url"
  }
]
```

## Development Notes

- The application loads JSON data at startup and keeps it in memory
- Vietnamese comments are present in the codebase
- Debug mode is enabled in development (`app.run(debug=True)`)
- Production deployment uses Gunicorn via Procfile for Heroku
- Frontend uses Bootstrap 3.3.6 and React 15.1.0 via Bower

## Template Structure

The templates follow Flask best practices:
- **base.html**: Contains the main HTML structure, head, and body layout
- **components/**: Reusable template fragments (navbar, footer, etc.)
- **pages/**: Individual page templates that extend base.html
- **errors/**: Error page templates for different HTTP status codes

All page templates extend `base.html` and define their content in the `{% block content %}` section.