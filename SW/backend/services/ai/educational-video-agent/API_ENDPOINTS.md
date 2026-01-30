# Video Generation API Integration - Quick Reference

## Overview
The video generation pipeline has been successfully integrated with the FastAPI router without modifying any existing endpoints.

## Files Added/Modified

### New Files:
1. **`services/ai/educational_video_service.py`** - Video generation service with async support
   
### Modified Files:
1. **`routers/ai_router.py`** - Added 5 new video endpoints + Pydantic models

## API Endpoints

### 1. Generate Video (Synchronous)
**Endpoint:** `POST /ai/video/generate`

**Request:**
```json
{
  "topic": "The Solar System for elementary students",  // Optional
  "duration": 2.0,                                      // Optional (minutes)
  "student_id": 123,                                    // Optional
  "session_id": "custom_session_id"                     // Optional
}
```

**Response (Success):**
```json
{
  "success": true,
  "video_path": "/path/to/final_video.mp4",
  "video_url": "/ai/video/download/20260130_204843_0e06",
  "session_id": "20260130_204843_0e06",
  "message": "Video generated successfully",
  "generation_time_seconds": 45.5,
  "error": null
}
```

**Response (Failure):**
```json
{
  "success": false,
  "video_path": null,
  "video_url": null,
  "session_id": null,
  "message": "Video generation failed",
  "generation_time_seconds": null,
  "error": "No topic provided and prompt.txt is empty"
}
```

**Behavior:**
- If `topic` not provided → reads from `prompt.txt`
- If `duration` not provided → reads from `duration.txt`
- Both missing → returns 400 error
- Returns **only the final video path**, no intermediate assets

---

### 2. Generate Video (Asynchronous)
**Endpoint:** `POST /ai/video/generate-async`

**Request:**
```json
{
  "topic": "Photosynthesis process",      // Optional
  "duration": 1.5,                        // Optional
  "student_id": 456,                      // Optional
  "session_id": "custom_id"               // Optional
}
```

**Response (Queued):**
```json
{
  "success": true,
  "job_id": "a1b2c3d4",
  "status": "queued",
  "message": "Video generation queued. Job ID: a1b2c3d4",
  "poll_url": "/ai/video/status/a1b2c3d4",
  "error": null
}
```

**Response (Failure):**
```json
{
  "success": false,
  "job_id": null,
  "status": "error",
  "message": "Invalid parameters",
  "poll_url": null,
  "error": "Invalid duration"
}
```

**Behavior:**
- Immediately returns with `job_id`
- Video generates in background
- Use `job_id` to poll for progress
- Same fallback logic as synchronous endpoint

---

### 3. Check Job Status
**Endpoint:** `GET /ai/video/status/{job_id}`

**Example:** `GET /ai/video/status/a1b2c3d4`

**Response (Processing):**
```json
{
  "job_id": "a1b2c3d4",
  "status": "processing",
  "progress": 45,
  "topic": "Photosynthesis process",
  "duration": 1.5,
  "video_path": null,
  "session_id": null,
  "error": null,
  "started_at": "2026-01-30T21:30:00",
  "completed_at": null
}
```

**Response (Completed):**
```json
{
  "job_id": "a1b2c3d4",
  "status": "completed",
  "progress": 100,
  "topic": "Photosynthesis process",
  "duration": 1.5,
  "video_path": "/path/to/final_video.mp4",
  "session_id": "20260130_213000_a1b2",
  "error": null,
  "started_at": "2026-01-30T21:30:00",
  "completed_at": "2026-01-30T21:45:00"
}
```

**Response (Failed):**
```json
{
  "job_id": "a1b2c3d4",
  "status": "failed",
  "progress": 0,
  "topic": "Photosynthesis process",
  "duration": 1.5,
  "video_path": null,
  "session_id": null,
  "error": "Manim rendering failed",
  "started_at": "2026-01-30T21:30:00",
  "completed_at": "2026-01-30T21:35:00"
}
```

**Status Values:**
- `"queued"` - Waiting to start
- `"processing"` - Currently generating (check progress %)
- `"completed"` - Done, video_path available
- `"failed"` - Error occurred, check error message

---

### 4. Download Video
**Endpoint:** `GET /ai/video/download/{session_id}`

**Example:** `GET /ai/video/download/20260130_204843_0e06`

**Response:** MP4 video file (streamed)

**Headers:**
```
Content-Type: video/mp4
Content-Disposition: attachment; filename="educational_video_20260130_204843_0e06.mp4"
```

**Behavior:**
- Returns the final video as a streaming response
- Automatically sets proper Content-Type and Content-Disposition headers
- Can be used in `<video>` tag or direct download link

---

