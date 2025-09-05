#region generated meta
import typing
class Inputs(typing.TypedDict):
    zip_path: str
    password: str
    output_directory: str
    create_subfolder: bool
    overwrite_existing: bool
    verify_password_first: bool
class Outputs(typing.TypedDict):
    extracted_path: str
    extracted_files_count: float
    extracted_files: list[str]
    total_size: float
    password_verified: bool
#endregion

from oocana import Context
import os
import pyzipper

def main(params: Inputs, context: Context) -> Outputs:
    """
    Extract encrypted ZIP archive contents to specified directory
    
    Args:
        params: Input parameters for encrypted extraction
        context: OOMOL context object
        
    Returns:
        Information about extracted files and password verification
    """
    zip_path = params["zip_path"]
    password = params["password"]
    output_directory = params["output_directory"]
    create_subfolder = params["create_subfolder"]
    overwrite_existing = params["overwrite_existing"]
    verify_password_first = params["verify_password_first"]
    
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"ZIP file does not exist: {zip_path}")
    
    if not password:
        raise ValueError("Password is required for encrypted ZIP extraction")
    
    password_verified = False
    
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
        zip_file.setpassword(password.encode('utf-8'))
        
        # Verify password if requested
        if verify_password_first:
            try:
                # Try to read the first file to verify password
                file_list = [f for f in zip_file.infolist() if not f.is_dir()]
                if file_list:
                    with zip_file.open(file_list[0].filename) as test_file:
                        test_file.read(1)  # Read just one byte to test
                password_verified = True
            except Exception:
                raise ValueError("Invalid password for encrypted ZIP file")
        else:
            password_verified = True
        
        # Extract all files
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
                
            except Exception:
                # Skip files that can't be extracted
                continue
    
    return {
        "extracted_path": extracted_path,
        "extracted_files_count": extracted_files_count,
        "extracted_files": extracted_files,
        "total_size": total_size,
        "password_verified": password_verified
    }