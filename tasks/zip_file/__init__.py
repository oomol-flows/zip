from oocana import Context
import pyzipper
import os
#region generated meta
import typing
class Inputs(typing.TypedDict):
    file_to_zip: str
    zip_file_name: str | None
    password: str | None
class Outputs(typing.TypedDict):
    output: str
#endregion

def main(params: Inputs, context: Context) -> Outputs:

    # 要压缩的文件路径
    file_to_zip = params.get("file_to_zip")
    # 输出的ZIP文件路径
    zip_file_name = params.get("zip_file_name")
    # 密码
    password = params.get("password")

    if zip_file_name is None:
        base_name = os.path.basename(file_to_zip)
        dir_name = os.path.dirname(file_to_zip)
        zip_file_name = base_name + ".zip"
        zip_file_path = os.path.join(dir_name, zip_file_name)
        count = 1
        while os.path.exists(zip_file_path):
            zip_file_name = f"{base_name}_{count}.zip"
            zip_file_path = os.path.join(dir_name, zip_file_name)
            count += 1
    else:
        zip_file_path = zip_file_name

    # 创建一个新的ZIP文件
    create_encrypted_zip_no_path(file_to_zip, zip_file_path, password)

    return { "output": zip_file_path }

def create_encrypted_zip_no_path(source_file, zip_path, password):
    # 只获取文件名，不含路径
    base_name = os.path.basename(source_file)

    with pyzipper.AESZipFile(zip_path, 'w', compression=pyzipper.ZIP_DEFLATED) as zf:
        if password is not None:
            zf.setpassword(password.encode())
            zf.setencryption(pyzipper.WZ_AES, nbits=128)
        # 使用 arcname 指定文件名（不含路径）
        zf.write(source_file, arcname=base_name)