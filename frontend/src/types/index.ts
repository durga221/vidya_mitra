export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
}

export interface Feature {
  id: string;
  title: string;
  description: string;
  icon: string;
  path: string;
}

export interface NavigationItem {
  name: string;
  path: string;
  icon: string;
}