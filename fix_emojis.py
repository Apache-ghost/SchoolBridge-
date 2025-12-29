#!/usr/bin/env python3
# Fix emoji encoding in HTML files

import sys

files_to_fix = ['static/client_portal.html', 'static/admin.html']

emoji_map = {
    'â˜ï¸': '☁️',
    'ðŸ"': '🔍',
    'ðŸ'¾': '💾',
    'âž•': '➕',
    'ðŸ"': '📁',
    'ðŸ•'': '🕒',
    'ðŸ"¤': '📤',
    'ðŸ'Ž': '💎',
    'ðŸŽ‰': '🎉',
    'ðŸ"²': '🔲',
    'ðŸ"‚': '📂',
    'ðŸ"„': '📄',
    'ðŸ"Š': '📊',
    'ðŸ"': '📝',
    'ðŸ›¡': '🛡',
    'ðŸ'¥': '👥',
    'â›"': '⛔',
    'â†': '←'
}

for file_path in files_to_fix:
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        for bad, good in emoji_map.items():
            content = content.replace(bad, good)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f'✅ Fixed emojis in {file_path}')
    except Exception as e:
        print(f'❌ Error fixing {file_path}: {e}')

print('\n✅ All emoji encoding fixed!')
