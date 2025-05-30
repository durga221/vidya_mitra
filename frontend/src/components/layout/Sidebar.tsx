import React from 'react';
import { Link } from 'react-router-dom';
import { Home, BookOpen, Brain, Bot, Map, Book, Lightbulb, Puzzle, CheckSquare, FileCode, Settings, LogOut, Pen, Camera } from 'lucide-react';
import { NavigationItem } from '../../types';

const navigation: NavigationItem[] = [
  { name: 'Dashboard', path: '/', icon: 'Home' },
  { name: 'Resource Provider', path: '/resource_generator', icon: 'Book' },
  { name: 'Chatbot', path: '/chatbot', icon: 'Bot' },
  { name: 'Smart Canvas', path: '/canvas', icon: 'Pen' },
  { name: 'Code Generator', path: '/code_generator', icon: 'FileCode' },
  { name: 'SOS Exam Prep', path: '/sos_exam_prep_kit', icon: 'Lightbulb' },
 
  { name: 'Content Generator', path: '/bos', icon: 'BookOpen' },
  
    
];

const Sidebar = () => {
  const iconMap: Record<string, React.ReactNode> = {
    Home: <Home className="w-5 h-5" />,
    BookOpen: <BookOpen className="w-5 h-5" />,
    Brain: <Brain className="w-5 h-5" />,
    Map: <Map className="w-5 h-5" />,
    Book: <Book className="w-5 h-5" />,
    Lightbulb: <Lightbulb className="w-5 h-5" />,
    Puzzle: <Puzzle className="w-5 h-5" />,
    FileCode: <FileCode className="w-5 h-5" />,
    CheckSquare: <CheckSquare className="w-5 h-5" />,
    Pen: <Pen className="w-5 h-5" />,
    Camera: <Camera className="w-5 h-5" />,
    Bot: <Bot className="w-5 h-5" />,
  };

  return (
    <div className="sticky top-0 flex h-screen w-64 flex-col bg-white border-r border-gray-200 transition-all duration-300 hover:shadow-xl">
      <div className="flex h-16 items-center justify-center border-b border-gray-200">
        <div className="flex items-center space-x-2 px-4 transition-transform duration-300 hover:scale-105">
          <Brain className="h-8 w-8 text-blue-600" />
          <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            Vidya Mitra
          </span>
        </div>
      </div>
      
      <nav className="flex-1 space-y-1 overflow-y-auto p-4">
        {navigation.map((item) => (
          <Link
            key={item.name}
            to={item.path}
            className="group flex items-center px-4 py-3 text-gray-700 rounded-xl transition-all duration-300 hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50 hover:text-blue-700"
          >
            <span className="transition-transform duration-300 group-hover:scale-110">
              {iconMap[item.icon]}
            </span>
            <span className="ml-3 flex-1">{item.name}</span>
            <span className="transform opacity-0 transition-all duration-300 group-hover:translate-x-0 group-hover:opacity-100">
              →
            </span>
          </Link>
        ))}
      </nav>

      <div className="border-t border-gray-200 p-4">
        <button className="flex w-full items-center px-4 py-2 text-gray-700 rounded-xl transition-all duration-300 hover:bg-red-50 hover:text-red-700 group">
          <span className="transition-transform duration-300 group-hover:scale-110">
            <LogOut className="h-5 w-5" />
          </span>
          <span className="ml-3">Logout</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
