import traceback
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from backend.luma_client import luma_client
import openai
from openai.types.chat import ChatCompletion
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
from pydantic import BaseModel
from typing import List
import ffmpeg
import boto3
import tempfile
import requests
from botocore.exceptions import NoCredentialsError

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
    "Em7": {
        "empty": "https://i.ibb.co/Vv2hWC1/Clean-Shot-2024-09-28-at-14-41-07-2x.png",
        "fingered": "https://i.ibb.co/8gyP7Fp/Clean-Shot-2024-09-28-at-14-41-19-2x.png"
    },
    "G": {
        "empty": "https://i.ibb.co/Vv2hWC1/Clean-Shot-2024-09-28-at-14-41-07-2x.png",
        "fingered": "https://i.ibb.co/k09pdj5/Clean-Shot-2024-09-28-at-14-41-30-2x.png"
    },
    "Dsus4": {
        "empty": "https://i.ibb.co/Vv2hWC1/Clean-Shot-2024-09-28-at-14-41-07-2x.png",
        "fingered": "https://i.ibb.co/pyqFbSW/Clean-Shot-2024-09-28-at-14-41-47-2x.png"
    },
    "A7sus4": {
        "empty": "https://i.ibb.co/Vv2hWC1/Clean-Shot-2024-09-28-at-14-41-07-2x.png",
        "fingered": "https://i.ibb.co/GR0pJsB/Clean-Shot-2024-09-28-at-14-42-04-2x.png"
    },
    "C": {
        "empty": "https://i.ibb.co/mSXy7J7/Clean-Shot-2024-09-28-at-15-05-04-2x.png",
        "fingered": "https://i.ibb.co/GnP9cNX/Clean-Shot-2024-09-28-at-15-05-40-2x.png"
    },
    "D": {
        "empty": "https://i.ibb.co/M17PF0W/Clean-Shot-2024-09-28-at-15-07-34-2x.png",
        "fingered": "https://i.ibb.co/f96RG5T/Clean-Shot-2024-09-28-at-15-07-45-2x.png"
    },
    "Em": {
        "empty": "https://i.ibb.co/Vv2hWC1/Clean-Shot-2024-09-28-at-14-41-07-2x.png",
        "fingered": "https://i.ibb.co/8gyP7Fp/Clean-Shot-2024-09-28-at-14-41-19-2x.png"
    }
}
VIDEO_GENERATION_PROMPT = """This is a video of a person placing their fingers on a guitar to play the {chord_name} chord. The video starts with a guitar being help by a person and there are no fingers on the guitar. Then the persons hand moves up and their fingers curl and are moving the location of the {chord_name} chord. Once the guitarist places their fingers on the {chord_name} chord, the video ends."""
# Set your OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Initialize S3 client
s3_client = boto3.client('s3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
)

class TabInput(BaseModel):
    tab: str

class ChordInput(BaseModel):
    chord_name: str

class ChordProgressionInput(BaseModel):
    chords: List[str]

# In-memory KV store
video_cache = {}

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

    chords = response.choices[0].message.content.strip() # type: ignore[union-attr]
    return [chord.strip() for chord in chords.split(',')]

async def loop_and_wait_for_generation(gen_id):
    generation = await luma_client.generations.get(id=gen_id)
    while generation.assets is None:
        print("Waiting for generation to complete: ", generation.id)
        await asyncio.sleep(1)
        generation = await luma_client.generations.get(id=gen_id)
    return generation

@app.get("/")
async def root():
    return {"message": "Welcome to Guitar Tab Video Generator API"}

@app.post("/api/extract-chords")
async def extract_chords_api(tab_input: TabInput):
    """
    Extract chords from a given guitar tablature and return unique chords in order.

    Example curl call:
    curl -X POST "http://localhost:8000/api/extract-chords" \
         -H "Content-Type: application/json" \
         -d '{"tab": "Em7   G    Dsus4\\ne|---0---3----2----\\nB|---3---0----3----\\nG|---0---0----2----\\nD|---2---0----0----\\nA|---2---2----x----\\nE|---0---3----x----"}'
    """
    try:
        chords = extract_chords(tab_input.tab)
        unique_chords = []
        for chord in chords:
            if chord not in unique_chords:
                unique_chords.append(chord)
        return {"chords": unique_chords}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def generate_video(chord_name: str):
    if chord_name not in CHORD_IMAGE_MAP:
        raise HTTPException(status_code=400, detail="Chord not found in image map")

    chord_image_urls = CHORD_IMAGE_MAP[chord_name]
    prompt = VIDEO_GENERATION_PROMPT.format(chord_name=chord_name)
    print("Running generation with prompt: ", prompt)
    generation = await luma_client.generations.create(
        prompt=VIDEO_GENERATION_PROMPT.format(chord_name=chord_name),
        keyframes={
            "frame0": {
                "type": "image",
                "url": chord_image_urls["empty"]
            },
            "frame1": {
                "type": "image",
                "url": chord_image_urls["fingered"]
            }
        }
    )
    
    print(generation.id)

    final_generation = await loop_and_wait_for_generation(generation.id)
    video_url = final_generation.assets.video if final_generation.assets else None

    if not video_url:
        raise HTTPException(status_code=500, detail="Video generation failed")
    print(video_url)
    return video_url

