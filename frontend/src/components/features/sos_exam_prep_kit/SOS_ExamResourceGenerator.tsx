import React, { useState } from 'react';
import { ClipboardList, Brain, AlertTriangle, Loader2 } from 'lucide-react';

type AidType = 'cheat_sheet' | 'mnemonics' | 'mistakes';

interface AidTypeInfo {
  name: string;
  icon: React.ElementType;
  color: string;
}

const SOSExamRescueKit = () => {
  const [examTopic, setExamTopic] = useState('');
  const [selectedComponent, setSelectedComponent] = useState<AidType>('cheat_sheet');
  const [generatedContent, setGeneratedContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const aidTypeMap: Record<AidType, AidTypeInfo> = {
    cheat_sheet: { name: 'Cheat Sheet', icon: ClipboardList, color: 'text-blue-600' },
    mnemonics: { name: 'Memory Aids', icon: Brain, color: 'text-green-600' },
    mistakes: { name: 'Common Mistakes', icon: AlertTriangle, color: 'text-red-600' }
  };

  const handleGenerate = async () => {
    setLoading(true);
    setError('');
    setGeneratedContent('');

    try {
      const response = await fetch(' http://localhost:8006/generate-study-aid', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: examTopic,
          aid_type: selectedComponent
        }),
        credentials: 'omit'  
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate content');
      }

      const data = await response.json();
      
      setGeneratedContent(data.result);
    } catch (err) {
      setError(err.message || 'Failed to generate content. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-6 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-xl p-4 sm:p-6 shadow-lg">
          <div className="flex flex-col sm:flex-row items-center gap-4">
            <ClipboardList className="w-8 h-8 text-blue-600 shrink-0" />
            <div className="text-center sm:text-left">
              <h1 className="text-xl sm:text-2xl font-bold text-gray-900">SOS Exam Rescue Kit</h1>
              <p className="text-sm sm:text-base text-gray-600">Last minute study aids for Exam preparation</p>
            </div>
          </div>
        </div>

        
        <div className="grid gap-6 lg:grid-cols-[1fr_2fr]">
          
          <div className="bg-white rounded-xl p-4 sm:p-6 shadow-lg">
            <h2 className="text-lg font-semibold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Generate Study Aid
            </h2>
            <div className="space-y-4">
              <input
                type="text"
                value={examTopic}
                onChange={(e) => setExamTopic(e.target.value)}
                placeholder="Enter your exam topic..."
                className="w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />

              <select
                value={selectedComponent}
                onChange={(e) => setSelectedComponent(e.target.value as AidType)}
                className="w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {Object.entries(aidTypeMap).map(([value, { name }]) => (
                  <option key={value} value={value}>{name}</option>
                ))}
              </select>

              <button
                onClick={handleGenerate}
                disabled={!examTopic.trim() || loading}
                className="w-full py-2 px-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg
                          hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Generating...
                  </span>
                ) : 'Generate Content'}
              </button>
            </div>
          </div>

    
          <div className="bg-white rounded-xl p-4 sm:p-6 shadow-lg">
            <h2 className="text-lg font-semibold mb-4">Generated Content</h2>

            <div className="min-h-[300px]">
              {loading ? (
                <div className="flex flex-col items-center justify-center h-64 gap-3">
                  <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
                  <p className="text-gray-600">Generating your study aid...</p>
                </div>
              ) : error ? (
                <div className="flex flex-col items-center justify-center h-64 text-red-500">
                  <AlertTriangle className="w-8 h-8 mb-2" />
                  <p>{error}</p>
                </div>
              ) : generatedContent ? (
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    {(() => {
                      const IconComponent = aidTypeMap[selectedComponent].icon;
                      return (
                        <IconComponent 
                          className={`w-5 h-5 ${aidTypeMap[selectedComponent].color}`} 
                        />
                      );
                    })()}
                    <h3 className="font-semibold text-gray-800">
                      {aidTypeMap[selectedComponent].name}
                    </h3>
                  </div>
                  <div className="prose prose-sm sm:prose-base max-w-none">
                    <pre className="whitespace-pre-wrap text-gray-900 font-sans">
                      {generatedContent}
                    </pre>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-64 text-gray-400">
                  <ClipboardList className="w-12 h-12 mb-2" />
                  <p>Enter a topic to generate study content</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SOSExamRescueKit;