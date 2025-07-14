from flask import Flask, render_template, request, jsonify ,redirect
import json
import os
import logging

app = Flask(__name__)

# ========== DATA VALIDATION ==========
def validate_projects_data(projects):
    """Validate projects.json structure"""
    if not isinstance(projects, list):
        raise ValueError("Projects data must be a list")
    
    required_fields = ['title', 'description', 'technologies']
    for i, project in enumerate(projects):
        if not isinstance(project, dict):
            raise ValueError(f"Project {i} must be a dictionary")
        
        for field in required_fields:
            if field not in project:
                raise ValueError(f"Project {i} missing required field: {field}")
        
        # Validate specific field types
        if not isinstance(project['title'], str) or not project['title'].strip():
            raise ValueError(f"Project {i} title must be a non-empty string")
        
        if not isinstance(project['description'], str) or not project['description'].strip():
            raise ValueError(f"Project {i} description must be a non-empty string")
        
        if not isinstance(project['technologies'], list):
            raise ValueError(f"Project {i} technologies must be a list")
        
        # Optional fields validation
        if 'github' in project and project['github'] and not isinstance(project['github'], str):
            raise ValueError(f"Project {i} github must be a string")
        
        if 'demo' in project and project['demo'] and not isinstance(project['demo'], str):
            raise ValueError(f"Project {i} demo must be a string")

def validate_skills_data(skills_data):
    """Validate skills.json structure"""
    if not isinstance(skills_data, dict):
        raise ValueError("Skills data must be a dictionary")
    
    if 'skills' not in skills_data:
        raise ValueError("Skills data must contain 'skills' key")
    
    skills = skills_data['skills']
    if not isinstance(skills, list):
        raise ValueError("Skills must be a list")
    
    for i, category in enumerate(skills):
        if not isinstance(category, dict):
            raise ValueError(f"Skills category {i} must be a dictionary")
        
        if 'category' not in category:
            raise ValueError(f"Skills category {i} missing 'category' field")
        
        if 'items' not in category:
            raise ValueError(f"Skills category {i} missing 'items' field")
        
        if not isinstance(category['items'], list):
            raise ValueError(f"Skills category {i} items must be a list")
        
        for j, item in enumerate(category['items']):
            if not isinstance(item, dict):
                raise ValueError(f"Skills category {i} item {j} must be a dictionary")
            
            if 'name' not in item or 'proficiency' not in item:
                raise ValueError(f"Skills category {i} item {j} missing required fields")
            
            if not isinstance(item['name'], str) or not item['name'].strip():
                raise ValueError(f"Skills category {i} item {j} name must be a non-empty string")
            
            if not isinstance(item['proficiency'], int) or not (1 <= item['proficiency'] <= 5):
                raise ValueError(f"Skills category {i} item {j} proficiency must be an integer between 1 and 5")

def validate_timeline_data(timeline_data):
    """Validate timeline.json structure"""
    if not isinstance(timeline_data, list):
        raise ValueError("Timeline data must be a list")
    
    required_fields = ['year', 'title', 'description']
    for i, event in enumerate(timeline_data):
        if not isinstance(event, dict):
            raise ValueError(f"Timeline event {i} must be a dictionary")
        
        for field in required_fields:
            if field not in event:
                raise ValueError(f"Timeline event {i} missing required field: {field}")
        
        if not isinstance(event['title'], str) or not event['title'].strip():
            raise ValueError(f"Timeline event {i} title must be a non-empty string")
        
        if not isinstance(event['description'], str) or not event['description'].strip():
            raise ValueError(f"Timeline event {i} description must be a non-empty string")
        
        # Year can be string or number
        if not isinstance(event['year'], (str, int)):
            raise ValueError(f"Timeline event {i} year must be a string or number")
        
        # Optional fields validation
        if 'event_type' in event and event['event_type'] and not isinstance(event['event_type'], str):
            raise ValueError(f"Timeline event {i} event_type must be a string")
        
        if 'icon' in event and event['icon'] and not isinstance(event['icon'], str):
            raise ValueError(f"Timeline event {i} icon must be a string")
        
        if 'link' in event and event['link'] and not isinstance(event['link'], str):
            raise ValueError(f"Timeline event {i} link must be a string")

def load_and_validate_data():
    """Load and validate all JSON data files"""
    global projects, skills, timeline_data
    
    # Load and validate projects
    try:
        with open('static/data/projects.json', 'r', encoding='utf-8') as f:
            projects_data = json.load(f)
        validate_projects_data(projects_data)
        projects = projects_data
        logging.info("Projects data loaded and validated successfully")
    except FileNotFoundError:
        projects = []
        logging.warning("projects.json not found, using empty list")
    except (json.JSONDecodeError, ValueError) as e:
        logging.error(f"Error loading projects.json: {e}")
        projects = []
    
    # Load and validate skills
    try:
        with open('static/data/skills.json', 'r', encoding='utf-8') as f:
            skills_data = json.load(f)
        validate_skills_data(skills_data)
        skills = skills_data.get('skills', [])
        logging.info("Skills data loaded and validated successfully")
    except FileNotFoundError:
        skills = []
        logging.warning("skills.json not found, using empty list")
    except (json.JSONDecodeError, ValueError) as e:
        logging.error(f"Error loading skills.json: {e}")
        skills = []
    
    # Load and validate timeline
    try:
        with open('static/data/timeline.json', 'r', encoding='utf-8') as f:
            timeline_data = json.load(f)
        validate_timeline_data(timeline_data)
        logging.info("Timeline data loaded and validated successfully")
    except FileNotFoundError:
        timeline_data = []
        logging.warning("timeline.json not found, using empty list")
    except (json.JSONDecodeError, ValueError) as e:
        logging.error(f"Error loading timeline.json: {e}")
        timeline_data = []

