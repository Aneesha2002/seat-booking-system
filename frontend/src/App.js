import { useEffect, useState } from "react";

const API = process.env.REACT_APP_API_URL;

const getUserIdFromToken = (token) => {
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.sub; 
  } catch {
    return null;
  }
};

const LOCK_TIMEOUT_SECONDS = 60;

const getRemainingTime = (lockedAt) => {
  if (!lockedAt) return 0;

  // Treat backend time as UTC
  const lockedTime = new Date(lockedAt + "Z").getTime();
  const now = Date.now();

  const diff = LOCK_TIMEOUT_SECONDS - Math.floor((now - lockedTime) / 1000);
  return diff > 0 ? diff : 0;
};

function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [seats, setSeats] = useState([]);
  const currentUserId = getUserIdFromToken(token);
  const [message, setMessage] = useState("");

  /* ---------------- AUTH ---------------- */

 const signup = async () => {
  if (!username || !password) {
    alert("Username and password are required");
    return;
  }
  
  const res = await fetch(`${API}/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  const data = await res.json();

  if (!res.ok) {
    alert(data.detail || "Signup failed");
    return;
  }

  localStorage.setItem("token", data.access_token);
  setToken(data.access_token);
};

  const login = async () => {
    const res = await fetch(`${API}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (!res.ok) {
      alert("Login failed");
      return;
    }

    const data = await res.json();
    localStorage.setItem("token", data.access_token);
    setToken(data.access_token);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setSeats([]);
  };

  /* ---------------- SEATS ---------------- */

  const fetchSeats = async () => {
    const res = await fetch(`${API}/seats`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!res.ok) return;
    const data = await res.json();
    setSeats(Array.isArray(data) ? data : []);
  };

  const lockSeat = async (id) => {
    await fetch(`${API}/seats/${id}/lock`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    fetchSeats();
  };

  const bookSeat = async (id) => {
  setMessage("");

  const res = await fetch(`${API}/seats/${id}/book`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const err = await res.json();
    setMessage(err.detail || "Booking failed");
    fetchSeats();
    return;
  }

  setMessage("✅ Seat booked successfully!");
  fetchSeats();
};

  useEffect(() => {
  if (!token) return;

  const interval = setInterval(() => {
    fetchSeats();
  }, 1000);

  return () => clearInterval(interval);
}, [token]);

  /* ---------------- UI ---------------- */

  if (!token) {
    return (
      <div style={{ padding: 20 }}>
        <h2>Login / Signup</h2>

        <input
          placeholder="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <br />

        <input
          placeholder="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <br /><br />

        <button onClick={login} disabled={!username || !password}>
  Login
</button>

<button onClick={signup} disabled={!username || !password} style={{ marginLeft: 10 }}>
  Signup
</button>
      </div>
    );
  }

  return (
    <div style={{ padding: 20 }}>
      <h2>Seat Booking</h2>
      {message && (
  <div style={{ marginTop: 10, color: message.includes("failed") ? "red" : "green" }}>
    {message}
  </div>
)}
      <div style={{ marginTop: 10 }}>
  <strong>Legend:</strong>
  <div style={{ display: "flex", gap: 15, marginTop: 5 }}>
    <span>🟩 Available</span>
    <span>🟧 Locked by you</span>
    <span>⬜ Locked by others</span>
    <span>🟥 Booked</span>
  </div>
</div>
      <button onClick={logout}>Logout</button>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 60px)", gap: 10, marginTop: 20 }}>
      
      {seats.map((seat) => {
  const isMine = seat.locked_by === Number(currentUserId);

  const timeLeft =
  seat.status === "locked" && isMine
    ? getRemainingTime(seat.locked_at)
    : null;

  let background;
  let cursor = "pointer";

  if (seat.status === "available") {
    background = "green";
  } else if (seat.status === "locked") {
    background = isMine ? "orange" : "gray";
    if (!isMine) cursor = "not-allowed";
  } else {
    background = "red";
    cursor = "not-allowed";
  }

  return (
    <div
      key={seat.id}
      onClick={() => {
        if (seat.status === "available") {
          lockSeat(seat.id);
        } else if (seat.status === "locked" && isMine) {
          bookSeat(seat.id);
        }
      }}
      style={{
        width: 60,
        height: 60,
        background,
        color: "white",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        cursor,
      }}
      title={
        seat.status === "locked" && !isMine
          ? "Temporarily held by another user"
          : seat.status === "locked" && isMine
          ? "Locked by you"
          : seat.status === "booked"
          ? "Booked"
          : "Available"
      }
    >
      <div style={{ textAlign: "center" }}>
  <div>{seat.id}</div>
  {timeLeft !== null && <small>{timeLeft}s</small>}
</div>
    </div>
  );
})}

      </div>
    </div>
  );
}

export default App;
