import re

with open("frontend/src/index.css", "r", encoding="utf-8") as f:
    css = f.read()

nav_pattern = r'\.nav-item\s*\{[^}]+\}'
new_nav = """.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 1rem;
  border-radius: 0.375rem;
  color: var(--text-secondary);
  transition: all 0.15s;
  font-size: 0.9rem;
}
.nav-item:hover {
  background-color: rgba(20, 184, 166, 0.06);
  color: var(--text-primary);
  text-decoration: none;
}
.nav-item.active {
  background-color: rgba(20, 184, 166, 0.10);
  color: var(--text-primary);
}
.nav-item.active svg {
  color: var(--accent);
}"""

css = re.sub(nav_pattern + r'\s*\.nav-item:hover\s*\{[^}]+\}\s*\.nav-item\.active\s*\{[^}]+\}', new_nav, css)


input_pattern = r'\.input-field\s*\{[^}]+\}'
new_input = """.input-field {
  width: 100%;
  padding: 0.65rem 0.875rem;
  background-color: #0F151C;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  color: var(--text-primary);
  font-family: inherit;
  transition: border-color 0.15s, box-shadow 0.15s;
}
:root.light .input-field {
  background-color: var(--bg-surface);
}"""

css = re.sub(input_pattern, new_input, css)

with open("frontend/src/index.css", "w", encoding="utf-8") as f:
    f.write(css)

print("Nav & Input styles patched.")
