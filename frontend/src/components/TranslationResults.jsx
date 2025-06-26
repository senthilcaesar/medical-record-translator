import React from "react";
import ReactMarkdown from "react-markdown";
import { FiFileText, FiDownload, FiRefreshCw } from "react-icons/fi";

const TranslationResults = ({ result, onNewTranslation }) => {
  const { document_type, sections, translation } = result.result;

  const handleDownload = () => {
    const content = translation;
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `medical-record-translation-${
      new Date().toISOString().split("T")[0]
    }.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const renderSection = (title, content) => {
    if (!content || content.trim() === "") return null;

    return (
      <div className="mb-6">
        <h3 className="section-header flex items-center gap-2">
          <FiFileText className="text-primary-600" />
          {title}
        </h3>
        <div className="prose prose-gray max-w-none">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      </div>
    );
  };

  const getDocumentTypeLabel = (type) => {
    switch (type) {
      case "lab_results":
        return "Lab Results";
      case "prescription":
        return "Prescription";
      default:
        return "Medical Document";
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Translation Complete
          </h2>
          <p className="text-gray-600 mt-1">
            Document Type:{" "}
            <span className="font-medium">
              {getDocumentTypeLabel(document_type)}
            </span>
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleDownload}
            className="btn-secondary flex items-center gap-2"
          >
            <FiDownload />
            Download
          </button>
          <button
            onClick={onNewTranslation}
            className="btn-primary flex items-center gap-2"
          >
            <FiRefreshCw />
            New Translation
          </button>
        </div>
      </div>

      {/* Lab Results with Conversational Format */}
      {document_type === "lab_results" && sections && (
        <div className="space-y-6">
          {/* Conversational Sections */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="bg-gradient-to-r from-green-50 to-blue-50 px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
                <span className="text-2xl">📋</span>
                Your Lab Results Explained
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                A caring explanation of what your results mean for your health
              </p>
            </div>
            
            <div className="p-6 space-y-8">
              {/* Good News Section */}
              {sections.good_news && (
                <div className="bg-green-50 border-l-4 border-green-400 p-6 rounded-r-lg">
                  <h4 className="text-lg font-semibold text-green-800 mb-3 flex items-center gap-2">
                    <span className="text-xl">🎉</span>
                    First, the good news about your results...
                  </h4>
                  <div className="prose prose-green max-w-none text-green-700">
                    <ReactMarkdown>{sections.good_news}</ReactMarkdown>
                  </div>
                </div>
              )}

              {/* Keep Eye On Section */}
              {sections.keep_eye_on && (
                <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6 rounded-r-lg">
                  <h4 className="text-lg font-semibold text-yellow-800 mb-3 flex items-center gap-2">
                    <span className="text-xl">👀</span>
                    Here's what we need to keep an eye on...
                  </h4>
                  <div className="prose prose-yellow max-w-none text-yellow-700">
                    <ReactMarkdown>{sections.keep_eye_on}</ReactMarkdown>
                  </div>
                </div>
              )}

              {/* Should Worry Section */}
              {sections.should_worry && (
                <div className="bg-blue-50 border-l-4 border-blue-400 p-6 rounded-r-lg">
                  <h4 className="text-lg font-semibold text-blue-800 mb-3 flex items-center gap-2">
                    <span className="text-xl">🤔</span>
                    Should you be worried?
                  </h4>
                  <div className="prose prose-blue max-w-none text-blue-700">
                    <ReactMarkdown>{sections.should_worry}</ReactMarkdown>
                  </div>
                </div>
              )}

              {/* Daily Life Section */}
              {sections.daily_life && (
                <div className="bg-purple-50 border-l-4 border-purple-400 p-6 rounded-r-lg">
                  <h4 className="text-lg font-semibold text-purple-800 mb-3 flex items-center gap-2">
                    <span className="text-xl">🏃‍♀️</span>
                    What this means for your daily life...
                  </h4>
                  <div className="prose prose-purple max-w-none text-purple-700">
                    <ReactMarkdown>{sections.daily_life}</ReactMarkdown>
                  </div>
                </div>
              )}

              {/* Next Steps Section */}
              {sections.next_steps && (
                <div className="bg-indigo-50 border-l-4 border-indigo-400 p-6 rounded-r-lg">
                  <h4 className="text-lg font-semibold text-indigo-800 mb-3 flex items-center gap-2">
                    <span className="text-xl">📝</span>
                    Your next steps...
                  </h4>
                  <div className="prose prose-indigo max-w-none text-indigo-700">
                    <ReactMarkdown>{sections.next_steps}</ReactMarkdown>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Prescription Results with Conversational Format */}
      {document_type === "prescription" && sections && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
                <span className="text-2xl">💊</span>
                Your Prescription Explained
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                A caring explanation of your medications and how to take them
              </p>
            </div>
            
            <div className="p-6 space-y-8">
              {/* Prescribed Medications Section */}
              {sections.prescribed_medications && (
                <div className="bg-blue-50 border-l-4 border-blue-400 p-6 rounded-r-lg">
                  <h4 className="text-lg font-semibold text-blue-800 mb-3 flex items-center gap-2">
                    <span className="text-xl">📋</span>
                    Here's what your doctor has prescribed for you...
                  </h4>
                  <div className="prose prose-blue max-w-none text-blue-700">
                    <ReactMarkdown>{sections.prescribed_medications}</ReactMarkdown>
                  </div>
                </div>
              )}

              {/* Medicine Purposes Section */}
              {sections.medicine_purposes && (
                <div className="bg-green-50 border-l-4 border-green-400 p-6 rounded-r-lg">
                  <h4 className="text-lg font-semibold text-green-800 mb-3 flex items-center gap-2">
                    <span className="text-xl">🎯</span>
                    What each medicine does for your health...
                  </h4>
                  <div className="prose prose-green max-w-none text-green-700">
                    <ReactMarkdown>{sections.medicine_purposes}</ReactMarkdown>
                  </div>
                </div>
              )}

              {/* Medication Instructions Section */}
              {sections.medication_instructions && (
                <div className="bg-purple-50 border-l-4 border-purple-400 p-6 rounded-r-lg">
                  <h4 className="text-lg font-semibold text-purple-800 mb-3 flex items-center gap-2">
                    <span className="text-xl">⏰</span>
                    How to take your medications properly...
                  </h4>
                  <div className="prose prose-purple max-w-none text-purple-700">
                    <ReactMarkdown>{sections.medication_instructions}</ReactMarkdown>
                  </div>
                </div>
              )}

              {/* Side Effects Section */}
              {sections.side_effects && (
                <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6 rounded-r-lg">
                  <h4 className="text-lg font-semibold text-yellow-800 mb-3 flex items-center gap-2">
                    <span className="text-xl">⚠️</span>
                    What to expect and side effects to know about...
                  </h4>
                  <div className="prose prose-yellow max-w-none text-yellow-700">
                    <ReactMarkdown>{sections.side_effects}</ReactMarkdown>
                  </div>
                </div>
              )}

              {/* Important Warnings Section */}
              {sections.important_warnings && (
                <div className="bg-red-50 border-l-4 border-red-400 p-6 rounded-r-lg">
                  <h4 className="text-lg font-semibold text-red-800 mb-3 flex items-center gap-2">
                    <span className="text-xl">🚨</span>
                    Important things to remember...
                  </h4>
                  <div className="prose prose-red max-w-none text-red-700">
                    <ReactMarkdown>{sections.important_warnings}</ReactMarkdown>
                  </div>
                </div>
              )}

              {/* Pharmacist Questions Section */}
              {sections.pharmacist_questions && (
                <div className="bg-indigo-50 border-l-4 border-indigo-400 p-6 rounded-r-lg">
                  <h4 className="text-lg font-semibold text-indigo-800 mb-3 flex items-center gap-2">
                    <span className="text-xl">❓</span>
                    Questions to ask your pharmacist...
                  </h4>
                  <div className="prose prose-indigo max-w-none text-indigo-700">
                    <ReactMarkdown>{sections.pharmacist_questions}</ReactMarkdown>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Fallback for unstructured content */}
      {!sections && (
        <div className="card">
          <div className="prose prose-gray max-w-none">
            <ReactMarkdown>{translation}</ReactMarkdown>
          </div>
        </div>
      )}

      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-800">
          <strong>Important:</strong> This translation is provided for
          educational purposes only. Always consult with your healthcare
          provider for medical advice and clarification.
        </p>
      </div>
    </div>
  );
};

export default TranslationResults;
