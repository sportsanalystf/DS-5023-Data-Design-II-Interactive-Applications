// ============================================
// Activity 1: Update date in header and footer
// ============================================
// Get the current date
var today = new Date();

// Format the date (e.g., "January 15, 2026")
var options = { year: 'numeric', month: 'long', day: 'numeric' };
var formattedDate = today.toLocaleDateString('en-US', options);

// Update the header date
document.getElementById("current-date").textContent = formattedDate;

// Update the footer with last updated time
var timeOptions = { hour: '2-digit', minute: '2-digit', second: '2-digit' };
var formattedTime = today.toLocaleTimeString('en-US', timeOptions);
document.getElementById("last-updated").textContent = "Last updated: " + formattedDate + " at " + formattedTime;


// ============================================
// Activity 2: Calculate and display total
// ============================================
function updateTotal() {
    // Select all transaction rows
    var rows = document.querySelectorAll(".table-row");
    var total = 0;
    var customerSet = new Set();
    
    // Loop through each row and sum the amounts
    for (var i = 0; i < rows.length; i++) {
        var amount = parseFloat(rows[i].dataset.amount);
        if (!isNaN(amount)) {
            total = total + amount;
        }
        // Get product name as a proxy for unique customers
        var product = rows[i].querySelectorAll("td")[1].textContent;
        customerSet.add(product);
    }
    
    // Update row count display
    document.getElementById("row-count").textContent = "Showing " + rows.length + " transactions";
    
    // Update table total display
    document.getElementById("table-total").textContent = "Total: $" + total.toFixed(2);
    
    // Update total sales in stats card
    document.getElementById("total-sales").textContent = "$" + total.toFixed(2);
    
    // Update total orders
    document.getElementById("total-orders").textContent = rows.length;
    
    // Update total customers (unique products as proxy)
    document.getElementById("total-customers").textContent = customerSet.size;
    
    // Update average order value
    var avgOrder = rows.length > 0 ? total / rows.length : 0;
    document.getElementById("avg-order").textContent = "$" + avgOrder.toFixed(2);
}

// Call updateTotal on page load
updateTotal();


// ============================================
// Activity 3: Toggle Table (click event)
// ============================================
document.getElementById("btn-toggle-table").addEventListener("click", function() {
    // Select the data table section
    var tableSection = document.getElementById("data-table-section");
    
    // Toggle the hidden class
    if (tableSection.classList.contains("hidden")) {
        tableSection.classList.remove("hidden");
    } else {
        tableSection.classList.add("hidden");
    }
});


// ============================================
// Activity 4: Total Sales Hover Highlighting (mouse event)
// ============================================
// Select the Total Sales card
var salesCard = document.getElementById("card-sales");

// Add mouseenter event listener
salesCard.addEventListener("mouseenter", function() {
    // Add highlighted class when mouse enters
    salesCard.classList.add("highlighted");
});

// Add mouseleave event listener
salesCard.addEventListener("mouseleave", function() {
    // Remove highlighted class when mouse leaves
    salesCard.classList.remove("highlighted");
});


// ============================================
// Activity 5: Filter by Status (click event)
// ============================================
document.getElementById("btn-apply-filter").addEventListener("click", function() {
    // Get the selected status filter value
    var statusFilter = document.getElementById("filter-status").value;
    
    // Get the minimum amount filter value
    var minAmount = parseFloat(document.getElementById("filter-min").value);
    
    // If minAmount is not a number, set it to 0
    if (isNaN(minAmount)) {
        minAmount = 0;
    }
    
    // Select all transaction rows
    var rows = document.querySelectorAll(".table-row");
    
    // Loop through each row
    for (var i = 0; i < rows.length; i++) {
        // Get the row's status and amount
        var rowStatus = rows[i].dataset.status;
        var rowAmount = parseFloat(rows[i].dataset.amount);
        
        // Determine if row should be shown
        var showByStatus = (statusFilter === "all" || rowStatus === statusFilter);
        var showByAmount = (rowAmount >= minAmount);
        
        // Show or hide the row
        if (showByStatus && showByAmount) {
            rows[i].classList.remove("hidden");
        } else {
            rows[i].classList.add("hidden");
        }
    }
    
    // Update totals after filtering
    updateVisibleTotal();
});

// Helper function to update totals for visible rows only
function updateVisibleTotal() {
    var rows = document.querySelectorAll(".table-row:not(.hidden)");
    var total = 0;
    
    for (var i = 0; i < rows.length; i++) {
        var amount = parseFloat(rows[i].dataset.amount);
        if (!isNaN(amount)) {
            total = total + amount;
        }
    }
    
    // Update row count display
    document.getElementById("row-count").textContent = "Showing " + rows.length + " transactions";
    
    // Update table total display
    document.getElementById("table-total").textContent = "Total: $" + total.toFixed(2);
}


// ============================================
// Activity 6: Highlight High Sales (>100)(click event)
// ============================================
document.getElementById("btn-highlight").addEventListener("click", function() {
    // Select all transaction rows in the table using table-row class
    var rows = document.querySelectorAll(".table-row");
    
    // Loop through each row
    for (var i = 0; i < rows.length; i++) {
        // Read the transaction amount from the row's data attribute
        var amount = parseFloat(rows[i].dataset.amount);
        
        // If amount is greater than 100, change background color to yellow
        if (amount > 100) {
            rows[i].style.backgroundColor = "yellow";
        }
    }
});


