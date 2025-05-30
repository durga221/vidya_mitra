import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './components/dashboard/Dashboard';
import BOSGenerator from './components/features/bos/BOSGenerator';
import CodeGenerator from './components/features/code_generator/CodeGenerator';
import ResourceGenerator from './components/features/resource_generator/ResourceGenerator';
import SOSExamRescueKit from './components/features/sos_exam_prep_kit/SOS_ExamResourceGenerator';
import Canvas from './components/features/canvas/Canvas';
import MultilingualChatbot from './components/features/chatbot/chatbot';
function AppContent() {
  const location = useLocation();

  return (
    <Layout>
      <Routes location={location}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/bos" element={<BOSGenerator />} />
        <Route path="/code_generator" element={<CodeGenerator />} />
        
        <Route path="/resource_generator" element={<ResourceGenerator />} />
        <Route path="/sos_exam_prep_kit" element={<SOSExamRescueKit />} />
        <Route path="/canvas" element={<Canvas />} />
        <Route path="/chatbot" element={<MultilingualChatbot/>} />
      </Routes>
    </Layout>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;

