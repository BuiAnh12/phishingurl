const backendApi = "http://127.0.0.1:5000";
const phishingCache = new Map(); // To cache the result of URL checks

// Function to check a URL
async function checkUrl(url, tabId) {
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

// Listen for tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.url) {
    console.log("New URL detected:", changeInfo.url);
    checkUrl(changeInfo.url, tabId);
  }
});
