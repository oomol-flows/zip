#region generated meta
import typing
class Inputs(typing.TypedDict):
    zip_path: str
    password: str | None
    calculate_checksums: bool
class Outputs(typing.TypedDict):
    file_info: typing.NotRequired[dict]
    archive_stats: typing.NotRequired[dict]
    is_encrypted: typing.NotRequired[bool]
    compression_method: typing.NotRequired[str]
    total_entries: typing.NotRequired[float]
    size_on_disk: typing.NotRequired[float]
    uncompressed_total_size: typing.NotRequired[float]
#endregion

from oocana import Context
import os
import hashlib
import datetime
import pandas as pd
import pyzipper

def main(params: Inputs, context: Context) -> Outputs:
    """
    Analyze ZIP file and extract detailed information and statistics
    
    Args:
        params: Input parameters for ZIP analysis
        context: OOMOL context object
        
    Returns:
        Comprehensive information about the ZIP archive
    """
    zip_path = params["zip_path"]
    password = params.get("password")
    calculate_checksums = params["calculate_checksums"]
    
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"ZIP file does not exist: {zip_path}")
    
    # Get file system information
    file_stat = os.stat(zip_path)
    size_on_disk = file_stat.st_size
    created_time = datetime.datetime.fromtimestamp(file_stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
    modified_time = datetime.datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    
    # Calculate file checksum if requested
    file_checksums = {}
    if calculate_checksums:
        with open(zip_path, 'rb') as f:
            content = f.read()
            file_checksums = {
                "md5": hashlib.md5(content).hexdigest(),
                "sha1": hashlib.sha1(content).hexdigest(),
                "sha256": hashlib.sha256(content).hexdigest()
            }
    
    is_encrypted = False
    total_entries = 0
    uncompressed_total_size = 0
    compression_methods = set()
    file_types = {}
    largest_file = {"name": "", "size": 0}
    oldest_file = {"name": "", "date": None}
    newest_file = {"name": "", "date": None}
    
    try:
        with pyzipper.AESZipFile(zip_path, 'r') as zip_file:
            if password:
                zip_file.setpassword(password.encode('utf-8'))
            
            for file_info in zip_file.infolist():
                total_entries += 1
                
                # Check if encrypted
                if file_info.flag_bits & 0x1:  # Encryption bit
                    is_encrypted = True
                
                # Skip directories for size calculations
                if not file_info.is_dir():
                    uncompressed_total_size += file_info.file_size
                    
                    # Track compression methods
                    compression_methods.add(_get_compression_method(file_info.compress_type))
                    
                    # Track file types
                    file_ext = os.path.splitext(file_info.filename)[1].lower()
                    if file_ext in file_types:
                        file_types[file_ext] += 1
                    else:
                        file_types[file_ext] = 1
                    
                    # Track largest file
                    if file_info.file_size > largest_file["size"]:
                        largest_file = {"name": file_info.filename, "size": file_info.file_size}
                    
                    # Track oldest and newest files
                    try:
                        file_date = datetime.datetime(*file_info.date_time)
                        if oldest_file["date"] is None or file_date < oldest_file["date"]:
                            oldest_file = {"name": file_info.filename, "date": file_date}
                        if newest_file["date"] is None or file_date > newest_file["date"]:
                            newest_file = {"name": file_info.filename, "date": file_date}
                    except (ValueError, TypeError):
                        pass
    
    except Exception as e:
        if "Bad password" in str(e) or "password required" in str(e).lower():
            is_encrypted = True
        # Continue with basic file information even if ZIP can't be opened
    
    # Prepare file info
    file_info_data = {
        "filename": os.path.basename(zip_path),
        "full_path": zip_path,
        "size_bytes": size_on_disk,
        "size_mb": round(size_on_disk / 1024 / 1024, 3),
        "created": created_time,
        "modified": modified_time,
        "is_encrypted": is_encrypted
    }
    
    if file_checksums:
        file_info_data.update(file_checksums)
    
    # Prepare archive statistics
    compression_ratio = 0.0
    if uncompressed_total_size > 0:
        compression_ratio = ((uncompressed_total_size - size_on_disk) / uncompressed_total_size) * 100
    
    archive_stats_data = {
        "total_entries": total_entries,
        "uncompressed_total_size_bytes": uncompressed_total_size,
        "uncompressed_total_size_mb": round(uncompressed_total_size / 1024 / 1024, 3),
        "compressed_size_bytes": size_on_disk,
        "compressed_size_mb": round(size_on_disk / 1024 / 1024, 3),
        "compression_ratio_percent": round(compression_ratio, 2),
        "compression_methods": list(compression_methods) if compression_methods else ["Unknown"],
        "file_types_count": dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True)),
        "largest_file": largest_file,
        "oldest_file": {
            "name": oldest_file["name"],
            "date": oldest_file["date"].strftime("%Y-%m-%d %H:%M:%S") if oldest_file["date"] else "Unknown"
        },
        "newest_file": {
            "name": newest_file["name"], 
            "date": newest_file["date"].strftime("%Y-%m-%d %H:%M:%S") if newest_file["date"] else "Unknown"
        }
    }
    
    # Convert to DataFrames
    file_info_df = pd.DataFrame([file_info_data])
    archive_stats_df = pd.DataFrame([archive_stats_data])
    
    # Determine primary compression method
    primary_compression = list(compression_methods)[0] if compression_methods else "Unknown"
    
    return {
        "file_info": file_info_df,
        "archive_stats": archive_stats_df,
        "is_encrypted": is_encrypted,
        "compression_method": primary_compression,
        "total_entries": total_entries,
        "size_on_disk": size_on_disk,
        "uncompressed_total_size": uncompressed_total_size
    }

def _get_compression_method(compress_type):
    """Helper function to map compression type to method name"""
    compression_map = {
        0: "Stored (no compression)",
        8: "DEFLATED",
        12: "BZIP2", 
        14: "LZMA"
    }
    return compression_map.get(compress_type, f"Unknown ({compress_type})")