import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './index.css';

import Login from './pages/Login';
import Register from './pages/Register';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Pricing from './pages/Pricing';
import Sentiment from './pages/Sentiment';
import Gaps from './pages/Gaps';
import Strategy from './pages/Strategy';
import Listing from './pages/Listing';
import Chat from './pages/Chat';
import Competitors from './pages/Competitors';

function PrivateRoute({ children }) {
  const token = localStorage.getItem('token');
  return token ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="pricing" element={<Pricing />} />
          <Route path="sentiment" element={<Sentiment />} />
          <Route path="gaps" element={<Gaps />} />
          <Route path="strategy" element={<Strategy />} />
          <Route path="listing" element={<Listing />} />
          <Route path="chat" element={<Chat />} />
          <Route path="competitors" element={<Competitors />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
