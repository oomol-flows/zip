#region generated meta
import typing
class Inputs(typing.TypedDict):
    zip_path: str
    files_to_extract: list[str]
    output_directory: str
    password: str | None
    preserve_structure: bool
    overwrite_existing: bool
class Outputs(typing.TypedDict):
    extracted_path: typing.NotRequired[str]
    extracted_files_count: typing.NotRequired[float]
    extracted_files: typing.NotRequired[list[str]]
    skipped_files: typing.NotRequired[list[str]]
    total_size: typing.NotRequired[float]
#endregion

from oocana import Context
import os
import pyzipper

def main(params: Inputs, context: Context) -> Outputs:
    """
    Extract specific files from a ZIP archive
    
    Args:
        params: Input parameters for selective extraction
        context: OOMOL context object
        
    Returns:
        Information about extracted and skipped files
    """
    zip_path = params["zip_path"]
    files_to_extract = params["files_to_extract"]
    output_directory = params["output_directory"]
    password = params.get("password")
    preserve_structure = params["preserve_structure"]
    overwrite_existing = params["overwrite_existing"]
    
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"ZIP file does not exist: {zip_path}")
    
    if not files_to_extract:
        raise ValueError("At least one file must be specified for extraction")
    
    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)
    
    extracted_files = []
    skipped_files = []
    extracted_files_count = 0
    total_size = 0
    
    with pyzipper.AESZipFile(zip_path, 'r') as zip_file:
        if password:
            zip_file.setpassword(password.encode('utf-8'))
        
        # Get list of all files in ZIP
        available_files = {info.filename: info for info in zip_file.infolist()}
        
        for file_to_extract in files_to_extract:
            # Normalize path separators
            normalized_file = file_to_extract.replace('\\', '/')
            
            # Check if file exists in ZIP
            if normalized_file not in available_files:
                skipped_files.append(f"Not found: {file_to_extract}")
                continue
            
            file_info = available_files[normalized_file]
            
            # Skip directories
            if file_info.is_dir():
                skipped_files.append(f"Directory: {file_to_extract}")
                continue
            
            # Determine output path
            if preserve_structure:
                # Keep original directory structure
                file_path = os.path.join(output_directory, file_info.filename)
            else:
                # Extract to flat structure
                filename = os.path.basename(file_info.filename)
                file_path = os.path.join(output_directory, filename)
            
            # Check if file already exists
            if os.path.exists(file_path) and not overwrite_existing:
                skipped_files.append(f"Already exists: {file_to_extract}")
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
                skipped_files.append(f"Error extracting {file_to_extract}: {str(e)}")
    
    return {
        "extracted_path": output_directory,
        "extracted_files_count": extracted_files_count,
        "extracted_files": extracted_files,
        "skipped_files": skipped_files,
        "total_size": total_size
    }