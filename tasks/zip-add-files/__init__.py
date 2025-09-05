#region generated meta
import typing
class Inputs(typing.TypedDict):
    zip_path: str
    files_to_add: list[str]
    archive_path_prefix: str | None
    password: str | None
    overwrite_existing: bool
class Outputs(typing.TypedDict):
    zip_path: str
    added_files_count: float
    new_size: float
    files_added: list[str]
#endregion

from oocana import Context
import os
import shutil
import tempfile
import pyzipper

def main(params: Inputs, context: Context) -> Outputs:
    """
    Add files to an existing ZIP archive
    
    Args:
        params: Input parameters containing ZIP path and files to add
        context: OOMOL context object
        
    Returns:
        Information about the modified ZIP file
    """
    zip_path = params["zip_path"]
    files_to_add = params["files_to_add"]
    archive_path_prefix = params.get("archive_path_prefix", "") or ""
    password = params.get("password")
    overwrite_existing = params["overwrite_existing"]
    
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"ZIP file does not exist: {zip_path}")
    
    # Verify all files to add exist
    for file_path in files_to_add:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File to add does not exist: {file_path}")
    
    files_added = []
    added_files_count = 0
    
    # Create temporary file for modification
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
        temp_zip_path = temp_file.name
    
    try:
        # Read existing ZIP and copy contents to new ZIP
        with pyzipper.AESZipFile(zip_path, 'r') as existing_zip:
            if password:
                existing_zip.setpassword(password.encode('utf-8'))
            
            # Get list of existing files
            existing_files = set(existing_zip.namelist())
            
            with pyzipper.AESZipFile(temp_zip_path, 'w', compression=pyzipper.ZIP_DEFLATED) as new_zip:
                if password:
                    new_zip.setpassword(password.encode('utf-8'))
                
                # Copy existing files
                for item in existing_files:
                    data = existing_zip.read(item)
                    new_zip.writestr(item, data)
                
                # Add new files
                for file_path in files_to_add:
                    if os.path.isfile(file_path):
                        # Single file
                        filename = os.path.basename(file_path)
                        archive_name = os.path.join(archive_path_prefix, filename) if archive_path_prefix else filename
                        
                        # Check if file already exists
                        if archive_name in existing_files and not overwrite_existing:
                            continue
                        
                        new_zip.write(file_path, archive_name)
                        files_added.append(archive_name)
                        added_files_count += 1
                        
                    elif os.path.isdir(file_path):
                        # Directory
                        for root, dirs, files in os.walk(file_path):
                            for file in files:
                                full_file_path = os.path.join(root, file)
                                rel_path = os.path.relpath(full_file_path, os.path.dirname(file_path))
                                archive_name = os.path.join(archive_path_prefix, rel_path) if archive_path_prefix else rel_path
                                
                                # Check if file already exists
                                if archive_name in existing_files and not overwrite_existing:
                                    continue
                                
                                new_zip.write(full_file_path, archive_name)
                                files_added.append(archive_name)
                                added_files_count += 1
        
        # Replace original ZIP with modified one
        shutil.move(temp_zip_path, zip_path)
        
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_zip_path):
            os.unlink(temp_zip_path)
        raise e
    
    # Get new file size
    new_size = os.path.getsize(zip_path)
    
    return {
        "zip_path": zip_path,
        "added_files_count": added_files_count,
        "new_size": new_size,
        "files_added": files_added
    }