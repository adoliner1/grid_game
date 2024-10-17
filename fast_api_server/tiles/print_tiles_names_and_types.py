import os
import ast
import csv

def extract_info_from_super_init(node):
    for item in node.body:
        if isinstance(item, ast.FunctionDef) and item.name == '__init__':
            for stmt in item.body:
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                    func = stmt.value.func
                    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Call) and func.attr == '__init__':
                        info = {}
                        for keyword in stmt.value.keywords:
                            if keyword.arg in ['name', 'type', 'minimum_influence_to_rule', 'number_of_slots', 'influence_tiers']:
                                if isinstance(keyword.value, ast.Str):
                                    info[keyword.arg] = keyword.value.s
                                elif isinstance(keyword.value, ast.Num):
                                    info[keyword.arg] = keyword.value.n
                                elif isinstance(keyword.value, ast.List):
                                    info[keyword.arg] = extract_list_content(keyword.value)
                        return info
    return {}

def extract_list_content(node):
    if isinstance(node, ast.List):
        return [extract_dict_content(elt) for elt in node.elts if isinstance(elt, ast.Dict)]
    return []

def extract_dict_content(node):
    if isinstance(node, ast.Dict):
        return {
            (k.s if isinstance(k, ast.Str) else k.value.s if isinstance(k, ast.Constant) else None): 
            (v.s if isinstance(v, ast.Str) else 
             v.value if isinstance(v, ast.Constant) else 
             v.n if isinstance(v, ast.Num) else 
             v.id if isinstance(v, ast.Name) else None)
            for k, v in zip(node.keys, node.values)
        }
    return {}

def analyze_tiles(directory, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['Name', 'Type 1', 'Type 2', 'Type 3', 'Minimum Influence to Rule', 'Number of Slots',
                      'Influence to Reach Tier', 'Must Be Ruler', 'Is On Cooldown', 'Has A Cooldown', 'Leader Must Be Present']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for filename in os.listdir(directory):
            if filename.endswith(".py") and filename != "tile.py":
                filepath = os.path.join(directory, filename)
               
                with open(filepath, 'r') as file:
                    tree = ast.parse(file.read())
               
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check if the class inherits from Tile
                        if any(base.id == 'Tile' for base in node.bases if isinstance(base, ast.Name)):
                            info = extract_info_from_super_init(node)
                            if info:
                                types = info.get('type', '').split('/')
                                types += ['N/A'] * (3 - len(types))  # Ensure we always have 3 type fields
                                
                                influence_tiers = info.get('influence_tiers', [])
                                influence_tier = influence_tiers[0] if influence_tiers else {}
                                
                                writer.writerow({
                                    'Name': info.get('name', 'Unknown'),
                                    'Type 1': types[0].strip(),
                                    'Type 2': types[1].strip(),
                                    'Type 3': types[2].strip(),
                                    'Minimum Influence to Rule': info.get('minimum_influence_to_rule', 'N/A'),
                                    'Number of Slots': info.get('number_of_slots', 'N/A'),
                                    'Influence to Reach Tier': influence_tier.get('influence_to_reach_tier', 'N/A'),
                                    'Must Be Ruler': influence_tier.get('must_be_ruler', 'N/A'),
                                    'Is On Cooldown': influence_tier.get('is_on_cooldown', 'N/A'),
                                    'Has A Cooldown': influence_tier.get('has_a_cooldown', 'N/A'),
                                    'Leader Must Be Present': influence_tier.get('leader_must_be_present', 'N/A')
                                })

# Usage
tile_directory = "/mnt/c/Users/Sly/grid_game/fast_api_server/tiles"
output_csv = "tile_analysis.csv"
analyze_tiles(tile_directory, output_csv)
print(f"Analysis complete. Results saved to {output_csv}")