import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import TestProgress from "./components/TestProgress.jsx";
import "./index.css";

// Check URL parameter to decide which component to render
const urlParams = new URLSearchParams(window.location.search);
const isTestMode = urlParams.get("test") === "progress";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>{isTestMode ? <TestProgress /> : <App />}</React.StrictMode>
);
