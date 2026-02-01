import { useEffect, useState } from "react";

function App() {
  const [seats, setSeats] = useState([]);

  // --- helpers FIRST ---
  const getSeatColor = (status) => {
    if (status === "available") return "#4CAF50"; // green
    if (status === "locked") return "#FFC107";    // yellow
    if (status === "booked") return "#F44336";    // red
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

  const lockSeat = (id) => {
    fetch(`http://127.0.0.1:8000/seats/${id}/lock`, {
      method: "POST",
    }).then(() => {
      fetch("http://127.0.0.1:8000/seats")
        .then((res) => res.json())
        .then(setSeats);
    });
  };

  // --- fetch seats ---
  useEffect(() => {
    fetch("http://127.0.0.1:8000/seats")
      .then((res) => res.json())
      .then(setSeats)
      .catch(console.error);
  }, []);

  // --- JSX ---
  return (
    <div style={{ padding: "20px" }}>
      <h2>Event Seat Booking</h2>

      <div style={styles.grid}>
        {seats.map((seat) => (
          <div
            key={seat.id}
            onClick={() =>
              seat.status === "available" && lockSeat(seat.id)
            }
            style={{
              ...styles.seat,
              backgroundColor: getSeatColor(seat.status),
              cursor:
                seat.status === "available" ? "pointer" : "not-allowed",
            }}
          >
            {seat.id}
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
