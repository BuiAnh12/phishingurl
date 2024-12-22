// Extract the phishing URL from the query string
const urlParams = new URLSearchParams(window.location.search);
const phishingUrl = urlParams.get("phishingUrl");

// Display the phishing URL
document.getElementById("url").textContent = phishingUrl;

// Allow the user to proceed to the flagged URL
document.getElementById("proceed-button").addEventListener("click", () => {
    chrome.runtime.sendMessage(
        { action: "whitelist", url: phishingUrl },
        (response) => {
            if (response.success) {
                window.location.href = phishingUrl;
            }
        }
    );
});

