import re

app_path = r"c:\Users\higosantos\Documents\gestao_editais\gestao_editais_novo\app.py"

with open(app_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

routes = []
current_route = None

for i, line in enumerate(lines):
    route_match = re.search(r'@app\.route\(\'(.*?)\'', line)
    if route_match:
        route_path = route_match.group(1)
        # Look for the function name in the next lines
        func_name = "unknown"
        for j in range(i + 1, min(i + 5, len(lines))):
            func_match = re.search(r'def (.*?)\(', lines[j])
            if func_match:
                func_name = func_match.group(1)
                break
        routes.append((i + 1, route_path, func_name))

print(f"Total routes found: {len(routes)}")
for line_num, path, name in routes:
    print(f"{line_num:4} | {path:40} | {name}")
