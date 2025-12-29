#!/usr/bin/env python3
# Fix all remaining emoji issues in file icons map

# Read file
with open('static/client_portal.html', 'rb') as f:
    content = f.read()

count = 0

# Picture frame: ðŸ–¼ï¸ -> 🖼️
# Bytes: c3 b0 c5 b8 e2 80 93 c2 bc c3 af c2 b8 c2 8f
if b'\xc3\xb0\xc5\xb8\xe2\x80\x93\xc2\xbc\xc3\xaf\xc2\xb8\xc2\x8f' in content:
    before = content.count(b'\xc3\xb0\xc5\xb8\xe2\x80\x93\xc2\xbc\xc3\xaf\xc2\xb8\xc2\x8f')
    content = content.replace(b'\xc3\xb0\xc5\xb8\xe2\x80\x93\xc2\xbc\xc3\xaf\xc2\xb8\xc2\x8f', b'\xf0\x9f\x96\xbc\xef\xb8\x8f')
    count += before
    print(f"Fixed {before} picture frame emojis")

# Video camera: ðŸŽ¥ -> 🎥
# Need to find the byte pattern
idx = content.find(b"'mp4':")
if idx > 0:
    bytes_after = content[idx+6:idx+20]
    print(f"\nBytes after 'mp4:': {' '.join(f'{b:02x}' for b in bytes_after)}")

# Music note: ðŸŽµ -> 🎵  
idx = content.find(b"'mp3':")
if idx > 0:
    bytes_after = content[idx+6:idx+20]
    print(f"Bytes after 'mp3:': {' '.join(f'{b:02x}' for b in bytes_after)}")

# Spreadsheet icon: 📝Š -> 📊
if b'\xf0\x9f\x93\x9d\xc5\xa0' in content:
    before = content.count(b'\xf0\x9f\x93\x9d\xc5\xa0')
    content = content.replace(b'\xf0\x9f\x93\x9d\xc5\xa0', b'\xf0\x9f\x93\x8a')
    count += before
    print(f"Fixed {before} spreadsheet emojis")

# Package/zip icon: 📝¦ -> 📦
if b'\xf0\x9f\x93\x9d\xc2\xa6' in content:
    before = content.count(b'\xf0\x9f\x93\x9d\xc2\xa6')
    content = content.replace(b'\xf0\x9f\x93\x9d\xc2\xa6', b'\xf0\x9f\x93\xa6')
    count += before
    print(f"Fixed {before} package emojis")

# Text file icon: 📝ƒ -> 📃
if b'\xf0\x9f\x93\x9d\xc6\x92' in content:
    before = content.count(b'\xf0\x9f\x93\x9d\xc6\x92')
    content = content.replace(b'\xf0\x9f\x93\x9d\xc6\x92', b'\xf0\x9f\x93\x83')
    count += before
    print(f"Fixed {before} text file emojis")

# Default document icon: 📝„ -> 📄
if b'\xf0\x9f\x93\x9d\xe2\x80\x9e' in content:
    before = content.count(b'\xf0\x9f\x93\x9d\xe2\x80\x9e')
    content = content.replace(b'\xf0\x9f\x93\x9d\xe2\x80\x9e', b'\xf0\x9f\x93\x84')
    count += before
    print(f"Fixed {before} default document emojis")

# Write back
with open('static/client_portal.html', 'wb') as f:
    f.write(content)

print(f"\nTotal emojis fixed: {count}")
