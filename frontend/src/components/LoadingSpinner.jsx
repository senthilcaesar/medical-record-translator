import React from "react";

const LoadingSpinner = ({ message = "Processing...", progress = null }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div className="relative">
        <div className="w-16 h-16 border-4 border-gray-200 rounded-full"></div>
        <div className="absolute top-0 left-0 w-16 h-16 border-4 border-primary-600 rounded-full animate-spin border-t-transparent"></div>
      </div>
      <p className="mt-4 text-gray-700 font-medium">{message}</p>
      {progress !== null && (
        <div className="mt-4 w-64">
          <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
            <div
              className="bg-primary-600 h-full transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-sm text-gray-500 mt-2 text-center">{progress}%</p>
        </div>
      )}
    </div>
  );
};

export default LoadingSpinner;
