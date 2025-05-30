

import React, { useState } from 'react';
import { BookOpen, MonitorPlay, Globe, Youtube, Loader2, Info } from 'lucide-react';


interface Book {
  title: string;
  author: string;
  description: string;
}

interface OnlineCourse {
  platform: string;
  course_name: string;
  url: string;
  description: string;
}

interface Website {
  name: string;
  url: string;
  description: string;
}

interface YoutubeChannel {
  channel_name: string;
  url: string;
  description: string;
}

interface ApiResponse {
  learning_plan?: string;
  books: Book[];
  online_courses: OnlineCourse[];
  websites: Website[];
  youtube_channels: YoutubeChannel[];
}

const LearningResourceGenerator = () => {
  const [topic, setTopic] = useState('');
  const [resources, setResources] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeCategory, setActiveCategory] = useState<string>('All');

  const handleGenerate = async () => {
    if (!topic.trim()) return;
    
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('http://localhost:8000/generate-resources/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch resources');
      }

      const data = await response.json();
      setResources(data);
    } catch (err) {
      setError('Failed to generate resources. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getResourcesByCategory = () => {
    if (!resources) return [];

    switch (activeCategory) {
      case 'Books':
        return [{
          title: 'Books',
          icon: <BookOpen className="w-5 h-5 text-blue-600" />,
          items: resources.books.map(book => ({
            title: book.title,
            description: `By ${book.author} - ${book.description}`,
            link: '#'
          }))
        }];
      case 'Courses':
        return [{
          title: 'Courses',
          icon: <MonitorPlay className="w-5 h-5 text-green-600" />,
          items: resources.online_courses.map(course => ({
            title: course.course_name,
            description: `${course.platform} - ${course.description}`,
            link: course.url
          }))
        }];
      case 'Websites':
        return [{
          title: 'Websites',
          icon: <Globe className="w-5 h-5 text-purple-600" />,
          items: resources.websites.map(website => ({
            title: website.name,
            description: website.description,
            link: website.url
          }))
        }];
      case 'YouTube':
        return [{
          title: 'YouTube',
          icon: <Youtube className="w-5 h-5 text-red-600" />,
          items: resources.youtube_channels.map(channel => ({
            title: channel.channel_name,
            description: channel.description,
            link: channel.url
          }))
        }];
      default:
        return [
          {
            title: 'Books',
            icon: <BookOpen className="w-5 h-5 text-blue-600" />,
            items: resources.books.map(book => ({
              title: book.title,
              description: `By ${book.author} - ${book.description}`,
              link: '#'
            }))
          },
          {
            title: 'Courses',
            icon: <MonitorPlay className="w-5 h-5 text-green-600" />,
            items: resources.online_courses.map(course => ({
              title: course.course_name,
              description: `${course.platform} - ${course.description}`,
              link: course.url
            }))
          },
          {
            title: 'Websites',
            icon: <Globe className="w-5 h-5 text-purple-600" />,
            items: resources.websites.map(website => ({
              title: website.name,
              description: website.description,
              link: website.url
            }))
          },
          {
            title: 'YouTube',
            icon: <Youtube className="w-5 h-5 text-red-600" />,
            items: resources.youtube_channels.map(channel => ({
              title: channel.channel_name,
              description: channel.description,
              link: channel.url
            }))
          }
        ];
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 animate-fade-in">
      {/* Header */}
      <div className="bg-white rounded-2xl p-8 shadow-lg mb-8 animate-slide-in-top">
        <div className="flex items-center space-x-4">
          <BookOpen className="w-8 h-8 text-blue-600 transition-transform duration-300 hover:scale-110" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Learning Resource Generator</h1>
            <p className="text-gray-600">Discover the best resources to master any topic</p>
          </div>
        </div>
      </div>

      <div className="grid gap-8 md:grid-cols-[1fr_2fr]">
        {/* Input Section */}
        <div className="bg-white rounded-2xl p-6 shadow-lg transform transition-all duration-500 hover:shadow-xl animate-slide-in-left">
          <h2 className="text-lg font-semibold mb-6 text-gradient bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Enter Your Learning Topic
          </h2>
          <div className="space-y-6">
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Machine Learning, Web Development..."
              className="w-full px-4 py-3 rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 
                        transition-all duration-300 hover:border-blue-300 focus:scale-[1.02]"
              onKeyPress={(e) => e.key === 'Enter' && handleGenerate()}
            />
            
            <button
              onClick={handleGenerate}
              disabled={!topic.trim() || loading}
              className="w-full py-3 px-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg 
                        hover:scale-[1.02] disabled:opacity-50 disabled:scale-100 disabled:cursor-not-allowed 
                        transition-all duration-300 shadow-md hover:shadow-lg"
            >
              {loading ? (
                <div className="flex items-center justify-center space-x-2">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Generating...</span>
                </div>
              ) : 'Generate Resources'}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-50 text-red-600 rounded-lg">
              {error}
            </div>
          )}
          
          {resources?.learning_plan && (
            <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-100">
              <div className="flex items-center space-x-2 mb-2">
                <Info className="w-5 h-5 text-blue-600" />
                <h3 className="font-medium text-blue-700">Learning Plan Overview</h3>
              </div>
              <p className="text-sm text-blue-800">{resources.learning_plan}</p>
            </div>
          )}
        </div>

        {/* Results Section */}
        <div className="bg-white rounded-2xl p-6 shadow-lg animate-slide-in-right">
          <h2 className="text-lg font-semibold mb-6">Recommended Resources</h2>

          {/* Navigation Bar */}
          {resources && (
            <div className="flex space-x-4 mb-6 overflow-x-auto pb-2">
              {['All', 'Books', 'Courses', 'Websites', 'YouTube'].map((category) => (
                <button
                  key={category}
                  onClick={() => setActiveCategory(category)}
                  className={`px-4 py-2 rounded-lg transition-all duration-300 whitespace-nowrap ${
                    activeCategory === category
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-blue-100'
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
          )}

          <div className="space-y-8">
            {loading ? (
              <div className="flex flex-col items-center justify-center h-64 space-y-4">
                <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
                <p className="text-gray-600">Searching best resources...</p>
              </div>
            ) : !resources ? (
              <div className="flex flex-col items-center justify-center h-64 text-gray-400 animate-pulse">
                <BookOpen className="w-12 h-12 mb-2" />
                <p>Enter a topic to get learning resources</p>
              </div>
            ) : (
              getResourcesByCategory().map((category) => (
                <div 
                  key={category.title} 
                  className="bg-gray-50 rounded-xl p-5 transform transition-all duration-300 hover:scale-[1.01]"
                >
                  <div className="flex items-center space-x-2 mb-4">
                    {category.icon}
                    <h3 className="font-semibold text-gray-800">{category.title}</h3>
                  </div>
                  {category.items.length > 0 ? (
                    <div className="space-y-3">
                      {category.items.map((item, index) => (
                        <a
                          key={index}
                          href={item.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block p-3 bg-white rounded-lg hover:shadow-md transition-all duration-300 
                                    transform hover:-translate-y-1 hover:border-blue-200 border border-transparent"
                        >
                          <div className="font-medium text-gray-900">{item.title}</div>
                          <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                        </a>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 italic">No resources found in this category.</p>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LearningResourceGenerator;