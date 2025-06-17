from oocana import Context
import pyzipper
import os
#region generated meta
import typing
class Inputs(typing.TypedDict):
    zip_file: str
    zip_dir: str | None
    password: str | None
class Outputs(typing.TypedDict):
    output: str
#endregion

def main(params: Inputs, context: Context) -> Outputs:

    # path of the file to be compressed
    zip_file = params.get("zip_file")
    # path of the output ZIP file
    zip_dir = params.get("zip_dir")
    if zip_dir is None:
        zip_dir = context.session_dir
    # password
    password = params.get("password")

    extract_zip(zip_file, zip_dir, password)

    return { "output": zip_dir }
    

def extract_zip(zip_path, extract_dir, password=None):
    try:
        with pyzipper.AESZipFile(zip_path) as zf:
            # If there is a password
            if password:
                zf.pwd = password.encode('utf-8')  # password must be converted to bytes
            
            # Extract all files to the specified directory
            zf.extractall(extract_dir)
            print(f"Successfully extracted to {extract_dir}")
    
    except RuntimeError as e:
        if 'encrypted' in str(e).lower():
            raise RuntimeError("Error: File is encrypted but no password was provided or the password is incorrect") from e
        else:
            raise RuntimeError(f"Extraction error: {e}") from e
    except FileNotFoundError:
        raise FileNotFoundError("Error: ZIP file not found")
    except Exception as e:
        raise Exception(f"Unknown error: {e}") from e