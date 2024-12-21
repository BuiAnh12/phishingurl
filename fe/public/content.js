chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.url && message.status === "Phishing") {
        console.log("Phishing URL detected:", message.url);
        
    }
  });