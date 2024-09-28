# Guitar Tab Video Generator

## Project Overview
Guitar Tab Video Generator is an innovative web application developed during a hackathon. It allows users to input guitar tablature and receive a video demonstration of how to play the corresponding chords. The application leverages the LumaAI API for generating videos from text and images.

## Features
- Guitar tab input interface
- Chord extraction from tablature
- Public image retrieval of chord fingerings
- Video generation of chord demonstrations using LumaAI
- Sequential playback of generated chord videos

## Tech Stack
- Frontend: Next.js
- Backend: FastAPI
- Video Generation: LumaAI API

## Architecture
The application consists of a Next.js frontend that communicates with a FastAPI backend. The backend exposes two main APIs:

1. Chord Extraction API
2. Video Generation API (using LumaAI)

The backend processes the user input, extracts chord information, fetches relevant images, and interacts with the LumaAI API to create the final output.

## API Endpoints

### 1. Chord Extraction API
- **Endpoint:** `/api/extract-chords`
- **Method:** POST
- **Input:** Raw guitar tablature text
- **Output:** JSON array of identified chords

```
curl -X POST http://localhost:8000/api/extract-chords -H "Content-Type: application/json" -d '{"tab": "Em7   G    Dsus4\ne|---0---3----2----\nB|---3---0----3----\nG|---0---0----2----\nD|---2---0----0----\nA|---2---2----x----\nE|---0---3----x----"}'
```

### 2. Video Generation API
- **Endpoint:** `/api/generate-video`
- **Method:** POST
- **Input:** Chord information and associated images
- **Output:** URL or data for the generated video

## Workflow
1. User inputs guitar tabs into the web interface
2. Frontend sends tab data to the backend
3. Backend extracts chord information from the tabs
4. Backend fetches public images of humans playing these chords
5. Backend uses LumaAI API to generate videos demonstrating each chord
6. Backend compiles the videos and sends the result back to the frontend
7. Frontend displays the chord demonstration videos to the user

## Implementation Tasks

1. Set up project structure
   - [ ] Initialize Next.js frontend
   - [ ] Set up FastAPI backend
   - [ ] Configure project dependencies
   - [ ] Set up LumaAI client with API key

2. Frontend Development
   - [ ] Create main page layout
   - [ ] Implement tab input component
   - [ ] Design video playback interface
   - [ ] Develop API communication functions

3. Backend Development
   - [ ] Implement chord extraction algorithm
   - [ ] Create API endpoint for chord extraction
   - [ ] Develop image fetching functionality
   - [ ] Create API endpoint for video generation using LumaAI
   - [ ] Integrate with LumaAI API for video generation

4. LumaAI API Integration
   - [ ] Implement generation creation using LumaAI client
   - [ ] Handle asynchronous generation process
   - [ ] Implement error handling and validation
   - [ ] Optimize API responses and requests
   - [ ] Ensure secure communication between backend and LumaAI API

5. Video Processing
   - [ ] Implement video compilation logic using LumaAI generated assets
   - [ ] Optimize video delivery to frontend

6. Testing
   - [ ] Develop unit tests for backend functions
   - [ ] Create integration tests for API endpoints
   - [ ] Perform end-to-end testing of the entire application
   - [ ] Test LumaAI API integration thoroughly

7. Documentation
   - [ ] Write API documentation, including LumaAI integration
   - [ ] Create user guide for the application
   - [ ] Document setup and deployment processes, including LumaAI API key configuration

8. Deployment
   - [ ] Set up deployment environment
   - [ ] Configure CI/CD pipeline
   - [ ] Deploy application to chosen hosting platform
   - [ ] Ensure secure storage of LumaAI API key in production

9. Final Testing and Polishing
   - [ ] Conduct thorough testing in production environment
   - [ ] Address any last-minute bugs or issues
   - [ ] Optimize performance and user experience
   - [ ] Fine-tune LumaAI generation parameters for best results