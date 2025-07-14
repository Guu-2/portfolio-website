# Security Middleware for Portfolio Chatbot
import time
import hashlib
from functools import wraps
from flask import request, jsonify
import logging

class SecurityMiddleware:
    def __init__(self, app):
        self.app = app
        self.request_counts = {}
        self.blocked_ips = set()
        self.suspicious_patterns = [
            "ignore previous",
            "system:",
            "assistant:",
            "new instructions",
            "forget everything",
            "jailbreak",
            "prompt injection"
        ]
    
    def rate_limit(self, max_requests=5, window=60):
        """Rate limiting decorator"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                client_ip = request.remote_addr
                current_time = time.time()
                
                # Check if IP is blocked
                if client_ip in self.blocked_ips:
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
                    return jsonify({"error": "Rate limit exceeded"}), 429
                
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
            raise ValueError("Message too long")
        
        # Check for suspicious patterns
        message_lower = message.lower()
        for pattern in self.suspicious_patterns:
            if pattern in message_lower:
                logging.warning(f"Suspicious pattern detected: {pattern}")
                raise ValueError("Invalid message content")
        
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
    
    def detect_anomalies(self, message):
        """Detect potential security threats"""
        threats = []
        
        # Check message length
        if len(message) > 500:
            threats.append("long_message")
        
        # Check for repeated characters
        if any(char * 10 in message for char in "abcdefghijklmnopqrstuvwxyz"):
            threats.append("repeated_chars")
        
        # Check for special characters
        special_char_count = sum(1 for char in message if not char.isalnum() and char != ' ')
        if special_char_count > len(message) * 0.3:
            threats.append("excessive_special_chars")
        
        # Check for multiple languages (simple heuristic)
        if any(ord(char) > 127 for char in message):
            non_ascii_count = sum(1 for char in message if ord(char) > 127)
            if non_ascii_count > len(message) * 0.5:
                threats.append("mixed_languages")
        
        return threats