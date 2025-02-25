import type { Context } from "@oomol/types/oocana";
import fs from "fs";
import path from "path";
import AdmZip from "adm-zip";

type Inputs = {
  file_path: string;
  save_path: string | null;
}
type Outputs = {
  unzip_address: string;
}

export default async function (
  params: Inputs,
  context: Context<Inputs, Outputs>
): Promise<Outputs> {
  const { file_path, save_path } = params;

  const outputFilePath = save_path ? save_path : context.sessionDir;

  unzipFile(file_path, outputFilePath);

  return { unzip_address: outputFilePath };
};

function unzipFile(zipFilePath: string, outputDir: string) {
  // Load the ZIP file
  const zip = new AdmZip(zipFilePath);

  // Extract to the specified directory
  zip.extractAllTo(outputDir, /* overwrite */ true);

  console.log(`ZIP file successfully extracted to: ${outputDir}`);
}