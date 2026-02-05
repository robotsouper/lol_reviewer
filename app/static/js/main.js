// Basic form validation and UX enhancements

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // Add loading state to form submission
    const reviewForm = document.querySelector('.review-form');
    if (reviewForm) {
        reviewForm.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Analyzing...';
                submitBtn.style.opacity = '0.7';
            }
        });
    }

    // Format Riot ID input (convert to uppercase tag)
    const riotIdInput = document.getElementById('riot_id');
    if (riotIdInput) {
        riotIdInput.addEventListener('blur', function() {
            if (this.value.includes('#')) {
                const parts = this.value.split('#');
                if (parts.length === 2) {
                    this.value = parts[0] + '#' + parts[1].toUpperCase();
                }
            }
        });
    }
});
