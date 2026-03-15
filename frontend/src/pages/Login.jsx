import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { login } from '../api/client';

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]       = useState('');
  const [loading, setLoading]   = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await login(email, password);
      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('seller_email', email);
      navigate('/', { replace: true });
    } catch (err) {
      setError(err?.response?.data?.detail || 'Login failed. Check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-box">
        <h1>Welcome back 👋</h1>
        <p className="auth-sub">Sign in to your intelligence dashboard</p>

        {error && <div className="auth-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              placeholder="you@brand.com"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
          </div>
          <button
            className="btn btn-primary"
            style={{ width: '100%', justifyContent: 'center', marginTop: 4 }}
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign in →'}
          </button>
        </form>

        <div className="auth-link">
          New seller? <Link to="/register">Create account</Link>
        </div>
      </div>
    </div>
  );
}
