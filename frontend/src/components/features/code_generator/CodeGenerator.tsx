import React, { useState } from 'react';
import { Copy, Terminal, Info, Rocket } from 'lucide-react';

interface CodeResponse {
  code_blocks: string[];
  explanation: string;
  messages: Array<{
    role: string;
    content: string;
    timestamp: string;
  }>;
}

const CodeGenerator = () => {
  const [inputText, setInputText] = useState('');
  const [generatedCode, setGeneratedCode] = useState<CodeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generateCode = async (prompt: string): Promise<CodeResponse> => {
    const response = await fetch('http://localhost:8008/generate-code/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    });

    console.log(response)

    if (!response.ok) {
      throw new Error('Failed to generate code');
    }

    return response.json();
  };

  const handleGenerate = async () => {
    if (!inputText.trim()) {
      setError('Please enter a code-related question or description');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await generateCode(inputText);
      setGeneratedCode(response);
    } catch (err) {
      setError('Failed to generate code. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      <div className="bg-white rounded-2xl p-8 shadow-lg">
        <div className="flex items-center space-x-4 mb-6">
          <Terminal className="w-8 h-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Code Generator</h1>
            <p className="text-gray-600">Describe your programming problem or request to generate simple , effective ,Optimized code</p>
          </div>
        </div>

        <div className="space-y-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-gray-700">
                Describe your code needs
              </label>
              <span className="text-sm text-gray-500">Example: "JavaScript function that reverses a string"</span>
            </div>
            
            <textarea
              value={inputText}
              onChange={(e) => {
                setInputText(e.target.value);
                setError('');
              }}
              placeholder="Enter your code request here..."
              className="w-full h-32 p-4 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
            />

            {error && <p className="text-red-500 text-sm">{error}</p>}

            <button
              onClick={handleGenerate}
              disabled={loading}
              className="w-full py-3 px-6 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 flex items-center justify-center disabled:opacity-50"
            >
              {loading ? (
                <>
                  <span className="animate-spin mr-2">🌀</span>
                  Generating...
                </>
              ) : (
                <>
                  <Rocket className="w-5 h-5 mr-2" />
                  Generate Code
                </>
              )}
            </button>
          </div>

          {generatedCode && (
            <div className="space-y-6">
              {generatedCode.code_blocks.map((code, index) => (
                <div key={index} className="bg-gray-50 rounded-xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold flex items-center">
                      <Terminal className="w-5 h-5 mr-2 text-blue-600" />
                      Generated Code {generatedCode.code_blocks.length > 1 ? `(${index + 1})` : ''}
                    </h3>
                    <button
                      onClick={() => copyToClipboard(code)}
                      className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
                      title="Copy to clipboard"
                    >
                      <Copy className="w-5 h-5 text-gray-600" />
                    </button>
                  </div>

                  <pre className="bg-gray-900 text-gray-100 rounded-lg p-4 overflow-x-auto">
                    <code className="text-sm font-mono">{code}</code>
                  </pre>
                </div>
              ))}

              <div className="bg-blue-50 rounded-xl p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <Info className="w-5 h-5 mr-2 text-blue-600" />
                  Explanation
                </h3>
                <p className="text-gray-700 whitespace-pre-line">{generatedCode.explanation}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CodeGenerator;