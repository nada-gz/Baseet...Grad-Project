# Testing User Model with Roles in Swagger

## Step 1: Start the Backend Server

Run the server:
```powershell
cd SW\backend
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Or use the script:
```powershell
.\start_server.ps1
```

## Step 2: Open Swagger UI

Once the server is running, open your browser and go to:
```
http://127.0.0.1:8000/docs
```

## Step 3: Test POST User with Role

1. In Swagger UI, find the **POST /users/** endpoint
2. Click "Try it out"
3. Enter the request body with a role:

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "role": "teacher"
}
```

**Available roles:**
- `"student"` (default)
- `"teacher"`
- `"parent"`
- `"supervisor"`
- `"admin"`

4. Click "Execute"
5. Verify the response includes the `role` field

## Step 4: Test GET All Users

1. Find the **GET /users/** endpoint
2. Click "Try it out"
3. Click "Execute"
4. Verify all users in the response include their `role` field

## Example Test Cases

### Test Case 1: Create User with Teacher Role
```json
{
  "username": "teacher1",
  "email": "teacher1@school.com",
  "password": "password123",
  "role": "teacher"
}
```

### Test Case 2: Create User with Admin Role
```json
{
  "username": "admin1",
  "email": "admin@school.com",
  "password": "admin123",
  "role": "admin"
}
```

### Test Case 3: Create User with Default Role (Student)
```json
{
  "username": "student1",
  "email": "student1@school.com",
  "password": "student123"
}
```
Note: If `role` is omitted, it defaults to `"student"`

## Expected Response Format

### POST /users/ Response:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "role": "teacher"
}
```

### GET /users/ Response:
```json
[
  {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "teacher"
  },
  {
    "id": 2,
    "username": "student1",
    "email": "student1@school.com",
    "role": "student"
  }
]
```

