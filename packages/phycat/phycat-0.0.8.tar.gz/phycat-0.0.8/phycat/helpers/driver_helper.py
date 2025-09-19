import importlib.util
import os
from pathlib import Path
from typing import Type, Any, Union
import logging
log = logging.getLogger(__name__)

def load_plugin_class(class_path: str) -> Type[Any]:
    """
    Dynamically imports a class from either a module path (e.g., 'package.module:ClassName')
    or a file path containing the class.
    
    Args:
        class_path: String in format 'module.path:ClassName' or '/path/to/file.py:ClassName'
        
    Returns:
        The requested class
        
    Raises:
        ImportError: If the module/file or class cannot be imported
        ValueError: If the class_path format is invalid
    """
    if ':' not in class_path:
        raise ValueError("Class path must be in format 'module.path:ClassName' or '/path/to/file.py:ClassName'")
        
    module_path, class_name = class_path.split(':')
    
    # Check if it's a file path
    if os.path.exists(module_path) or module_path.endswith('.py'):
        path = Path(module_path).resolve()
        if not path.exists():
            raise ImportError(f"File not found: {module_path}")
            
        # Import from file path
        spec = importlib.util.spec_from_file_location(path.stem, str(path))
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module from file: {module_path}")
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    else:
        # Import from module path
        try:
            module = importlib.import_module(module_path)
        except ImportError:
            raise ImportError(f"Could not import module: {module_path}")
    
    # Get the class from the module
    try:
        class_obj = getattr(module, class_name)
    except AttributeError:
        raise ImportError(f"Class '{class_name}' not found in module '{module_path}'")
        
        
    return class_obj


def find_plugins_in_dir(directory: str, base_class: Type[Any]) -> list[Type[Any]]:
    """
    Scans a directory for Python files and imports classes that are subclasses of the specified base class.
    
    Args:
        directory: Path to the directory to scan
        base_class: The base class that plugins should inherit from

    Returns:
        A list of plugin classes found in the directory
    """
    plugins = []
    
    # Convert directory to absolute path
    abs_dir = Path(directory).resolve()

    for root, dirs, files in os.walk(abs_dir):
        for filename in files:
            if filename.endswith(".py") and filename != "__init__.py":
                file_path = Path(root) / filename
                
                # Load module from file path
                try:
                    spec = importlib.util.spec_from_file_location(filename[:-3], str(file_path))
                    if spec is None or spec.loader is None:
                        log.error(f"Could not load module from file: {file_path}")
                        continue
                        
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find classes that inherit from base_class
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, base_class) and attr != base_class:
                            plugins.append(attr)
                except Exception as e:
                    log.error(f"Error loading plugin {file_path}: {e}")

    return plugins