@app.post("/api/generate-video")
async def generate_video_api(chord_input: ChordInput):
    """
    Generate a video showing how to play a specific guitar chord.

    Example curl call:
    curl -X POST "http://localhost:8000/api/generate-video" \
         -H "Content-Type: application/json" \
         -d '{"chord_name": "Em7"}'
    """
    try:
        chord_name = chord_input.chord_name
        if chord_name in video_cache:
            return {"video_url": video_cache[chord_name]}
        
        video_url = await generate_video(chord_name)
        video_cache[chord_name] = video_url
        return {"video_url": video_url}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

async def download_video(url: str, output_path: str):
    response = requests.get(url)
    with open(output_path, 'wb') as f:
        f.write(response.content)

def merge_videos(video_paths: List[str], output_path: str):
    inputs = [ffmpeg.input(video) for video in video_paths]
    (
        ffmpeg
        .concat(*inputs)
        .output(output_path)
        .run(overwrite_output=True)
    )

def upload_to_s3(local_file: str, s3_file: str) -> str:
    try:
        s3_client.upload_file(local_file, os.environ.get('AWS_S3_BUCKET_NAME'), s3_file)
        return f"https://{os.environ.get('AWS_S3_BUCKET_NAME')}.s3.amazonaws.com/{s3_file}"
    except NoCredentialsError:
        print("Credentials not available")
        return ""

@app.post("/api/create_chord_progression_video")
async def create_chord_progression_video(chord_progression_input: ChordProgressionInput):
    """
    Generate a single video showing transitions between chords in a progression.

    Example curl call:
    curl -X POST "http://localhost:8000/api/create_chord_progression_video" \
         -H "Content-Type: application/json" \
         -d '{"chords": ["C", "D", "Em", "G"]}'
    """
    chords = chord_progression_input.chords
    
    if len(chords) < 1:
        raise HTTPException(status_code=400, detail="At least one chord is required for a progression")

    async def generate_transition_video(chord1: str, chord2: str, is_first: bool = False):
        if chord1 not in CHORD_IMAGE_MAP or chord2 not in CHORD_IMAGE_MAP:
            raise HTTPException(status_code=400, detail=f"Chord not found in image map: {chord1} or {chord2}")

        if is_first:
            prompt = f"This video shows how to form the {chord1} chord on a guitar. The video starts with an empty guitar neck, then the hand moves in and positions the fingers to form the {chord1} chord."
            start_image = CHORD_IMAGE_MAP[chord1]["empty"]
            end_image = CHORD_IMAGE_MAP[chord1]["fingered"]
        else:
            prompt = f"This video shows a transition from {chord1} chord to {chord2} chord on a guitar. The video starts with fingers positioned for {chord1}, then the hand lifts slightly, moves, and repositions to form the {chord2} chord."
            start_image = CHORD_IMAGE_MAP[chord1]["fingered"]
            end_image = CHORD_IMAGE_MAP[chord2]["fingered"]
        
        generation = await luma_client.generations.create(
            prompt=prompt,
            keyframes={
                "frame0": {
                    "type": "image",
                    "url": start_image
                },
                "frame1": {
                    "type": "image",
                    "url": end_image
                }
            }
        )
        
        final_generation = await loop_and_wait_for_generation(generation.id)
        video_url = final_generation.assets.video if final_generation.assets else None

        if not video_url:
            raise HTTPException(status_code=500, detail=f"Video generation failed for {chord1} to {chord2} transition")
        
        return video_url

    # Generate videos for each chord transition, including the first chord's empty to fingered
    video_tasks = [generate_transition_video(chords[0], chords[0], is_first=True)]  # First chord empty to fingered
    video_tasks += [generate_transition_video(chords[i], chords[i+1]) for i in range(len(chords) - 1)]  # Transitions between chords
    
    try:
        video_urls = await asyncio.gather(*video_tasks)
        
        # Download and merge videos
        with tempfile.TemporaryDirectory() as temp_dir:
            video_paths = []
            for i, url in enumerate(video_urls):
                video_path = os.path.join(temp_dir, f"video_{i}.mp4")
                await download_video(url, video_path)
                video_paths.append(video_path)
            
            output_path = os.path.join(temp_dir, "merged_video.mp4")
            merge_videos(video_paths, output_path)
            
            # Upload to S3
            s3_file_name = f"chord_progression_{'_'.join(chords)}.mp4"
            s3_url = upload_to_s3(output_path, s3_file_name)
            
            if not s3_url:
                raise HTTPException(status_code=500, detail="Failed to upload video to S3")
            
            return {"video_url": s3_url}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))