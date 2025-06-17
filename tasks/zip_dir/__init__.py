from oocana import Context
import pyzipper
import os
#region generated meta
import typing
class Inputs(typing.TypedDict):
    # path to the directory to be zipped
    dir_to_zip: str
    # output ZIP file name
    zip_file_name: str | None
    # password for the ZIP file
    password: str | None
class Outputs(typing.TypedDict):
    output: str
#endregion

def main(params: Inputs, context: Context) -> Outputs:

    # Path to the file to be compressed
    dir_to_zip = params.get("dir_to_zip")
    # Output ZIP file path
    zip_file_name = params.get("zip_file_name")

    if zip_file_name is None:
        base_name = os.path.basename(dir_to_zip)
        dir_name = os.path.dirname(dir_to_zip)
        zip_file_name = base_name + ".zip"
        zip_file_path = os.path.join(dir_name, zip_file_name)
        count = 1
        while os.path.exists(zip_file_path):
            zip_file_name = f"{base_name}_{count}.zip"
            zip_file_path = os.path.join(dir_name, zip_file_name)
            count += 1
    else:
        zip_file_path = zip_file_name

    # Check if the output path is within the compressed folder
    if os.path.commonpath([dir_to_zip, zip_file_path]) == dir_to_zip:
        raise ValueError("Output file cannot be inside the compressed folder")

    # Password
    password = params.get("password")

    # Create a new ZIP file
    zip_directory_no_path(dir_to_zip, zip_file_path, password)

    return { "output": zip_file_path }

def zip_directory_no_path(source_dir, zip_path, password):
    with pyzipper.AESZipFile(zip_path, 'w', compression=pyzipper.ZIP_DEFLATED) as zf:
        if password is not None:
            zf.setpassword(password.encode())
            zf.setencryption(pyzipper.WZ_AES, nbits=128)

        # Iterate through the directory (including subdirectories)
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Calculate the relative path (to strip the source directory structure)
                relative_path = os.path.relpath(root, source_dir)

                if relative_path == '.':
                    # Root directory files use the file name directly
                    zf.write(file_path, arcname=file)
                else:
                    # Subdirectory files concatenate the relative path + file name (but strip the source directory structure)
                    arcname = os.path.join(relative_path, file)
                    zf.write(file_path, arcname=arcname)