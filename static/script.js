document.addEventListener("DOMContentLoaded", function () {
    // Target the counter elements inside the layout view
    const counterElement = document.getElementById("live-percent");
    const progressBar = document.getElementById("live-progress-bar");

    if (counterElement) {
        // Parse the initial baseline set by the Python dictionary variables
        let currentPercentage = parseFloat(counterElement.getAttribute("data-base")) || 14.7;

        // Interval tracking routine to auto-increment values dynamically
        const simulationInterval = setInterval(function () {
            // Generate a random marginal value to make the growth look organic
            const organicIncrement = Math.random() * 0.04;
            currentPercentage += organicIncrement;

            // Restrict maximum values safely under 100% capacity parameters
            if (currentPercentage >= 100.0) {
                currentPercentage = 100.0;
                clearInterval(simulationInterval);
            }

            // Update numerical text parameters formatted to 4 decimal accuracy values
            counterElement.innerText = currentPercentage.toFixed(4);

            // Synchronize the linear progress filling metric safely
            if (progressBar) {
                progressBar.style.width = currentPercentage + "%";
            }

        }, 1200); // Ticks smoothly every 1200 milliseconds (1.2 seconds)
    }
});
