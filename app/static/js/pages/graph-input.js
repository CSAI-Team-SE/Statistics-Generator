window.addEventListener("DOMContentLoaded", () => {
    document.getElementById("submit-btn").addEventListener("click", async () => {
        // get graph info
        const payload = {
            title: document.getElementById("title").value,
            x_label: document.getElementById("x-label").value,
            x_data: document.getElementById("x-data").value,
            y_label: document.getElementById("y-label").value,
            y_data: document.getElementById("y-data").value,
            graph_type: document.getElementById("graph-type").value,
            lat_low: document.getElementById("lat-low").value,
            lat_high: document.getElementById("lat-high").value,
            long_low: document.getElementById("long-low").value,
            long_high: document.getElementById("long-high").value
        };

    // Require graph type
    if (!payload.graph_type) {
        alert("Please select a graph type.");
        return;
    }

    // Validate X/Y if it's NOT a special graph
    const specialGraphs = [
        "quakes_per_year",
        "quakes_per_month",
        "avg_mag_per_year",
        "tsunamis_per_year",
        "depth_distribution",
        "location_map"
    ];

    if (!specialGraphs.includes(payload.graph_type)) {
        if (!payload.x_data) {
            alert("Please select an X-axis data column.");
            return;
        }
        if (!payload.y_data) {
            alert("Please select a Y-axis data column.");
            return;
        }
    }

        const response = await fetch("/graph-generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        // Reset the AI conversation history when a new graph is generated
        localStorage.removeItem("conversationHistory");

        // Save the request so we can show it on the output page for context
        localStorage.setItem("graph_request", JSON.stringify(payload));

        // Save result so graph-output.html can read it
        localStorage.setItem("graph_result", JSON.stringify(result));

        // redirect to output page
        window.location.href = "/graph-output";
    });
});