#region generated meta
import typing
class Inputs(typing.TypedDict):
    zip_path: str
    output_directory: str
    create_subfolder: bool
    overwrite_existing: bool
class Outputs(typing.TypedDict):
    extracted_path: str
    extracted_files_count: float
    extracted_files: list[str]
    total_size: float
#endregion

from oocana import Context
import os
import pyzipper

def main(params: Inputs, context: Context) -> Outputs:
    """
    Extract ZIP archive contents to specified directory
    
    Args:
        params: Input parameters for extraction
        context: OOMOL context object
        
    Returns:
        Information about extracted files
    """
    zip_path = params["zip_path"]
    output_directory = params["output_directory"]
    create_subfolder = params["create_subfolder"]
    overwrite_existing = params["overwrite_existing"]
    
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"ZIP file does not exist: {zip_path}")
    
    # Determine extraction directory
    if create_subfolder:
        zip_basename = os.path.splitext(os.path.basename(zip_path))[0]
        extracted_path = os.path.join(output_directory, zip_basename)
    else:
        extracted_path = output_directory
    
    # Ensure extraction directory exists
    os.makedirs(extracted_path, exist_ok=True)
    
    extracted_files = []
    extracted_files_count = 0
    total_size = 0
    
    with pyzipper.AESZipFile(zip_path, 'r') as zip_file:
        # Get list of files in ZIP
        file_list = zip_file.namelist()
        
        for file_info in zip_file.infolist():
            # Skip directories
            if file_info.is_dir():
                continue
            
            file_path = os.path.join(extracted_path, file_info.filename)
            
            # Check if file already exists
            if os.path.exists(file_path) and not overwrite_existing:
                continue
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Extract file
            try:
                with zip_file.open(file_info.filename) as source, open(file_path, 'wb') as target:
                    target.write(source.read())
                
                extracted_files.append(file_path)
                extracted_files_count += 1
                total_size += file_info.file_size
                
            except Exception as e:
                # Skip files that can't be extracted
                continue
    
    return {
        "extracted_path": extracted_path,
        "extracted_files_count": extracted_files_count,
        "extracted_files": extracted_files,
        "total_size": total_size
    }