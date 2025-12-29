#!/usr/bin/env python3
import sys
import io

# Force UTF-8 for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Read file
with open('static/client_portal.html', 'rb') as f:
    content = f.read()

# Track replacements
replacements_made = 0

# Diamond emoji fix: Find UTF-8 encoded 💎 that was misinterpreted as Windows-1252
# Looking for: C3 B0 C5 B8 E2 80 99 C5 8E (ðŸ'Ž in Windows-1252)
# Replace with: F0 9F 92 8E (💎 in UTF-8)
if b'\xc3\xb0\xc5\xb8\xe2\x80\x99\xc5\x8e' in content:
    content = content.replace(b'\xc3\xb0\xc5\xb8\xe2\x80\x99\xc5\x8e', b'\xf0\x9f\x92\x8e')
    replacements_made += content.count(b'\xf0\x9f\x92\x8e')
    print(f"Fixed diamond emoji")

# Checkmark fix
if b'\xc3\xa2\xc5\x93\xe2\x80\x9c' in content:
    content = content.replace(b'\xc3\xa2\xc5\x93\xe2\x80\x9c', b'\xe2\x9c\x93')
    replacements_made += 1
    print(f"Fixed checkmark")

# Plus sign fix  
if b'\xc3\xa2\xc5\xbe\xe2\x80\x95' in content:
    content = content.replace(b'\xc3\xa2\xc5\xbe\xe2\x80\x95', b'\xe2\x9e\x95')
    replacements_made += 1
    print(f"Fixed plus sign")

# Write back
with open('static/client_portal.html', 'wb') as f:
    f.write(content)

print(f"\nTotal replacements: {replacements_made}")
print("Emoji fixes applied!")
