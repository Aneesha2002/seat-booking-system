import { useEffect, useState } from "react";

// Get user_id from query param
const params = new URLSearchParams(window.location.search);
const USER_ID = Number(params.get("user"));

function App() {
  const [seats, setSeats] = useState([]);

  // --- Helpers ---
  const getSeatColor = (status) => {
    const s = (status || "").toLowerCase();
    if (s === "available") return "#4CAF50"; // green
    if (s === "locked") return "#FFC107";    // yellow
    if (s === "booked") return "#F44336";    // red
    return "#ccc";
  };

  const styles = {
    grid: {
      display: "grid",
      gridTemplateColumns: "repeat(5, 60px)",
      gap: "10px",
      marginTop: "20px",
    },
    seat: {
      width: "60px",
      height: "60px",
      color: "white",
      fontWeight: "bold",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      borderRadius: "8px",
      userSelect: "none",
    },
  };

  // --- API calls ---
  const refreshSeats = () => {
    fetch("http://127.0.0.1:8000/seats")
      .then((res) => res.json())
      .then((data) => {
        console.log("SEATS FROM BACKEND:", data);
        setSeats(data);
      })
      .catch(console.error);
  };

  const lockSeat = (seatId) => {
    fetch(`http://127.0.0.1:8000/seats/${seatId}/lock`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: USER_ID }),
    }).finally(refreshSeats);
  };

  const bookSeat = (seatId) => {
    fetch(`http://127.0.0.1:8000/seats/${seatId}/book`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: USER_ID }),
    }).finally(refreshSeats);
  };

  // --- Hooks ---
  useEffect(() => {
    refreshSeats();
    const interval = setInterval(refreshSeats, 1000); // auto refresh every 1s
    return () => clearInterval(interval);
  }, []);

  // --- No user selected ---
  if (!USER_ID) {
    return (
      <div style={{ padding: "20px" }}>
        <h3>No user selected</h3>
        <p>
          Open app as:
          <br />
          http://localhost:3000/?user=1
          <br />
          http://localhost:3000/?user=2
        </p>
      </div>
    );
  }

  // --- JSX ---
  return (
    <div style={{ padding: "20px" }}>
      <h2>Event Seat Booking</h2>

      <div style={styles.grid}>
        {seats.map((seat) => {
          const status = (seat.status || "").toLowerCase();
          const canClick =
            status === "available" ||
            (status === "locked" && Number(seat.locked_by) === USER_ID);

          // Debugging
          console.log(
            "Seat:",
            seat.id,
            "status:",
            status,
            "locked_by:",
            seat.locked_by,
            "USER_ID:",
            USER_ID,
            "canClick:",
            canClick
          );

          return (
            <div
              key={seat.id}
              onClick={() => {
                if (!canClick) return;

                if (status === "available") lockSeat(seat.id);
                else if (status === "locked" && Number(seat.locked_by) === USER_ID)
                  bookSeat(seat.id);
              }}
              style={{
                ...styles.seat,
                backgroundColor: getSeatColor(status),
                cursor: canClick ? "pointer" : "not-allowed",
              }}
            >
              {seat.id}
            </div>
          );
        })}
      </div>

      <p style={{ marginTop: "20px" }}>
        🟩 Available &nbsp;&nbsp;
        🟨 Locked &nbsp;&nbsp;
        🟥 Booked
      </p>
    </div>
  );
}

export default App;
