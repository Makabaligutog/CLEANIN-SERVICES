function filterByMonth() {
    const selectedMonth = document.getElementById("month").value;
    const rows = document.querySelectorAll("#ratings-table tr");

    rows.forEach(row => {
        row.style.display = selectedMonth === "all" || row.getAttribute("data-month") === selectedMonth ? "" : "none";
    });
}