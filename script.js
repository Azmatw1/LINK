const registerForm = document.getElementById("registerForm")

//only run this if register form exists!
if(registerForm)
{
    registerForm.addEventListener("submit", async function(event){
        event.preventDefault();
        const fullname = document.getElementById("fullName").value;
        const phoneNumber = document.getElementById("phoneNumber").value;
        const village = document.getElementById("village").value;
        const password = document.getElementById("password").value;

        // Send the farmer's data to our Flask backend
        const response = await fetch("http://127.0.0.1:5000/api/register", {

            // We are sending data, so we use POST
            method: "POST",

            // Tell Flask that we are sending JSON
            headers: {
                "Content-Type": "application/json"
            },

            // Convert our JavaScript data into JSON
            body: JSON.stringify({
                fullName: fullname,
                phoneNumber: phoneNumber,
                village: village,
                password: password
            })
        });
        // Get Flask's response
        const result = await response.json();

        // Show the result
        alert(result.message);

        // If registration succeeded, go to login
        if (response.ok) {
            window.location.href = "index.html";
        }
    });
}
const loginForm = document.getElementById("loginForm");

    // Only run this if the login form exists
    if (loginForm) {

    loginForm.addEventListener("submit", async function(event) {

        // Stop the normal page refresh
        event.preventDefault();

        // Get login details
        const phoneNumber = document.getElementById("phoneNumber").value;
        const password = document.getElementById("password").value;

        // Send login details to Flask
        const response = await fetch("http://127.0.0.1:5000/api/login", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },
              body: JSON.stringify({
                phoneNumber: phoneNumber,
                password: password
            })
        });

        // Read Flask's response
        const result = await response.json();

        // Show the result
        alert(result.message);

        // If login worked, go to dashboard
       if (response.ok) {

    localStorage.setItem("userId", result.userId);
    localStorage.setItem("fullName", result.fullName);

    window.location.href = "dashboard.html";
}
    });
}
    
const centreDropdown = document.getElementById("centre");
// Only run this on the booking page
if (centreDropdown) {
     // Ask Flask for the centres
    fetch("http://127.0.0.1:5000/api/centers")
        .then(response => response.json())
        .then(centers => {// Clear the loading message
            centreDropdown.innerHTML =
                '<option value="">Select centre</option>';

            // Add every centre from the database
            centers.forEach(center => {

                const option = document.createElement("option");

                option.value = center.id;
                option.textContent = center.name;

                centreDropdown.appendChild(option);
            });
             })
        .catch(error => {
            console.error("Could not load centres:", error);
        });
}

const cropDropdown = document.getElementById("crop");
const appleFields = document.getElementById("appleFields");
const generalQuantity = document.getElementById("generalQuantity");

if (cropDropdown) {

    cropDropdown.addEventListener("change", function() {

        if (cropDropdown.value === "Apple") {

            appleFields.style.display = "block";
            generalQuantity.style.display = "none";

        } else {

            appleFields.style.display = "none";
            generalQuantity.style.display = "block";
        }
    });
}
const boxCount = document.getElementById("boxCount");
const boxWeight = document.getElementById("boxWeight");
const quantity = document.getElementById("quantity");
const totalQuantity = document.getElementById("totalQuantity");

if (boxCount && boxWeight && totalQuantity) {

    function calculateAppleTotal() {

        const boxes = Number(boxCount.value);
        const weight = Number(boxWeight.value);

        if (boxes > 0 && weight > 0) {
            totalQuantity.value = boxes * weight;
        } else {
            totalQuantity.value = "";
        }
    }

    boxCount.addEventListener("input", calculateAppleTotal);
    boxWeight.addEventListener("input", calculateAppleTotal);
}
if (quantity && totalQuantity && cropDropdown) {

    quantity.addEventListener("input", function() {

        if (cropDropdown.value !== "Apple") {
            totalQuantity.value = quantity.value;
        }

    });
}
const bookingDate = document.getElementById("bookingDate");
const timeSlotDropdown = document.getElementById("timeSlot");

