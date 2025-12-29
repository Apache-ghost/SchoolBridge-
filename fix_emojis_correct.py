#!/usr/bin/env python3
# Fix all emoji encoding issues by finding actual byte patterns

# Read file
with open('static/client_portal.html', 'rb') as f:
    content = f.read()

count = 0

# Diamond emoji: c3 b0 c5 b8 e2 80 99 c5 bd -> f0 9f 92 8e (💎)
if b'\xc3\xb0\xc5\xb8\xe2\x80\x99\xc5\xbd' in content:
    before = content.count(b'\xc3\xb0\xc5\xb8\xe2\x80\x99\xc5\xbd')
    content = content.replace(b'\xc3\xb0\xc5\xb8\xe2\x80\x99\xc5\xbd', b'\xf0\x9f\x92\x8e')
    count += before
    print(f"Fixed {before} diamond emojis")

# Plus sign: c3 a2 c5 be e2 80 95 -> e2 9e 95 (➕)
if b'\xc3\xa2\xc5\xbe\xe2\x80\x95' in content:
    before = content.count(b'\xc3\xa2\xc5\xbe\xe2\x80\x95')
    content = content.replace(b'\xc3\xa2\xc5\xbe\xe2\x80\x95', b'\xe2\x9e\x95')
    count += before
    print(f"Fixed {before} plus sign emojis")

# Picture frame: Need to find the pattern
idx = content.find(b'Picture frame')
if idx > 0:
    bytes_before = content[max(0, idx-30):idx]
    print(f"Bytes near 'Picture frame': {' '.join(f'{b:02x}' for b in bytes_before[-20:])}")

# Document icon: Need to find the pattern  
idx = content.find(b'document')
if idx > 0:
    bytes_before = content[max(0, idx-30):idx]
    print(f"Bytes near 'document': {' '.join(f'{b:02x}' for b in bytes_before[-20:])}")

# Write back
with open('static/client_portal.html', 'wb') as f:
    f.write(content)

print(f"\nTotal emojis fixed: {count}")
print("Done!")
