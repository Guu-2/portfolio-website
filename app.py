from flask import Flask, render_template, request, jsonify ,redirect
import json
import os
import logging
import re
import time
import hashlib
from datetime import datetime
from functools import wraps
from dotenv import load_dotenv
import openai
import anthropic
import google.generativeai as genai
import tiktoken

# Load environment variables
load_dotenv()

# ========== SECURITY MIDDLEWARE ==========
class SecurityMiddleware:
    def __init__(self):
        self.request_counts = {}
        self.blocked_ips = set()
        self.suspicious_patterns = [
            "ignore previous",
            "system:",
            "assistant:",
            "new instructions",
            "forget everything",
            "jailbreak",
            "prompt injection",
            "override",
            "admin mode"
        ]
    
    def rate_limit(self, max_requests=10, window=60):
        """Rate limiting decorator"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                client_ip = request.remote_addr
                current_time = time.time()
                
                # Check if IP is blocked
                if client_ip in self.blocked_ips:
                    logging.warning(f"Blocked IP attempted access: {client_ip}")
                    return jsonify({"error": "Access denied"}), 429
                
                # Initialize or clean old entries
                if client_ip not in self.request_counts:
                    self.request_counts[client_ip] = []
                
                # Remove old requests outside window
                self.request_counts[client_ip] = [
                    req_time for req_time in self.request_counts[client_ip]
                    if current_time - req_time < window
                ]
                
                # Check rate limit
                if len(self.request_counts[client_ip]) >= max_requests:
                    logging.warning(f"Rate limit exceeded for IP: {client_ip}")
                    return jsonify({"error": "Rate limit exceeded. Please wait before sending more messages."}), 429
                
                # Add current request
                self.request_counts[client_ip].append(current_time)
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def validate_input(self, message):
        """Input validation and sanitization"""
        if not message or not isinstance(message, str):
            raise ValueError("Invalid message format")
        
        # Length check
        if len(message) > 1000:
            raise ValueError("Message too long (max 1000 characters)")
        
        # Check for suspicious patterns
        message_lower = message.lower()
        for pattern in self.suspicious_patterns:
            if pattern in message_lower:
                logging.warning(f"Suspicious pattern detected: {pattern} from IP: {request.remote_addr}")
                raise ValueError("Message contains prohibited content")
        
        # Check for excessive special characters
        special_char_count = sum(1 for char in message if not char.isalnum() and char not in ' .,!?-')
        if special_char_count > len(message) * 0.3:
            logging.warning(f"Excessive special characters from IP: {request.remote_addr}")
            raise ValueError("Message contains too many special characters")
        
        # Sanitize
        return message.strip()
    
    def log_request(self, message, response_type="normal"):
        """Secure request logging"""
        client_ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Hash sensitive data
        message_hash = hashlib.sha256(message.encode()).hexdigest()[:16]
        
        log_entry = {
            "timestamp": time.time(),
            "ip": client_ip,
            "message_hash": message_hash,
            "message_length": len(message),
            "response_type": response_type,
            "user_agent": user_agent[:50]  # Truncate
        }
        
        logging.info(f"Chat request: {log_entry}")

# Initialize security middleware
security = SecurityMiddleware()

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

# ========== LLM INTEGRATION ==========
class LLMProvider:
    """Base class for LLM providers"""
    
    def __init__(self):
        self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', 500))
        self.temperature = float(os.getenv('OPENAI_TEMPERATURE', 0.7))
        self.max_context_length = int(os.getenv('CHATBOT_MAX_CONTEXT_LENGTH', 2000))
    
    def count_tokens(self, text, model="gpt-3.5-turbo"):
        """Count tokens in text"""
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except:
            # Fallback: approximate token count
            return len(text.split()) * 1.3
    
    def truncate_context(self, context, max_tokens=1500):
        """Truncate context to fit within token limits"""
        if self.count_tokens(context) <= max_tokens:
            return context
        
        # Split by sections and keep most relevant
        sections = context.split('\n\n')
        result = ""
        for section in sections:
            if self.count_tokens(result + section) <= max_tokens:
                result += section + "\n\n"
            else:
                break
        return result.strip()

class OpenAIProvider(LLMProvider):
    """OpenAI GPT integration"""
    
    def __init__(self):
        super().__init__()
        self.client = None
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
    
    def is_available(self):
        return self.client is not None
    
    def generate_response(self, prompt, context=""):
        """Generate response using OpenAI GPT"""
        if not self.is_available():
            raise Exception("OpenAI API key not configured")
        
        # Truncate context if too long
        context = self.truncate_context(context)
        
        messages = [
            {
                "role": "system",
                "content": f"""You are Guu's portfolio assistant. You help visitors learn about Guu's projects, skills, and experience.

