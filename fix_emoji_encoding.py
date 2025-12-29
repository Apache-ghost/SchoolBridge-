import codecs
import re

# Read the file
with open('static/client_portal.html', 'rb') as f:
    data = f.read()

# Decode and re-encode properly
try:
    text = data.decode('utf-8')
except:
    text = data.decode('latin-1')

# Replace all garbled text patterns with proper emojis using simple string replacement
replacements = {
    'âž•': '➕',
    'ðŸ'Ž': '💎',
    '📝¤': '📤',
    '🔍²': '🔲',
    'â˜°': '☰',
    'ðŸ"': '📁',
    'ðŸ•'': '🕒',
    'ðŸ"¤': '📤',
    'ðŸŽ‰': '🎉',
    'ðŸ"²': '🔲',
    'ðŸ"‚': '📂',
    'ðŸ"„': '📄',
    'ðŸ"Š': '📊',
}

for bad, good in replacements.items():
    text = text.replace(bad, good)

# Write back with proper UTF-8
with open('static/client_portal.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('✅ Fixed all emoji encoding in client_portal.html')
