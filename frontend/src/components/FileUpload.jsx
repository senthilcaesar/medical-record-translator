import React, { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { FiUploadCloud, FiFile, FiX } from "react-icons/fi";

const FileUpload = ({
  onFileSelect,
  selectedFile,
  onRemoveFile,
  isUploading,
}) => {
  const onDrop = useCallback(
    (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        onFileSelect(acceptedFiles[0]);
      }
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
    },
    maxFiles: 1,
    disabled: isUploading,
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  return (
    <div className="w-full">
      {!selectedFile ? (
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
            transition-all duration-200 
            ${
              isDragActive
                ? "border-primary-500 bg-primary-50"
                : "border-gray-300 hover:border-primary-400 hover:bg-gray-50"
            }
            ${isUploading ? "opacity-50 cursor-not-allowed" : ""}
          `}
        >
          <input {...getInputProps()} />
          <FiUploadCloud className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <p className="text-lg font-medium text-gray-700 mb-2">
            {isDragActive
              ? "Drop your PDF here"
              : "Drag & drop your medical record"}
          </p>
          <p className="text-sm text-gray-500 mb-4">
            or click to browse from your computer
          </p>
          <p className="text-xs text-gray-400">Supports PDF files up to 10MB</p>
        </div>
      ) : (
        <div className="border-2 border-gray-200 rounded-xl p-6 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <FiFile className="h-8 w-8 text-primary-600" />
              <div>
                <p className="font-medium text-gray-900">{selectedFile.name}</p>
                <p className="text-sm text-gray-500">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            {!isUploading && (
              <button
                onClick={onRemoveFile}
                className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
                aria-label="Remove file"
              >
                <FiX className="h-5 w-5 text-gray-600" />
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
