import sys

def remove_bom(filename):
    with open(filename, 'rb') as f:
        content = f.read()
    if content.startswith(b'\xef\xbb\xbf'):
        with open(filename, 'wb') as f:
            f.write(content[3:])
        print(f"Removed BOM from {filename}")
    else:
        print(f"No BOM in {filename}")

remove_bom('frontend/package.json')