### 5. List Generated Videos
**Endpoint:** `GET /ai/video/list?limit=10`

**Query Parameters:**
- `limit` (optional): Maximum videos to return (default: 10, max: 100)

**Example:** `GET /ai/video/list?limit=5`

**Response:**
```json
{
  "success": true,
  "videos": [
    {
      "session_id": "20260130_213000_a1b2",
      "video_path": "/outputs/final/20260130_213000_a1b2/final_photosynthesis.mp4",
      "created_at": "2026-01-30T21:30:00",
      "video_url": "/ai/video/download/20260130_213000_a1b2"
    },
    {
      "session_id": "20260130_204843_0e06",
      "video_path": "/outputs/final/20260130_204843_0e06/final_solar_system.mp4",
      "created_at": "2026-01-30T20:48:00",
      "video_url": "/ai/video/download/20260130_204843_0e06"
    }
  ],
  "count": 2,
  "message": "Found 2 videos"
}
```

**Behavior:**
- Returns most recently created videos first
- Each video includes download URL
- Useful for UI showing recent generated videos

---

### 6. Video Service Health Check
**Endpoint:** `GET /ai/video/health`

**Response (Healthy):**
```json
{
  "status": "healthy",
  "service": "video_generation",
  "config": {
    "prompt_available": true,
    "duration_available": true,
    "default_duration": 1.0
  }
}
```

**Response (Unhealthy):**
```json
{
  "status": "unhealthy",
  "service": "video_generation",
  "error": "Config files not found"
}
```

**Behavior:**
- Checks if prompt.txt and duration.txt are accessible
- Shows default duration value
- Can be used for monitoring/health checks

---

## Fallback Logic

### When topic is not provided:
1. Check if `topic` parameter is provided → use it
2. If not → read from `prompt.txt`
3. If file doesn't exist or is empty → return 400 error

### When duration is not provided:
1. Check if `duration` parameter is provided → use it
2. If not → read from `duration.txt`
3. If file doesn't exist or value invalid → use default 1.0 minute
4. Never fails due to duration - always has a valid default

---

## Usage Examples

### Example 1: Generate with all defaults
```bash
curl -X POST http://localhost:8000/ai/video/generate \
  -H "Content-Type: application/json" \
  -d '{}'
```
**Behavior:** Uses prompt.txt and duration.txt

### Example 2: Generate with custom topic
```bash
curl -X POST http://localhost:8000/ai/video/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Photosynthesis", "duration": 2.0}'
```
**Behavior:** Uses provided topic and duration, ignores config files

### Example 3: Generate asynchronously
```bash
curl -X POST http://localhost:8000/ai/video/generate-async \
  -H "Content-Type: application/json" \
  -d '{"topic": "Gravity", "duration": 1.5}'
```
**Response:** `{"job_id": "xyz123", ...}`

Then poll:
```bash
curl http://localhost:8000/ai/video/status/xyz123
```

### Example 4: Download video
```bash
curl -X GET http://localhost:8000/ai/video/download/20260130_204843_0e06 \
  -o video.mp4
```

### Example 5: Check service health
```bash
curl http://localhost:8000/ai/video/health
```

---

## Integration Notes

✅ **All existing endpoints remain unchanged:**
- `/lesson/start`
- `/lesson/chat`
- `/voice`
- `/speak`
- `/orchestrator/process`
- `/orchestrator/health`
- `/interactive-lesson`

✅ **New endpoints are completely separate:**
- No conflicts with existing imports
- No modification to existing services
- Video service is independent of lesson orchestrator

✅ **Configuration:**
- Reads from `educational-video-agent/prompt.txt`
- Reads from `educational-video-agent/duration.txt`
- Edit these files to change defaults without API restart

✅ **Output:**
- Only returns final video path/file
- No intermediate assets (temp files, images, audio) in responses
- Temp files stored in session directory for cleanup

---

## Error Handling

| Scenario | Status Code | Error Message |
|----------|------------|---------------|
| Missing topic and prompt.txt empty | 400 | "No topic provided and prompt.txt is empty" |
| Video generation fails | 400 | Error details from pipeline |
| Job ID not found | 404 | "Job {job_id} not found" |
| Video file not found | 404 | "Video not found for session {session_id}" |
| Server error | 500 | "Video generation error: {details}" |

---

## Testing Checklist

- [ ] Synchronous generation with user input
- [ ] Synchronous generation with defaults
- [ ] Synchronous generation missing topic
- [ ] Asynchronous generation and status polling
- [ ] Video download endpoint
- [ ] List videos endpoint
- [ ] Health check endpoint
- [ ] Verify existing endpoints still work
- [ ] Check error handling for invalid inputs
- [ ] Verify config file fallback

---
