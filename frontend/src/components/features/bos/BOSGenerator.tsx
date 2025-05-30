
import React, { useState } from 'react';
import { BookOpen, Loader, Check } from 'lucide-react';

const BOSGenerator = () => {
  const [topic, setTopic] = useState('');
  const [level, setLevel] = useState<'beginner' | 'intermediate' | 'advanced'>('beginner');
  const [generating, setGenerating] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [generatedContent, setGeneratedContent] = useState('');
  const [revisionNotes, setRevisionNotes] = useState<string[]>([]);
  const [error, setError] = useState('');

  const generateContent = async () => {
    try {
      setGenerating(true);
      setError('');
      const response = await fetch('http://127.0.0.1:8001/get_content', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          subject: '',
          topic: topic,
          student_level: level,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate content');
      }

      const data = await response.json();
      setGeneratedContent(data.content);
      setRevisionNotes(data.revision_notes);
      setIsSubmitted(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error generating content');
      console.error(err);
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = () => {
    const content = `
Topic: ${topic}
Level: ${level}

Content:
${generatedContent}

Revision Notes:
${revisionNotes.join('\n')}
    `.trim();
  
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${topic}_Study_Materials.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const renderForm = () => (
    <div className="bg-white rounded-2xl p-6 shadow-lg space-y-6">
      <div className="space-y-4">
        <h3 className="font-semibold">1. Enter Topic</h3>
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter topic name"
          className="w-full rounded-lg border-gray-200 p-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
      <div className="space-y-4">
        <h3 className="font-semibold">2. Select Level</h3>
        <select
          value={level}
          onChange={(e) => setLevel(e.target.value as 'beginner' | 'intermediate' | 'advanced')}
          className="w-full rounded-lg border-gray-200 p-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
      </div>
      <button
        onClick={generateContent}
        disabled={generating || !topic}
        className="w-full py-2 px-4 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition-colors duration-200"
      >
        {generating ? (
          <div className="flex items-center justify-center space-x-2">
            <Loader className="w-4 h-4 animate-spin" />
            <span>Generating Content...</span>
          </div>
        ) : (
          'Generate Study Materials'
        )}
      </button>
    </div>
  );

  const renderResults = () => (
    <div className="bg-white rounded-2xl p-6 shadow-lg space-y-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">Generated Content for "{topic}"</h2>
        <Check className="w-6 h-6 text-green-600" />
      </div>

      <div className="space-y-4">
        <button
          onClick={handleDownload}
          className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
        >
          Download Study Materials
        </button>

        <div className="p-4 bg-white rounded-lg shadow-sm">
          <h3 className="font-semibold mb-4">Content:</h3>
          <div className="prose max-w-none whitespace-pre-wrap">
            {generatedContent}
          </div>
        </div>

        <div className="p-4 bg-gray-50 rounded-lg">
          <h3 className="font-semibold mb-4">Revision Notes:</h3>
          <ul className="list-disc pl-5 space-y-2">
            {revisionNotes.map((note, index) => (
              <li key={index}>{note}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="bg-white rounded-2xl p-8 shadow-lg">
          <div className="flex items-center space-x-4">
            <BookOpen className="w-8 h-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Study Materials Generator
              </h1>
              <p className="text-gray-600">
                Enter a topic and select difficulty level to generate study materials
              </p>
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {!isSubmitted ? renderForm() : renderResults()}
      </div>
    </div>
  );
};

export default BOSGenerator;
