# Seat Booking System

A full-stack seat booking application built with FastAPI and React.

This project demonstrates authentication, seat reservation, and safe concurrent booking using PostgreSQL row-level locking and transactional integrity.

---

## Overview

This system simulates a real-world seat booking workflow where multiple users can attempt to reserve the same seat concurrently.

To prevent double booking, the backend uses PostgreSQL row-level locking (`SELECT FOR UPDATE`) within transactions. A seat is first locked temporarily before booking is confirmed. If the booking is not completed within a defined timeout period, the lock expires and is handled during subsequent operations.

---

## Tech Stack

### Backend

* Python
* FastAPI
* SQLAlchemy ORM
* PostgreSQL
* JWT authentication (python-jose)
* Passlib (bcrypt)
* Deployment: Render

### Frontend

* React
* Fetch API
* Deployment: Vercel

---

## Authentication

The system uses JWT-based authentication to secure protected routes.

Features:

* User signup and login
* Password hashing using bcrypt
* JWT token generation after authentication
* Protected routes using OAuth2 Bearer token

Tokens are stored on the client and sent with each request.

---

## Seat Model

Each seat has:

* id
* status → `available | locked | booked`
* locked_at → timestamp when seat was locked
* locked_by → user ID who locked the seat

---

## Seat Booking Flow

1. User logs in
2. User fetches all seats
3. User locks a seat
4. Seat becomes temporarily locked for that user
5. User attempts booking
6. Seat becomes permanently booked if successful

If booking is not completed within the timeout period, the lock expires and is handled automatically during subsequent operations.

---

## Booking Rules

* Only one user can lock a seat at a time
* Only the user who locked a seat can book it
* Lock expires after 1 minute
* Locked seats cannot be booked by other users
* Booking requires prior locking

---

## API Endpoints

### Authentication

* POST /signup → Create new user
* POST /login → Login and receive JWT token

### Health Check

* GET / → API status

### Seats (Protected Routes)

* GET /seats → Get all seats
* POST /seats/{seat_id}/lock → Lock a seat
* POST /seats/{seat_id}/book → Book a seat

All seat routes require authentication.

---

## Concurrency Handling

To prevent race conditions when multiple users attempt to book the same seat:

* Row-level locks are acquired using `SELECT FOR UPDATE`
* Each operation runs inside a database transaction
* Competing requests for the same seat are serialized at the database level
* Seat state is validated before every update

This ensures that only one transaction can modify a seat at a time, preventing double booking.

---

## Lock Expiration

* Lock timeout: 1 minute
* Each seat stores:

  * `locked_at`
  * `locked_by`

Expired locks are handled within transactional flows:

* Before locking or booking, the system checks whether an existing lock has expired
* If expired, the seat is reset to `available` within the same transaction

This ensures consistency even without a background cleanup job.

---

## Transaction Handling

* Each booking operation runs within a database transaction
* Row-level locks are held until commit
* Rollback is triggered on failure to maintain consistency

---

## Frontend Behavior

* Periodically fetches seat data (polling) to reflect near real-time updates
* Displays lock ownership and remaining lock time for the current user
* Prevents invalid actions based on seat state

Polling is used for simplicity; real-time updates can be implemented using WebSockets.

---

## UI Status Indicators

* 🟩 Available
* 🟧 Locked by current user
* ⬜ Locked by another user
* 🟥 Booked

---

## Live Demo

Frontend:
https://seat-booking-system-omega.vercel.app/

Backend:
https://seat-booking-backend-9sam.onrender.com

Note: Render free tier may introduce cold start delays.

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

* Service layer separates business logic from API routes
* PostgreSQL ensures consistency using row-level locking
* Transactional handling ensures safe concurrent updates
* JWT authentication secures all booking endpoints
* Stateless frontend communicates via REST APIs

---

## Future Improvements

* WebSocket-based real-time updates
* Background worker for periodic cleanup (cron or queue system)
* Redis-based distributed locking for higher scalability
* Retry logic for failed transactions
* Booking history per user
* Admin dashboard
