#!/usr/bin/env python3
# Fix the upload icon emoji

# Read file
with open('static/client_portal.html', 'rb') as f:
    content = f.read()

count = 0

# Upload icon: f0 9f 93 9d c2 a4 -> f0 9f 93 a4 (📤)
# This appears to be 📝 (f0 9f 93 9d) + garbled bytes (c2 a4)
if b'\xf0\x9f\x93\x9d\xc2\xa4' in content:
    before = content.count(b'\xf0\x9f\x93\x9d\xc2\xa4')
    content = content.replace(b'\xf0\x9f\x93\x9d\xc2\xa4', b'\xf0\x9f\x93\xa4')
    count += before
    print(f"Fixed {before} upload icon emojis")

# Write back
with open('static/client_portal.html', 'wb') as f:
    f.write(content)

print(f"\nTotal emojis fixed: {count}")
print("All emoji fixes complete!")
