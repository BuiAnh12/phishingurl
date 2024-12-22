// Extract the phishing URL from the query string
const urlParams = new URLSearchParams(window.location.search);
const phishingUrl = urlParams.get("phishingUrl");

// Display the phishing URL
document.getElementById("url").textContent = phishingUrl;

// Allow the user to proceed to the flagged URL
document.getElementById("proceed-button").addEventListener("click", () => {
  // Notify the background script to whitelist this URL for the current session
  chrome.runtime.sendMessage({ action: "whitelist", url: phishingUrl });
  window.location.href = phishingUrl;
});

// Prevent re-checking the URL when reopened
chrome.runtime.onMessage.addListener((message) => {
  if (message.action === "warn-again" && message.url === phishingUrl) {
    alert("This URL is still flagged as phishing. Please proceed with caution.");
  }
});
