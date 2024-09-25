import os
import ast

def analyze_tiles(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "tile.py":
            filepath = os.path.join(directory, filename)
            
            with open(filepath, 'r') as file:
                tree = ast.parse(file.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if the class inherits from Tile
                    if any(base.id == 'Tile' for base in node.bases if isinstance(base, ast.Name)):
                        name = node.name
                        type_value = "Unknown"
                        
                        # Look for __init__ method
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                                # Look for super().__init__() call
                                for stmt in item.body:
                                    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                                        func = stmt.value.func
                                        if isinstance(func, ast.Attribute) and func.attr == '__init__':
                                            # Look for the 'type' keyword argument
                                            for keyword in stmt.value.keywords:
                                                if keyword.arg == 'type':
                                                    if isinstance(keyword.value, ast.Str):
                                                        type_value = keyword.value.s
                                                    elif isinstance(keyword.value, ast.Name):
                                                        type_value = keyword.value.id
                        
                        print(f"Tile Name: {name}, Type: {type_value}")

# Usage
tile_directory = "/mnt/c/Users/Sly/grid_game/fast_api_server/tiles"
analyze_tiles(tile_directory)