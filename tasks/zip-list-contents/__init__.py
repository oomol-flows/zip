#region generated meta
import typing
class Inputs(typing.TypedDict):
    zip_path: str
    password: str | None
    show_directories: bool
    detailed_info: bool
    sort_by: typing.Literal["name", "size", "date", "type"]
class Outputs(typing.TypedDict):
    file_list: typing.NotRequired[list[str]]
    detailed_contents: typing.NotRequired[dict]
    total_files: typing.NotRequired[float]
    total_directories: typing.NotRequired[float]
    uncompressed_size: typing.NotRequired[float]
    compressed_size: typing.NotRequired[float]
#endregion

from oocana import Context
import os
import datetime
import pandas as pd
import pyzipper

def main(params: Inputs, context: Context) -> Outputs:
    """
    List and analyze contents of a ZIP archive
    
    Args:
        params: Input parameters for listing ZIP contents
        context: OOMOL context object
        
    Returns:
        Detailed information about ZIP archive contents
    """
    zip_path = params["zip_path"]
    password = params.get("password")
    show_directories = params["show_directories"]
    detailed_info = params["detailed_info"]
    sort_by = params["sort_by"]
    
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"ZIP file does not exist: {zip_path}")
    
    file_list = []
    detailed_contents = []
    total_files = 0
    total_directories = 0
    uncompressed_size = 0
    compressed_size = 0
    
    with pyzipper.AESZipFile(zip_path, 'r') as zip_file:
        if password:
            zip_file.setpassword(password.encode('utf-8'))
        
        for file_info in zip_file.infolist():
            is_directory = file_info.is_dir()
            
            # Count files and directories
            if is_directory:
                total_directories += 1
                if not show_directories:
                    continue
            else:
                total_files += 1
                uncompressed_size += file_info.file_size
                compressed_size += file_info.compress_size
            
            # Add to file list
            file_list.append(file_info.filename)
            
            if detailed_info:
                # Get modification time
                try:
                    mod_time = datetime.datetime(*file_info.date_time)
                    mod_time_str = mod_time.strftime("%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError):
                    mod_time_str = "Unknown"
                
                # Determine file type
                file_type = "Directory" if is_directory else _get_file_type(file_info.filename)
                
                # Calculate compression ratio
                if file_info.file_size > 0 and not is_directory:
                    compression_ratio = ((file_info.file_size - file_info.compress_size) / file_info.file_size) * 100
                else:
                    compression_ratio = 0.0
                
                detailed_item = {
                    "filename": file_info.filename,
                    "type": file_type,
                    "size_bytes": file_info.file_size,
                    "size_mb": round(file_info.file_size / 1024 / 1024, 3),
                    "compressed_size_bytes": file_info.compress_size,
                    "compressed_size_mb": round(file_info.compress_size / 1024 / 1024, 3),
                    "compression_ratio": round(compression_ratio, 2),
                    "modified_date": mod_time_str,
                    "crc32": file_info.CRC,
                    "is_directory": is_directory
                }
                detailed_contents.append(detailed_item)
    
    # Sort results if detailed info requested
    if detailed_info and detailed_contents:
        sort_key_map = {
            "name": "filename",
            "size": "size_bytes",
            "date": "modified_date",
            "type": "type"
        }
        sort_key = sort_key_map.get(sort_by, "filename")
        
        try:
            detailed_contents.sort(key=lambda x: x[sort_key])
        except (KeyError, TypeError):
            # Fallback to filename sorting if sort key fails
            detailed_contents.sort(key=lambda x: x["filename"])
        
        # Also sort file list to match
        file_list = [item["filename"] for item in detailed_contents]
    else:
        file_list.sort()
    
    # Convert detailed contents to DataFrame if requested
    if detailed_info and detailed_contents:
        detailed_df = pd.DataFrame(detailed_contents)
    else:
        detailed_df = pd.DataFrame()
    
    return {
        "file_list": file_list,
        "detailed_contents": detailed_df,
        "total_files": total_files,
        "total_directories": total_directories,
        "uncompressed_size": uncompressed_size,
        "compressed_size": compressed_size
    }

def _get_file_type(filename):
    """Helper function to determine file type from extension"""
    _, ext = os.path.splitext(filename.lower())
    
    file_type_map = {
        '.txt': 'Text',
        '.doc': 'Document', '.docx': 'Document', '.pdf': 'Document',
        '.jpg': 'Image', '.jpeg': 'Image', '.png': 'Image', '.gif': 'Image', '.bmp': 'Image',
        '.mp3': 'Audio', '.wav': 'Audio', '.flac': 'Audio',
        '.mp4': 'Video', '.avi': 'Video', '.mkv': 'Video', '.mov': 'Video',
        '.zip': 'Archive', '.rar': 'Archive', '.7z': 'Archive',
        '.py': 'Code', '.js': 'Code', '.html': 'Code', '.css': 'Code', '.json': 'Code',
        '.exe': 'Executable', '.dll': 'Executable',
        '.xml': 'Data', '.csv': 'Data', '.xlsx': 'Data'
    }
    
    return file_type_map.get(ext, 'Unknown')