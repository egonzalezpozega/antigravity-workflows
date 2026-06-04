/**
 * NextGen Schedule - Client App Logic
 * Manages UI interactions, state, searching, filtering, and database API integration.
 * Adheres strictly to security guidelines, avoiding unsafe DOM manipulation (e.g., innerHTML).
 */

document.addEventListener("DOMContentLoaded", () => {
    // State management
    let eventsState = [];
    let activeFilter = "all";
    let searchQuery = "";
    let starredEventIds = [];

    // DOM Elements
    const themeToggleBtn = document.getElementById("theme-toggle-btn");
    const themeIconIndicator = document.getElementById("theme-icon-indicator");
    const openModalBtn = document.getElementById("open-modal-btn");
    const closeModalBtn = document.getElementById("close-modal-btn");
    const cancelFormBtn = document.getElementById("cancel-form-btn");
    const eventModalBackdrop = document.getElementById("event-modal-backdrop");
    const addEventForm = document.getElementById("add-event-form");
    const formErrorBanner = document.getElementById("form-error-banner");
    const eventSearchInput = document.getElementById("event-search-input");
    const categoriesFilterList = document.getElementById("categories-filter-list");
    const eventsGridContainer = document.getElementById("events-grid-container");
    const eventsLoader = document.getElementById("events-loader");
    const noEventsView = document.getElementById("no-events-view");

    // Stats Elements
    const statValTotal = document.getElementById("stat-val-total");
    const statValWorkshops = document.getElementById("stat-val-workshops");
    const statValKeynotes = document.getElementById("stat-val-keynotes");
    const statValStarred = document.getElementById("stat-val-starred");

    // Initialize Application
    initApp();

    /**
     * Set up theme, favorites list, and event listeners.
     */
    function initApp() {
        // 1. Initialize Theme (default to dark)
        const savedTheme = localStorage.getItem("theme") || "dark-theme";
        document.body.className = savedTheme;
        updateThemeIcon(savedTheme);

        // 2. Initialize Starred Schedule
        try {
            starredEventIds = JSON.parse(localStorage.getItem("starredEvents")) || [];
        } catch (e) {
            starredEventIds = [];
        }

        // 3. Attach Event Listeners
        themeToggleBtn.addEventListener("click", toggleTheme);
        openModalBtn.addEventListener("click", showModal);
        closeModalBtn.addEventListener("click", hideModal);
        cancelFormBtn.addEventListener("click", hideModal);
        eventModalBackdrop.addEventListener("click", (e) => {
            if (e.target === eventModalBackdrop) hideModal();
        });

        // Search input with basic debounce or immediate feedback
        eventSearchInput.addEventListener("input", (e) => {
            searchQuery = e.target.value.toLowerCase().trim();
            renderEvents();
        });

        // Category filter buttons
        categoriesFilterList.addEventListener("click", (e) => {
            const button = e.target.closest(".filter-btn");
            if (!button) return;

            // Update active state class
            document.querySelectorAll(".filter-btn").forEach(btn => btn.classList.remove("active"));
            button.classList.add("active");

            activeFilter = button.dataset.category;
            renderEvents();
        });

        // Form submission
        addEventForm.addEventListener("submit", handleFormSubmit);

        // 4. Fetch Events from Backend
        fetchEvents();
    }

    /**
     * Toggles between dark and light themes and saves choice to localStorage.
     */
    function toggleTheme() {
        if (document.body.classList.contains("dark-theme")) {
            document.body.className = "light-theme";
            localStorage.setItem("theme", "light-theme");
            updateThemeIcon("light-theme");
        } else {
            document.body.className = "dark-theme";
            localStorage.setItem("theme", "dark-theme");
            updateThemeIcon("dark-theme");
        }
    }

    /**
     * Updates the theme button icon based on the active theme.
     */
    function updateThemeIcon(themeName) {
        themeIconIndicator.textContent = themeName === "dark-theme" ? "☀️" : "🌙";
    }

    /**
     * Opens the modal dialog and resets validation states.
     */
    function showModal() {
        formErrorBanner.classList.add("hidden");
        formErrorBanner.replaceChildren();
        addEventForm.reset();
        eventModalBackdrop.classList.remove("hidden");
        document.getElementById("event-title-field").focus();
    }

    /**
     * Closes the modal dialog.
     */
    function hideModal() {
        eventModalBackdrop.classList.add("hidden");
    }

    /**
     * Fetches events from the server API.
     */
    async function fetchEvents() {
        showLoader(true);
        try {
            const response = await fetch("/api/events");
            if (!response.ok) {
                throw new Error("HTTP error " + response.status);
            }
            const data = await response.json();
            eventsState = data;
            renderEvents();
        } catch (error) {
            console.error("Failed to load events:", error);
            // Render basic empty state in case of connection failure
            showNoEvents(true, "Could not sync schedule with server.");
        } finally {
            showLoader(false);
        }
    }

    /**
     * Controls the loader spinner state.
     */
    function showLoader(visible) {
        if (visible) {
            eventsLoader.classList.remove("hidden");
            eventsGridContainer.classList.add("hidden");
        } else {
            eventsLoader.classList.add("hidden");
            eventsGridContainer.classList.remove("hidden");
        }
    }

    /**
     * Displays the "no events" empty state message.
     */
    function showNoEvents(visible, customMessage = "") {
        if (visible) {
            noEventsView.classList.remove("hidden");
            eventsGridContainer.classList.add("hidden");
            if (customMessage) {
                const desc = noEventsView.querySelector("p");
                if (desc) desc.textContent = customMessage;
            }
        } else {
            noEventsView.classList.add("hidden");
            eventsGridContainer.classList.remove("hidden");
        }
    }

    /**
     * Handles event starring toggles.
     */
    function toggleStar(eventId) {
        const index = starredEventIds.indexOf(eventId);
        if (index > -1) {
            starredEventIds.splice(index, 1);
        } else {
            starredEventIds.push(eventId);
        }
        localStorage.setItem("starredEvents", JSON.stringify(starredEventIds));
        
        // Re-render to update icon state and stats
        renderEvents();
    }

    /**
     * Helper to format raw datetime-local inputs into user-friendly layouts.
     */
    function formatEventTimeRange(startStr, endStr) {
        try {
            const start = new Date(startStr);
            const end = new Date(endStr);

            const dateOptions = { month: "short", day: "numeric", year: "numeric" };
            const timeOptions = { hour: "numeric", minute: "2-digit", hour12: true };

            const datePart = start.toLocaleDateString(undefined, dateOptions);
            const startPart = start.toLocaleTimeString(undefined, timeOptions);
            const endPart = end.toLocaleTimeString(undefined, timeOptions);

            return `${datePart} | ${startPart} - ${endPart}`;
        } catch (e) {
            return startStr + " to " + endStr;
        }
    }

    /**
     * Filters, counts stats, and renders event cards using secure DOM APIs.
     */
    function renderEvents() {
        // Clear previous cards list securely
        eventsGridContainer.replaceChildren();

        // 1. Calculate Stats
        let totalCount = eventsState.length;
        let workshopsCount = eventsState.filter(e => e.category === "Workshop").length;
        let keynotesCount = eventsState.filter(e => e.category === "Keynote").length;
        let starredCount = eventsState.filter(e => starredEventIds.includes(e.id)).length;

        statValTotal.textContent = String(totalCount);
        statValWorkshops.textContent = String(workshopsCount);
        statValKeynotes.textContent = String(keynotesCount);
        statValStarred.textContent = String(starredCount);

        // 2. Apply Filters
        let filteredEvents = eventsState.filter(event => {
            // Category check
            if (activeFilter === "Favorites") {
                if (!starredEventIds.includes(event.id)) return false;
            } else if (activeFilter !== "all") {
                if (event.category !== activeFilter) return false;
            }

            // Search query check
            if (searchQuery) {
                const titleMatch = event.title.toLowerCase().includes(searchQuery);
                const descMatch = event.description.toLowerCase().includes(searchQuery);
                const speakerMatch = event.speaker.toLowerCase().includes(searchQuery);
                const roomMatch = event.location.toLowerCase().includes(searchQuery);
                return titleMatch || descMatch || speakerMatch || roomMatch;
            }

            return true;
        });

        // 3. Handle Empty Filter Result
        if (filteredEvents.length === 0) {
            showNoEvents(true, searchQuery ? "No events match your search term." : "No events scheduled in this track.");
            return;
        }

        showNoEvents(false);

        // 4. Generate Cards Securely
        filteredEvents.forEach(event => {
            const card = createEventCardDOM(event);
            eventsGridContainer.appendChild(card);
        });
    }

    /**
     * Builds and returns an event card DOM element securely without innerHTML.
     */
    function createEventCardDOM(event) {
        const card = document.createElement("article");
        card.className = "event-card";
        
        // Dynamic track-specific styling hooks
        const cleanCategory = event.category.toLowerCase().replace(/\s+/g, "");
        card.classList.add("track-" + cleanCategory);

        // Header containing Tag and Favorite Button
        const header = document.createElement("div");
        header.className = "card-header";

        const tag = document.createElement("span");
        tag.className = "event-tag";
        tag.textContent = event.category;
        header.appendChild(tag);

        const starBtn = document.createElement("button");
        starBtn.className = "favorite-btn";
        starBtn.setAttribute("aria-label", starredEventIds.includes(event.id) ? "Remove from my schedule" : "Add to my schedule");
        starBtn.textContent = starredEventIds.includes(event.id) ? "★" : "☆";
        if (starredEventIds.includes(event.id)) {
            starBtn.classList.add("starred");
        }
        starBtn.addEventListener("click", () => toggleStar(event.id));
        header.appendChild(starBtn);

        card.appendChild(header);

        // Title
        const title = document.createElement("h3");
        title.textContent = event.title;
        card.appendChild(title);

        // Description
        const desc = document.createElement("p");
        desc.className = "event-description";
        desc.textContent = event.description;
        card.appendChild(desc);

        // Meta parameters container
        const meta = document.createElement("div");
        meta.className = "event-meta";

        // Time metadata row
        const timeItem = document.createElement("div");
        timeItem.className = "meta-item";
        const timeIcon = document.createElement("span");
        timeIcon.className = "meta-icon";
        timeIcon.textContent = "📅";
        timeItem.appendChild(timeIcon);
        const timeText = document.createElement("span");
        timeText.textContent = formatEventTimeRange(event.start_time, event.end_time);
        timeItem.appendChild(timeText);
        meta.appendChild(timeItem);

        // Speaker metadata row
        const speakerItem = document.createElement("div");
        speakerItem.className = "meta-item";
        const speakerIcon = document.createElement("span");
        speakerIcon.className = "meta-icon";
        speakerIcon.textContent = "🗣️";
        speakerItem.appendChild(speakerIcon);
        const speakerText = document.createElement("span");
        speakerText.textContent = event.speaker;
        speakerItem.appendChild(speakerText);
        meta.appendChild(speakerItem);

        // Location metadata row
        const locationItem = document.createElement("div");
        locationItem.className = "meta-item";
        const locationIcon = document.createElement("span");
        locationIcon.className = "meta-icon";
        locationIcon.textContent = "📍";
        locationItem.appendChild(locationIcon);
        const locationText = document.createElement("span");
        locationText.textContent = event.location;
        locationItem.appendChild(locationText);
        meta.appendChild(locationItem);

        card.appendChild(meta);

        return card;
    }

    /**
     * Handles event submission, validates details, and posts JSON data.
     */
    async function handleFormSubmit(e) {
        e.preventDefault();

        // Retrieve field values
        const title = document.getElementById("event-title-field").value.trim();
        const speaker = document.getElementById("event-speaker-field").value.trim();
        const location = document.getElementById("event-location-field").value.trim();
        const category = document.getElementById("event-category-field").value;
        const startTime = document.getElementById("event-start-field").value;
        const endTime = document.getElementById("event-end-field").value;
        const description = document.getElementById("event-desc-field").value.trim();

        // Reset error banner
        formErrorBanner.classList.add("hidden");
        formErrorBanner.replaceChildren();

        const errors = [];

        // Client-side validations
        if (!title) errors.push("Title is required.");
        if (!speaker) errors.push("Speaker name is required.");
        if (!location) errors.push("Location / Room is required.");
        if (!category) errors.push("Please select an event category.");
        if (!startTime) errors.push("Start time is required.");
        if (!endTime) errors.push("End time is required.");
        if (!description) errors.push("Description is required.");

        if (startTime && endTime) {
            const start = new Date(startTime);
            const end = new Date(endTime);
            if (end <= start) {
                errors.append ? errors.append("End time must be after the start time.") : errors.push("End time must be after the start time.");
            }
        }

        if (errors.length > 0) {
            displayFormErrors(errors);
            return;
        }

        // Disable save button to avoid duplicate clicks
        const submitBtn = document.getElementById("submit-form-btn");
        submitBtn.disabled = true;
        submitBtn.textContent = "Saving...";

        const payload = {
            title,
            speaker,
            location,
            category,
            start_time: startTime,
            end_time: endTime,
            description
        };

        try {
            const response = await fetch("/api/events", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const resData = await response.json();

            if (!response.ok) {
                const serverErrors = resData.errors || [resData.error || "Failed to create event."];
                throw new Error(serverErrors.join(" "));
            }

            // Success: Close modal, refresh events schedule
            hideModal();
            fetchEvents();
        } catch (err) {
            console.error("Submission failed:", err);
            displayFormErrors([err.message || "An unexpected error occurred."]);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = "Save Event";
        }
    }

    /**
     * Renders validation and connection error messages safely within the modal card.
     */
    function displayFormErrors(errorsList) {
        formErrorBanner.replaceChildren();

        const heading = document.createElement("p");
        heading.style.fontWeight = "bold";
        heading.textContent = "Please correct the following errors:";
        formErrorBanner.appendChild(heading);

        const list = document.createElement("ul");
        errorsList.forEach(err => {
            const item = document.createElement("li");
            item.textContent = err;
            list.appendChild(item);
        });

        formErrorBanner.appendChild(list);
        formErrorBanner.classList.remove("hidden");
        formErrorBanner.scrollIntoView({ behavior: "smooth" });
    }
});
