# Seat Booking System

A full-stack seat booking application built with FastAPI and React.

The project demonstrates secure authentication, backend seat-locking logic, and safe handling of concurrent booking attempts.

---

## Overview

This system simulates a real-world seat reservation workflow where multiple users interact with the same seats concurrently.

To prevent double booking, the backend implements a **temporary seat locking mechanism with database-level concurrency control**. When a user selects a seat, it is locked for a short duration so that other users cannot book it simultaneously. If the booking is completed successfully, the seat becomes permanently reserved. If not, the lock expires automatically and the seat becomes available again.

---

## Tech Stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- JWT authentication
- PostgreSQL / SQLite (development)
- Deployment: Render

### Frontend
- React
- Fetch API
- Deployment: Vercel

---

## Authentication

The system uses **JWT-based authentication** to secure protected routes.

Features:
- User signup and login
- Password hashing using bcrypt
- JWT token generation after successful authentication
- Protected endpoints requiring valid token

Tokens are stored client-side and sent with each request for authorization.

---

## Seat Booking Logic

Each seat has three possible states:

- Available → Seat is free
- Locked → Temporarily reserved by a user
- Booked → Permanently reserved

### Booking Flow

1. User logs in
2. User fetches available seats
3. User locks a seat
4. Seat is temporarily reserved for that user
5. User confirms booking
6. Seat becomes permanently booked

If the booking is not completed within the timeout period, the lock expires automatically.

---

## Booking Rules

- Only one user can lock a seat at a time
- Only the user who locked a seat can book it
- Lock expires automatically after a timeout
- Locked seats are not available to other users
- Booking is only allowed after locking

---

## API Endpoints

### Authentication
- POST `/signup` → Register user
- POST `/login` → Login and receive JWT token

### Health Check
- GET `/` → API status

### Seats (Protected)
- POST `/seats/init` → Initialize seats
- GET `/seats` → Get all seats
- POST `/seats/{seat_id}/lock` → Lock a seat
- POST `/seats/{seat_id}/book` → Confirm booking

---

## Concurrency Handling

To prevent race conditions when multiple users try to access the same seat, the backend uses **database-level row locking**.

Key mechanisms:
- Transactions
- Row-level locking using SELECT FOR UPDATE
- Seat status validation before updates

This ensures that concurrent requests cannot modify the same seat simultaneously, preventing double booking at the database level.

---

## Lock Expiration

Locks are temporary and simulate real-world booking systems.

- Lock timeout: 1 minute
- If booking is not completed in time:
  - Lock expires automatically
  - Seat becomes available again

---

## Payment Simulation

A mock payment step is included to simulate real-world behavior.

- Booking may randomly fail
- If payment fails, seat remains locked until timeout
- If successful, seat is marked as booked

---

## UI Status Indicators

- Green → Available
- Orange → Locked by current user
- Grey → Locked by another user
- Red → Booked

---

## Live Demo

Frontend:
https://seat-booking-system-omega.vercel.app/

Backend:
https://seat-booking-backend-9sam.onrender.com

Note: Render free tier may cause a cold start delay on first request.

---

## Run Locally

### Backend
pip install -r requirements.txt
uvicorn app.main:app --reload

### Frontend
npm install
npm start

---

## Design Notes

- Backend enforces concurrency safety using database row locking
- JWT authentication secures all booking operations
- Stateless frontend communicates via REST APIs
- System is designed to scale to PostgreSQL with minimal changes

---

## Future Improvements

- WebSocket-based real-time seat updates
- Redis distributed locking for horizontal scaling
- Real payment gateway integration
- Booking history per user
- Admin dashboard