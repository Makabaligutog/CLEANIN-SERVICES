
document.addEventListener('DOMContentLoaded', () => {
    const bookingModal = document.getElementById('bookingModal');
    const closeModal = document.getElementById('closeModal');
    const serviceInput = document.getElementById('cleaning_service');
    const selectedServiceName = document.getElementById('selectedServiceName');
    const bookNowButtons = document.querySelectorAll('.book-now-btn');
    const bookingForm = document.getElementById('bookingForm');
    const bookedDatesGrid = document.getElementById('bookedDatesGrid');

    // Open modal and populate with service data
    bookNowButtons.forEach(button => {
        button.addEventListener('click', () => {
            const serviceName = button.getAttribute('data-service');
            const displayName = button.previousElementSibling.previousElementSibling.innerText;
            serviceInput.value = serviceName;
            selectedServiceName.textContent = displayName;
            bookingModal.style.display = 'flex';
        });
    });

    // Close modal when 'X' is clicked
    closeModal.addEventListener('click', () => {
        bookingModal.style.display = 'none';
        clearMessages(); // Clear previous messages
    });

    // Close modal when clicking outside the modal content
    window.addEventListener('click', event => {
        if (event.target === bookingModal) {
            bookingModal.style.display = 'none';
            clearMessages(); // Clear previous messages
        }
    });

    // Handle form submission with AJAX
    bookingForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission

        const formData = new FormData(bookingForm);
        try {
            const response = await fetch("{% url 'submit_booking' %}", {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                // Update booked dates dynamically
                updateBookedDates(data.booked_dates);

                // Display success message
                showSuccessMessage(data.success);

                // Close the modal after a delay
                setTimeout(() => {
                    bookingModal.style.display = 'none';
                    clearMessages(); // Clear success message after closing
                }, 3000);
            } else {
                // Display error message
                showErrorMessage(data.error);
            }
        } catch (error) {
            showErrorMessage("An unexpected error occurred. Please try again later.");
        }
    });

    // Function to update booked dates dynamically
    function updateBookedDates(dates) {
        bookedDatesGrid.innerHTML = ''; // Clear current dates

        if (dates.length === 0) {
            const noDatesElement = document.createElement('p');
            noDatesElement.textContent = "No dates have been booked yet.";
            bookedDatesGrid.appendChild(noDatesElement);
        } else {
            dates.forEach(date => {
                const dateElement = document.createElement('div');
                dateElement.classList.add('booked-date');
                dateElement.textContent = date;
                bookedDatesGrid.appendChild(dateElement);
            });
        }
    }

    // Function to display success messages
    function showSuccessMessage(message) {
        clearMessages();
        const successMessageElement = document.createElement('p');
        successMessageElement.style.color = 'green';
        successMessageElement.textContent = message;
        successMessageElement.classList.add('success-message');
        bookingModal.querySelector('.modal-content').appendChild(successMessageElement);
    }

    // Function to display error messages
    function showErrorMessage(message) {
        clearMessages();
        const errorMessageElement = document.createElement('p');
        errorMessageElement.style.color = 'red';
        errorMessageElement.textContent = message;
        errorMessageElement.classList.add('error-message');
        bookingModal.querySelector('.modal-content').appendChild(errorMessageElement);
    }

    // Function to clear messages (error or success)
    function clearMessages() {
        const modalContent = bookingModal.querySelector('.modal-content');
        const existingMessages = modalContent.querySelectorAll('.error-message, .success-message');
        existingMessages.forEach(msg => msg.remove());
    }
    function submitBooking() {
        const bookingData = {
            cleaning_service: document.getElementById("cleaning_service").value,
            first_name: document.getElementById("first_name").value,
            last_name: document.getElementById("last_name").value,
            contact_number: document.getElementById("contact_number").value,
            address: document.getElementById("address").value,
            additional_info: document.getElementById("additional_info").value,
            booking_date: document.getElementById("booking_date").value,
            confirm_booking: 'false', // Initially false
        };
    
        fetch('/submit-booking/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(), // Ensure CSRF token is included
            },
            body: JSON.stringify(bookingData),
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                // Show confirmation dialog
                showConfirmationDialog(data.details);
            } else if (data.error) {
                // Show error message
                alert(data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
    // Open modal and populate with service data
    bookNowButtons.forEach(button => {
        button.addEventListener('click', async () => {
            const serviceName = button.getAttribute('data-service');
            const displayName = button.previousElementSibling.previousElementSibling.innerText;
            serviceInput.value = serviceName;
            selectedServiceName.textContent = displayName;
    
            try {
                // Check if the service is already booked
                const response = await fetch(`/check-booking/${serviceName}/`);
                const data = await response.json();
    
                if (data.error) {
                    // Show error message if the service is already booked
                    showErrorMessage(data.error);
                } else {
                    // Show the booking modal if no existing booking
                    bookingModal.style.display = 'flex';
                }
            } catch (error) {
                console.error("Error checking service booking:", error);
                showErrorMessage("An error occurred while checking the service. Please try again.");
            }
        });
    });
    
    
});
