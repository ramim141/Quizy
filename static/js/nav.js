   // Simple toggle functionality for mobile menu and profile dropdown
   document.addEventListener('click', function(event) {
    const profileMenu = document.getElementById('profileMenu');
    const mobileMenu = document.getElementById('mobileMenu');
    
    if (!event.target.closest('#profileMenu') && !event.target.closest('button')) {
        profileMenu?.classList.add('hidden');
    }
    
    if (!event.target.closest('#mobileMenu') && !event.target.closest('button')) {
        mobileMenu?.classList.add('hidden');
    }
});