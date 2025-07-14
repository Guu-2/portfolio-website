from flask import Flask, render_template, request, jsonify ,redirect
import json
import os

app = Flask(__name__)

# Đọc danh sách dự án từ JSON
try:
    with open('static/data/projects.json', 'r') as f:
        projects_data = json.load(f)
    projects = projects_data  # Giả định projects.json là danh sách trực tiếp
except FileNotFoundError:
    projects = []


# Đọc danh sách kỹ năng từ JSON
try:
    with open('static/data/skills.json', 'r') as f:
        skills_data = json.load(f)
    skills = skills_data.get('skills', [])  # Lấy danh sách skills từ key 'skills'
    # print("Skills list:", skills)  # Debug: In danh sách skills
except FileNotFoundError:
    skills = []

# Đọc danh sách timeline từ JSON
try:
    with open('static/data/timeline.json', 'r') as f:
        timeline_data = json.load(f)
except FileNotFoundError:
    timeline_data = []

# ========== ERROR HANDLERS ==========
@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', 
                         error=error,
                         message="Page not found",
                         status=404), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error.html',
                         error=error,
                         message="Internal server error",
                         status=500), 500

@app.errorhandler(403)
def forbidden(error):
    return render_template('error.html',
                         error=error,
                         message="Forbidden access",
                         status=403), 403

@app.errorhandler(400)
def bad_request(error):
    return render_template('error.html',
                         error=error,
                         message="Bad request",
                         status=400), 400


@app.route('/')
def home():
    return render_template('home.html', skills=skills)

@app.route('/timeline')
def timeline_page():
    return render_template('timeline.html', timeline=timeline_data)

@app.route('/projects')
def projects_page():
    return render_template('projects.html', projects=projects)

@app.route('/skills')
def skills_page():
    # print("Skills data:", skills)  # Debug: In giá trị của skills
    # print("Type of skills:", type(skills))  # Debug: Kiểm tra kiểu của skills
    # for category in skills:
    #     print("Category:", category)
    #     print("Type of category.items:", type(category.get('items')))
    return render_template('skills.html', skills=skills)

@app.route('/blog')
def blog_page():
    return redirect("https://guutran.wordpress.com", code=302)

@app.route('/project/<project_id>')
def project_detail(project_id):
    return jsonify({"id": project_id, "message": "Project detail endpoint, to be implemented"})



if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
    app.run(debug=True)