IMPORTANT GUIDELINES:
- Always answer in a friendly, professional tone
- Base your responses on the provided context data
- If asked about something not in the context, politely redirect to available topics
- Keep responses concise but informative
- Use markdown formatting for better readability
- Always refer to the person as "Guu" in third person

AVAILABLE CONTEXT DATA:
{context}

Remember: You can only discuss information provided in the context above."""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"OpenAI API error: {str(e)}")

class AnthropicProvider(LLMProvider):
    """Anthropic Claude integration"""
    
    def __init__(self):
        super().__init__()
        self.client = None
        self.model = os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
    
    def is_available(self):
        return self.client is not None
    
    def generate_response(self, prompt, context=""):
        """Generate response using Anthropic Claude"""
        if not self.is_available():
            raise Exception("Anthropic API key not configured")
        
        # Truncate context if too long
        context = self.truncate_context(context)
        
        system_prompt = f"""You are Guu's portfolio assistant. You help visitors learn about Guu's projects, skills, and experience.

IMPORTANT GUIDELINES:
- Always answer in a friendly, professional tone
- Base your responses on the provided context data
- If asked about something not in the context, politely redirect to available topics
- Keep responses concise but informative
- Use markdown formatting for better readability
- Always refer to the person as "Guu" in third person

AVAILABLE CONTEXT DATA:
{context}

Remember: You can only discuss information provided in the context above."""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text.strip()
        except Exception as e:
            logging.error(f"Anthropic API error: {str(e)}")
            raise Exception(f"Anthropic API error: {str(e)}")

class GeminiProvider(LLMProvider):
    """Google Gemini integration"""
    
    def __init__(self):
        super().__init__()
        self.client = None
        self.model = os.getenv('GEMINI_MODEL', 'gemini-pro')
        
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.model)
    
    def is_available(self):
        return self.client is not None
    
    def generate_response(self, prompt, context=""):
        """Generate response using Google Gemini"""
        if not self.is_available():
            raise Exception("Gemini API key not configured")
        
        # Truncate context if too long
        context = self.truncate_context(context)
        
        full_prompt = f"""You are Guu's portfolio assistant. You help visitors learn about Guu's projects, skills, and experience.

IMPORTANT GUIDELINES:
- Always answer in a friendly, professional tone
- Base your responses on the provided context data
- If asked about something not in the context, politely redirect to available topics
- Keep responses concise but informative
- Use markdown formatting for better readability
- Always refer to the person as "Guu" in third person

AVAILABLE CONTEXT DATA:
{context}

Remember: You can only discuss information provided in the context above.

USER QUESTION: {prompt}

