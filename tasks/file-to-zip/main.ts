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
  zip.getEntries(); // Get all entries in the ZIP file
  // Check if the source path is a file or a directory
  const stats = fs.statSync(sourcePath);

  if (stats.isFile()) {
      // If it's a file, add it directly to the ZIP
      zip.addLocalFile(sourcePath);
  } else if (stats.isDirectory()) {
      // If it's a folder, recursively add all files in the folder
      zip.addLocalFolder(sourcePath);
  } else {
      throw new Error('Source path is neither a file nor a directory');
  }

  // Write the ZIP file to disk
  zip.writeZip(outputPath);
  console.log(`ZIP file successfully created: ${outputPath}`);
}
