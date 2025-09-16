#region generated meta
import typing
class Inputs(typing.TypedDict):
    source_folders: list[str]
    output_directory: str
    compression_level: int
    add_timestamp: bool
    password: str | None
    include_subdirectories: bool
class Outputs(typing.TypedDict):
    created_zips: list[str]
    total_original_size: float
    total_compressed_size: float
    overall_compression_ratio: float
    processing_summary: dict
#endregion

from oocana import Context
import os
import datetime
import pandas as pd
import pyzipper

def main(params: Inputs, context: Context) -> Outputs:
    """
    Compress multiple folders into separate ZIP archives
    
    Args:
        params: Input parameters for batch compression
        context: OOMOL context object
        
    Returns:
        Information about all created ZIP files and processing summary
    """
    source_folders = params["source_folders"]
    output_directory = params["output_directory"]
    compression_level = params["compression_level"]
    add_timestamp = params["add_timestamp"]
    password = params.get("password")
    include_subdirectories = params["include_subdirectories"]
    
    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)
    
    created_zips = []
    total_original_size = 0
    total_compressed_size = 0
    processing_results = []
    
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") if add_timestamp else ""
    
    for i, folder_path in enumerate(source_folders):
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            continue
        
        folder_name = os.path.basename(folder_path.rstrip(os.sep))
        
        # Create ZIP filename
        if add_timestamp:
            zip_filename = f"{folder_name}_{timestamp_str}.zip"
        else:
            zip_filename = f"{folder_name}.zip"
        
        zip_path = os.path.join(output_directory, zip_filename)
        
        # Handle duplicate filenames
        counter = 1
        while os.path.exists(zip_path):
            base_name = zip_filename.rsplit('.', 1)[0]
            zip_filename = f"{base_name}_{counter}.zip"
            zip_path = os.path.join(output_directory, zip_filename)
            counter += 1
        
        folder_original_size = 0
        
        try:
            # Create ZIP file
            if password:
                with pyzipper.AESZipFile(zip_path, 'w', compression=pyzipper.ZIP_DEFLATED, 
                                       compresslevel=compression_level, encryption=pyzipper.WZ_AES256) as zip_file:
                    zip_file.setpassword(password.encode('utf-8'))
                    folder_original_size = _add_folder_to_zip(zip_file, folder_path, include_subdirectories)
            else:
                with pyzipper.AESZipFile(zip_path, 'w', compression=pyzipper.ZIP_DEFLATED, 
                                       compresslevel=compression_level) as zip_file:
                    folder_original_size = _add_folder_to_zip(zip_file, folder_path, include_subdirectories)
            
            # Get compressed size
            compressed_size = os.path.getsize(zip_path)
            compression_ratio = ((folder_original_size - compressed_size) / folder_original_size) * 100 if folder_original_size > 0 else 0
            
            created_zips.append(zip_path)
            total_original_size += folder_original_size
            total_compressed_size += compressed_size
            
            processing_results.append({
                "folder_name": folder_name,
                "zip_path": zip_path,
                "original_size_mb": round(folder_original_size / 1024 / 1024, 2),
                "compressed_size_mb": round(compressed_size / 1024 / 1024, 2),
                "compression_ratio": round(compression_ratio, 2),
                "status": "Success"
            })
            
        except Exception as e:
            processing_results.append({
                "folder_name": folder_name,
                "zip_path": "",
                "original_size_mb": 0,
                "compressed_size_mb": 0,
                "compression_ratio": 0,
                "status": f"Error: {str(e)}"
            })
    
    # Calculate overall compression ratio
    overall_compression_ratio = ((total_original_size - total_compressed_size) / total_original_size) * 100 if total_original_size > 0 else 0
    
    # Create summary DataFrame
    summary_df = pd.DataFrame(processing_results)
    
    return {
        "created_zips": created_zips,
        "total_original_size": total_original_size,
        "total_compressed_size": total_compressed_size,
        "overall_compression_ratio": round(overall_compression_ratio, 2),
        "processing_summary": summary_df
    }

def _add_folder_to_zip(zip_file, folder_path, include_subdirectories):
    """Helper function to add folder contents to ZIP file"""
    total_size = 0
    
    for root, dirs, files in os.walk(folder_path):
        # Skip subdirectories if not included
        if not include_subdirectories and root != folder_path:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            total_size += file_size
            
            # Calculate relative path for archive
            if include_subdirectories:
                arcname = os.path.relpath(file_path, os.path.dirname(folder_path))
            else:
                arcname = os.path.join(os.path.basename(folder_path), file)
            
            zip_file.write(file_path, arcname)
    
    return total_size