// ============================================
// Activity 7: Calculate Statistics
// ============================================
function calStats() {
    // Create an empty array to store all transaction amounts
    var salesData = [];
    
    // Create three counter variables initialized to 0
    var completed = 0;
    var pending = 0;
    var cancelled = 0;
    
    // Create a sum variable initialized to 0
    var sum = 0;
    
    // Select all transaction rows in the table
    var rows = document.querySelectorAll(".table-row");
    
    // Loop through each row
    for (var i = 0; i < rows.length; i++) {
        // Read the row's amount
        var amount = parseFloat(rows[i].dataset.amount);
        
        // Add the amount to the array
        salesData.push(amount);
        
        // Add the amount to sum
        sum = sum + amount;
        
        // Read the row's status and increment the correct counter
        var status = rows[i].dataset.status;
        
        if (status === "completed") {
            completed = completed + 1;
        } else if (status === "pending") {
            pending = pending + 1;
        } else if (status === "cancelled") {
            cancelled = cancelled + 1;
        }
    }
    
    // After the loop: compute highest, lowest, and average
    var salesMax = Math.max(...salesData);
    var salesMin = Math.min(...salesData);
    var average = sum / salesData.length;
    
    // Update the webpage with statistics
    document.getElementById("stat-highest").textContent = "$" + salesMax;
    document.getElementById("stat-lowest").textContent = "$" + salesMin;
    document.getElementById("stat-average").textContent = "$" + average.toFixed(2);
    
    // Update the completed, pending, and cancelled counters
    document.getElementById("stat-completed").textContent = completed;
    document.getElementById("stat-pending").textContent = pending;
    document.getElementById("stat-cancelled").textContent = cancelled;
}

// Call calStats() once on page load so the statistics appear immediately
calStats();


// ============================================
// Activity 8: Refresh Dashboard Time (click event)
// ============================================
document.getElementById("btn-refresh").addEventListener("click", function() {
    // Get the current date and time
    var now = new Date();
    
    // Format the date
    var options = { year: 'numeric', month: 'long', day: 'numeric' };
    var formattedDate = now.toLocaleDateString('en-US', options);
    
    // Format the time
    var timeOptions = { hour: '2-digit', minute: '2-digit', second: '2-digit' };
    var formattedTime = now.toLocaleTimeString('en-US', timeOptions);
    
    // Update the header date
    document.getElementById("current-date").textContent = formattedDate;
    
    // Update the footer with last updated time
    document.getElementById("last-updated").textContent = "Last updated: " + formattedDate + " at " + formattedTime;
    
    // Recalculate totals and statistics
    updateTotal();
    calStats();
});


// ============================================
// Activity 9: Reset All (click event)
// ============================================
document.getElementById("btn-reset").addEventListener("click", function() {
    // Clear content of Add New Transaction Card/Widget
    // Clear the Date input
    document.getElementById("input-date").value = "";
    
    // Clear the Product input
    document.getElementById("input-product").value = "";
    
    // Clear the Amount input
    document.getElementById("input-amount").value = "";
    
    // Reset the Status input to default option
    document.getElementById("input-status").value = "completed";
    
    // Clear content of Filter Transactions Card/Widget
    // Reset the Status filter dropdown
    document.getElementById("filter-status").value = "all";
    
    // Clear the Minimum amount filter
    document.getElementById("filter-min").value = "";
    
    // Select all transaction rows in the table
    var rows = document.querySelectorAll(".table-row");
    
    // Loop through each row
    for (var i = 0; i < rows.length; i++) {
        // Read the transaction amount from row.dataset.amount
        var amount = parseFloat(rows[i].dataset.amount);
        
        // If amount is greater than 100, reset background color to white
        if (amount > 100) {
            rows[i].style.backgroundColor = "white";
        }
        
        // Remove the hidden class from the row using classList method
        rows[i].classList.remove("hidden");
    }
    
    // Update totals after reset
    updateTotal();
});


// ============================================
// Activity 10: Add Transaction (click event)
// ============================================
document.getElementById("btn-submit-transaction").addEventListener("click", function() {
    // Read the date from input-date
    var date = document.getElementById("input-date").value;
    
    // Read the product name, use trim() to remove extra spaces
    var product = document.getElementById("input-product").value.trim();
    
    // Read the amount, convert to number using parseFloat
    var amount = parseFloat(document.getElementById("input-amount").value);
    
    // Read the status
    var status = document.getElementById("input-status").value;
    
    // Create a new table row using document.createElement
    var newRow = document.createElement("tr");
    
    // Set the row's class to table-row
    newRow.className = "table-row";
    
    // Set custom data attribute for amount
    newRow.setAttribute("data-amount", amount);
    
    // Set custom data attribute for status
    newRow.setAttribute("data-status", status);
    
    // Capitalize the first letter of status
    var statusDisplay = status.charAt(0).toUpperCase() + status.slice(1);
    
    // Fill the new row with table cells
    newRow.innerHTML = 
        '<td>' + date + '</td>' +
        '<td>' + product + '</td>' +
        '<td class="amount">$' + amount.toFixed(2) + '</td>' +
        '<td><span class="status ' + status + '">' + statusDisplay + '</span></td>' +
        '<td><button class="btn-delete">🗑️</button></td>';
    
    // Append the new row to the table
    document.getElementById("sales-table").appendChild(newRow);
    
    // Update the dashboard calculations
    updateTotal();
    calStats();
    
    // Clear the form inputs after adding the row
    document.getElementById("input-date").value = "";
    document.getElementById("input-product").value = "";
    document.getElementById("input-amount").value = "";
    document.getElementById("input-status").value = "completed";
});