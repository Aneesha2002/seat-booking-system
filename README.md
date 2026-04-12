# Seat Booking System

A full-stack seat booking application built with FastAPI and React.

This project demonstrates authentication, seat reservation, and safe concurrent booking using PostgreSQL row-level locking.

---

## Overview

This system simulates a real-world seat booking workflow where multiple users can attempt to reserve the same seats at the same time.

To prevent double booking, the backend uses PostgreSQL row-level locking (SELECT FOR UPDATE) and a temporary seat locking mechanism. A seat is locked for a short duration before booking is confirmed. If the booking is not completed within the timeout period, the lock expires automatically and the seat becomes available again.

---

## Tech Stack

### Backend
- Python
- FastAPI
- SQLAlchemy ORM
- PostgreSQL
- JWT authentication (python-jose)
- Passlib (bcrypt)
- Deployment: Render

### Frontend
- React
- Fetch API
- Deployment: Vercel

---

## Authentication

The system uses JWT-based authentication to secure protected routes.

Features:
- User signup and login
- Password hashing using bcrypt
- JWT token generation after authentication
- Protected routes using OAuth2 Bearer token

Tokens are stored on the client and sent with each request.

---

## Seat Model

Each seat has:

- id
- status → available | locked | booked
- locked_at → timestamp when seat was locked
- locked_by → user ID who locked the seat

---

## Seat Booking Flow

1. User logs in
2. User fetches all seats
3. User locks a seat
4. Seat becomes temporarily locked for that user
5. User attempts booking
6. Seat becomes permanently booked if successful

If booking is not completed within the timeout period, the lock expires automatically and the seat becomes available again.

---

## Booking Rules

- Only one user can lock a seat at a time
- Only the user who locked a seat can book it
- Lock expires after 1 minute
- Locked seats cannot be booked by other users
- Booking requires prior locking

---

## API Endpoints

### Authentication
- POST /signup → Create new user
- POST /login → Login and receive JWT token

### Health Check
- GET / → API status

### Seats (Protected Routes)
- POST /seats/init → Initialize 30 seats
- GET /seats → Get all seats
- POST /seats/{seat_id}/lock → Lock a seat
- POST /seats/{seat_id}/book → Book a seat

All seat routes require authentication.

---

## Concurrency Handling

To prevent race conditions when multiple users try to book the same seat, the backend uses:

- PostgreSQL row-level locking (SELECT FOR UPDATE)
- SQLAlchemy transactions
- Seat status validation before updates

This ensures that only one request can modify a seat at a time.

---

## Lock Expiration

- Lock timeout: 1 minute
- Each seat stores:
  - locked_at
  - locked_by

If the lock is not completed within the timeout:
- It is treated as expired
- Seat becomes available again

Lock cleanup happens during seat fetch requests.

---

## Payment Simulation

A mock payment step is included to simulate real-world booking behavior.

- Payment success is randomly simulated
- If booking fails, seat remains locked until timeout expires
- If booking succeeds, seat status is updated to booked

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

Note: Render free tier may have cold start delays.

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

- Service layer separates business logic from API routes
- PostgreSQL handles concurrency using row-level locking
- JWT authentication secures all booking endpoints
- Stateless frontend communicates via REST APIs

---

## Future Improvements

- WebSocket-based real-time seat updates
- Background worker for lock cleanup (Celery or cron job)
- Redis distributed locking for horizontal scaling
- Real payment gateway integration
- Booking history per user
- Admin dashboard