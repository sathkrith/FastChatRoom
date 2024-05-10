import React from 'react';
import {
  BrowserRouter as Router,
  Route,
  Routes 
} from 'react-router-dom';
import Login from './pages/Login';  
import Dashboard from './pages/Dashboard';  
import { AuthProvider } from './contexts/AuthContext';
import RequireAuth from './components/RequireAuth';
const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={
            <RequireAuth>
              <Dashboard />
            </RequireAuth>
          } />
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
