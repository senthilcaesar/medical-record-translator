import React, { useState } from "react";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import FileUpload from "./components/FileUpload";
import LoadingSpinner from "./components/LoadingSpinner";
import TranslationResults from "./components/TranslationResults";
import { translationAPI, pollJobStatus } from "./services/api";
import { FiHeart, FiShield, FiZap } from "react-icons/fi";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [processingMessage, setProcessingMessage] = useState("");

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setResult(null);
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setResult(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setIsProcessing(true);
    setProgress(0);

    try {
      // Upload the file
      const uploadResponse = await translationAPI.uploadDocument(selectedFile);
      const jobId = uploadResponse.job_id;

      toast.success("File uploaded successfully!");

      // Poll for status
      pollJobStatus(
        jobId,
        (status) => {
          // Update progress
          setProgress(status.progress || 0);

          // Update message based on status
          switch (status.status) {
            case "extracting_text":
              setProcessingMessage("Extracting text from your document...");
              break;
            case "identifying_document_type":
              setProcessingMessage("Identifying document type...");
              break;
            case "translating":
              setProcessingMessage("Translating medical terminology...");
              break;
            default:
              setProcessingMessage("Processing your document...");
          }
        },
        (result) => {
          // Success
          setResult(result);
          setIsProcessing(false);
          setIsUploading(false);
          toast.success("Translation completed successfully!");
        },
        (error) => {
          // Error
          console.error("Translation error:", error);
          toast.error(error.message || "Translation failed. Please try again.");
          setIsProcessing(false);
          setIsUploading(false);
        }
      );
    } catch (error) {
      console.error("Upload error:", error);
      toast.error("Failed to upload file. Please try again.");
      setIsProcessing(false);
      setIsUploading(false);
    }
  };

  const handleNewTranslation = () => {
    setSelectedFile(null);
    setResult(null);
    setProgress(0);
    setProcessingMessage("");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <ToastContainer position="top-right" />

      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Medical Record Translator
              </h1>
              <p className="mt-2 text-gray-600">
                Understand your health records in plain English
              </p>
            </div>
            <div className="hidden md:flex items-center space-x-6">
              <div className="flex items-center text-sm text-gray-600">
                <FiShield className="mr-2 text-primary-600" />
                Secure & Private
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <FiZap className="mr-2 text-primary-600" />
                AI-Powered
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {!result ? (
          <div className="max-w-2xl mx-auto">
            {/* Features */}
            {!selectedFile && !isProcessing && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                <div className="text-center">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <FiShield className="text-primary-600 text-xl" />
                  </div>
                  <h3 className="font-semibold text-gray-900">100% Private</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Your data is never stored
                  </p>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <FiZap className="text-primary-600 text-xl" />
                  </div>
                  <h3 className="font-semibold text-gray-900">Fast Results</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Get translations in seconds
                  </p>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <FiHeart className="text-primary-600 text-xl" />
                  </div>
                  <h3 className="font-semibold text-gray-900">
                    Easy to Understand
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Plain English explanations
                  </p>
                </div>
              </div>
            )}

            {/* Upload Section */}
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">
                Upload Your Medical Record
              </h2>

              {!isProcessing ? (
                <>
                  <FileUpload
                    onFileSelect={handleFileSelect}
                    selectedFile={selectedFile}
                    onRemoveFile={handleRemoveFile}
                    isUploading={isUploading}
                  />

                  {selectedFile && (
                    <div className="mt-6 flex justify-center">
                      <button
                        onClick={handleUpload}
                        disabled={isUploading}
                        className="btn-primary"
                      >
                        Translate Document
                      </button>
                    </div>
                  )}
                </>
              ) : (
                <LoadingSpinner
                  message={processingMessage}
                  progress={progress}
                />
              )}
            </div>

            {/* Instructions */}
            {!selectedFile && !isProcessing && (
              <div className="mt-8 text-center text-sm text-gray-600">
                <p className="mb-2">
                  Supported formats: PDF files containing lab results or
                  prescriptions
                </p>
                <p>Maximum file size: 10MB</p>
              </div>
            )}
          </div>
        ) : (
          <TranslationResults
            result={result}
            onNewTranslation={handleNewTranslation}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-600">
            © 2025 Medical Record Translator. For educational purposes only.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
