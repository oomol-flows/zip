#region generated meta
import typing
class Inputs(typing.TypedDict):
    zip_files: list[str]
    output_path: str
    passwords: list[str] | None
    output_password: str | None
    handle_duplicates: typing.Literal["skip", "rename", "overwrite"]
    compression_level: int
class Outputs(typing.TypedDict):
    merged_zip_path: typing.NotRequired[str]
    total_files_merged: typing.NotRequired[float]
    merge_summary: typing.NotRequired[typing.Any]
    duplicate_files_count: typing.NotRequired[float]
    merged_size: typing.NotRequired[float]
#endregion

from oocana import Context
import os
import pandas as pd
import pyzipper

def main(params: Inputs, context: Context) -> Outputs:
    """
    Merge multiple ZIP archives into a single ZIP file
    
    Args:
        params: Input parameters for ZIP merge operation
        context: OOMOL context object
        
    Returns:
        Information about the merged ZIP file and operation summary
    """
    zip_files = params["zip_files"]
    output_path = params["output_path"]
    passwords = params.get("passwords", [])
    output_password = params.get("output_password")
    handle_duplicates = params["handle_duplicates"]
    compression_level = params["compression_level"]
    
    if not zip_files:
        raise ValueError("At least one ZIP file must be provided")
    
    # Verify all input files exist
    for zip_file in zip_files:
        if not os.path.exists(zip_file):
            raise FileNotFoundError(f"ZIP file does not exist: {zip_file}")
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # Ensure passwords list matches zip_files length
    if passwords:
        while len(passwords) < len(zip_files):
            passwords.append(None)
    else:
        passwords = [None] * len(zip_files)
    
    total_files_merged = 0
    duplicate_files_count = 0
    existing_files = set()
    merge_details = []
    
    # Create output ZIP file
    output_encryption = pyzipper.WZ_AES256 if output_password else None
    
    with pyzipper.AESZipFile(output_path, 'w', compression=pyzipper.ZIP_DEFLATED, 
                            compresslevel=compression_level, encryption=output_encryption) as output_zip:
        
        if output_password:
            output_zip.setpassword(output_password.encode('utf-8'))
        
        for i, zip_file in enumerate(zip_files):
            zip_password = passwords[i]
            files_from_this_zip = 0
            duplicates_from_this_zip = 0
            
            try:
                with pyzipper.AESZipFile(zip_file, 'r') as input_zip:
                    if zip_password:
                        input_zip.setpassword(zip_password.encode('utf-8'))
                    
                    for file_info in input_zip.infolist():
                        # Skip directories
                        if file_info.is_dir():
                            continue
                        
                        original_filename = file_info.filename
                        final_filename = original_filename
                        
                        # Handle duplicate filenames
                        if original_filename in existing_files:
                            duplicate_files_count += 1
                            duplicates_from_this_zip += 1
                            
                            if handle_duplicates == "skip":
                                continue
                            elif handle_duplicates == "rename":
                                # Add suffix to avoid conflict
                                base_name, extension = os.path.splitext(original_filename)
                                counter = 1
                                while final_filename in existing_files:
                                    final_filename = f"{base_name}_{counter}{extension}"
                                    counter += 1
                            # If "overwrite", we use the original filename
                        
                        # Copy file to output ZIP
                        file_data = input_zip.read(original_filename)
                        output_zip.writestr(final_filename, file_data)
                        
                        existing_files.add(final_filename)
                        files_from_this_zip += 1
                        total_files_merged += 1
                
                merge_details.append({
                    "source_zip": os.path.basename(zip_file),
                    "files_added": files_from_this_zip,
                    "duplicates_encountered": duplicates_from_this_zip,
                    "status": "Success"
                })
                
            except Exception as e:
                merge_details.append({
                    "source_zip": os.path.basename(zip_file),
                    "files_added": 0,
                    "duplicates_encountered": 0,
                    "status": f"Error: {str(e)}"
                })
    
    # Get merged file size
    merged_size = os.path.getsize(output_path)
    
    # Create summary DataFrame
    summary_df = pd.DataFrame(merge_details)
    
    return {
        "merged_zip_path": output_path,
        "total_files_merged": total_files_merged,
        "merge_summary": summary_df,
        "duplicate_files_count": duplicate_files_count,
        "merged_size": merged_size
    }