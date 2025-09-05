#region generated meta
import typing
class Inputs(typing.TypedDict):
    source_path: str
    output_path: str
    include_subdirectories: bool
class Outputs(typing.TypedDict):
    zip_path: str
    compressed_size: float
    original_size: float
    compression_ratio: float
#endregion

from oocana import Context
import os
import pyzipper

def main(params: Inputs, context: Context) -> Outputs:
    """
    Create a ZIP archive from files or folders
    
    Args:
        params: Input parameters containing source path, output path, and options
        context: OOMOL context object
        
    Returns:
        ZIP file information and compression statistics
    """
    source_path = params["source_path"]
    output_path = params["output_path"]
    include_subdirectories = params["include_subdirectories"]
    
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source path does not exist: {source_path}")
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    original_size = 0
    
    with pyzipper.AESZipFile(output_path, 'w', compression=pyzipper.ZIP_DEFLATED) as zip_file:
        if os.path.isfile(source_path):
            # Single file compression
            file_size = os.path.getsize(source_path)
            original_size += file_size
            zip_file.write(source_path, os.path.basename(source_path))
            
        elif os.path.isdir(source_path):
            # Directory compression
            for root, dirs, files in os.walk(source_path):
                # Skip subdirectories if not included
                if not include_subdirectories and root != source_path:
                    continue
                    
                for file in files:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    original_size += file_size
                    
                    # Calculate relative path for archive
                    if include_subdirectories:
                        arcname = os.path.relpath(file_path, os.path.dirname(source_path))
                    else:
                        arcname = file
                    
                    zip_file.write(file_path, arcname)
    
    # Get compressed size
    compressed_size = os.path.getsize(output_path)
    
    # Calculate compression ratio
    if original_size > 0:
        compression_ratio = ((original_size - compressed_size) / original_size) * 100
    else:
        compression_ratio = 0.0
    
    return {
        "zip_path": output_path,
        "compressed_size": compressed_size,
        "original_size": original_size,
        "compression_ratio": round(compression_ratio, 2)
    }