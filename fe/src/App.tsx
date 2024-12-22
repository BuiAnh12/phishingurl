"use client";

import { useEffect, useState } from "react";
import axios from "axios";

export default function Popup() {
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [manualUrl, setManualUrl] = useState<string>("");
  const [modelType, setModelType] = useState<string>("cnn");
  const [whitelist, setWhitelist] = useState<string[]>([]);
  const backend_api = "http://127.0.0.1:5000";

  useEffect(() => {
    // Load whitelist from background script
    chrome.runtime.sendMessage({ action: "getWhitelist" }, (response) => {
      if (response && response.whitelist) {
        setWhitelist(response.whitelist);
      }
    });

    if (typeof chrome !== "undefined" && chrome.runtime) {
      chrome.runtime.onMessage.addListener((message) => {
        if (message.status === "Phishing" && message.url) {
          setStatus("Phishing");
          setManualUrl(message.url);
          alert(`Phishing detected for ${message.url}`); // Optionally show an alert
        }
      });
    }
  }, []);

  const checkUrl = async (urlToCheck: string, model: string) => {
    if (!urlToCheck || !/^https?:\/\/[^\s$.?#].[^\s]*$/.test(urlToCheck)) {
      setStatus("Invalid URL.");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${backend_api}/predict`, {
        url: urlToCheck,
        model: model,
      });
      const data = response.data;
      setStatus(data.is_phishing ? "Phishing" : "Safe");
    } catch (error) {
      console.error("Error checking URL:", error);
      setStatus("Error checking the URL");
    }
    setLoading(false);
  };

  const handleSubmit = () => {
    if (manualUrl.trim()) {
      checkUrl(manualUrl.trim(), modelType);
    } else {
      setStatus("Please enter a URL.");
    }
  };

  // Remove a URL from the whitelist
  const removeUrl = (url: string) => {
    chrome.runtime.sendMessage(
      { action: "removeWhitelist", url },
      (response) => {
        if (response.success) {
          setWhitelist((prev) => prev.filter((item) => item !== url));
        }
      }
    );
  };

  return (
    <div className="min-w-[320px] p-4 bg-white dark:bg-gray-800 shadow-md">
      <header className="pb-4 border-b border-gray-200 dark:border-gray-700">
        <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
          Phishing Detector
        </h1>
      </header>

      <main className="mt-4">
        <div className="mb-4">
          <input
            type="text"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter URL to check..."
            value={manualUrl}
            onChange={(e) => setManualUrl(e.target.value)}
          />
          <button
            onClick={handleSubmit}
            className="mt-2 w-full bg-green-500 text-white rounded px-4 py-2 hover:bg-green-600"
            disabled={loading}
          >
            {loading ? "Checking..." : "Check Entered URL"}
          </button>
        </div>

        <div className="mb-4">
          <label
            htmlFor="modelVersion"
            className="block text-sm text-gray-700 dark:text-gray-300 mb-2"
          >
            Select Model Version
          </label>
          <select
            id="modelVersion"
            value={modelType}
            onChange={(e) => setModelType(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="cnn">CNN</option>
            <option value="ltsm">LTSM</option>
          </select>
        </div>

        {status && (
          <p
            className={`mt-4 p-2 rounded text-white ${status === "Phishing"
                ? "bg-red-500"
                : status === "Safe"
                  ? "bg-green-500"
                  : "bg-yellow-500 text-black"
              }`}
          >
            {status}
          </p>
        )}

        {/* Whitelist Display */}
        <div className="mt-6">
          <h2 className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Whitelisted URLs
          </h2>
          <ul className="mt-2 space-y-2">
            {whitelist.length > 0 ? (
              whitelist.map((url, index) => (
                <li
                  key={index}
                  className="flex items-center justify-between p-2 border border-gray-300 rounded dark:border-gray-600 dark:bg-gray-700"
                >
                  <span className="text-gray-700 dark:text-gray-300">{url}</span>
                  <button
                    className="bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600"
                    onClick={() => removeUrl(url)}
                  >
                    Remove
                  </button>
                </li>
              ))
            ) : (
              <li className="text-gray-500 dark:text-gray-400">No URLs whitelisted.</li>
            )}
          </ul>
        </div>
      </main>
    </div>
  );
}
