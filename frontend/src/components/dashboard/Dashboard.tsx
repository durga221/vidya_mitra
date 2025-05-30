
import React from 'react';
import FeatureCard from './FeatureCard';
import { Feature } from '../../types';
import { BookOpen, Brain, Map, Book,Bot, Lightbulb, Puzzle as PuzzlePiece, FileCode, Pen, CheckSquare, Camera } from 'lucide-react';

const features: Feature[] = [
   {
    id: '1',
    title: 'Resource Provider',
    description: 'Find curated learning resources and materials',
    icon: 'Book',
    path: '/resource_generator'
  },
  {
    id: '2',
    title: 'Chatbot',
    description:  'Chatbot that interacts in multiple languages',
    icon: 'Bot',
    path: '/chatbot'
  },
  {
    id: '3',
    title: 'Smart_Canvas',
    description: 'Draw or write problems to get step-by-step solutions',
    icon: 'Pen',
    path: '/canvas'
  },
  {
    id: '4',
    title: 'Code Generator',
    description: 'Generate and explain simple , Optimized code solutions',
    icon: 'FileCode',
    path: '/code_generator'
  },
  {
    id: '7',
    title: 'SOS Exam Prep',
    description: 'Quick exam preparation with cheat sheets and mnemonics',
    icon: 'Lightbulb',
    path: '/sos_exam_prep_kit'
  },
  
  {
    id: '6',
    title: 'Content Generator',
    description: 'Generate study materials and flashcards based on your syllabus',
    icon: 'BookOpen',
    path: '/bos'
  },
  
 
  
];

const Dashboard = () => {
  return (
    <div className="space-y-8">
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 p-8 shadow-lg">
        <div className="relative z-10">
          <h1 className="text-4xl font-bold tracking-tight text-white animate-fade-in">
            Welcome to VidyaMitra
          </h1>
          <p className="mt-4 max-w-xl text-lg text-blue-100 animate-slide-up">
            Empowering your learning journey with AI-powered tools
          </p>
        </div>
        <div className="absolute top-0 right-0 -translate-y-1/4 translate-x-1/4">
          <div className="h-64 w-64 rounded-full bg-white/10 blur-3xl"></div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 ">
        {features.map((feature, index) => (
          <div
            key={feature.id}
            className="animate-fade-in"
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <FeatureCard feature={feature} />
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;