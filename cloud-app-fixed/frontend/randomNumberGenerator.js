//the issue could be with the buttons here
// compare with waynes code and see
document.addEventListener("DOMContentLoaded", function () {
    const generateButton = document.getElementById("generateButton");
    const getResultsButton = document.getElementById("getResultsButton");
    const resultsContainer = document.getElementById("resultsContainer");
    const smallestNumberElement = document.getElementById("smallestNumber");
    const largestNumberElement = document.getElementById("largestNumber");

    generateButton.addEventListener("click", function () {
        // Display message or loading indicator
        resultsContainer.innerHTML = "<p>Generating random numbers...</p>";
        
        const requests = [];
        for (let i = 0; i < 10000; i++) {
            requests.push(fetch("/generate_and_store", { method: "POST" }));
        }
        
        Promise.all(requests)
            .then(() => {
                generateButton.disabled = true;
                getResultsButton.disabled = false; // Enable the "Get Results" button
                resultsContainer.innerHTML = "<p>Random numbers generated successfully!</p>";
            })
            .catch((error) => {
                console.error("Error:", error);
                resultsContainer.innerHTML = "<p>Error generating random numbers. Please try again.</p>";
            });
    });

    getResultsButton.addEventListener("click", function () {
        fetch("/get_results")
            .then((response) => response.json())
            .then((data) => {
                generateButton.disabled = false;
                getResultsButton.disabled = true;
                smallestNumberElement.textContent = `Smallest Number: ${data.smallest_number}`;
                largestNumberElement.textContent = `Largest Number: ${data.largest_number}`;
                resultsContainer.classList.remove("hidden");
            })
            .catch((error) => {
                console.error("Error:", error);
            });
    });

    // Disable the "Get Results" button initially
    getResultsButton.disabled = true;
});
