#region generated meta
import typing
class Inputs(typing.TypedDict):
    zip_path: str
    max_size_mb: float
    output_directory: str
    password: str | None
    output_password: str | None
    naming_pattern: typing.Literal["sequential", "size_based", "alphabetical"]
    compression_level: int
class Outputs(typing.TypedDict):
    split_files: typing.NotRequired[list[str]]
    split_count: typing.NotRequired[float]
    split_summary: typing.NotRequired[typing.Any]
    total_split_size: typing.NotRequired[float]
    original_size: typing.NotRequired[float]
#endregion

from oocana import Context
import os
import pandas as pd
import pyzipper

def main(params: Inputs, context: Context) -> Outputs:
    """
    Split a ZIP archive into smaller files based on size limit
    
    Args:
        params: Input parameters for ZIP split operation
        context: OOMOL context object
        
    Returns:
        Information about the split files and operation summary
    """
    zip_path = params["zip_path"]
    max_size_mb = params["max_size_mb"]
    output_directory = params["output_directory"]
    password = params.get("password")
    output_password = params.get("output_password")
    naming_pattern = params["naming_pattern"]
    compression_level = params["compression_level"]
    
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"ZIP file does not exist: {zip_path}")
    
    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)
    
    original_size = os.path.getsize(zip_path)
    max_size_bytes = int(max_size_mb * 1024 * 1024)
    
    # Get base filename for split files
    base_filename = os.path.splitext(os.path.basename(zip_path))[0]
    
    split_files = []
    split_details = []
    current_split = 1
    current_size = 0
    current_zip = None
    total_split_size = 0
    
    # Read original ZIP and get file list
    with pyzipper.AESZipFile(zip_path, 'r') as source_zip:
        if password:
            source_zip.setpassword(password.encode('utf-8'))
        
        # Get all files and sort them based on naming pattern
        file_list = [info for info in source_zip.infolist() if not info.is_dir()]
        
        if naming_pattern == "size_based":
            # Sort by file size (largest first)
            file_list.sort(key=lambda x: x.file_size, reverse=True)
        elif naming_pattern == "alphabetical":
            # Sort alphabetically
            file_list.sort(key=lambda x: x.filename.lower())
        # Sequential keeps original order
        
        def create_new_split():
            nonlocal current_zip, current_split, current_size
            if current_zip:
                current_zip.close()
            
            split_filename = f"{base_filename}_part{current_split:03d}.zip"
            split_path = os.path.join(output_directory, split_filename)
            
            # Handle encryption
            output_encryption = pyzipper.WZ_AES256 if output_password else None
            
            current_zip = pyzipper.AESZipFile(split_path, 'w', compression=pyzipper.ZIP_DEFLATED, 
                                            compresslevel=compression_level, encryption=output_encryption)
            
            if output_password:
                current_zip.setpassword(output_password.encode('utf-8'))
            
            split_files.append(split_path)
            current_size = 0
            return split_path
        
        # Create first split
        current_split_path = create_new_split()
        files_in_current_split = 0
        
        for file_info in file_list:
            # Read file data
            file_data = source_zip.read(file_info.filename)
            estimated_compressed_size = len(file_data)
            
            # Check if adding this file would exceed size limit
            if current_size + estimated_compressed_size > max_size_bytes and files_in_current_split > 0:
                # Record details of current split
                actual_size = os.path.getsize(current_split_path)
                split_details.append({
                    "split_file": os.path.basename(current_split_path),
                    "files_count": files_in_current_split,
                    "size_bytes": actual_size,
                    "size_mb": round(actual_size / 1024 / 1024, 2)
                })
                total_split_size += actual_size
                
                # Create new split
                current_split += 1
                current_split_path = create_new_split()
                files_in_current_split = 0
            
            # Add file to current split
            current_zip.writestr(file_info.filename, file_data)
            current_size += estimated_compressed_size
            files_in_current_split += 1
        
        # Close final split and record details
        if current_zip:
            current_zip.close()
            actual_size = os.path.getsize(current_split_path)
            split_details.append({
                "split_file": os.path.basename(current_split_path),
                "files_count": files_in_current_split,
                "size_bytes": actual_size,
                "size_mb": round(actual_size / 1024 / 1024, 2)
            })
            total_split_size += actual_size
    
    # Create summary DataFrame
    summary_df = pd.DataFrame(split_details)
    
    # Add summary statistics
    if not summary_df.empty:
        summary_stats = {
            "original_file": os.path.basename(zip_path),
            "original_size_mb": round(original_size / 1024 / 1024, 2),
            "max_size_limit_mb": max_size_mb,
            "total_splits": len(split_files),
            "naming_pattern": naming_pattern,
            "compression_level": compression_level,
            "total_split_size_mb": round(total_split_size / 1024 / 1024, 2),
            "size_efficiency": round((total_split_size / original_size) * 100, 2) if original_size > 0 else 0
        }
        
        # Add summary row
        summary_row = pd.DataFrame([summary_stats])
        summary_df = pd.concat([summary_df, pd.DataFrame([{}]), summary_row], ignore_index=True)
    
    return {
        "split_files": split_files,
        "split_count": len(split_files),
        "split_summary": summary_df,
        "total_split_size": total_split_size,
        "original_size": original_size
    }