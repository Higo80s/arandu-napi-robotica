// Animated Counter Function (Enhanced)
function animateCounter(element) {
    const targetPath = element.getAttribute('data-target');
    // Handle float parsing
    const target = parseFloat(targetPath);
    if (isNaN(target)) return;

    const decimalPlaces = parseInt(element.getAttribute('data-decimal')) || 0;
    const suffix = element.getAttribute('data-suffix') || '';
    const duration = 1500; // 1.5 seconds
    const fps = 60;
    const totalFrames = (duration / 1000) * fps;
    const increment = target / totalFrames;

    let current = 0;
    let frame = 0;

    const updateCounter = () => {
        frame++;
        current += increment;

        // Prevent overshooting
        if (frame <= totalFrames) {
            // Check if we need decimal formatting
            let displayValue;
            if (decimalPlaces > 0) {
                displayValue = current.toFixed(decimalPlaces);
            } else {
                displayValue = Math.floor(current);
            }
            element.textContent = displayValue + suffix;
            requestAnimationFrame(updateCounter);
        } else {
            // Final value
            let finalValue = decimalPlaces > 0 ? target.toFixed(decimalPlaces) : target;
            element.textContent = finalValue + suffix;
        }
    };

    updateCounter();
}

// Initialize counters when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Select both .stat-number (Landing) and .stat-value/.counter (Admin)
    const counters = document.querySelectorAll('.stat-number[data-target], .counter[data-target], .stat-value[data-target]');

    // Delay for visual effect
    setTimeout(() => {
        counters.forEach(counter => animateCounter(counter));
    }, 300);

    // Initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});
