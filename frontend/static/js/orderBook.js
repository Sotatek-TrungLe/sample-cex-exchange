// Function to update the order book in the HTML table
function updateOrderBook(data) {
    const tbody = document.getElementById('order-book');
    tbody.innerHTML = '';  // Clear existing rows

    // Determine the maximum length between bids and asks to balance the table rows
    const maxLength = Math.max(data.bids.length, data.asks.length);
    for (let i = 0; i < maxLength; i++) {
        const row = document.createElement('tr');

        // Add Bid side data
        if (data.bids[i]) {
            row.innerHTML += `<td class="bid">${data.bids[i].quantity}</td><td class="bid">${data.bids[i].price}</td>`;
        } else {
            row.innerHTML += '<td></td><td></td>';  // Empty cells if no bid data
        }

        // Add Ask side data
        if (data.asks[i]) {
            row.innerHTML += `<td class="ask">${data.asks[i].price}</td><td class="ask">${data.asks[i].quantity}</td>`;
        } else {
            row.innerHTML += '<td></td><td></td>';  // Empty cells if no ask data
        }

        tbody.appendChild(row);  // Append the row to the table body
    }
}

// Establish Socket.IO connection to the server
const socket = io.connect('http://localhost:5555');

// Connection events
socket.on('connect', () => {
    console.log('Connected to Socket.IO server');
});

socket.on('disconnect', () => {
    console.log('Disconnected from Socket.IO server');
});

// Receive order book updates and update the table
socket.on('order_book_update', (data) => {
    console.log("Received order book update:", data);
    updateOrderBook(JSON.parse(data));  // Parse and pass data to update function
});
