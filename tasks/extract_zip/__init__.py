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

    # 要压缩的文件路径
    zip_file = params.get("zip_file")
    # 输出的ZIP文件路径
    zip_dir = params.get("zip_dir")
    if zip_dir is None:
        zip_dir = context.session_dir
    # 密码
    password = params.get("password")

    extract_zip(zip_file, zip_dir, password)

    return { "output": zip_dir }
    

def extract_zip(zip_path, extract_dir, password=None):
    try:
        with pyzipper.AESZipFile(zip_path) as zf:
            # 如果有密码
            if password:
                zf.pwd = password.encode('utf-8')  # 密码必须转为bytes
            
            # 解压所有文件到指定目录
            zf.extractall(extract_dir)
            print(f"成功解压到 {extract_dir}")
    
    except RuntimeError as e:
        if 'encrypted' in str(e).lower():
            raise RuntimeError("错误：文件被加密但未提供密码或密码错误") from e
        else:
            raise RuntimeError(f"解压错误: {e}") from e
    except FileNotFoundError:
        raise FileNotFoundError("错误：ZIP文件不存在")
    except Exception as e:
        raise Exception(f"未知错误: {e}") from e