
//Activity 1: Update date in header and footer

var updateDate = function()
{
	var headerEle = document.getElementById('current-date')
	console.log(headerEle.textContent)
	var now = new Date()
	var options = {weekday:'long',year:'numeric',month:'long',day:'numeric'}
	headerEle.textContent = now.toLocaleDateString('en-US',options) + " " +now.toLocaleTimeString()

	var footerEle = document.getElementById('last-updated')
	console.log(footerEle.textContent)

	footerEle.textContent = "Last Updated :" + now.toLocaleString()

} 

updateDate()

//Activity 2: Calculate and display total 

var calTotal = function()
{
	//rows = document.getElementsByClassName('table-row')
	//console.log(rows)

	var rows = document.querySelectorAll('.table-row')
	//console.log(rows)

	var total = 0

	for(let row of rows)
	{
		//console.log(row)

		//amount = row.dataset.amount
		var amount = parseFloat(row.querySelector('.amount').textContent.trim().slice(1))
		// console.log(amount)
		// console.log(typeof(amount))
		total += amount
		document.getElementById('row-count').textContent = "Showing " + rows.length + " Transactions"
		document.getElementById('table-total').textContent = "Total: $ " + total
	}
	console.log(total)
}
calTotal()

// Activity 3: Toggle Table (click event)

var toggleEle = function()
{
	var ele = document.getElementById('data-table-section')
	ele.classList.toggle('hidden')
}
document.getElementById('btn-toggle-table').addEventListener('click',toggleEle)


// Activity 4: Total Sales Hover Highlighting (mouse event)

var salesHover = function () {
    document.getElementById('card-sales').classList.add('highlighted')
}

var salesOut = function () {
    document.getElementById('card-sales').classList.remove('highlighted')
}

var salesCard = document.getElementById('card-sales')
salesCard.addEventListener('mouseenter', salesHover)
salesCard.addEventListener('mouseleave', salesOut)



//Activity 5: Filter by Status (click event)


var filterStatus = function () {
    var statusVal = document.getElementById('filter-status').value
    var minVal = document.getElementById('filter-min').value
    var rows = document.querySelectorAll('.table-row')

    for (let row of rows) {
        var rowStatus = row.dataset.status
        var amount = parseFloat(row.dataset.amount)

        if (
            (statusVal === 'all' || rowStatus === statusVal) &&
            (minVal === '' || amount >= minVal)
        ) {
            row.classList.remove('hidden')
        } else {
            row.classList.add('hidden')
        }
    }

    calTotal()
}

document.getElementById('btn-apply-filter')
    .addEventListener('click', filterStatus)


// Activity 6: Highlight High Sales (>100)(click event)

var highlightHigh = function () {
    var rows = document.querySelectorAll('.table-row')

    for (let row of rows) {
        var amount = parseFloat(row.dataset.amount)

        if (amount > 100) {
            row.classList.add('high-value')
        } else {
            row.classList.remove('high-value')
        }
    }
}

document.getElementById('btn-highlight')
    .addEventListener('click', highlightHigh)



//Activity 7: Calculate Statistics (click event)

var calcStats = function () {
    var rows = document.querySelectorAll('.table-row')
    var amounts = []
    var completed = 0
    var pending = 0
    var cancelled = 0

    for (let row of rows) {
        var amount = parseFloat(row.dataset.amount)
        amounts.push(amount)

        if (row.dataset.status === 'completed') completed++
        if (row.dataset.status === 'pending') pending++
        if (row.dataset.status === 'cancelled') cancelled++
    }

    document.getElementById('stat-highest').textContent =
        "$" + Math.max(...amounts)

    document.getElementById('stat-lowest').textContent =
        "$" + Math.min(...amounts)

    var avg = amounts.reduce((a, b) => a + b, 0) / amounts.length
    document.getElementById('stat-average').textContent =
        "$" + Math.round(avg)

    document.getElementById('stat-completed').textContent = completed
    document.getElementById('stat-pending').textContent = pending
    document.getElementById('stat-cancelled').textContent = cancelled
}

document.getElementById('btn-refresh')
    .addEventListener('click', calcStats)



//Activity 8: Refresh Dashboard Time (click event)


document.getElementById('btn-refresh')
    .addEventListener('click', updateDate)



//Activity 9 (optional):   Reset All (click event)

var resetAll = function () {
    document.getElementById('filter-status').value = 'all'
    document.getElementById('filter-min').value = ''

    var rows = document.querySelectorAll('.table-row')
    for (let row of rows) {
        row.classList.remove('hidden')
        row.classList.remove('high-value')
    }

    calTotal()
    updateDate()
}

document.getElementById('btn-reset')
    .addEventListener('click', resetAll)


//Activity 10 (optional):  Add Transaction (click event)


var addTransaction = function () {
    var date = document.getElementById('input-date').value
    var product = document.getElementById('input-product').value
    var amount = document.getElementById('input-amount').value
    var status = document.getElementById('input-status').value

    if (date === '' || product === '' || amount === '') {
        alert('Please fill all fields')
        return
    }

    var table = document.getElementById('sales-table')
    var row = document.createElement('tr')

    row.classList.add('table-row')
    row.dataset.amount = amount
    row.dataset.status = status

    row.innerHTML = `
        <td>${date}</td>
        <td>${product}</td>
        <td class="amount">$${parseFloat(amount).toFixed(2)}</td>
        <td><span class="status ${status}">${status}</span></td>
        <td><button class="btn-delete">🗑️</button></td>
    `

    table.appendChild(row)
    calTotal()
}

document.getElementById('btn-submit-transaction')
    .addEventListener('click', addTransaction)
