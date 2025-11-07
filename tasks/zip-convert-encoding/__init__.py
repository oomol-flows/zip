#region generated meta
import typing
class Inputs(typing.TypedDict):
    zip_path: str
    output_path: str
    source_encoding: typing.Literal["gbk", "gb2312", "big5", "shift_jis", "euc-kr", "cp437", "auto"]
    target_encoding: typing.Literal["utf-8", "gbk", "gb2312", "big5", "shift_jis", "euc-kr"]
    fix_garbled_names: bool
    password: str | None
    output_password: str | None
    preserve_timestamps: bool
class Outputs(typing.TypedDict):
    converted_zip_path: typing.NotRequired[str]
    conversion_summary: typing.NotRequired[typing.Any]
    files_converted: typing.NotRequired[float]
    encoding_issues_found: typing.NotRequired[float]
    detected_encoding: typing.NotRequired[str]
#endregion

from oocana import Context
import os
import chardet
import pandas as pd
import pyzipper

def main(params: Inputs, context: Context) -> Outputs:
    """
    Convert ZIP file encoding to fix filename issues
    
    Args:
        params: Input parameters for encoding conversion
        context: OOMOL context object
        
    Returns:
        Information about the encoding conversion process
    """
    zip_path = params["zip_path"]
    output_path = params["output_path"]
    source_encoding = params["source_encoding"]
    target_encoding = params["target_encoding"]
    password = params.get("password")
    output_password = params.get("output_password")
    fix_garbled_names = params["fix_garbled_names"]
    preserve_timestamps = params["preserve_timestamps"]
    
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"ZIP file does not exist: {zip_path}")
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    files_converted = 0
    encoding_issues_found = 0
    detected_encoding = "unknown"
    conversion_details = []
    
    # Common encodings to try for auto-detection
    common_encodings = ['gbk', 'gb2312', 'big5', 'shift_jis', 'euc-kr', 'cp437', 'utf-8']
    
    def detect_filename_encoding(raw_filename_bytes):
        """Detect encoding of filename bytes"""
        if source_encoding != "auto":
            return source_encoding
        
        # Try chardet first
        try:
            detection = chardet.detect(raw_filename_bytes)
            if detection and detection['confidence'] > 0.7:
                return detection['encoding'].lower()
        except:
            pass
        
        # Try common encodings
        for encoding in common_encodings:
            try:
                decoded = raw_filename_bytes.decode(encoding)
                # Check if contains valid characters (not just replacement characters)
                if '\ufffd' not in decoded:
                    return encoding
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        return 'utf-8'  # Fallback
    
    def fix_garbled_chinese(filename):
        """Attempt to fix garbled Chinese filenames"""
        if not fix_garbled_names:
            return filename
        
        # Common garbled patterns for Chinese characters
        fixes = [
            # Try to decode as if it was wrongly encoded
            lambda s: s.encode('latin1').decode('gbk', errors='ignore'),
            lambda s: s.encode('latin1').decode('gb2312', errors='ignore'),
            lambda s: s.encode('cp437').decode('gbk', errors='ignore'),
        ]
        
        for fix_func in fixes:
            try:
                fixed = fix_func(filename)
                # Check if the fix produced readable Chinese characters
                if any('\u4e00' <= char <= '\u9fff' for char in fixed):
                    return fixed
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        return filename
    
    # Read source ZIP and create output ZIP
    output_encryption = pyzipper.WZ_AES256 if output_password else None
    
    with pyzipper.AESZipFile(zip_path, 'r') as source_zip:
        if password:
            source_zip.setpassword(password.encode('utf-8'))
        
        with pyzipper.AESZipFile(output_path, 'w', compression=pyzipper.ZIP_DEFLATED, 
                                encryption=output_encryption) as output_zip:
            
            if output_password:
                output_zip.setpassword(output_password.encode('utf-8'))
            
            for file_info in source_zip.infolist():
                original_filename = file_info.filename
                converted_filename = original_filename
                had_encoding_issue = False
                conversion_method = "no_change"
                
                try:
                    # Check if filename has encoding issues
                    filename_bytes = original_filename.encode('cp437', errors='ignore')
                    
                    # Auto-detect or use specified encoding
                    if source_encoding == "auto":
                        detected_encoding = detect_filename_encoding(filename_bytes)
                    else:
                        detected_encoding = source_encoding
                    
                    # Try to decode with detected/specified encoding
                    if detected_encoding != 'utf-8':
                        try:
                            decoded_filename = filename_bytes.decode(detected_encoding)
                            converted_filename = decoded_filename
                            conversion_method = f"decoded_from_{detected_encoding}"
                            had_encoding_issue = True
                        except (UnicodeDecodeError, UnicodeError):
                            # Try garbled name fixing
                            fixed_filename = fix_garbled_chinese(original_filename)
                            if fixed_filename != original_filename:
                                converted_filename = fixed_filename
                                conversion_method = "garbled_fix"
                                had_encoding_issue = True
                    
                    # Convert to target encoding if different from UTF-8
                    if target_encoding != 'utf-8':
                        try:
                            converted_filename = converted_filename.encode(target_encoding, errors='ignore').decode(target_encoding)
                        except (UnicodeDecodeError, UnicodeError):
                            pass  # Keep UTF-8 version
                    
                    # Read file data
                    file_data = source_zip.read(original_filename)
                    
                    # Create new ZipInfo with corrected filename
                    new_info = pyzipper.ZipInfo(converted_filename)
                    if preserve_timestamps:
                        new_info.date_time = file_info.date_time
                    new_info.compress_type = file_info.compress_type
                    
                    # Write to output ZIP
                    output_zip.writestr(new_info, file_data)
                    
                    files_converted += 1
                    if had_encoding_issue:
                        encoding_issues_found += 1
                    
                    conversion_details.append({
                        "original_filename": original_filename,
                        "converted_filename": converted_filename,
                        "had_encoding_issue": had_encoding_issue,
                        "conversion_method": conversion_method,
                        "detected_encoding": detected_encoding if had_encoding_issue else "utf-8",
                        "file_size": file_info.file_size
                    })
                    
                except Exception as e:
                    # Log conversion error but continue
                    conversion_details.append({
                        "original_filename": original_filename,
                        "converted_filename": original_filename,  # Keep original on error
                        "had_encoding_issue": True,
                        "conversion_method": f"error_{str(e)[:30]}",
                        "detected_encoding": "error",
                        "file_size": getattr(file_info, 'file_size', 0)
                    })
    
    # Create summary DataFrame
    summary_df = pd.DataFrame(conversion_details)
    
    # Add summary statistics
    if not summary_df.empty:
        summary_stats = {
            "original_file": os.path.basename(zip_path),
            "converted_file": os.path.basename(output_path),
            "source_encoding_setting": source_encoding,
            "target_encoding": target_encoding,
            "total_files": len(conversion_details),
            "files_with_issues": encoding_issues_found,
            "files_converted": files_converted,
            "success_rate": round((files_converted / len(conversion_details)) * 100, 1) if conversion_details else 0,
            "most_detected_encoding": detected_encoding
        }
        
        # Add summary row
        summary_row = pd.DataFrame([summary_stats])
        summary_df = pd.concat([summary_df, pd.DataFrame([{}]), summary_row], ignore_index=True)
    
    return {
        "converted_zip_path": output_path,
        "conversion_summary": summary_df,
        "files_converted": files_converted,
        "encoding_issues_found": encoding_issues_found,
        "detected_encoding": detected_encoding
    }