import React from "react";
import ReactMarkdown from "react-markdown";
import { FiFileText, FiDownload, FiRefreshCw } from "react-icons/fi";
import TestResultsTable from "./TestResultsTable";

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

      {/* Lab Results with Interactive Table */}
      {document_type === "lab_results" && sections && sections.test_data && (
        <div className="space-y-8">
          {/* Interactive Test Results Table */}
          <TestResultsTable testData={sections.test_data} />

          {/* Additional Sections */}
          <div className="card">
            {renderSection("Summary", sections.summary)}
            {renderSection("Risk Assessment", sections.risk_assessment)}
            {renderSection(
              "What This Means for Your Health",
              sections.what_this_means_for_your_health
            )}
            {renderSection("Important Notes", sections.important_notes)}
            {renderSection(
              "Lifestyle Recommendations",
              sections.lifestyle_recommendations
            )}
            {renderSection("Next Steps", sections.next_steps)}
          </div>
        </div>
      )}

      {/* Fallback for Lab Results without structured data */}
      {document_type === "lab_results" && sections && !sections.test_data && (
        <div className="card">
          {renderSection("Summary", sections.summary)}
          {renderSection(
            "Detailed Test Results",
            sections.detailed_test_results
          )}
          {renderSection("Risk Assessment", sections.risk_assessment)}
          {renderSection(
            "What This Means for Your Health",
            sections.what_this_means_for_your_health
          )}
          {renderSection("Important Notes", sections.important_notes)}
          {renderSection(
            "Lifestyle Recommendations",
            sections.lifestyle_recommendations
          )}
          {renderSection("Next Steps", sections.next_steps)}
        </div>
      )}

      {/* Prescription Results */}
      {document_type === "prescription" && sections && (
        <div className="card">
          {renderSection("Medications Summary", sections.medications_summary)}
          {renderSection(
            "What Each Medicine Does",
            sections.what_each_medicine_does
          )}
          {renderSection(
            "How to Take Your Medicine",
            sections.how_to_take_your_medicine
          )}
          {renderSection(
            "Possible Side Effects",
            sections.possible_side_effects
          )}
          {renderSection("Important Warnings", sections.important_warnings)}
          {renderSection(
            "Questions for Your Pharmacist",
            sections.questions_for_your_pharmacist
          )}
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
