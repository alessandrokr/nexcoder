from pathlib import Path
from os import getcwd
from openai.types.chat import ChatCompletionToolParam

class Tools:
    def __init__(self) -> None:
        self.tool_declarations: list[ChatCompletionToolParam] = [
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "Lists files in a given directory. If no directory is provided, it lists files in the current directory.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "The directory to list files from. If not provided, the current directory will be used."
                            }
                        }
                    },
                }
            }
        ]
        
        self.tool_functions = {
            "list_files": self._list_files
        }
    
    
    def _list_files(self, directory: str | None = None) -> list[str]:
        """
        Lists files in a given directory. If no directory is provided, it lists files in the current directory.
        
        Parameters
        ----------
        directory : str, optional
            The directory to list files from. If not provided, the current directory will be used.
        
        Returns
        -------
        list
            A list of file names in the specified directory.
        """
        if directory is None:
            directory = getcwd()
        
        try:
            return [f.name for f in Path(directory).iterdir() if f.is_file()]
        except Exception as e:
            print(f"Error listing files in directory {directory}: {e}")
            return []
        
