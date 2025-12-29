#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix all emoji encoding issues in client_portal.html"""

import codecs

# Read the file
with codecs.open('static/client_portal.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all garbled emojis
replacements = [
    ('\u00f0\u009f\u0092\u008e', '\U0001f48e'),  # Diamond
    ('\u00e2\u009c\u0093', '\u2713'),  # Checkmark
    ('\u00e2\u009e\u0095', '\u2795'),  # Plus sign
    ('\u00f0\u009f\u0096\u00bc\u00ef\u00b8\u008f', '\U0001f5bc\ufe0f'),  # Picture frame
    ('\U0001f4dd\u0084', '\U0001f4c4'),  # Document
    ('\u00f0\u009f\u0093\u00bc', '\U0001f4e4'),  # Outbox tray
]

for old, new in replacements:
    content = content.replace(old, new)

# Write back
with codecs.open('static/client_portal.html', 'w', encoding='utf-8-sig') as f:
    f.write(content)

print("✅ All emoji fixes applied successfully!")
print(f"Replaced {len(replacements)} emoji patterns")
