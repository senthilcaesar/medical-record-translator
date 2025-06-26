import React, { useState, useEffect } from "react";

const TestResultsTable = ({ testData }) => {
  const [animatedCards, setAnimatedCards] = useState(new Set());

  useEffect(() => {
    // Animate cards on mount
    testData.forEach((_, index) => {
      setTimeout(() => {
        setAnimatedCards((prev) => new Set([...prev, index]));
      }, index * 100);
    });
  }, [testData]);

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case "normal":
        return "bg-gradient-to-r from-green-500 to-green-600";
      case "high":
      case "low":
        return "bg-gradient-to-r from-red-500 to-red-600";
      case "borderline":
        return "bg-gradient-to-r from-yellow-500 to-yellow-600";
      case "desirable":
        return "bg-gradient-to-r from-blue-500 to-blue-600";
      default:
        return "bg-gradient-to-r from-gray-500 to-gray-600";
    }
  };

  const getStatusBadgeColor = (status) => {
    switch (status.toLowerCase()) {
      case "normal":
        return "bg-gradient-to-r from-green-100 to-green-200 text-green-800 border-green-300";
      case "high":
      case "low":
        return "bg-gradient-to-r from-red-100 to-red-200 text-red-800 border-red-300";
      case "borderline":
        return "bg-gradient-to-r from-yellow-100 to-yellow-200 text-yellow-800 border-yellow-300";
      case "desirable":
        return "bg-gradient-to-r from-blue-100 to-blue-200 text-blue-800 border-blue-300";
      default:
        return "bg-gradient-to-r from-gray-100 to-gray-200 text-gray-800 border-gray-300";
    }
  };

  const getCategoryIcon = (category) => {
    switch (category.toLowerCase()) {
      case "blood count":
        return "🩸";
      case "immune system":
        return "🛡️";
      case "metabolic":
        return "🧪";
      case "cardiovascular":
        return "❤️";
      default:
        return "📊";
    }
  };

  const groupedTests = testData.reduce((acc, test) => {
    const category = test.category || "Other";
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(test);
    return acc;
  }, {});

  const getTotalStats = () => {
    const total = testData.length;
    const normal = testData.filter(
      (t) =>
        t.status.toLowerCase() === "normal" ||
        t.status.toLowerCase() === "desirable"
    ).length;
    const abnormal = testData.filter(
      (t) =>
        t.status.toLowerCase() === "high" || t.status.toLowerCase() === "low"
    ).length;
    const borderline = testData.filter(
      (t) => t.status.toLowerCase() === "borderline"
    ).length;

    return { total, normal, abnormal, borderline };
  };

  const stats = getTotalStats();

  return (
    <div className="w-full max-w-7xl mx-auto">
      {/* Header Dashboard */}
      <div className="mb-8 p-6 bg-gradient-to-r from-blue-600 to-purple-700 rounded-2xl text-white shadow-2xl">
        <h2 className="text-3xl font-bold mb-4 text-center">
          🏥 Medical Test Results Dashboard
        </h2>
        <p className="text-center text-blue-100 mb-6">
          Comprehensive Health Analysis Report
        </p>

        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white/20 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{stats.total}</div>
            <div className="text-sm opacity-90">Total Tests</div>
          </div>
          <div className="bg-white/20 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-green-300">
              {stats.normal}
            </div>
            <div className="text-sm opacity-90">Normal Results</div>
          </div>
          <div className="bg-white/20 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-red-300">
              {stats.abnormal}
            </div>
            <div className="text-sm opacity-90">Abnormal Results</div>
          </div>
          <div className="bg-white/20 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-yellow-300">
              {stats.borderline}
            </div>
            <div className="text-sm opacity-90">Borderline Results</div>
          </div>
        </div>
      </div>

      {/* Test Results by Category */}
      {Object.entries(groupedTests).map(([category, tests]) => (
        <div key={category} className="mb-8">
          {/* Category Header */}
          <div className="mb-6 p-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl text-center shadow-lg">
            <h3 className="text-xl font-bold">
              {getCategoryIcon(category)} {category} Analysis
            </h3>
          </div>

          {/* Test Cards Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {tests.map((test, index) => (
              <div
                key={`${category}-${index}`}
                className={`
                  bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden
                  transform transition-all duration-500 hover:scale-105 hover:shadow-2xl
                  ${
                    animatedCards.has(index)
                      ? "translate-y-0 opacity-100"
                      : "translate-y-8 opacity-0"
                  }
                `}
                style={{
                  transitionDelay: `${index * 100}ms`,
                }}
              >
                {/* Status Bar */}
                <div className={`h-2 ${getStatusColor(test.status)}`}></div>

                {/* Card Content */}
                <div className="p-6">
                  {/* Header */}
                  <div className="flex justify-between items-start mb-4">
                    <h4 className="text-lg font-bold text-gray-900 flex-1">
                      {test.test_name}
                    </h4>
                    <span
                      className={`
                      px-3 py-1 rounded-full text-xs font-semibold border
                      ${getStatusBadgeColor(test.status)}
                    `}
                    >
                      {test.status.charAt(0).toUpperCase() +
                        test.status.slice(1)}{" "}
                      {test.status_emoji}
                    </span>
                  </div>

                  {/* Result Value */}
                  <div className="mb-4">
                    <div className="text-2xl font-bold text-gray-800 mb-1">
                      {test.your_result}
                    </div>
                    <div className="text-sm text-gray-600 bg-gray-100 px-3 py-1 rounded-lg inline-block">
                      Normal: {test.normal_range}
                    </div>
                  </div>

                  {/* Test Details Table */}
                  <div className="space-y-3">
                    {test.purpose && (
                      <div className="border-l-4 border-blue-500 pl-3">
                        <div className="text-sm font-semibold text-gray-700">
                          Purpose
                        </div>
                        <div className="text-sm text-gray-600">
                          {test.purpose}
                        </div>
                      </div>
                    )}

                    {test.what_this_means && (
                      <div className="border-l-4 border-green-500 pl-3">
                        <div className="text-sm font-semibold text-gray-700">
                          What This Means
                        </div>
                        <div className="text-sm text-gray-600">
                          {test.what_this_means}
                        </div>
                      </div>
                    )}

                    {test.health_impact && (
                      <div className="border-l-4 border-purple-500 pl-3">
                        <div className="text-sm font-semibold text-gray-700">
                          Health Impact
                        </div>
                        <div className="text-sm text-gray-600">
                          {test.health_impact}
                        </div>
                      </div>
                    )}

                    {test.medical_significance && (
                      <div className="border-l-4 border-orange-500 pl-3">
                        <div className="text-sm font-semibold text-gray-700">
                          Medical Significance
                        </div>
                        <div className="text-sm text-gray-600">
                          {test.medical_significance}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* Overall Assessment */}
      <div className="mt-8 p-6 bg-gradient-to-r from-indigo-600 to-purple-700 text-white rounded-2xl text-center shadow-2xl">
        <h3 className="text-xl font-bold mb-4">📊 Overall Health Assessment</h3>
        <p className="text-indigo-100 leading-relaxed">
          🏥 <strong>Summary:</strong> Most parameters are within normal ranges.
          Some values require monitoring and potential lifestyle adjustments.
          Consult with your healthcare provider for personalized
          recommendations.
        </p>
      </div>
    </div>
  );
};

export default TestResultsTable;
