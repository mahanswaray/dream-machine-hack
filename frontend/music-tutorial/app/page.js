'use client';

import { useState } from 'react';
import Image from 'next/image';

const ExtractedChords = ({ chords }) => (
  <div className="mt-4 p-4 bg-purple-50 rounded-lg border border-purple-200">
    <h3 className="text-xl font-semibold mb-2 text-purple-700">Extracted Chords:</h3>
    <ul className="space-y-1">
      {chords.map((chord, index) => (
        <li key={index} className="text-purple-600 flex items-center">
          <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
          {chord}
        </li>
      ))}
    </ul>
  </div>
);

const VideoPlayer = ({ videoUrl }) => (
  <div className="mt-4">
    <h3 className="text-xl font-semibold mb-2 text-green-700">Generated Video:</h3>
    <div className="relative pt-56.25%">
      <video src={videoUrl} controls className="absolute top-0 left-0 w-full h-full rounded-lg shadow-lg" />
    </div>
  </div>
);

export default function Home() {
  const [tab, setTab] = useState('');
  const [chords, setChords] = useState([]);
  const [chordName, setChordName] = useState('');
  const [videoUrl, setVideoUrl] = useState('');

  const extractChords = async () => {
    // ... (same as before)
    try {
      const response = await fetch('http://localhost:8000/api/extract-chords', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tab }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setChords(data.chords);
    } catch (error) {
      console.error('Error extracting chords:', error);
      // You might want to set an error state here and display it to the user
    }
  };

  const generateVideo = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/generate-video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chord_name: chordName }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setVideoUrl(data.video_url);
    } catch (error) {
      console.error('Error generating video:', error);
      // You might want to set an error state here and display it to the user
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-purple-100 via-blue-100 to-green-100">
      {/* Hero Section */}
      <div className="relative bg-purple-800 overflow-hidden">
        <div className="max-w-7xl mx-auto">
          <div className="relative z-10 pb-8 sm:pb-16 md:pb-20 lg:max-w-2xl lg:w-full lg:pb-28 xl:pb-32">
            <main className="mt-10 mx-auto max-w-7xl px-4 sm:mt-12 sm:px-6 md:mt-16 lg:mt-20 lg:px-8 xl:mt-28">
              <div className="sm:text-center lg:text-left">
                <h1 className="text-4xl tracking-tight font-extrabold text-white sm:text-5xl md:text-6xl">
                  <span className="block xl:inline">Enlighten</span>{' '}
                  <span className="block text-purple-300 xl:inline">my music</span>
                </h1>
                <p className="mt-3 text-base text-purple-200 sm:mt-5 sm:text-lg sm:max-w-xl sm:mx-auto md:mt-5 md:text-xl lg:mx-0">
                  Discover chords from your favorite songs and learn to play them with our interactive video generator.
                </p>
              </div>
            </main>
          </div>
        </div>
        <div className="lg:absolute lg:inset-y-0 lg:right-0 lg:w-1/2">
          <Image
            className="h-56 w-full object-cover sm:h-72 md:h-96 lg:w-full lg:h-full"
            src="/guitar-hero.jpg"
            alt="Guitar player"
            width={1000}
            height={1000}
          />
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          <div className="p-8">
            <h2 className="text-3xl font-bold text-gray-800 mb-6">Guitar Tab Video Generator</h2>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Extract Chords Section */}
              <section className="space-y-4">
                <h3 className="text-2xl font-semibold text-purple-600">Extract Chords</h3>
                <div className="relative">
                  <textarea
                    className="w-full p-3 border-2 border-purple-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    value={tab}
                    onChange={(e) => setTab(e.target.value)}
                    placeholder="Enter guitar tablature here"
                    rows="4"
                  />
                  <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                    <svg className="h-5 w-5 text-purple-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                    </svg>
                  </div>
                </div>
                <button
                  className="w-full px-6 py-3 bg-purple-600 text-white rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 transition duration-300"
                  onClick={extractChords}
                >
                  Extract Chords
                </button>
                {chords.length > 0 && <ExtractedChords chords={chords} />}
              </section>

              {/* Generate Video Section */}
              <section className="space-y-4">
                <h3 className="text-2xl font-semibold text-green-600">Generate Video</h3>
                <div className="relative">
                  <input
                    className="w-full p-3 border-2 border-green-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    value={chordName}
                    onChange={(e) => setChordName(e.target.value)}
                    placeholder="Enter chord name"
                  />
                  <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                    <svg className="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
                <button
                  className="w-full px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition duration-300"
                  onClick={generateVideo}
                >
                  Generate Video
                </button>
                {videoUrl && (
                  <div className="mt-4">
                    <h3>Generated Video:</h3>
                    <video controls width="320" height="240">
                      <source src={videoUrl} type="video/mp4" />
                      Your browser does not support the video tag.
                    </video>
                  </div>
                )}
              </section>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <p>© 2023 Enlighten My Music. All rights reserved.</p>
            <p>Powered by Next.js and FastAPI</p>
          </div>
        </div>
      </footer>
    </main>
  );
}