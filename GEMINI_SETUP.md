# 🤖 Gemini AI Chatbot Setup Guide

## Quick Setup

Your portfolio website now uses Google Gemini AI for intelligent chatbot responses.

### 1. Get Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create new API key
3. Copy the key (format: `AIza...`)

### 2. Local Development
```bash
# Create .env file
echo "GEMINI_API_KEY=your_key_here" > .env

# Test locally
python app.py
```

### 3. Production Deployment

#### Render:
1. Deploy as usual
2. Add in Environment settings:
   - `GEMINI_API_KEY` = your_key_here

#### Vercel:
1. Deploy as usual  
2. Add in Environment Variables:
   - `GEMINI_API_KEY` = your_key_here

## Features

### ✅ Intelligent Responses
- Context-aware answers based on your JSON data
- Natural conversation flow
- Fallback to local responses if API fails

### ✅ Security
- Rate limiting: 10 requests/minute per IP
- Input validation and sanitization
- Secure API key management
- No sensitive data in logs

### ✅ Cost
- **Free**: Google Gemini API free tier
- **1,500 requests/day** limit
- **No credit card** required

## Configuration

Default settings in `.env`:
```bash
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-pro
GEMINI_MAX_TOKENS=500
GEMINI_TEMPERATURE=0.7
```

## Backup

The original local chatbot (pattern-matching) is backed up in:
- **Branch**: `backup/local-chatbot`
- **GitHub**: [View backup](https://github.com/Guu-2/portfolio-website/tree/backup/local-chatbot)

To restore local chatbot:
```bash
git checkout backup/local-chatbot
```

## Testing

Test the chatbot with these questions:
- "Tell me about Guu's projects"
- "What skills does Guu have?"
- "How can I contact Guu?"
- "What is Guu's experience?"

The chatbot will use Gemini AI when available, or fall back to local responses.