from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from nlp import extract_fields
import edge_tts
import io

app = FastAPI(title="ClearGov API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    text: str

@app.get("/")
def root():
    return {"message": "ClearGov API is running"}

@app.post("/api/extract")
def extract(message: Message):
    return extract_fields(message.text)


class TTSRequest(BaseModel):
    text: str
    voice: str = "vi-VN-HoaiMyNeural"
    rate: str = "-20%"
    volume: str = "+0%"

@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """
    Tạo giọng đọc tiếng Việt bằng Microsoft Edge neural TTS thông qua edge-tts.
    Voice mặc định: vi-VN-HoaiMyNeural.
    """
    communicate = edge_tts.Communicate(
        request.text,
        request.voice,
        rate=request.rate,
        volume=request.volume
    )

    audio = io.BytesIO()

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.write(chunk["data"])

    return Response(
        content=audio.getvalue(),
        media_type="audio/mpeg",
        headers={
            "Cache-Control": "no-cache"
        }
    )
