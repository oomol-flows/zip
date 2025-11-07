#region generated meta
import typing
class Inputs(typing.TypedDict):
    zip_path: str
    password: str | None
    test_extraction: bool
    check_crc: bool
    max_files_to_test: int
class Outputs(typing.TypedDict):
    is_valid: typing.NotRequired[bool]
    validation_summary: typing.NotRequired[dict]
    tested_files_count: typing.NotRequired[float]
    corrupted_files: typing.NotRequired[list[str]]
    validation_errors: typing.NotRequired[list[str]]
    can_open_archive: typing.NotRequired[bool]
#endregion

from oocana import Context
import os
import tempfile
import pandas as pd
import pyzipper
import zlib

def main(params: Inputs, context: Context) -> Outputs:
    """
    Validate ZIP archive integrity and test file extraction
    
    Args:
        params: Input parameters for ZIP validation
        context: OOMOL context object
        
    Returns:
        Comprehensive validation results and error information
    """
    zip_path = params["zip_path"]
    password = params.get("password")
    test_extraction = params["test_extraction"]
    check_crc = params["check_crc"]
    max_files_to_test = params["max_files_to_test"]
    
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"ZIP file does not exist: {zip_path}")
    
    validation_errors = []
    corrupted_files = []
    tested_files_count = 0
    can_open_archive = False
    is_valid = True
    
    # Check if file is actually a ZIP file
    try:
        with open(zip_path, 'rb') as f:
            header = f.read(4)
            if not header.startswith(b'PK'):
                validation_errors.append("File does not have valid ZIP header")
                is_valid = False
    except Exception as e:
        validation_errors.append(f"Cannot read file: {str(e)}")
        is_valid = False
    
    if is_valid:
        try:
            with pyzipper.AESZipFile(zip_path, 'r') as zip_file:
                can_open_archive = True
                
                if password:
                    zip_file.setpassword(password.encode('utf-8'))
                
                # Get list of files to test
                file_list = [info for info in zip_file.infolist() if not info.is_dir()]
                
                # Limit number of files to test if specified
                if max_files_to_test > 0 and len(file_list) > max_files_to_test:
                    file_list = file_list[:max_files_to_test]
                
                tested_files_count = len(file_list)
                
                for file_info in file_list:
                    try:
                        # Test if file can be opened
                        with zip_file.open(file_info.filename) as test_file:
                            if check_crc:
                                # Read file content and verify CRC
                                content = test_file.read()
                                calculated_crc = zlib.crc32(content) & 0xffffffff
                                
                                if calculated_crc != file_info.CRC:
                                    corrupted_files.append(file_info.filename)
                                    validation_errors.append(f"CRC mismatch for {file_info.filename}")
                                    is_valid = False
                            
                            elif test_extraction:
                                # Test extraction to temporary location
                                with tempfile.NamedTemporaryFile() as temp_file:
                                    temp_file.write(test_file.read())
                    
                    except Exception as e:
                        corrupted_files.append(file_info.filename)
                        validation_errors.append(f"Cannot extract {file_info.filename}: {str(e)}")
                        is_valid = False
                
                # Test ZIP file structure
                try:
                    zip_file.testzip()
                except Exception as e:
                    validation_errors.append(f"ZIP structure test failed: {str(e)}")
                    is_valid = False
                
        except Exception as e:
            can_open_archive = False
            validation_errors.append(f"Cannot open ZIP archive: {str(e)}")
            is_valid = False
    
    # Prepare validation summary
    validation_results = {
        "file_path": zip_path,
        "can_open_archive": can_open_archive,
        "is_valid": is_valid,
        "total_errors": len(validation_errors),
        "corrupted_files_count": len(corrupted_files),
        "tested_files_count": tested_files_count,
        "validation_method": {
            "crc_checked": check_crc,
            "extraction_tested": test_extraction,
            "max_files_limit": max_files_to_test if max_files_to_test > 0 else "No limit"
        }
    }
    
    if validation_errors:
        validation_results["errors"] = validation_errors[:10]  # Limit to first 10 errors
        if len(validation_errors) > 10:
            validation_results["additional_errors"] = len(validation_errors) - 10
    
    if corrupted_files:
        validation_results["corrupted_files"] = corrupted_files[:10]  # Limit to first 10 files
        if len(corrupted_files) > 10:
            validation_results["additional_corrupted_files"] = len(corrupted_files) - 10
    
    validation_summary_df = pd.DataFrame([validation_results])
    
    return {
        "is_valid": is_valid,
        "validation_summary": validation_summary_df,
        "tested_files_count": tested_files_count,
        "corrupted_files": corrupted_files,
        "validation_errors": validation_errors,
        "can_open_archive": can_open_archive
    }