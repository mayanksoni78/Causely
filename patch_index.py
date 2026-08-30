import re

with open("frontend/src/index.css", "r", encoding="utf-8") as f:
    css = f.read()

# Replace auth gradients and text gradients
css = re.sub(r'#1e1b4b', 'var(--bg-elevated)', css)
css = re.sub(r'#c4b5fd', 'var(--accent)', css)
css = re.sub(r'#818cf8', 'var(--accent-hover)', css)

# Fix accent2 mapping to info
css = re.sub(r'var\(--accent2\)', 'var(--info)', css)

# Make sure --info is defined in :root
root_match = re.search(r':root\s*\{[^}]+\}', css)
if root_match:
    root_content = root_match.group(0)
    if '--info' not in root_content:
        root_content = root_content.replace('}', '  --info: #38BDF8;\n}')
        css = css[:root_match.start()] + root_content + css[root_match.end():]

# Make sure --info is defined in :root.light
root_light_match = re.search(r':root\.light\s*\{[^}]+\}', css)
if root_light_match:
    root_light_content = root_light_match.group(0)
    if '--info' not in root_light_content:
        root_light_content = root_light_content.replace('--accent2: #8F9779;', '--info: #8F9779;')
        css = css[:root_light_match.start()] + root_light_content + css[root_light_match.end():]

# Fix badge info alpha colors from cyan to teal or blue
css = re.sub(r'rgba\(6,182,212,\.1\)', 'rgba(56, 189, 248, 0.1)', css)
css = re.sub(r'rgba\(6,182,212,\.3\)', 'rgba(56, 189, 248, 0.3)', css)
css = re.sub(r'rgba\(6, 182, 212, 0\.1\)', 'rgba(56, 189, 248, 0.1)', css)
css = re.sub(r'rgba\(6, 182, 212, 0\.2\)', 'rgba(56, 189, 248, 0.2)', css)
css = re.sub(r'rgba\(13,13,31,0\.85\)', 'rgba(17, 24, 32, 0.85)', css) # dark slate
css = re.sub(r'rgba\(10,10,20,0\.95\)', 'rgba(11, 15, 20, 0.95)', css) # darker slate

with open("frontend/src/index.css", "w", encoding="utf-8") as f:
    f.write(css)

print("index.css fully patched")
