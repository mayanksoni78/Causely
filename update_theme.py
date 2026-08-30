import re

with open("frontend/src/index.css", "r", encoding="utf-8") as f:
    css = f.read()

new_root = """:root {
  --bg-main: #0B0F14;       /* Primary Background */
  --bg-surface: #111820;    /* Secondary Background */
  --bg-card: #151D26;       /* Card Background */
  --bg-elevated: #1A2530;   /* Elevated Card */
  --border-color: #263442;  /* Border */
  
  --text-primary: #F1F5F9;
  --text-secondary: #94A3B8;
  --text-muted: #64748B;

  --accent: #14B8A6;        /* Teal Primary Accent */
  --accent-hover: #0D9488;  /* Teal Hover */
  --accent-soft: rgba(20, 184, 166, 0.12); /* Teal Soft */

  --status-high: #22C55E;   /* Green */
  --status-medium: #F59E0B; /* Amber */
  --status-low: #EF4444;    /* Red */
  --status-insufficient: #F59E0B; /* Amber */

  --font-prose: 'Plus Jakarta Sans', sans-serif;
  --font-code: 'JetBrains Mono', monospace;

  --sidebar-width: 260px;
  --topbar-height: 64px;
}"""

# Replace the :root block (up to the next })
css = re.sub(r':root\s*\{[^}]+\}', new_root, css, count=1)

with open("frontend/src/index.css", "w", encoding="utf-8") as f:
    f.write(css)

print("Updated index.css")
