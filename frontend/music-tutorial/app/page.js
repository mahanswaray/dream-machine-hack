'use client';

import { useState } from 'react';

const ExtractedChords = ({ chords }) => (
  <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
    <h3 className="text-xl font-semibold mb-2 text-blue-700">Extracted Chords:</h3>
    <ul className="space-y-1">
      {chords.map((chord, index) => (
        <li key={index} className="text-blue-600 flex items-center">
          <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
          {chord}
        </li>
      ))}
    </ul>
  </div>
);

const VideoPlayer = ({ videoUrl, isLoading, chordName }) => (
  <div className="mt-4">
    <h3 className="text-xl font-semibold mb-2 text-green-700">Video for {chordName}:</h3>
      {isLoading ? (
        <div className="w-full h-full flex items-center justify-center bg-gray-200 rounded-lg">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
        </div>
      ) : videoUrl ? (
        <video src={videoUrl} controls className="w-full h-full rounded-lg shadow-lg" />
      ) : (
        <div className="w-full h-full flex items-center justify-center bg-gray-200 rounded-lg">
          <p className="text-gray-500">Video not available</p>
        </div>
      )}
  </div>
);

export default function Home() {
  const [tab, setTab] = useState('');
  const [chords, setChords] = useState([]);
  const [videos, setVideos] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const extractChordsAndGenerateVideos = async () => {
    setIsLoading(true);
    try {
      // Extract chords
      const chordsResponse = await fetch('http://localhost:8000/api/extract-chords', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tab }),
      });
      if (!chordsResponse.ok) {
        throw new Error(`HTTP error! status: ${chordsResponse.status}`);
      }
      const chordsData = await chordsResponse.json();
      setChords(chordsData.chords);

      // Generate videos for all chords in parallel
      const videoPromises = chordsData.chords.map(async (chord) => {
        const videoResponse = await fetch('http://localhost:8000/api/generate-video', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ chord_name: chord }),
        });
        if (!videoResponse.ok) {
          throw new Error(`HTTP error! status: ${videoResponse.status}`);
        }
        const videoData = await videoResponse.json();
        return { chord, videoUrl: videoData.video_url };
      });

      const videoResults = await Promise.all(videoPromises);
      const newVideos = {};
      videoResults.forEach(({ chord, videoUrl }) => {
        newVideos[chord] = videoUrl;
      });
      setVideos(newVideos);
    } catch (error) {
      console.error('Error extracting chords or generating videos:', error);
      // You might want to set an error state here and display it to the user
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-100 via-blue-50 to-white">
      {/* Hero Section */}
      <div className="relative bg-blue-100 overflow-hidden">
        <div className="max-w-7xl mx-auto">
          <div className="relative z-10 pb-8 sm:pb-16 md:pb-20 lg:max-w-2xl lg:w-full lg:pb-28 xl:pb-32">
            <main className="mt-10 mx-auto max-w-7xl px-4 sm:mt-12 sm:px-6 md:mt-16 lg:mt-20 lg:px-8 xl:mt-28">
              <div className="sm:text-center lg:text-left">
                <h1 className="text-4xl tracking-tight font-extrabold text-white sm:text-5xl md:text-6xl">
                  <span className="block text-blue-800 xl:inline">Enlighten</span>{' '}
                  <span className="block text-blue-400 xl:inline">my music</span>
                </h1>
                <p className="mt-3 text-base text-blue-500 sm:mt-5 sm:text-lg sm:max-w-xl sm:mx-auto md:mt-5 md:text-xl lg:mx-0">
                  Discover chords from your favorite songs and learn to play them with our interactive video generator.
                </p>
              </div>
            </main>
          </div>
        </div>
        {/* Replace the Image component with a colored div */}
        <div className="lg:absolute lg:inset-y-0 lg:right-0 lg:w-1/2">
          <div className="h-56 w-full bg-blue-700 sm:h-72 md:h-96 lg:w-full lg:h-full"></div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          <div className="p-8">
            <h2 className="text-3xl font-bold text-blue-800 mb-6">Guitar Tab Video Generator</h2>

            <div className="space-y-4">
              <h3 className="text-2xl font-semibold text-purple-600">Extract Chords and Generate Videos</h3>
              <div className="relative">
                <textarea
                  className="w-full p-3 border-2 border-purple-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  value={tab}
                  onChange={(e) => setTab(e.target.value)}
                  placeholder="Enter guitar tablature here"
                  rows="4"
                />
              </div>
              <button
                className="w-full px-6 py-3 bg-purple-600 text-white rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 transition duration-300"
                onClick={extractChordsAndGenerateVideos}
                disabled={isLoading}
              >
                {isLoading ? 'Processing...' : 'Extract Chords and Generate Videos'}
              </button>
            </div>

            {chords.length > 0 && (
              <div className="mt-8">
                <ExtractedChords chords={chords} />
                <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {chords.map((chord) => (
                    <VideoPlayer
                      key={chord}
                      videoUrl={videos[chord]}
                      isLoading={isLoading}
                      chordName={chord}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-blue-800 text-white py-8">
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