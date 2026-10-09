import yaml
from os import makedirs, getcwd
from pathlib import Path
from .lib.CallingHandler import CallingHandler

CONFIG_FILE = "./config.yaml"
WORKING_DIR = getcwd()
FILE_PATH = Path(__file__).resolve().parent

def main() -> None:
    with open(CONFIG_FILE, "r") as f:
        config = yaml.safe_load(f)
        cache_dir = config.get("cache_dir", "./cache/nexcoder/")
        cb_indexes = Path(cache_dir) / "cb_indexes" # CodeBase Schematic Indexes are saved as .txt
        try:
            makedirs(cb_indexes, exist_ok=True)
        except Exception as e:
            print(f"Error creating cache directories which are needed: {e}")
            quit(1)
    try:
        with open(Path(cache_dir) / "index.txt", "a+") as cache_index_file:
            cache_index_file.read()
    except Exception as e:
        print(f"Error creating index.txt file which is needed: {e}")
        quit(1)
    
    handler = CallingHandler(config.get("api_base_url"), config.get("api_key"), config.get("model"))
    # while True:
    print(handler.make_call([{"role":"user","content":"Hello! What tools do you have?"}]))
    
