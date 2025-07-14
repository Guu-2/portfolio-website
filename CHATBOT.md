# Portfolio Chatbot Integration

## Overview

This portfolio website now includes an intelligent chatbot that can answer questions about your projects, skills, timeline, and contact information based on your JSON data files.

## Features

### 🤖 **Smart Responses**
- Analyzes user questions using pattern matching
- Supports both English and Vietnamese queries
- Provides contextual responses based on your portfolio data

### 📊 **Data Integration**
- Reads from `projects.json`, `skills.json`, and `timeline.json`
- Real-time data updates when JSON files change
- Formatted responses with markdown support

### 🎨 **Modern Interface**
- Floating chat button on all pages
- Responsive design for mobile and desktop
- Typing indicators and smooth animations
- Quick suggestion chips for easy interaction

### 🔍 **Intent Recognition**
The chatbot can understand queries about:
- **Projects**: "Tell me about your projects", "What have you built?"
- **Skills**: "What are your skills?", "What technologies do you use?"
- **Timeline**: "Show me your experience", "Tell me about your journey"
- **Contact**: "How can I contact you?", "What's your GitHub?"
- **Greetings**: "Hello", "Hi", "Chào bạn"

## Technical Implementation

### Backend (app.py)

```python
# New chatbot endpoints
@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chatbot messages"""
    # Process user message and return AI response

@app.route('/api/chat/suggestions')
def chat_suggestions():
    """Get suggested questions"""
    # Return list of suggested questions
```

### Frontend (JavaScript)

```javascript
class PortfolioChatbot {
    // Modern chatbot interface
    // Real-time messaging
    // Suggestion chips
    // Typing indicators
}
```

### Styling (CSS)

```css
/* Modern, responsive chatbot UI */
.chatbot-container { /* Floating button */ }
.chatbot-window { /* Chat interface */ }
.message { /* Message styling */ }
```

## Usage Examples

### English Queries
```
User: "Tell me about your projects"
Bot: "Here are the projects Guu has worked on:
      **Image Classification App**
      Ứng dụng phân loại hình ảnh sử dụng CNN.
      Technologies: Python, TensorFlow, OpenCV"

User: "What skills do you have?"
Bot: "Here are Guu's technical skills:
      **Programming Languages:**
      • Python: ⭐⭐⭐⭐⭐ (5/5)
      • Java: ⭐⭐⭐⭐ (4/5)"
```

### Vietnamese Queries
```
User: "Kể về dự án của bạn"
Bot: "Let me tell you about Guu's projects..."

User: "Kỹ năng gì bạn có?"
Bot: "Here are Guu's technical skills..."
```

## Configuration

### Chatbot Settings
Located in `static/js/script.js`:

```javascript
// Chatbot behavior
this.responses = {
    'greeting': [...],
    'projects': [...],
    'skills': [...],
    // Add more response types
}
```

### Styling Customization
Located in `static/css/style.css`:

```css
/* Change chatbot colors */
.chatbot-toggle {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Customize message bubbles */
.message.user .message-content {
    background: #667eea;
}
```

## Data Structure

### Projects Response Format
```json
{
  "text": "Here are the projects Guu has worked on:",
  "data": [
    "**Project Name**\nDescription\nTechnologies: Python, React\n[GitHub](url)"
  ],
  "suggestions": ["Tell me more about a specific project"]
}
```

### Skills Response Format
```json
{
  "text": "Here are Guu's technical skills:",
  "data": [
    "**Programming Languages:**\n• Python: ⭐⭐⭐⭐⭐ (5/5)\n• Java: ⭐⭐⭐⭐ (4/5)"
  ],
  "suggestions": ["Tell me about your projects"]
}
```

## Adding New Intents

### 1. Add Pattern Recognition
```python
# In detect_intent() method
new_patterns = [
    r'\\b(keyword1|keyword2|pattern)\\b',
    r'\\b(từ khóa|pattern tiếng việt)\\b'
]
```

### 2. Add Response Logic
```python
# In generate_response() method
elif intent == 'new_intent':
    response_text = "Your response here..."
    return {
        'text': response_text,
        'data': [...],
        'suggestions': [...]
    }
```

### 3. Add Response Templates
```python
# In __init__() method
self.responses['new_intent'] = [
    "Response option 1",
    "Response option 2",
    "Response option 3"
]
```

## Deployment Considerations

### 1. Static Deployment
- All data is embedded in JSON files
- No external AI API calls required
- Fast responses, no rate limits

### 2. Enhanced Features (Optional)
- Add OpenAI API integration for more complex queries
- Implement conversation memory
- Add analytics tracking

### 3. Performance Optimization
- Implement response caching
- Add request throttling
- Optimize for mobile devices

## Testing

### Manual Testing
1. Open your portfolio website
2. Click the chatbot button (💬)
3. Try these test queries:
   - "Hello"
   - "Tell me about your projects"
   - "What skills do you have?"
   - "Show me your timeline"
   - "How can I contact you?"

### API Testing
```bash
# Test chatbot endpoint
curl -X POST http://localhost:5000/api/chat \\
  -H "Content-Type: application/json" \\
  -d '{"message": "Tell me about your projects"}'
```

## Troubleshooting

### Common Issues

1. **Chatbot not appearing**
   - Check if JavaScript is enabled
   - Verify script.js is loading correctly
   - Check browser console for errors

2. **Responses not working**
   - Verify Flask server is running
   - Check `/api/chat` endpoint is accessible
   - Validate JSON data files

3. **Styling issues**
   - Check CSS file is loading
   - Verify chatbot styles are not overridden
   - Test on different screen sizes

### Debug Mode
Add to `app.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

### Phase 1 (Current)
- [x] Basic intent recognition
- [x] JSON data integration
- [x] Modern UI interface
- [x] Bilingual support

### Phase 2 (Planned)
- [ ] Advanced NLP with spaCy
- [ ] Conversation context memory
- [ ] Analytics dashboard
- [ ] Admin interface for responses

### Phase 3 (Advanced)
- [ ] OpenAI GPT integration
- [ ] Voice input/output
- [ ] Multi-language support
- [ ] Personality customization

## Support

For issues or questions about the chatbot integration:
1. Check the troubleshooting section
2. Review browser console for errors
3. Test API endpoints directly
4. Verify JSON data structure

The chatbot is now fully integrated and ready for deployment! 🚀