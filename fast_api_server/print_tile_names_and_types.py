import os
import importlib.util

def analyze_tiles(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "tile.py":
            filepath = os.path.join(directory, filename)
            
            # Load the module
            spec = importlib.util.spec_from_file_location(filename[:-3], filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find classes that inherit from Tile
            for name, obj in module.__dict__.items():
                if isinstance(obj, type) and issubclass(obj, module.Tile) and obj != module.Tile:
                    # Create an instance of the tile
                    tile_instance = obj(name=name, type=getattr(obj, 'type', 'Unknown'))
                    
                    # Print the name and type
                    print(f"Tile Name: {tile_instance.name}, Type: {tile_instance.type}")

# Usage
tile_directory = "/mnt/c/Users/Sly/grid_game/fast_api_server/tiles"
analyze_tiles(tile_directory)