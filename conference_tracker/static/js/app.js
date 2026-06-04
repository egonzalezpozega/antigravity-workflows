/**
 * Client-side script for the Aura Events Conference Tracker.
 *
 * Implements real-time filtering, search functionality, and automatic
 * toast dismissal. Uses clean, secure DOM element styling manipulation to
 * comply with strict XSS prevention guidelines.
 */

document.addEventListener("DOMContentLoaded", () => {
    logger("JavaScript initialized successfully.");

    // --- Search & Filtering Elements ---
    const searchInput = document.getElementById("search-input");
    const categoryFilter = document.getElementById("category-filter");
    const eventCards = document.querySelectorAll(".event-card");
    const noEventsMessage = document.getElementById("no-events-message");

    /**
     * Filters event cards dynamically based on category dropdown and search query.
     */
    function filterEvents() {
        const query = searchInput ? searchInput.value.toLowerCase().trim() : "";
        const selectedCategory = categoryFilter ? categoryFilter.value.toLowerCase() : "all";
        
        let visibleCount = 0;

        eventCards.forEach((card) => {
            // Retrieve metadata from securely encoded data attributes
            const cardCategory = card.getAttribute("data-category") || "";
            const title = card.getAttribute("data-title") || "";
            const speaker = card.getAttribute("data-speaker") || "";
            const location = card.getAttribute("data-location") || "";
            const description = card.getAttribute("data-description") || "";

            // Check category match
            const categoryMatch = (selectedCategory === "all") || (cardCategory === selectedCategory);

            // Check search text match across title, speaker, location, and description
            const searchMatch = (query === "") || 
                                title.includes(query) || 
                                speaker.includes(query) || 
                                location.includes(query) || 
                                description.includes(query);

            // Toggle card display based on matching conditions
            if (categoryMatch && searchMatch) {
                card.style.display = "flex";
                visibleCount++;
            } else {
                card.style.display = "none";
            }
        });

        // Toggle visibility of the "No Events Found" feedback block
        if (noEventsMessage) {
            if (visibleCount === 0) {
                noEventsMessage.style.display = "block";
            } else {
                noEventsMessage.style.display = "none";
            }
        }
    }

    // Bind event listeners for search and filtering
    if (searchInput) {
        searchInput.addEventListener("input", filterEvents);
    }
    if (categoryFilter) {
        categoryFilter.addEventListener("change", filterEvents);
    }


    // --- Auto-Dismiss Notifications ---
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach((alert) => {
        // Set a timer to smoothly fade out and remove alerts after 5 seconds
        setTimeout(() => {
            alert.style.transition = "opacity 0.5s ease, transform 0.5s ease";
            alert.style.opacity = "0";
            alert.style.transform = "translateY(-10px)";
            
            // Remove from DOM after transition completes
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });
});

/**
 * Clean logging helper. Avoids printing structured user objects
 * or secrets in logs in accordance with security guidelines.
 */
function logger(message) {
    console.log(`[Aura Events] ${message}`);
}
