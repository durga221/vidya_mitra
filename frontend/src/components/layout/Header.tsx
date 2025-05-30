import React, { useState } from 'react';
import { Bell, Search, Settings } from 'lucide-react';
import { Link } from 'react-router-dom';

const Header = () => {
  const [isSearchFocused, setIsSearchFocused] = useState(false);

  return (
    <header className="sticky top-0 z-30 bg-white border-b border-gray-200 transition-shadow duration-300 hover:shadow-sm">
      <div className="mx-auto max-w-7xl">
        <div className="flex h-16 items-center justify-between px-6">
          <div className="flex items-center flex-1">
            <div className={`flex items-center transition-all duration-300 ${isSearchFocused ? 'w-96' : 'w-72'}`}>
              <div className="relative flex items-center w-full">
                <Search className={`absolute left-3 w-5 h-5 transition-colors duration-300 ${isSearchFocused ? 'text-blue-600' : 'text-gray-400'}`} />
                <input
                  type="text"
                  placeholder="Search..."
                  onFocus={() => setIsSearchFocused(true)}
                  onBlur={() => setIsSearchFocused(false)}
                  className="w-full pl-10 pr-4 py-2 text-sm text-gray-700 bg-gray-50 rounded-xl border-2 border-transparent transition-all duration-300 focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-4 focus:ring-blue-50"
                />
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <button className="relative p-2 text-gray-500 rounded-lg transition-all duration-300 hover:bg-blue-50 hover:text-blue-600 focus:outline-none focus:ring-4 focus:ring-blue-50">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-red-500 ring-2 ring-white"></span>
            </button>
            <button className="p-2 text-gray-500 rounded-lg transition-all duration-300 hover:bg-blue-50 hover:text-blue-600 focus:outline-none focus:ring-4 focus:ring-blue-50">
              <Settings className="w-5 h-5" />
            </button>
            <div className="relative group">
              <button className="flex items-center transition-transform duration-300 group-hover:scale-105">
                <img
                  src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80"
                  alt="User avatar"
                  className="w-8 h-8 rounded-full ring-2 ring-white transition-all duration-300 group-hover:ring-4 group-hover:ring-blue-50"
                />
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;