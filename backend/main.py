from fastapi import FastAPI, HTTPException
from backend.luma_client import luma_client
import openai
from openai.types.chat import ChatCompletion
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow requests from your Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Placeholder constant for chord-to-image map
CHORD_IMAGE_MAP = {
    "Em7": "https://www.becomegreatatguitar.com/wp-content/uploads/2021/07/SFyFlhQHSnK0nPQxy96QA_thumb_23a-min.jpg",
    "G": "https://jtgt-static.b-cdn.net/images/modules/BCS3/BC-131-GchordPhoto.jpg",
    "Dsus4": "https://i0.wp.com/breakthroughguitar.com/wp-content/uploads/2023/05/C-Major-guitar-chord-2.png",
    "A7sus4": "https://staticctf.ubisoft.com/J3yJr34U2pZ2Ieem48Dwy9uqj5PNUQTn/4ToPOauWGlxismv7CtyHhn/bfff362c22227b8e710dafe2a8dafc80/g7.jpeg",
    # Additional chords can be added here as needed
}

# Set your OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

class TabInput(BaseModel):
    tab: str

class ChordInput(BaseModel):
    chord_name: str

def extract_chords(tablature):
    prompt = f"""
    Extract only the chord names from the following guitar tablature:

    {tablature}

    List the chords in order of appearance, separated by commas.
    If you can't identify a chord, use 'Unknown'.
    Only return extracted chords and nothing else. The chords should be comma separated.
    """

    response: ChatCompletion = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a music expert specializing in guitar chords."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )

    chords = response.choices[0].message.content.strip()
    return chords.split(',')

async def loop_and_wait_for_generation(gen_id):
    generation = await luma_client.generations.get(id=gen_id)
    while generation.assets is None:
        await asyncio.sleep(1)
        generation = await luma_client.generations.get(id=gen_id)
    return generation

@app.get("/")
async def root():
    return {"message": "Welcome to Guitar Tab Video Generator API"}

@app.post("/api/extract-chords")
async def extract_chords_api(tab_input: TabInput):
    """
    Extract chords from a given guitar tablature.

    Example curl call:
    curl -X POST "http://localhost:8000/api/extract-chords" \
         -H "Content-Type: application/json" \
         -d '{"tab": "Em7   G    Dsus4\\ne|---0---3----2----\\nB|---3---0----3----\\nG|---0---0----2----\\nD|---2---0----0----\\nA|---2---2----x----\\nE|---0---3----x----"}'
    """
    try:
        chords = extract_chords(tab_input.tab)
        return {"chords": chords}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-video")
async def generate_video(chord_input: ChordInput):
    """
    Generate a video showing how to play a specific guitar chord.

    Example curl call:
    curl -X POST "http://localhost:8000/api/generate-video" \
         -H "Content-Type: application/json" \
         -d '{"chord_name": "Em7"}'
    """
    try:
        if chord_input.chord_name not in CHORD_IMAGE_MAP:
            raise HTTPException(status_code=400, detail="Chord not found in image map")

        chord_image_url = CHORD_IMAGE_MAP[chord_input.chord_name]
        
        generation = await luma_client.generations.create(
            prompt=f"Generate a video showing how to play the {chord_input.chord_name} chord on a guitar",
            keyframes={
                "frame0": {
                    "type": "image",
                    "url": chord_image_url
                }
            }
        )

        final_generation = await loop_and_wait_for_generation(generation.id)
        video_url = final_generation.assets.video if final_generation.assets else None

        if not video_url:
            raise HTTPException(status_code=500, detail="Video generation failed")
        print(video_url)
        return {"video_url": video_url}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))