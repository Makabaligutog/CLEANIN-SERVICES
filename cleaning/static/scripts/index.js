  // Toggle Sidebar
  function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    sidebar.style.width = sidebar.style.width === "250px" ? "0" : "250px";
}

// Toggle Modal
function toggleModal() {
    const modal = document.getElementById("bookingModal");
    modal.style.display = modal.style.display === "block" ? "none" : "block";
}

// Close Modal when clicking the 'x' or outside of the modal
document.getElementById("closeModal").onclick = function() {
    toggleModal();
}

window.onclick = function(event) {
    const modal = document.getElementById("bookingModal");
    if (event.target === modal) {
        modal.style.display = "none";
    }
}

// Form Submission
document.getElementById("bookingForm").onsubmit = function(event) {
    event.preventDefault(); // Prevent form from submitting traditionally
    const thankYouMessage = document.getElementById("thankYouMessage");
    thankYouMessage.style.display = "block";
    setTimeout(() => {
        thankYouMessage.style.display = "none";
        toggleModal(); // Close modal after showing thank you message
    }, 3000); // Hide message after 3 seconds
}

// Book Now button opens the modal
document.getElementById("bookNowBtn").onclick = function() {
    toggleModal();
}


