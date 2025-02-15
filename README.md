Below is an example of a README file that documents how to build, run, and test your fake AllTrails API, including details on each endpoint, expected responses, and performance considerations.

---

# Fake AllTrails API

This repository contains a RESTful API that simulates an AllTrails service. It is built with FastAPI and SQLAlchemy (using PostgreSQL as the database), and containerized using Docker Compose. The API allows you to manage trail resources—including creating, retrieving, updating, and deleting trails—with additional features such as batch delete route secured via an admin token.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation and Running](#installation-and-running)
- [API Endpoints](#api-endpoints)
  - [GET /trails](#get-trails)
  - [GET /trails/{trail_id}](#get-trailstrail_id)
  - [POST /trails](#post-trails)
  - [PUT /trails/{trail_id}](#put-trailstrail_id)
  - [DELETE /trails/{trail_id}](#delete-trailstrail_id)
  - [DELETE /trails (Batch Delete)](#delete-trails-batch-delete)
- [Testing](#testing)
- [Performance Improvements](#performance-improvements)

## Features

- **Trail Resource**:  
  Each trail includes:
  - **name**
  - **location**
  - **difficulty** (e.g., "Easy", "Moderate", "Hard")
  - **length** (in km)
  - **duration** (in minutes)
  - **elevation_gain** (in m)
  - **type** (allowed: "Circular", "Out-and-back", "Point To Point")

- **CRUD Operations**:
  - **GET**: Retrieve all trails with optional query parameters (`sortBy`, `count`, `difficulty`).
  - **GET**: Retrieve a single trail.
  - **POST**: Create a new trail.
  - **PUT**: Update an existing trail (only provided fields are updated).
  - **DELETE**: Delete a specific trail.

- **Batch Delete and Authorization**:
  - **DELETE /trails**: Batch delete trails that match a given condition (e.g., `difficulty`). Requires an admin token (`X-Admin-Token`).

## Installation and Running

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/matteolee72/fake-alltrails-api.git
    cd alltrails-api
    ```

2. **Build and Start the Containers:**

    ```bash
    docker-compose build
    docker-compose up
    ```

    This will start two services:
    - **db**: PostgreSQL (accessible on port 5432).
    - **web**: FastAPI application (accessible on port 8000).

3. **Stop the Containers:**

    Press `CTRL+C` in the terminal or run:

    ```bash
    docker-compose down
    ```

## API Endpoints

### GET /trails

Retrieves a list of all trails. Supports optional query parameters:

- **`sortBy`**: Sort results by a given field (e.g., `length`).
- **`count`**: Limit the number of results returned.
- **`difficulty`**: Filter trails by difficulty (e.g., "Moderate").

**Example Request:**

```bash
curl -X GET "http://localhost:8000/trails?difficulty=Moderate"
```

**Expected Response:**

```json
[
  {
    "id": 3,
    "name": "Forest Run",
    "location": "Redwood",
    "difficulty": "Moderate",
    "length": 4.2,
    "duration": 90,
    "elevation_gain": 300,
    "type": "Point To Point",
    "cover_photo": null
  }
]
```

### GET /trails/{trail_id}

Retrieve details for a specific trail.

**Example Request:**

```bash
curl -X GET "http://localhost:8000/trails/1"
```

**Expected Response:**

```json
{
  "id": 1,
  "name": "Sunny Trail",
  "location": "Mountain View",
  "difficulty": "Easy",
  "length": 3.5,
  "duration": 60,
  "elevation_gain": 200,
  "type": "Circular",
  "cover_photo": null
}
```

### POST /trails

Create a new trail.

**Example Request:**

```bash
curl -X POST "http://localhost:8000/trails" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "Trail 2",
           "location": "Boulder",
           "difficulty": "Hard",
           "length": 5.0,
           "duration": 120,
           "elevation_gain": 499,
           "type": "Out-and-back"
         }'
```

**Expected Response (HTTP 201 Created):**

```json
{
  "id": 2,
  "name": "Trail 2",
  "location": "Boulder",
  "difficulty": "Hard",
  "length": 5.0,
  "duration": 120,
  "elevation_gain": 499,
  "type": "Out-and-back",
  "cover_photo": null
}
```

### PUT /trails/{trail_id}

Update an existing trail. Only the fields provided in the request body will be updated.

**Example Request:**

```bash
curl -X PUT "http://localhost:8000/trails/2" \
     -H "Content-Type: application/json" \
     -d '{ "elevation_gain": 500 }'
```

**Expected Response:**

```json
{
  "id": 2,
  "name": "Trail 2",
  "location": "Boulder",
  "difficulty": "Hard",
  "length": 5.0,
  "duration": 120,
  "elevation_gain": 500,
  "type": "Out-and-back",
  "cover_photo": null
}
```

### DELETE /trails/{trail_id}

Delete a specific trail.

**Example Request:**

```bash
curl -X DELETE "http://localhost:8000/trails/2"
```

**Expected Response:**

HTTP 204 No Content (no response body).


### DELETE /trails (Batch Delete with Authorization)

Delete all trails that match a certain condition (e.g., by `difficulty`). This route requires an admin token in the request header (`X-Admin-Token`).

**Valid Admin Token Example:**

```bash
curl -X DELETE "http://localhost:8000/trails?difficulty=Hard" \
     -H "X-Admin-Token: secret-admin-token"
```

**Expected Response:**

HTTP 204 No Content.

**Invalid Admin Token Example:**

```bash
curl -X DELETE "http://localhost:8000/trails?difficulty=Hard" \
     -H "X-Admin-Token: wrong-token"
```

**Expected Response:**

```json
{
  "detail": "Not authorized"
}
```

**No Matching Trails Example:**

```bash
curl -X DELETE "http://localhost:8000/trails?difficulty=Nonexistent" \
     -H "X-Admin-Token: secret-admin-token"
```

**Expected Response:**

```json
{
  "detail": "No trails match the given condition"
}
```

## Testing

To run the test script:
1. Ensure the API is running (using Docker Compose).
2. Run the script:
    ```bash
    python tests/test_api.py
    ```

## Performance Improvements

While this implementation meets the basic requirements, here are some suggestions for improvement:
- **Caching**:  
  For frequently accessed endpoints (e.g., GET /trails), consider integrating a caching layer (like Redis) to reduce database load.
- **Database Indexing**:  
  Add indexes to fields that are frequently filtered (such as `difficulty` and `location`) to speed up queries.

  Below is an updated section for your README that identifies which routes are idempotent and provides supporting evidence.

---

### Idempotent Endpoints

1. **GET Endpoints**  
   - **GET /trails**  
   - **GET /trails/{trail_id}**  
   These endpoints only retrieve data and do not change the system state. No matter how many times you call them, the resource state remains unchanged.

2. **PUT /trails/{trail_id}**  
   This endpoint updates an existing trail. Updating a resource with the same data repeatedly yields the same state. For example:

   ```bash
   curl -X PUT "http://localhost:8000/trails/2" \
        -H "Content-Type: application/json" \
        -d '{ "elevation_gain": 500 }'
   ```

   Running this command multiple times will always result in the trail having an `elevation_gain` of `500`.

3. **DELETE Endpoints**  
   - **DELETE /trails/{trail_id}**  
   - **DELETE /trails** (Batch Delete)  
   Deleting a resource or a group of resources leaves the system in the same state, regardless of how many times you attempt the deletion. For instance, if you delete a trail once:

   ```bash
   curl -X DELETE "http://localhost:8000/trails/2"
   ```

   The first call will remove the trail (returning HTTP 204), and subsequent calls will return a 404 error (resource not found). Although the status code differs, the end state of the system remains unchanged (the trail remains deleted).

   Similarly, for batch deletion:

   ```bash
   curl -X DELETE "http://localhost:8000/trails?difficulty=Hard" \
        -H "X-Admin-Token: secret-admin-token"
   ```

   After the first successful deletion (HTTP 204), repeating the command yields a 404 error when no matching trails are found, confirming that the system's state remains consistent.

**Note on Non-Idempotent Endpoints:**  
- **POST /trails** is not idempotent because every call creates a new trail.  
- **POST /trails/{trail_id}/upload-photo** may or may not be idempotent depending on its implementation (in our case, it updates the trail’s cover photo, so if the same file is uploaded repeatedly, the final state remains the same).