import io
with io.open('plans/06-admin-dashboard.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_css = False
css_lines = []
for i, line in enumerate(lines):
    if line.strip().startswith('### 4. static/style.css'):
        in_css = True
    if in_css and line.strip() == '`css':
        for j in range(i+1, len(lines)):
            if lines[j].strip() == '`':
                break
            css_lines.append(lines[j])
        break

if css_lines:
    with io.open('static/style.css', 'a', encoding='utf-8') as f:
        f.write('\n\n' + ''.join(css_lines))
    print('CSS appended.')

in_md = False
md_lines = []
for i, line in enumerate(lines):
    if line.strip().startswith('### 5. README.md'):
        in_md = True
    if in_md and line.strip() == '`markdown':
        for j in range(i+1, len(lines)):
            if lines[j].strip() == '`':
                break
            md_lines.append(lines[j])
        break

if md_lines:
    with io.open('README.md', 'a', encoding='utf-8') as f:
        f.write('\n\n' + ''.join(md_lines))
    print('README appended.')
