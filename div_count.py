import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

div_stack = 0
for i, line in enumerate(lines):
    opens = len(re.findall(r'<div\b', line))
    closes = len(re.findall(r'</div\b', line))
    div_stack += (opens - closes)
    if i == 500 or i == 1000 or i == 2000 or i == 3000 or i == 3500 or i == len(lines)-1:
        print(f'Line {i+1} stack: {div_stack}')
