# -*- coding: utf-8 -*-
with open('static/client_portal.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Use unicode escapes for emojis
text = text.replace('\u00e2\u017e\u0095', '\u27a1\ufe0f')  # Plus
text = text.replace('\u00f0\u009f\u0092\u008e', '\U0001f48e')  # Diamond
text = text.replace('\u00e2\u0098\u00b0', '\u2630')  # Menu

# Write back
with open('static/client_portal.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('Done')
