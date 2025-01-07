function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const content = document.querySelector('.content');

    if (sidebar.style.display === 'block') {
        sidebar.style.display = 'none';
        content.style.marginLeft = '0';  // Adjust content margin when sidebar is closed
    } else {
        sidebar.style.display = 'block';
        content.style.marginLeft = '250px';  // Adjust content margin when sidebar is open
    }
}
