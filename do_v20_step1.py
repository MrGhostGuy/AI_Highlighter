import os, glob, json, subprocess

watermark_py = '# Created by Jeff Hollaway\n'
watermark_html = '<!-- Created by Jeff Hollaway -->\n'

# Get v1.5 commit hash
result = subprocess.run(['git', 'log', '--oneline', '-3'], capture_output=True, text=True)
print('Git log:', result.stdout)
v15_hash = result.stdout.strip().split('\n')[0].split()[0]

# Add watermark to Python files
py_files = glob.glob('*.py') + glob.glob('modules/*.py') + glob.glob('tests/*.py')
modified = []
for f in py_files:
    content = open(f, 'r', encoding='utf-8', errors='replace').read()
    if 'Created by Jeff Hollaway' not in content:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(watermark_py + content)
        modified.append(f)
        print(f'Watermark added to {f}')

# Add watermark to HTML files
for f in glob.glob('output/*.html'):
    content = open(f, 'r', encoding='utf-8', errors='replace').read()
    if 'Created by Jeff Hollaway' not in content:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(watermark_html + content)
        modified.append(f)
        print(f'Watermark added to {f}')

# Add watermark to version.json
vdata = json.load(open('version.json'))
if 'created_by' not in vdata:
    vdata['created_by'] = 'Jeff Hollaway'
    with open('version.json', 'w') as fh:
        json.dump(vdata, fh, indent=4)
    modified.append('version.json')
    print('Watermark added to version.json')

print(f'\nTotal files modified: {len(modified)}')
print('Step 1 complete: Watermarks added')
