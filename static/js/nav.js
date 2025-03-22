document.addEventListener('DOMContentLoaded', initializeProfileDropdown);

function initializeProfileDropdown() {
    const dropdownButton = document.getElementById('profileDropdownButton');
    const dropdownMenu = document.getElementById('profileDropdown');

    if (dropdownButton && dropdownMenu) {
        dropdownButton.addEventListener('click', function() {
            dropdownMenu.classList.toggle('hidden');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            if (!dropdownButton.contains(event.target) && !dropdownMenu.contains(event.target)) {
                dropdownMenu.classList.add('hidden');
            }
        });
    }
}