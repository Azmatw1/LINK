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

              // Check the LIVE remaining capacity for this slot.
const isFull =
    slot.remainingFarmerCapacity <= 0 ||
    slot.remainingProduceCapacityKg <= 0;

// Show the remaining capacity to the farmer.
option.textContent =
    `${slot.startTime} - ${slot.endTime} | ` +
    `${slot.remainingFarmerCapacity} farmers left | ` +
    `${slot.remainingProduceCapacityKg} kg left`;

// Disable the slot if either capacity has reached zero.
option.disabled = isFull;
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

    localStorage.setItem(
        "bookingId",
        result.bookingId
    );

    window.location.href = "token.html";
}
    });
}
// ------------------------------
// My Tokens
// ------------------------------

const tokensList = document.getElementById("tokensList");

if (tokensList) {

    const userId = localStorage.getItem("userId");

    if (!userId) {

        tokensList.innerHTML = "Please login first.";

    } else {

        fetch(`http://127.0.0.1:5000/api/my-bookings?user_id=${userId}`)

            .then(response => response.json())

            .then(bookings => {

                // Show a message if the farmer has no bookings.
                if (bookings.length === 0) {
                    tokensList.innerHTML = "You have no bookings yet.";
                    return;
                }

                // Clear the loading message.
                tokensList.innerHTML = "";

                // Create one compact card for each booking.
                bookings.forEach(booking => {

                    const card = document.createElement("div");

                    card.innerHTML = `
                        <h3>
                            APL-${String(booking.tokenNumber).padStart(3, "0")}
                        </h3>

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

                       

                        

                        <button
                            type="button"
                            onclick="viewBookingDetails(${booking.bookingId})">
                            View Details
                        </button>

                        <hr>
                    `;

                    tokensList.appendChild(card);
                });
            })

            .catch(error => {

                console.error("Could not load bookings:", error);

                tokensList.innerHTML =
                    "Could not load your bookings.";
            });
    }
}


// ------------------------------
// Open full booking details
// ------------------------------

function viewBookingDetails(bookingId) {

    // Send the selected booking ID to the details page.
    window.location.href =
        `booking-details.html?booking_id=${bookingId}`;
}
// Language toggle
const englishBtn = document.getElementById("englishBtn");
const urduBtn = document.getElementById("urduBtn");
if (englishBtn && urduBtn) {

    englishBtn.addEventListener("click", function() {

        // Change visible text to English
        document.getElementById("welcomeText").textContent =
            "Welcome to LINK";

        document.getElementById("descriptionText").textContent =
            "Login to manage your procurement slots.";

        document.getElementById("phoneNumber").placeholder =
            "Phone number";

        document.getElementById("password").placeholder =
            "Password";

        document.getElementById("loginButton").textContent =
            "Login";

        document.getElementById("registerQuestion").textContent =
            "Don't have an account?";
        document.getElementById("registerLink").textContent =
            "Register";
    });
       urduBtn.addEventListener("click", function() {

        // Change visible text to Urdu
        document.getElementById("welcomeText").textContent =
            "LINK میں خوش آمدید";

        document.getElementById("descriptionText").textContent =
            "اپنے خریداری کے اوقات کو منظم کرنے کے لیے لاگ اِن کریں۔";

        document.getElementById("phoneNumber").placeholder =
            "فون نمبر";

        document.getElementById("password").placeholder =
            "پاس ورڈ";

        document.getElementById("loginButton").textContent =
            "لاگ اِن";

        document.getElementById("registerQuestion").textContent =
            "کیا آپ کا اکاؤنٹ نہیں ہے؟";

        document.getElementById("registerLink").textContent =
            "رجسٹر کریں";
    });
}
// ------------------------------
// Show farmer name on dashboard
// ------------------------------

const farmerName = document.getElementById("farmerName");

if (farmerName) {

    // Get the farmer's name saved during login.
    const fullName = localStorage.getItem("fullName");

    if (fullName) {
        farmerName.textContent = `Welcome, ${fullName}`;
    }
}
// ------------------------------
// Logout
// ------------------------------

const logoutBtn = document.getElementById("logoutBtn");

if (logoutBtn) {

    logoutBtn.addEventListener("click", function() {

        // Remove the farmer's saved login information.
        localStorage.removeItem("userId");
        localStorage.removeItem("fullName");

        // Remove any saved booking information too.
        localStorage.removeItem("tokenNumber");
        localStorage.removeItem("bookingId");

        // Send the farmer back to the login page.
        window.location.href = "index.html";
    });
}
// ------------------------------
// Booking Details
// ------------------------------

const bookingDetails = document.getElementById("bookingDetails");

if (bookingDetails) {

    // Get the selected booking ID from the URL.
    const params = new URLSearchParams(window.location.search);
    const bookingId = params.get("booking_id");

    if (!bookingId) {

        bookingDetails.innerHTML = "Booking not found.";

    } else {

        // Get the logged-in farmer's ID.
        const userId = localStorage.getItem("userId");

        fetch(`http://127.0.0.1:5000/api/my-bookings?user_id=${userId}`)
            .then(response => response.json())
            .then(bookings => {

                // Find the booking selected by the farmer.
                const booking = bookings.find(
                    item => item.bookingId == bookingId
                );

                if (!booking) {
                    bookingDetails.innerHTML = "Booking not found.";
                    return;
                }

                // Create the full booking details.
                bookingDetails.innerHTML = `
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
                        <b>Procurement:</b> ${booking.status}
                    </p>

                    <p>
                        <b>Payment:</b> ${booking.paymentStatus}
                    </p>
                `;

                // Show the booking reference at the top.
                document.getElementById("bookingReference").textContent =
                    `Booking: APL-${String(booking.tokenNumber).padStart(3, "0")}`;

                // Make Track Queue open this exact booking.
                document.getElementById("trackQueueBtn").onclick =
                    function() {
                        window.location.href =
                            `queue.html?booking_id=${booking.bookingId}`;
                    };
            })

            .catch(error => {

                console.error(
                    "Could not load booking details:",
                    error
                );

                bookingDetails.innerHTML =
                    "Could not load booking details.";
            });
    }
}