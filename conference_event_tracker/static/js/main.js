/**
 * CosmicEvents Platform - Client-Side Interactive Engine
 * 
 * Implements premium client-side event filtering, searching, and micro-animations.
 * Follows strict secure coding standards (avoids innerHTML, enforces textContent).
 * 
 * Author: Antigravity AI
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Dashboard Features if elements are present on the current page
    initDashboardFilters();
});

/**
 * Safely animated dismissal handler for flash notifications.
 * @param {HTMLElement} buttonElement - The close button clicked by the user.
 */
function closeAlert(buttonElement) {
    const alertBox = buttonElement.closest('.flash-alert');
    if (alertBox) {
        alertBox.style.opacity = '0';
        alertBox.style.transform = 'translateY(-12px)';
        alertBox.style.transition = 'opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1), transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        
        setTimeout(() => {
            alertBox.remove();
            
            // If flash container is now empty, remove it to reclaim space
            const container = document.getElementById('flash-container');
            if (container && container.children.length === 0) {
                container.remove();
            }
        }, 300);
    }
}

/**
 * Implements high-performance, real-time client-side searching and filtering
 * across conference sessions without page reloads or DOM insertion vulnerabilities.
 */
function initDashboardFilters() {
    const searchInput = document.getElementById('event-search');
    const filterButtons = document.querySelectorAll('.filter-btn');
    const eventCards = document.querySelectorAll('.event-card');
    const countBadge = document.getElementById('filtered-count-badge');
    const noResultsFallback = document.getElementById('no-results-fallback');
    const noEventsFallback = document.getElementById('no-events-fallback');

    // Fail-safe exit if dashboard components are not present (e.g. on /add page)
    if (!eventCards.length && !noEventsFallback) return;

    let activeCategory = 'all';
    let activeQuery = '';

    /**
     * Executes the filter combining search keyword and category track.
     */
    function applyCombinedFilter() {
        let visibleCount = 0;
        
        eventCards.forEach(card => {
            const cardCategory = card.getAttribute('data-category') || '';
            const cardSearchText = card.getAttribute('data-search-text') || '';
            
            // Match 1: Category Check
            const matchesCategory = (activeCategory === 'all' || cardCategory === activeCategory);
            
            // Match 2: Text Search Check
            const matchesQuery = (!activeQuery || cardSearchText.includes(activeQuery));
            
            if (matchesCategory && matchesQuery) {
                card.classList.remove('hidden');
                visibleCount++;
                
                // Add an entering delay transition for stagger effect
                card.style.animation = 'fadeInPage 0.4s ease-out forwards';
            } else {
                card.classList.add('hidden');
                card.style.animation = 'none';
            }
        });
        
        // Safely update count badge text
        if (countBadge) {
            let label = '';
            if (activeCategory === 'all' && !activeQuery) {
                label = `Showing all ${visibleCount} sessions`;
            } else {
                label = `Found ${visibleCount} matching session${visibleCount === 1 ? '' : 's'}`;
            }
            countBadge.textContent = label;
        }

        // Toggle fallback for empty search matches
        if (noResultsFallback) {
            if (visibleCount === 0 && eventCards.length > 0) {
                noResultsFallback.classList.remove('hidden');
                noResultsFallback.style.animation = 'fadeInPage 0.3s ease-out forwards';
            } else {
                noResultsFallback.classList.add('hidden');
            }
        }
    }

    // Bind real-time input event listeners safely
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            activeQuery = e.target.value.toLowerCase().trim();
            applyCombinedFilter();
        });
    }

    // Bind category button click handlers safely
    filterButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Unset active class from siblings
            filterButtons.forEach(b => b.classList.remove('active'));
            
            // Set active class on target button
            const clickedBtn = e.currentTarget;
            clickedBtn.classList.add('active');
            
            activeCategory = clickedBtn.getAttribute('data-category') || 'all';
            applyCombinedFilter();
        });
    });
}
