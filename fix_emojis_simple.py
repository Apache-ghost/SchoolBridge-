# Fix emojis in client_portal.html
with open('static/client_portal.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the exact garbled text we see
content = content.replace('ðŸ'Ž', '💎')
content = content.replace('âœ"', '✓') 
content = content.replace('âž•', '➕')
content = content.replace('ðŸ–¼ï¸', '🖼️')
content = content.replace('📝„', '📄')
content = content.replace('ðŸ"¼', '📤')

with open('static/client_portal.html', 'w', encoding='utf-8-sig') as f:
    f.write(content)

print("Done!")
