import os
import re

os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract styles
styles = []
def style_replacer(match):
    styles.append(match.group(1))
    return ''

content = re.sub(r'<style>(.*?)</style>', style_replacer, content, flags=re.DOTALL)

with open('static/css/style.css', 'w', encoding='utf-8') as f:
    f.write('\n'.join(styles))

# Insert CSS link in head
content = content.replace('</head>', '    <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/style.css\') }}">\n</head>')

# Extract scripts
scripts = []
def script_replacer(match):
    s = match.group(1)
    if 'window.onerror' in s: # Keep error handler inline
        return match.group(0)
    scripts.append(s)
    return ''

content = re.sub(r'<script>(.*?)</script>', script_replacer, content, flags=re.DOTALL)

js_content = '\n'.join(scripts)
js_content = js_content.replace('\"{{ username }}\"', 'window.APP_CONFIG.username')
js_content = js_content.replace('"{{ \'true\' if is_admin else \'false\' }}" === "true"', 'window.APP_CONFIG.isAdmin')

with open('static/js/main.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

# Insert inline config and JS link before </body>
inline_script = '''
    <script>
        window.APP_CONFIG = {
            username: "{{ username }}",
            isAdmin: "{{ 'true' if is_admin else 'false' }}" === "true"
        };
        window.currentUserIsAdmin = window.APP_CONFIG.isAdmin;
    </script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
'''
content = content.replace('</body>', inline_script)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Optimization extraction complete!')
