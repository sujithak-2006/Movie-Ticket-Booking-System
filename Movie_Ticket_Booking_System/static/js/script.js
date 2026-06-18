// Global DOM Selectors
const seats = document.querySelectorAll(".seat");
const countLabel = document.getElementById("count");
const totalLabel = document.getElementById("total");
const bookBtn = document.getElementById("book-btn");
const showTimeLabel = document.getElementById("summary-show-time");
const timePills = document.querySelectorAll(".time-pill");

// ✅ DEFAULT BASE PRICE (Fallback if element doesn't exist yet)
let ticketPrice = 150;
let selectedTimeSlot = "None";

// Initialize base ticket price from the hidden input right away if it exists
const basePriceInput = document.getElementById('base-ticket-price');
if (basePriceInput) {
    ticketPrice = parseInt(basePriceInput.value);
}

// ================= SEAT SELECTION HANDLER =================
seats.forEach((seat) => {
    seat.addEventListener("click", () => {
        // Toggle the selected class styling on click
        seat.classList.toggle("selected");
        updateTotal();
    });
});

// ✅ FIXED CALCULATION AND TEXT DISPLAY LOGIC
function updateTotal() {
    let selectedSeats = document.querySelectorAll(".seat.selected");
    let seatCount = selectedSeats.length;

    // Check if a dynamic price update is available
    const activePriceInput = document.getElementById('base-ticket-price');
    if (activePriceInput) {
        ticketPrice = parseInt(activePriceInput.value);
    }

    if (seatCount === 0) {
        countLabel.innerText = "None";
        totalLabel.innerText = "0";
    } else {
        // Collect selected seat names (e.g., A1, A2) into an array and join with commas
        let seatNames = [...selectedSeats].map(seat => seat.innerText);
        countLabel.innerText = seatNames.join(', ');
        
        // Calculate the absolute total dynamically against your MySQL values
        totalLabel.innerText = seatCount * ticketPrice;
    }
}

// ================= ✅ FIXED SHOW TIME CAPTURE ENGINE =================
timePills.forEach(pill => {
    pill.style.cursor = "pointer"; // Changes cursor to hand pointer over the pills
    
    pill.addEventListener("click", () => {
        // Step 1: Reset existing selection borders on all other time slots
        timePills.forEach(p => {
            p.style.border = "none";
        });
        
        // Step 2: Highlight the clicked time slot with a gold accent border
        pill.style.border = "2px solid #ffd700";
        
        // Step 3: Capture the showtime text value and push it to your Summary block
        selectedTimeSlot = pill.innerText.trim();
        if (showTimeLabel) {
            showTimeLabel.innerText = selectedTimeSlot;
        }
    });
});

// ================= BOOKING SUBMISSION HANDLER =================
bookBtn.addEventListener("click", () => {
    let selectedSeats = document.querySelectorAll(".seat.selected");

    if (selectedSeats.length === 0) {
        alert("Please select at least one seat before booking.");
    } else if (selectedTimeSlot === "None") {
        alert("Please select a show time slot before proceeding.");
    } else {
        alert(`Booking Process Initialized!\nShow Time: ${selectedTimeSlot}\nSeats: ${countLabel.innerText}\nTotal Amount: ₹${totalLabel.innerText}`);
        // Connect form redirects or payment window operations here when needed
    }
});

// ================= GENRE MOVIES FILTER ENGINE =================
function filterMovies(genre) {
    let movies = document.querySelectorAll(".movie-card");

    movies.forEach(function (movie) {
        if (genre === "all") {
            movie.parentElement.style.display = "block";
        } else if (movie.classList.contains(genre)) {
            movie.parentElement.style.display = "block";
        } else {
            movie.parentElement.style.display = "none";
        }
    });

    const targetSection = document.getElementById("movies");
    if (targetSection) {
        targetSection.scrollIntoView({ behavior: "smooth" });
    }
}