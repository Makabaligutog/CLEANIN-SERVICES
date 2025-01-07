document.addEventListener('DOMContentLoaded', () => {
    const prevButton = document.querySelector('.prev');
    const nextButton = document.querySelector('.next');
    const monthYear = document.querySelector('.month-year');
    const daysContainer = document.querySelector('.days');
    
    const bookedDates = window.bookedDates || []; // These are booked dates passed from the server.
  
    let currentMonth = new Date().getMonth();
    let currentYear = new Date().getFullYear();
  
    // Function to update the calendar
    function updateCalendar() {
      daysContainer.innerHTML = ''; // Clear the existing days
      const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
      const firstDay = new Date(currentYear, currentMonth, 1).getDay();
  
      // Empty slots before the first day
      for (let i = 0; i < firstDay; i++) {
        const emptyCell = document.createElement('div');
        daysContainer.appendChild(emptyCell);
      }
  
      // Loop to create day cells
      for (let day = 1; day <= daysInMonth; day++) {
        const dateString = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        const dayElement = document.createElement('div');
        dayElement.classList.add('day');
        dayElement.textContent = day;
  
        // If the date is booked, add a 'booked' class
        if (bookedDates.includes(dateString)) {
          dayElement.classList.add('booked');
        }
  
        daysContainer.appendChild(dayElement);
      }
  
      monthYear.textContent = `${new Date(currentYear, currentMonth).toLocaleString('default', { month: 'long' })} ${currentYear}`;
    }
  
    // Handle the previous and next buttons
    prevButton.addEventListener('click', () => {
      currentMonth = currentMonth === 0 ? 11 : currentMonth - 1;
      currentYear = currentMonth === 11 ? currentYear - 1 : currentYear;
      updateCalendar();
    });
  
    nextButton.addEventListener('click', () => {
      currentMonth = currentMonth === 11 ? 0 : currentMonth + 1;
      currentYear = currentMonth === 0 ? currentYear + 1 : currentYear;
      updateCalendar();
    });
  
    // Initial calendar load
    updateCalendar();
  });
  