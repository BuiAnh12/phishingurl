const backendApi = "http://127.0.0.1:5000";

function openPhishingAlert(url) {
  // Get the current active tab
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const tab = tabs[0];

    
    // Get the tab's width and height from its content window
    const tabWidth = tab.width;
    const tabHeight = tab.height;

    // Define the popup window dimensions
    const popupWidth = 600;
    const popupHeight = 500;

    // Calculate position to center the window based on the tab size
    const left = Math.floor((tabWidth - popupWidth) / 2);
    const top = Math.floor((tabHeight - popupHeight) / 2);

    // Create the popup window with the calculated position
    chrome.windows.create({
      url: "phishingAlert.html",  // Path to the custom HTML page
      type: "popup",
      width: popupWidth,
      height: popupHeight,
      left: left,
      top: top,
    });
  });
}

// Function to check a URL
async function checkUrl(url) {
  try {
    const response = await fetch(`${backendApi}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, model: "cnn" }),
    });

    const data = await response.json();

    if (data.is_phishing) {
      console.log("Phishing URL detected:", url);

      // Show a notification if phishing is detected
      chrome.notifications.create({
        type: "basic",
        iconUrl: "extension-icon.png", // Replace with your extension's icon
        title: "Phishing Detected!",
        message: `The URL "${url}" is flagged as phishing.`,
      });
      // Background script: Send message when phishing URL is detected
      chrome.runtime.sendMessage({
        url: url,  // URL to send
        status: "Phishing"          // Status of the detection
      });
      openPhishingAlert(url)

    } else {
      console.log("Safe URL:", url);
      // chrome.notifications.create({
      //   type: "basic",
      //   iconUrl: "extension-icon.png", // Replace with your extension's icon
      //   title: "Save",
      //   message: `The URL "${url}" is flagged as save.`,
      // });
      // Optionally, open the popup automatically
      // chrome.action.openPopup();
    }
  } catch (error) {
    console.error("Error checking URL:", error);
  }
}

// Listen for tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.url) {
    console.log("New URL detected:", changeInfo.url);
    checkUrl(changeInfo.url);
  }
});
