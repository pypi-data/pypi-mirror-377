import os
from notebookutils import mssparkutils

def path_exists(path_to_check):
    """
    Check if a path exists
    Args:
        path_to_check: The path to check
    Returns:
        True if the path exists, False if it doesn't
    """
    if path_to_check.startswith("Tables/") or path_to_check.startswith("Files/"):
        try:
            mssparkutils.fs.ls(path_to_check)
            return True
        except:
            return False

    else:
        return os.path.exists(path_to_check)

def list_dir(path_to_list):
    """
    List a directory
    Args:
        path_to_list: The path to list
    Returns:
        A list of the files in the directory
    """
    return list(map_dir(path_to_list))

def map_dir(path_to_map):
    """
    Build a map generator of the files in a directory
    Args:
        path_to_map: The path to map
    Returns:
        A map generator of the files in the directory
    """
    return map(lambda x: x.name, mssparkutils.fs.ls(path_to_map))

def create_schema_if_not_exists(schema_name):
    """
    Create a schema if it doesn't exist
    Args:
        schema_name: The name of the schema
    Returns:
        True if the schema was created, False if it already existed
    """
    lakehouse_schema_folder = f"Tables/{schema_name}"
    schema_exists = path_exists(lakehouse_schema_folder)
    if not schema_exists:
        mssparkutils.fs.mkdirs(lakehouse_schema_folder)
        return True
    return False