RESPONSE:"""
        
        try:
            response = self.client.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
            )
            
            return response.text.strip()
        except Exception as e:
            logging.error(f"Gemini API error: {str(e)}")
            raise Exception(f"Gemini API error: {str(e)}")

# ========== CHATBOT FUNCTIONALITY ==========
class PortfolioChatbot:
    """Chatbot that answers questions based on portfolio data"""
    
    def __init__(self):
        self.mode = os.getenv('CHATBOT_MODE', 'hybrid')  # local, openai, anthropic, hybrid
        self.fallback_enabled = os.getenv('CHATBOT_FALLBACK_ENABLED', 'true').lower() == 'true'
        
        # Initialize LLM providers
        self.openai_provider = OpenAIProvider()
        self.anthropic_provider = AnthropicProvider()
        self.gemini_provider = GeminiProvider()
        
        # Determine which provider to use
        self.llm_provider = None
        if self.mode == 'openai' and self.openai_provider.is_available():
            self.llm_provider = self.openai_provider
        elif self.mode == 'anthropic' and self.anthropic_provider.is_available():
            self.llm_provider = self.anthropic_provider
        elif self.mode == 'gemini' and self.gemini_provider.is_available():
            self.llm_provider = self.gemini_provider
        elif self.mode == 'hybrid':
            # Prefer Gemini (free), fallback to OpenAI, then Anthropic
            if self.gemini_provider.is_available():
                self.llm_provider = self.gemini_provider
            elif self.openai_provider.is_available():
                self.llm_provider = self.openai_provider
            elif self.anthropic_provider.is_available():
                self.llm_provider = self.anthropic_provider
        self.responses = {
            'greeting': [
                "Hello! I'm Guu's portfolio assistant. I can help you learn about his projects, skills, and experience.",
                "Hi there! I'm here to help you explore Guu's portfolio. What would you like to know?",
                "Welcome! I can tell you about Guu's projects, skills, timeline, and experience. How can I help?"
            ],
            'projects': [
                "Let me tell you about Guu's projects...",
                "Here are the projects Guu has worked on:",
                "Guu has developed several interesting projects:"
            ],
            'skills': [
                "Here are Guu's technical skills:",
                "Guu has expertise in the following areas:",
                "Let me break down Guu's skills by category:"
            ],
            'timeline': [
                "Here's Guu's professional journey:",
                "Let me walk you through Guu's career timeline:",
                "Here's how Guu's career has progressed:"
            ],
            'contact': [
                "You can reach Guu through these channels:",
                "Here's how to get in touch with Guu:",
                "Guu is available on these platforms:"
            ],
            'default': [
                "I'm not sure about that. I can help you with information about Guu's projects, skills, timeline, or contact details.",
                "I can tell you about Guu's projects, skills, experience, or how to contact him. What interests you?",
                "I specialize in Guu's portfolio information. Ask me about his projects, skills, or professional journey!"
            ]
        }
    
    def detect_intent(self, message):
        """Detect user intent from message"""
        message_lower = message.lower()
        
        # Greeting patterns
        greeting_patterns = [
            r'\b(hi|hello|hey|greetings|good\s+(morning|afternoon|evening))\b',
            r'\b(chào|xin chào|hello|hi)\b'
        ]
        
        # Project patterns
        project_patterns = [
            r'\b(projects?|works?|portfolio|what.*(built|made|created|developed))\b',
            r'\b(dự án|project|công việc|làm gì)\b'
        ]
        
        # Skills patterns
        skill_patterns = [
            r'\b(skills?|technologies?|expertise|proficiency|languages?|frameworks?)\b',
            r'\b(kỹ năng|công nghệ|ngôn ngữ|framework|skill)\b'
        ]
        
        # Timeline patterns
        timeline_patterns = [
            r'\b(timeline|experience|career|journey|history|background)\b',
            r'\b(kinh nghiệm|quá trình|sự nghiệp|timeline|lịch sử)\b'
        ]
        
        # Contact patterns
        contact_patterns = [
            r'\b(contact|reach|email|phone|social|github|linkedin)\b',
            r'\b(liên hệ|contact|email|github|linkedin)\b'
        ]
        
        # Check patterns
        for pattern in greeting_patterns:
            if re.search(pattern, message_lower):
                return 'greeting'
        
        for pattern in project_patterns:
            if re.search(pattern, message_lower):
                return 'projects'
        
        for pattern in skill_patterns:
            if re.search(pattern, message_lower):
                return 'skills'
        
        for pattern in timeline_patterns:
            if re.search(pattern, message_lower):
                return 'timeline'
        
        for pattern in contact_patterns:
            if re.search(pattern, message_lower):
                return 'contact'
        
        return 'default'
    
    def build_portfolio_context(self):
        """Build comprehensive context from portfolio data"""
        context = "# Guu's Portfolio Information\n\n"
        
        # Add projects context
        if projects:
            context += "## Projects\n"
            for project in projects:
                context += f"### {project['title']}\n"
                context += f"Description: {project['description']}\n"
                context += f"Technologies: {', '.join(project['technologies'])}\n"
                if project.get('github'):
                    context += f"GitHub: {project['github']}\n"
                if project.get('demo'):
                    context += f"Demo: {project['demo']}\n"
                context += "\n"
        
        # Add skills context
        if skills:
            context += "## Skills\n"
            for category in skills:
                context += f"### {category['category']}\n"
                for skill in category['items']:
                    context += f"- {skill['name']}: {skill['proficiency']}/5 proficiency\n"
                context += "\n"
        
        # Add timeline context
        if timeline_data:
            context += "## Career Timeline\n"
            for event in sorted(timeline_data, key=lambda x: x['year'], reverse=True):
                context += f"### {event['year']} - {event['title']}\n"
                context += f"{event['description']}\n"
                if event.get('link'):
                    context += f"Link: {event['link']}\n"
                context += "\n"
        
        # Add contact information
        context += "## Contact Information\n"
        context += "- GitHub: https://github.com/yourusername\n"
        context += "- LinkedIn: https://linkedin.com/in/yourusername\n"
        context += "- Blog: https://guutran.wordpress.com\n"
        context += "- Email: Available through social media platforms\n\n"
        
        return context
    
    def generate_llm_response(self, query):
        """Generate response using LLM"""
        if not self.llm_provider:
            raise Exception("No LLM provider available")
        
        context = self.build_portfolio_context()
        
        try:
            response_text = self.llm_provider.generate_response(query, context)
            return {
                'text': response_text,
                'suggestions': [
                    'Tell me more about a specific project',
                    'What technologies does Guu use most?',
                    'How can I contact Guu?',
                    'What is Guu\'s experience level?'
                ]
            }
        except Exception as e:
            logging.error(f"LLM response error: {str(e)}")
            raise e
    
    def generate_response(self, intent, query=None):
        """Generate response based on intent and data"""
        import random
        
        # Try LLM first if available and not in local mode
        if self.mode != 'local' and self.llm_provider and query:
            try:
                llm_response = self.generate_llm_response(query)
                return llm_response
            except Exception as e:
                logging.warning(f"LLM failed, falling back to local: {str(e)}")
                if not self.fallback_enabled:
                    return {
                        'text': 'I apologize, but I\'m having trouble processing your request right now. Please try again later.',
                        'suggestions': ['Tell me about projects', 'What are your skills?']
                    }
        
        # Fallback to local responses
        if intent == 'greeting':
            return {
                'text': random.choice(self.responses['greeting']),
                'suggestions': ['Tell me about projects', 'What skills do you have?', 'Show me your timeline', 'How can I contact you?']
            }
        
        elif intent == 'projects':
            response_text = random.choice(self.responses['projects'])
            project_info = []
            
            for project in projects:
                project_details = f"**{project['title']}**\n{project['description']}\n"
                project_details += f"Technologies: {', '.join(project['technologies'])}"
                if project.get('github'):
                    project_details += f"\n[GitHub]({project['github']})"
                if project.get('demo'):
                    project_details += f" | [Demo]({project['demo']})"
                project_info.append(project_details)
            
            return {
                'text': response_text,
                'data': project_info,
                'suggestions': ['Tell me more about a specific project', 'What technologies do you use?', 'Show me your skills']
            }
        
        elif intent == 'skills':
            response_text = random.choice(self.responses['skills'])
            skill_info = []
            
            for category in skills:
                category_text = f"**{category['category']}:**\n"
                for skill in category['items']:
                    proficiency_stars = '⭐' * skill['proficiency']
                    category_text += f"• {skill['name']}: {proficiency_stars} ({skill['proficiency']}/5)\n"
                skill_info.append(category_text)
            
            return {
                'text': response_text,
                'data': skill_info,
                'suggestions': ['Tell me about your projects', 'What is your experience?', 'How can I contact you?']
            }
        
        elif intent == 'timeline':
            response_text = random.choice(self.responses['timeline'])
            timeline_info = []
            
            for event in sorted(timeline_data, key=lambda x: x['year'], reverse=True):
                event_text = f"**{event['year']}** - {event['title']}\n{event['description']}"
                if event.get('link'):
                    event_text += f"\n[Learn more]({event['link']})"
                timeline_info.append(event_text)
            
            return {
                'text': response_text,
                'data': timeline_info,
                'suggestions': ['Tell me about your projects', 'What are your skills?', 'How can I contact you?']
            }
        
        elif intent == 'contact':
            contact_info = [
                "**GitHub:** [github.com/yourusername](https://github.com/yourusername)",
                "**LinkedIn:** [linkedin.com/in/yourusername](https://linkedin.com/in/yourusername)",
                "**Email:** Contact through social media",
                "**Blog:** [guutran.wordpress.com](https://guutran.wordpress.com)"
            ]
            
            return {
                'text': random.choice(self.responses['contact']),
                'data': contact_info,
                'suggestions': ['Tell me about projects', 'What are your skills?', 'Show me your timeline']
            }
        
        else:
            return {
                'text': random.choice(self.responses['default']),
                'suggestions': ['Show me projects', 'What skills do you have?', 'Tell me about your experience', 'How can I contact you?']
            }

# Initialize chatbot
chatbot = PortfolioChatbot()

@app.route('/api/chat', methods=['POST'])
@security.rate_limit(max_requests=10, window=60)
def chat():
    """Handle chatbot messages with security"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        # Security validation
        try:
            user_message = security.validate_input(data['message'])
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        # Log request securely
        security.log_request(user_message)
        
        # Detect intent and generate response
        intent = chatbot.detect_intent(user_message)
        response = chatbot.generate_response(intent, user_message)
        
        # Log successful response
        logging.info(f"Chatbot response sent - Intent: {intent}, IP: {request.remote_addr}")
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'intent': intent
        })
    
    except Exception as e:
        logging.error(f"Chatbot error: {str(e)}")
        return jsonify({'error': 'I apologize, but I encountered an error. Please try again.'}), 500

@app.route('/api/chat/suggestions')
def chat_suggestions():
    """Get chat suggestions"""
    suggestions = [
        "Tell me about your projects",
        "What skills do you have?",
        "Show me your timeline",
        "How can I contact you?",
        "What technologies do you use?",
        "Tell me about your experience"
    ]
    return jsonify({'suggestions': suggestions})



if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
    app.run(debug=True)