import React from 'react';
import { Feature } from '../../types';
import * as Icons from 'lucide-react';

interface FeatureCardProps {
  feature: Feature;
}

const FeatureCard = ({ feature }: FeatureCardProps) => {
  const IconComponent = (Icons as any)[feature.icon];

  return (
    <a
      href={feature.path}
      className="group relative block overflow-hidden rounded-xl bg-gradient-to-b from-white to-gray-50 p-6 shadow-lg transition-all duration-300 hover:-translate-y-1 hover:shadow-xl"
    >
      <div className="relative z-10">
        <div className="mb-4 inline-flex rounded-lg bg-blue-50 p-3 text-blue-600 ring-4 ring-blue-50 transition-all duration-300 group-hover:bg-blue-600 group-hover:text-white group-hover:ring-blue-100">
          {IconComponent && <IconComponent className="h-6 w-6" />}
        </div>
        <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors duration-300">
          {feature.title}
        </h3>
        <p className="mt-2 text-sm text-gray-600">
          {feature.description}
        </p>
      </div>
      <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-blue-600 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
    </a>
  );
};

export default FeatureCard;