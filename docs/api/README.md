# Backend API Documentation

This document describes the structure, conventions, and usage of the Backend API.

---

## Base URL and Versioning
All endpoints are versioned:
api/routes/v1

## API Design Principles
- RESTful, resource-oriented endpoints
- JSON request and response bodies
- Explicit HTTP status codes
- Input validation via Pydantic schemas
- Business logic handled in services
- No database access in API routes

## API Documentation
Interactive documentation is available at:
Swagger UI: /docs
OpenAPI JSON: /openapi.json

## Adding a New Endpoint
- Create a route in app/api/routes/Vx
- Define schemas in app/api/schemas
- Implement logic in app/services
- Use repositories for database access
- Register the router

