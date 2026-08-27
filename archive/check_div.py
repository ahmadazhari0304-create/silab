with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

indent = 0
for i, line in enumerate(lines):
    if 'tab-content' in line:
        print(f'{i+1}: {line.strip()} (Indent: {indent})')
    div_opens = line.count('<div')
    div_closes = line.count('</div')
    indent += div_opens - div_closes

print(f'Final indent: {indent}')
