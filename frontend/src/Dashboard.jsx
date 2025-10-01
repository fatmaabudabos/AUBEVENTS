import { useState, useEffect } from 'react';
import { api } from './api';

function Dashboard() {
  const [user, setUser] = useState({ name: 'User' });

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const data = await api('/auth/me/', { auth: true });
        setUser({ name: data.email.split('@')[0] });
      } catch (err) {
        // Fallback to localStorage if API fails
        const userData = localStorage.getItem('user');
        if (userData) {
          setUser(JSON.parse(userData));
        }
      }
    };
    fetchUser();
  }, []);

  return (
    <div style={{
      backgroundColor: '#F5F5DC',
      minHeight: '100vh',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1 style={{
        fontSize: '3rem',
        color: '#333',
        textAlign: 'center'
      }}>
        Welcome, {user.name}!
      </h1>
    </div>
  );
}

export default Dashboard;