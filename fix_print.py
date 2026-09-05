import os
import glob

def replace_prints():
    # Only target these specific files to avoid breaking eval scripts or main.py init prints
    files = [
        "backend/src/api/auth.py",
        "backend/src/api/incidents.py",
        "backend/src/connectors/github.py",
        "backend/src/connectors/github_actions.py",
        "backend/src/connectors/postgres.py",
        "backend/src/connectors/stripe.py",
        "backend/src/pipeline/nodes.py"
    ]

    for fp in files:
        if not os.path.exists(fp): continue
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add import logging if not present
        if 'import logging' not in content:
            content = 'import logging\nlogger = logging.getLogger(__name__)\n' + content
        elif 'logger = logging.getLogger' not in content:
            content = content.replace('import logging', 'import logging\nlogger = logging.getLogger(__name__)')

        # Replace print(f"Error...: {e}") with logger.exception("Error...")
        # Since we just want a simple replace, we'll do line by line or regex
        import re
        content = re.sub(r'print\((f?["\'])(.*?)\{e\}(.*?)(["\'])\)', r'logger.exception(\1\2\3\4)', content)
        
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(content)

replace_prints()
