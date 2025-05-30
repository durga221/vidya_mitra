
import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import * as React from 'react';

interface GeneratedResult {
  solution: string | null;
  steps: Array<string>;
  explanation: string;
  assign: boolean;
}

interface TailwindDropdownProps {
  onActionSelect: (action: string) => void;
}

const ColorSwatch: React.FC<{color: string; onClick: () => void }> = ({ color, onClick }) => (
  <button
    onClick={onClick}
    className="w-8 h-8 rounded-full border border-gray-300 cursor-pointer transition-transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
    style={{ backgroundColor: color }}
  />
);

const CustomButton: React.FC<{
  onClick: () => void;
  children: React.ReactNode;
  className?: string;
}> = ({ onClick, children, className = "" }) => (
  <button
    onClick={onClick}
    className={`px-4 py-2 bg-gray-800 text-white rounded-md hover:bg-gray-700 transition-colors duration-200 ${className}`}
  >
    {children}
  </button>
);

const TailwindDropdown: React.FC<TailwindDropdownProps> = ({ onActionSelect }) => {
  const [selectedOption, setSelectedOption] = useState<string>("Mathematics");
  const [isOpen, setIsOpen] = useState<boolean>(false);

  const handleOptionSelect = (option: string): void => {
    setSelectedOption(option);
    onActionSelect(option);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="px-4 py-2 bg-gray-800 text-white rounded-md hover:bg-gray-700 transition-colors duration-200 text-left"
      >
        {selectedOption}
      </button>
      
      {isOpen && (
        <div className="absolute mt-1 bg-white border border-gray-200 rounded-md shadow-lg z-50 w-40">
          <div className="py-1">
            <button
              onClick={() => handleOptionSelect("Mathematics")}
              className="block w-full px-4 py-2 text-left text-gray-700 hover:bg-gray-100"
            >
              Mathematics
            </button>
            <button
              onClick={() => handleOptionSelect("Aptitude")}
              className="block w-full px-4 py-2 text-left text-gray-700 hover:bg-gray-100"
            >
              Aptitude
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

const Canvas: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isDrawing, setIsDrawing] = useState<boolean>(false);
  const [color, setColor] = useState<string>('#ffffff');
  const [dictOfVars, setDictOfVars] = useState<Record<string, any>>({});
  const [isEraser, setIsEraser] = useState<boolean>(false);
  const [selectedAction, setSelectedAction] = useState<string>("Mathematics");
  const [answer, setAnswer] = useState<{
    result: string | null;
    steps: string[];
  }>({
    result: null,
    steps: [],
  });
  
  const SWATCHES: string[] = ['#ffffff', '#ff0000', '#00ff00', '#0000ff', '#ffff00'];

  useEffect(() => {
    const resizeCanvas = () => {
      const canvas = canvasRef.current;
      const container = containerRef.current;
      
      if (canvas && container) {
        canvas.width = container.clientWidth;
        canvas.height = container.clientHeight;
        
        const ctx = canvas.getContext('2d');
        if (ctx) {
          ctx.lineCap = 'round';
          ctx.lineWidth = 3;
          canvas.style.background = 'black';
        }
      }
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    return () => window.removeEventListener('resize', resizeCanvas);
  }, []);

  // Canvas operation functions
  const resetCanvas = (): void => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
    }
  };

  const startDrawing = (e: React.MouseEvent<HTMLCanvasElement>): void => {
    const canvas = canvasRef.current;
    if (canvas) {
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.beginPath();
        ctx.moveTo(x, y);
        setIsDrawing(true);
        ctx.strokeStyle = isEraser ? 'black' : color;
      }
    }
  };

  const draw = (e: React.MouseEvent<HTMLCanvasElement>): void => {
    if (!isDrawing) return;
    const canvas = canvasRef.current;
    if (canvas) {
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        if (isEraser) {
          ctx.strokeStyle = 'black';
          ctx.lineWidth = 20;
          ctx.lineTo(x, y);
          ctx.stroke();
          ctx.beginPath();
          ctx.moveTo(x, y);
        } else {
          ctx.strokeStyle = color;
          ctx.lineWidth = 3;
          ctx.lineTo(x, y);
          ctx.stroke();
        }
      }
    }
  };

  const stopDrawing = (): void => {
    setIsDrawing(false);
  };

  const runRoute = async (): Promise<void> => {
  const canvas = canvasRef.current;
  if (canvas) {
    try {
      const response = await fetch("http://localhost:8900/calculate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          image: canvas.toDataURL("image/avif"),
          dict_of_vars: dictOfVars,
          action: selectedAction,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();

      setAnswer({
        result: data.data[0]["explanation"],
        steps: data.data[0]["steps"],
      });
    } catch (error) {
      console.error("Error processing image:", error);
    }
  }
};

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col">
      {/* Header with controls */}
      <header className="bg-black py-4 px-6 shadow-lg">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="text-3xl font-bold">
            <span className="text-cyan-400">BrainWave</span>
            <span className="text-white pl-3">Solver</span>
          </div>
          
          {/* Controls */}
          <div className="flex items-center space-x-4">
            <TailwindDropdown onActionSelect={setSelectedAction} />
            
            <div className="flex items-center space-x-2 bg-gray-800 p-2 rounded-md">
              {SWATCHES.map((swatch) => (
                <ColorSwatch
                  key={swatch}
                  color={swatch}
                  onClick={() => {
                    setColor(swatch);
                    setIsEraser(false);
                  }}
                />
              ))}
            </div>
            
            <CustomButton onClick={resetCanvas}>
              Clear Screen
            </CustomButton>
            
            <CustomButton
              onClick={() => setIsEraser(!isEraser)}
              className={isEraser ? 'bg-red-600 hover:bg-red-700' : ''}
            >
              {isEraser ? 'Disable Eraser' : 'Enable Eraser'}
            </CustomButton>
            
            <CustomButton
              onClick={runRoute}
              className="bg-cyan-600 hover:bg-cyan-700"
            >
              Analyse
            </CustomButton>
          </div>
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 flex">
        {/* Canvas Area */}
        <div className="flex-1 relative" ref={containerRef}>
          <canvas
            ref={canvasRef}
            onMouseDown={startDrawing}
            onMouseMove={draw}
            onMouseUp={stopDrawing}
            onMouseOut={stopDrawing}
            className="absolute inset-0 cursor-crosshair"
          />
        </div>

        {/* Analysis Panel */}
        <div className="w-80 bg-gray-800 p-4 overflow-y-auto text-white">
          <h2 className="text-xl font-semibold mb-4 text-cyan-400">Analysis Results</h2>
          
          {answer.steps.length > 0 && (
            <div className="mb-4">
              <h3 className="text-lg font-medium mb-2">Solution Steps:</h3>
              <ol className="list-decimal pl-4 space-y-2">
                {answer.steps.map((step, index) => (
                  <li key={index}>{step}</li>
                ))}
              </ol>
            </div>
          )}
          
          {answer.result && (
            <div className="mt-4">
              <h3 className="text-lg font-medium mb-2">Final Result:</h3>
              <p className="text-cyan-400">{answer.result}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Canvas;