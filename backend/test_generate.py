"""
Manual smoke test: exercises the REAL (un-mocked) pipeline end-to-end.

This requires either a working GEMINI_API_KEY in backend/.env (network
access to generativelanguage.googleapis.com) and/or the local fallback
dependencies (`pip install -r requirements-local.txt`), plus network access
for the Wikipedia research step. It is NOT part of the automated pytest
suite (see backend/tests/) which mocks all external calls.
"""
import io
from PIL import Image
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

# Create a small RGB image
img = Image.new("RGB", (640, 480), color=(128, 200, 255))
buffer = io.BytesIO()
img.save(buffer, format="JPEG")
buffer.seek(0)

files = {"image": ("test.jpg", buffer, "image/jpeg")}
data = {"style": "Cinematic", "context": "A. R. Rahman"}

print("Sending /generate request...")
resp = client.post("/generate", files=files, data=data, timeout=300)
print("Status code:", resp.status_code)
print(resp.json())

