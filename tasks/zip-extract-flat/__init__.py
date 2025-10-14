#region generated meta
import typing
class Inputs(typing.TypedDict):
    zip_path: str
    output_directory: str
    password: str | None
    handle_name_conflicts: typing.Literal["skip", "rename", "overwrite"]
    file_filter: str | None
    max_files: int
class Outputs(typing.TypedDict):
    extracted_path: typing.NotRequired[str]
    extracted_files_count: typing.NotRequired[float]
    extracted_files: typing.NotRequired[list[str]]
    skipped_files_count: typing.NotRequired[float]
    total_size: typing.NotRequired[float]
#endregion

from oocana import Context
import os
import pyzipper

def main(params: Inputs, context: Context) -> Outputs:
    """
    Extract ZIP archive contents to a flat directory structure
    
    Args:
        params: Input parameters for flat extraction
        context: OOMOL context object
        
    Returns:
        Information about extracted files in flat structure
    """
    zip_path = params["zip_path"]
    output_directory = params["output_directory"]
    password = params.get("password")
    handle_name_conflicts = params["handle_name_conflicts"]
    file_filter = params.get("file_filter", "") or ""
    max_files = params["max_files"]
    
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"ZIP file does not exist: {zip_path}")
    
    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)
    
    # Parse file filter
    allowed_extensions = []
    if file_filter:
        allowed_extensions = [ext.strip().lower() for ext in file_filter.split(',')]
        # Ensure extensions start with a dot
        allowed_extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in allowed_extensions]
    
    extracted_files = []
    skipped_files_count = 0
    extracted_files_count = 0
    total_size = 0
    
    with pyzipper.AESZipFile(zip_path, 'r') as zip_file:
        if password:
            zip_file.setpassword(password.encode('utf-8'))
        
        for file_info in zip_file.infolist():
            # Skip directories
            if file_info.is_dir():
                continue
            
            # Check max files limit
            if max_files > 0 and extracted_files_count >= max_files:
                break
            
            # Get just the filename without path
            filename = os.path.basename(file_info.filename)
            
            # Skip if filename is empty (can happen with some archives)
            if not filename:
                skipped_files_count += 1
                continue
            
            # Apply file filter
            if allowed_extensions:
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext not in allowed_extensions:
                    skipped_files_count += 1
                    continue
            
            # Determine output file path
            file_path = os.path.join(output_directory, filename)
            
            # Handle name conflicts
            if os.path.exists(file_path):
                if handle_name_conflicts == "skip":
                    skipped_files_count += 1
                    continue
                elif handle_name_conflicts == "rename":
                    # Add number suffix to avoid conflicts
                    base_name, extension = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(file_path):
                        new_filename = f"{base_name}_{counter}{extension}"
                        file_path = os.path.join(output_directory, new_filename)
                        counter += 1
                # If "overwrite", we proceed with the original path
            
            # Extract file
            try:
                with zip_file.open(file_info.filename) as source, open(file_path, 'wb') as target:
                    target.write(source.read())
                
                extracted_files.append(file_path)
                extracted_files_count += 1
                total_size += file_info.file_size
                
            except Exception:
                # Skip files that can't be extracted
                skipped_files_count += 1
                continue
    
    return {
        "extracted_path": output_directory,
        "extracted_files_count": extracted_files_count,
        "extracted_files": extracted_files,
        "skipped_files_count": skipped_files_count,
        "total_size": total_size
    }