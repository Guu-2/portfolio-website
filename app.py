from flask import Flask, render_template
import json

app = Flask(__name__)

@app.route('/')
def home():
    with open('projects.json', 'r') as f:
        projects = json.load(f)
    return render_template('index.html', projects=projects)


import os
if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))  # Render cung cấp PORT qua biến môi trường
    app.run(host='0.0.0.0', port=port)