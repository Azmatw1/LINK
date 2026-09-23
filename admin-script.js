// ------------------------------
// Procurement Dashboard
// ------------------------------

const procurementList =
    document.getElementById("procurementList");

if (procurementList) {

    // Get today's date in YYYY-MM-DD format.
    const today =
        new Date().toISOString().split("T")[0];

    // For the MVP, we use the first procurement centre.
    // We can add a centre selector later if needed.
    const centerId = 2;

    // Ask the admin backend for today's bookings.
    fetch(
        `http://127.0.0.1:5001/api/center-bookings?center_id=${centerId}&date=${today}`
    )
        .then(response => response.json())

        .then(bookings => {

            // Show a message if there are no bookings.
            if (bookings.length === 0) {

                procurementList.innerHTML =
                    "<p>No bookings for today.</p>";

                return;
            }

            // Clear the loading message.
            procurementList.innerHTML = "";

            // Create one card for each booking.
            bookings.forEach(booking => {

                const card =
                    document.createElement("div");

                card.innerHTML = `
                    <h3>
                        APL-${String(
                            booking.tokenNumber
                        ).padStart(3, "0")}
                    </h3>

                    <p>
                        <b>Crop:</b>
                        ${booking.crop}
                    </p>

                    <p>
                        <b>Quantity:</b>
                        ${booking.totalQuantityKg} kg
                    </p>

                    <p>
                        <b>Time:</b>
                        ${booking.slotStart}
                        -
                        ${booking.slotEnd}
                    </p>

                    <p>
                        <b>Procurement:</b>
                        ${booking.status}
                    </p>

                    <p>
                        <b>Payment:</b>
                        ${booking.paymentStatus}
                    </p>

                    <button
                        type="button"
                        onclick="markCompleted(
    ${booking.bookingId},
    '${booking.paymentStatus}'
)">
                        Mark Completed
                    </button>

                    <button
                        type="button"
                        onclick="markPaid(
                            ${booking.bookingId}
                        )">
                        Mark Paid
                    </button>

                    <hr>
                `;

                procurementList.appendChild(card);
            });
        })

        .catch(error => {

            console.error(
                "Could not load procurement bookings:",
                error
            );

            procurementList.innerHTML =
                "<p>Could not load bookings.</p>";
        });
}
// ------------------------------
// Mark a booking as completed
// ------------------------------

function markCompleted(bookingId, paymentStatus) {

    fetch("http://127.0.0.1:5001/api/update-status", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({

            bookingId: bookingId,

            // Change procurement status to Completed.
            procurementStatus: "Completed",

            // Keep the existing payment status unchanged.
            paymentStatus: paymentStatus

        })
    })

    .then(response => response.json())

    .then(result => {

        console.log(result);

        // Reload the page so the updated status appears.
        location.reload();

    })

    .catch(error => {

        console.error(
            "Could not update procurement status:",
            error
        );

    });
}
// ------------------------------
// Mark a booking as paid
// ------------------------------

// ------------------------------
// Mark a booking as paid
// ------------------------------

function markPaid(bookingId, procurementStatus) {

    console.log("Mark Paid clicked:", bookingId);

    fetch("http://127.0.0.1:5001/api/update-status", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            bookingId: bookingId,
            procurementStatus: procurementStatus,
            paymentStatus: "Paid"
        })
    })

    .then(response => {

        console.log("Server response:", response.status);

        return response.json();
    })

    .then(result => {

        console.log("Update result:", result);

        if (result.message) {
            alert(result.message);
        }

        // Reload after the database update.
        location.reload();
    })

    .catch(error => {

        console.error(
            "Could not update payment status:",
            error
        );

        alert("Could not update payment status.");
    });
}