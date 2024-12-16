// background.js
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.url) {
      chrome.runtime.sendMessage({ url: message.url });
    }
});


