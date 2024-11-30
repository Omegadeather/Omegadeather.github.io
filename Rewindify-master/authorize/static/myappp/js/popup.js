// static/myappp/js/popup.js

// Wait for the DOM to fully load
document.addEventListener("DOMContentLoaded", function() {
    // Function to open the popup
    function openPopup(containerId) {
        var popupContainer = document.getElementById(containerId);
        popupContainer.style.display = 'block'; // Show the popup
        setTimeout(function () {
            popupContainer.style.opacity = 1; // Fade in effect
        }, 100);
    }

    // Function to close the popup
    function closePopup(containerId) {
        var popupContainer = document.getElementById(containerId);
        popupContainer.style.opacity = 0; // Fade out effect
        setTimeout(function () {
            popupContainer.style.display = 'none'; // Hide the popup
        }, 500);
    }

    // Open the Sign In popup
    document.getElementById('open-signin-popup').onclick = function() {
        openPopup('signin-popup-container');
    };

    // Open the Sign Up popup
    document.getElementById('open-signup-popup').onclick = function() {
        openPopup('signup-popup-container');
    };

    // Close the popups when clicking outside the popup area
    document.querySelectorAll('.popup-container').forEach(function(container) {
        container.onclick = function() {
            closePopup(container.id);
        };

        // Prevent close when clicking inside the popup
        container.querySelector('.popup').onclick = function(e) {
            e.stopPropagation();
        };
    });
});
