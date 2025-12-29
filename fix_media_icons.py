#!/usr/bin/env python3
# Fix video and music icon emojis

# Read file
with open('static/client_portal.html', 'rb') as f:
    content = f.read()

count = 0

# Video camera: ðŸŽ¥ -> 🎥 
# Bytes: c3 b0 c5 b8 c5 bd c2 a5
if b'\xc3\xb0\xc5\xb8\xc5\xbd\xc2\xa5' in content:
    before = content.count(b'\xc3\xb0\xc5\xb8\xc5\xbd\xc2\xa5')
    content = content.replace(b'\xc3\xb0\xc5\xb8\xc5\xbd\xc2\xa5', b'\xf0\x9f\x8e\xa5')
    count += before
    print(f"Fixed {before} video camera emojis")

# Music note: ðŸŽµ -> 🎵
# Bytes: c3 b0 c5 b8 c5 bd c2 b5
if b'\xc3\xb0\xc5\xb8\xc5\xbd\xc2\xb5' in content:
    before = content.count(b'\xc3\xb0\xc5\xb8\xc5\xbd\xc2\xb5')
    content = content.replace(b'\xc3\xb0\xc5\xb8\xc5\xbd\xc2\xb5', b'\xf0\x9f\x8e\xb5')
    count += before
    print(f"Fixed {before} music note emojis")

# Write back
with open('static/client_portal.html', 'wb') as f:
    f.write(content)

print(f"\nTotal emojis fixed: {count}")
print("All file icon emojis fixed!")