# Initialize data
load_and_validate_data()


# ========== ERROR HANDLERS ==========
@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/error.html', 
                         error=error,
                         message="Page not found",
                         status=404), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('errors/error.html',
                         error=error,
                         message="Internal server error",
                         status=500), 500

@app.errorhandler(403)
def forbidden(error):
    return render_template('errors/error.html',
                         error=error,
                         message="Forbidden access",
                         status=403), 403

@app.errorhandler(400)
def bad_request(error):
    return render_template('errors/error.html',
                         error=error,
                         message="Bad request",
                         status=400), 400


@app.route('/')
def home():
    return render_template('pages/home.html', skills=skills)

@app.route('/timeline')
def timeline_page():
    return render_template('pages/timeline.html', timeline=timeline_data)

@app.route('/projects')
def projects_page():
    return render_template('pages/projects.html', projects=projects)

@app.route('/skills')
def skills_page():
    # print("Skills data:", skills)  # Debug: In giá trị của skills
    # print("Type of skills:", type(skills))  # Debug: Kiểm tra kiểu của skills
    # for category in skills:
    #     print("Category:", category)
    #     print("Type of category.items:", type(category.get('items')))
    return render_template('pages/skills.html', skills=skills)

@app.route('/blog')
def blog_page():
    return redirect("https://guutran.wordpress.com", code=302)

@app.route('/project/<project_id>')
def project_detail(project_id):
    return jsonify({"id": project_id, "message": "Project detail endpoint, to be implemented"})

# ========== ADMIN ENDPOINTS ==========
@app.route('/admin/reload-data')
def reload_data():
    """Reload and validate data from JSON files"""
    try:
        load_and_validate_data()
        return jsonify({"status": "success", "message": "Data reloaded successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/admin/data/projects', methods=['GET', 'POST'])
def admin_projects():
    """Admin endpoint to view/edit projects data"""
    if request.method == 'GET':
        return jsonify(projects)
    
    elif request.method == 'POST':
        try:
            new_data = request.get_json()
            if not new_data:
                return jsonify({"status": "error", "message": "No data provided"}), 400
            
            # Validate the new data
            validate_projects_data(new_data)
            
            # Save to file
            with open('static/data/projects.json', 'w', encoding='utf-8') as f:
                json.dump(new_data, f, indent=2, ensure_ascii=False)
            
            # Reload data
            load_and_validate_data()
            
            return jsonify({"status": "success", "message": "Projects updated successfully"})
        
        except ValueError as e:
            return jsonify({"status": "error", "message": f"Validation error: {str(e)}"}), 400
        except Exception as e:
            return jsonify({"status": "error", "message": f"Error updating projects: {str(e)}"}), 500

@app.route('/admin/data/skills', methods=['GET', 'POST'])
def admin_skills():
    """Admin endpoint to view/edit skills data"""
    if request.method == 'GET':
        return jsonify({"skills": skills})
    
    elif request.method == 'POST':
        try:
            new_data = request.get_json()
            if not new_data:
                return jsonify({"status": "error", "message": "No data provided"}), 400
            
            # Validate the new data
            validate_skills_data(new_data)
            
            # Save to file
            with open('static/data/skills.json', 'w', encoding='utf-8') as f:
                json.dump(new_data, f, indent=2, ensure_ascii=False)
            
            # Reload data
            load_and_validate_data()
            
            return jsonify({"status": "success", "message": "Skills updated successfully"})
        
        except ValueError as e:
            return jsonify({"status": "error", "message": f"Validation error: {str(e)}"}), 400
        except Exception as e:
            return jsonify({"status": "error", "message": f"Error updating skills: {str(e)}"}), 500

@app.route('/admin/data/timeline', methods=['GET', 'POST'])
def admin_timeline():
    """Admin endpoint to view/edit timeline data"""
    if request.method == 'GET':
        return jsonify(timeline_data)
    
    elif request.method == 'POST':
        try:
            new_data = request.get_json()
            if not new_data:
                return jsonify({"status": "error", "message": "No data provided"}), 400
            
            # Validate the new data
            validate_timeline_data(new_data)
            
            # Save to file
            with open('static/data/timeline.json', 'w', encoding='utf-8') as f:
                json.dump(new_data, f, indent=2, ensure_ascii=False)
            
            # Reload data
            load_and_validate_data()
            
            return jsonify({"status": "success", "message": "Timeline updated successfully"})
        
        except ValueError as e:
            return jsonify({"status": "error", "message": f"Validation error: {str(e)}"}), 400
        except Exception as e:
            return jsonify({"status": "error", "message": f"Error updating timeline: {str(e)}"}), 500



if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
    app.run(debug=True)