import type { Context } from "@oomol/types/oocana";
import fs from "fs";
import path from "path";
import AdmZip from "adm-zip";

type Inputs = {
  file_path: string;
  save_path: string | null;
}
type Outputs = {
  zip_address: string;
}

export default async function (
  params: Inputs,
  context: Context<Inputs, Outputs>
): Promise<Outputs> {
  const { file_path, save_path } = params;

  const fileName = path.basename(file_path);

  const outputFilePath = save_path ? `${save_path}/${fileName}.zip` : `${context.sessionDir}/${fileName}.zip`;

  zipFileOrFolder(file_path, outputFilePath);

  return { zip_address: outputFilePath };
};

function zipFileOrFolder(sourcePath:string, outputPath: string) {
  const zip = new AdmZip();
  zip.getEntries(); // 获取 ZIP 文件中的所有条目
  // 检查源路径是文件还是文件夹
  const stats = fs.statSync(sourcePath);

  if (stats.isFile()) {
      // 如果是文件，直接添加到 ZIP
      const fileName = path.basename(sourcePath);
      zip.addLocalFile(sourcePath);
  } else if (stats.isDirectory()) {
      // 如果是文件夹，递归添加文件夹中的所有文件
      zip.addLocalFolder(sourcePath);
  } else {
      throw new Error('源路径既不是文件也不是文件夹');
  }

  // 将 ZIP 文件写入磁盘
  zip.writeZip(outputPath);
  console.log(`ZIP 文件已成功创建: ${outputPath}`);
}