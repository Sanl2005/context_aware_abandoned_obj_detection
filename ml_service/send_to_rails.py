import requests
import datetime

RAILS_API = "http://127.0.0.1:3000/api/detected_objects"

payload = {
    "detected_object": {
        "track_id": "FLASK_T001",
        "object_type": "bag",
        "confidence": 0.95,
        "bbox": "[100,60,250,200]",
        "first_seen_at": datetime.datetime.utcnow().isoformat(),
        "last_seen_at": datetime.datetime.utcnow().isoformat(),
        "status": "abandoned",
        "camera_source_id": 1
    }
}

res = requests.post(RAILS_API, json=payload)
print("STATUS:", res.status_code)
print(res.json())
