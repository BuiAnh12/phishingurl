const backendApi = "http://127.0.0.1:5000";
const phishingCache = new Map(); // Cache for phishing checks
let userWhitelist = new Set(); // User-approved URLs to skip rechecking

// Load whitelist from local storage on startup
function loadWhitelist() {
  chrome.storage.local.get("whitelist", (result) => {
    userWhitelist = new Set(result.whitelist || []);
    console.log("Whitelist loaded:", userWhitelist);
  });
}

// Save whitelist to local storage
function saveWhitelist() {
  chrome.storage.local.set({ whitelist: Array.from(userWhitelist) }, () => {
    console.log("Whitelist saved:", userWhitelist);
  });
}

// Function to check a URL
async function checkUrl(url, tabId) {
  if (userWhitelist.has(url)) {
    console.log(`URL '${url}' is in the whitelist. Skipping phishing check.`);
    return;
  }

  if (phishingCache.has(url)) {
    const isPhishing = phishingCache.get(url);
    if (isPhishing) {
      showWarningPage(url, tabId);
    }
    return;
  }

  try {
    const response = await fetch(`${backendApi}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, model: "cnn" }),
    });

    const data = await response.json();
    phishingCache.set(url, data.is_phishing); // Cache the result

    if (data.is_phishing) {
      console.log("Phishing URL detected:", url);
      showWarningPage(url, tabId);
    } else {
      console.log("Safe URL:", url);
    }
  } catch (error) {
    console.error("Error checking URL:", error);
  }
}

// Function to open the warning page
function showWarningPage(phishingUrl, tabId) {
  const warningPageUrl = chrome.runtime.getURL("phishingAlert.html");
  chrome.tabs.update(tabId, { url: `${warningPageUrl}?phishingUrl=${encodeURIComponent(phishingUrl)}` });
}

// Listen for messages from the phishing alert page or popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "whitelist") {
    console.log(`Adding URL '${message.url}' to whitelist.`);
    userWhitelist.add(message.url);
    saveWhitelist();
    sendResponse({ success: true });
  } else if (message.action === "removeWhitelist") {
    console.log(`Removing URL '${message.url}' from whitelist.`);
    userWhitelist.delete(message.url);
    saveWhitelist();
    sendResponse({ success: true });
  } else if (message.action === "getWhitelist") {
    sendResponse({ whitelist: Array.from(userWhitelist) });
  }
});

// Listen for tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.url) {
    console.log("New URL detected:", changeInfo.url);
    checkUrl(changeInfo.url, tabId);
  }
});

// Initialize by loading the whitelist
loadWhitelist();
