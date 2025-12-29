# Fix emojis using byte-level operations
import os

# Read file as bytes
with open('static/client_portal.html', 'rb') as f:
    content = f.read()

# Define byte patterns for garbled text and correct emoji replacements
# Pattern for diamond: ðŸ'Ž -> 💎
content = content.replace(b'\xc3\xb0\xc5\xb8\xe2\x80\x99\xc5\x8e', b'\xf0\x9f\x92\x8e')
# Pattern for checkmark: âœ" -> ✓
content = content.replace(b'\xc3\xa2\xc5\x93\xe2\x80\x9c', b'\xe2\x9c\x93')
# Pattern for plus: âž• -> ➕
content = content.replace(b'\xc3\xa2\xc5\xbe\xe2\x80\x95', b'\xe2\x9e\x95')
# Pattern for picture: ðŸ–¼ï¸ -> 🖼️
content = content.replace(b'\xc3\xb0\xc5\xb8\xe2\x80\x93\xc2\xbc\xc3\xaf\xc2\xb8\xc2\x8f', b'\xf0\x9f\x96\xbc\xef\xb8\x8f')
# Pattern for document: 📝„ -> 📄  
content = content.replace(b'\xf0\x9f\x93\x9d\xe2\x80\x9e', b'\xf0\x9f\x93\x84')
# Pattern for outbox: ðŸ"¼ -> 📤
content = content.replace(b'\xc3\xb0\xc5\xb8\xe2\x80\x9cðŸ"¼', b'\xf0\x9f\x93\xa4')

# Write back
with open('static/client_portal.html', 'wb') as f:
    f.write(content)

print("Emoji fixes applied!")