if (centreDropdown && bookingDate && timeSlotDropdown) {

    async function loadTimeSlots() {

        const centerId = centreDropdown.value;
        const date = bookingDate.value;

        // Don't search until both are selected
        if (!centerId || !date) {
            timeSlotDropdown.innerHTML =
                '<option value="">Select centre and date first</option>';
            return;
        }

        timeSlotDropdown.innerHTML =
            '<option value="">Loading slots...</option>';

        try {

            const response = await fetch(
                `http://127.0.0.1:5000/api/time-slots?center_id=${centerId}&date=${date}`
            );

            const slots = await response.json();

            timeSlotDropdown.innerHTML =
                '<option value="">Select time slot</option>';

            slots.forEach(slot => {

                const option = document.createElement("option");

                option.value = slot.id;

                option.textContent =
                    `${slot.startTime} - ${slot.endTime} | ${slot.farmerCapacity} farmer slots | ${slot.produceCapacityKg} kg`;

                timeSlotDropdown.appendChild(option);
            });

        } catch (error) {

            console.error("Could not load time slots:", error);

            timeSlotDropdown.innerHTML =
                '<option value="">Could not load slots</option>';
        }
    }

    centreDropdown.addEventListener("change", loadTimeSlots);
    bookingDate.addEventListener("change", loadTimeSlots);
}
const bookingForm = document.getElementById("bookingForm");
if (bookingForm) {
    bookingForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const userId = localStorage.getItem("userId");

        if (!userId) {
            alert("Please login first.");
            window.location.href = "index.html";
            return;
        }
        const crop = document.getElementById("crop").value;
        const centerId = document.getElementById("centre").value;
        const slotId = document.getElementById("timeSlot").value;
        const totalQuantityKg = Number(
            document.getElementById("totalQuantity").value
        );
        const variety = crop === "Apple"
            ? document.getElementById("variety").value
            : null;

        const grade = crop === "Apple"
            ? document.getElementById("grade").value
            : null;

        const boxCount = crop === "Apple"
            ? Number(document.getElementById("boxCount").value)
            : null;

        const boxWeightKg = crop === "Apple"
            ? Number(document.getElementById("boxWeight").value)
            : null;

        if (!centerId || !slotId || !crop || !totalQuantityKg) {
            alert("Please complete the booking form.");
            return;
        }

        if (crop === "Apple") {
            if (!variety || !grade || !boxCount || !boxWeightKg) {
                alert("Please complete all Apple details.");
                return;
            }
        }
 const response = await fetch(
            "http://127.0.0.1:5000/api/book-slot",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    userId: Number(userId),
                    centerId: Number(centerId),
                    slotId: Number(slotId),
                    crop: crop,
                    variety: variety,
                    grade: grade,
                    boxCount: boxCount,
                    boxWeightKg: boxWeightKg,
                    totalQuantityKg: totalQuantityKg
                })
            }
        );

        const result = await response.json();
        
alert(result.message);
 if (response.ok) {
            localStorage.setItem(
                "tokenNumber",
                result.tokenNumber
            );

            window.location.href = "token.html";
        }
    });
}
const tokensList = document.getElementById("tokensList");

if (tokensList) {
    const userId = localStorage.getItem("userId");

    if (!userId) {
        tokensList.innerHTML = "Please login first.";
    } else {
        fetch(`http://127.0.0.1:5000/api/my-bookings?user_id=${userId}`)
            .then(response => response.json())
            .then(bookings => {

                if (bookings.length === 0) {
                    tokensList.innerHTML = "You have no bookings yet.";
                    return;
                }

                tokensList.innerHTML = "";

                bookings.forEach(booking => {

                    const card = document.createElement("div");

                    card.innerHTML = `
                        <h3>Token #${booking.tokenNumber}</h3>

                        <p>
                            <b>Centre:</b> ${booking.centerName}
                        </p>

                        <p>
                            <b>Date:</b> ${booking.bookingDate}
                        </p>

                        <p>
                            <b>Time:</b>
                            ${booking.slotStart} - ${booking.slotEnd}
                        </p>

                        <p>
                            <b>Crop:</b> ${booking.crop}
                        </p>

                        <p>
                            <b>Quantity:</b> ${booking.totalQuantityKg} kg
                        </p>

                        <p>
                            <b>Status:</b> ${booking.status}
                        </p>

                        <button onclick="viewQueue(${booking.bookingId})">
                            View Queue
                        </button>

                        <hr>
                    `;

                    tokensList.appendChild(card);
                });
            })
            .catch(error => {
                console.error("Could not load bookings:", error);
                tokensList.innerHTML = "Could not load your bookings.";
            });
    }
}


function viewQueue(bookingId) {
    window.location.href = `queue.html?booking_id=${bookingId}`;
}