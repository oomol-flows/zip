from oocana import Context
import pyzipper
import os
#region generated meta
import typing
class Inputs(typing.TypedDict):
    dir_to_zip: str
    zip_file_name: str | None
    password: str | None
class Outputs(typing.TypedDict):
    output: str
#endregion

def main(params: Inputs, context: Context) -> Outputs:

    # 要压缩的文件路径
    dir_to_zip = params.get("dir_to_zip")
    # 输出的ZIP文件路径
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

    # 密码
    password = params.get("password")

    # 创建一个新的ZIP文件
    zip_directory_no_path(dir_to_zip, zip_file_path, password)

    return { "output": zip_file_path }

def zip_directory_no_path(source_dir, zip_path, password):
    with pyzipper.AESZipFile(zip_path, 'w', compression=pyzipper.ZIP_DEFLATED) as zf:
        if password is not None:
            zf.setpassword(password.encode())
            zf.setencryption(pyzipper.WZ_AES, nbits=128)

        # 遍历目录（包括子目录）
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # 计算相对路径（用于剥离源目录结构）
                relative_path = os.path.relpath(root, source_dir)

                if relative_path == '.':
                    # 根目录文件直接使用文件名
                    zf.write(file_path, arcname=file)
                else:
                    # 子目录文件拼接相对路径+文件名（但剥离了源目录结构）
                    arcname = os.path.join(relative_path, file)
                    zf.write(file_path, arcname=arcname)