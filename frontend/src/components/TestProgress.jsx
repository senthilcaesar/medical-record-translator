import React, { useState } from "react";
import LoadingSpinner from "./LoadingSpinner";

const TestProgress = () => {
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("Processing...");

  const simulateProgress = () => {
    setProgress(0);
    setMessage("Extracting text from your document...");

    setTimeout(() => {
      setProgress(20);
      setMessage("Extracting text from your document...");
    }, 1000);

    setTimeout(() => {
      setProgress(40);
      setMessage("Identifying document type...");
    }, 2000);

    setTimeout(() => {
      setProgress(60);
      setMessage("Translating medical terminology...");
    }, 3000);

    setTimeout(() => {
      setProgress(80);
      setMessage("Finalizing translation...");
    }, 4000);

    setTimeout(() => {
      setProgress(100);
      setMessage("Translation complete!");
    }, 5000);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold mb-8">Progress Bar Test</h1>

        <div className="card mb-4">
          <h2 className="text-lg font-semibold mb-4">
            Current Progress: {progress}%
          </h2>
          <button onClick={simulateProgress} className="btn-primary mb-6">
            Simulate Progress
          </button>

          <LoadingSpinner message={message} progress={progress} />
        </div>

        <div className="card">
          <h3 className="font-semibold mb-2">Manual Controls</h3>
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => setProgress(0)}
              className="px-3 py-1 bg-gray-200 rounded"
            >
              0%
            </button>
            <button
              onClick={() => setProgress(20)}
              className="px-3 py-1 bg-gray-200 rounded"
            >
              20%
            </button>
            <button
              onClick={() => setProgress(40)}
              className="px-3 py-1 bg-gray-200 rounded"
            >
              40%
            </button>
            <button
              onClick={() => setProgress(60)}
              className="px-3 py-1 bg-gray-200 rounded"
            >
              60%
            </button>
            <button
              onClick={() => setProgress(80)}
              className="px-3 py-1 bg-gray-200 rounded"
            >
              80%
            </button>
            <button
              onClick={() => setProgress(100)}
              className="px-3 py-1 bg-gray-200 rounded"
            >
              100%
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TestProgress;
