#!/usr/bin/env python3
# Fix remaining emoji encoding issues

# Read file
with open('static/client_portal.html', 'rb') as f:
    content = f.read()

count = 0

# Plus sign: c3 a2 c5 be e2 80 a2 -> e2 9e 95 (➕)
if b'\xc3\xa2\xc5\xbe\xe2\x80\xa2' in content:
    before = content.count(b'\xc3\xa2\xc5\xbe\xe2\x80\xa2')
    content = content.replace(b'\xc3\xa2\xc5\xbe\xe2\x80\xa2', b'\xe2\x9e\x95')
    count += before
    print(f"Fixed {before} plus sign emojis")

# Search for other patterns by looking at nav icons
idx = content.find(b'My Files')
if idx > 0:
    bytes_before = content[max(0, idx-60):idx]
    print(f"\nBytes near 'My Files':")
    print(' '.join(f'{b:02x}' for b in bytes_before[-40:]))

# Write back
with open('static/client_portal.html', 'wb') as f:
    f.write(content)

print(f"\nTotal emojis fixed: {count}")
