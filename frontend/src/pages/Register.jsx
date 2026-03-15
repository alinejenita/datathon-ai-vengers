import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { register } from '../api/client';

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm]       = useState({ email: '', password: '', seller_name: '' });
  const [error, setError]     = useState('');
  const [loading, setLoading] = useState(false);

  const set = (field) => (e) => setForm(f => ({ ...f, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(form.email, form.password, form.seller_name);
      navigate('/login');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-box">
        <h1>Create account ✨</h1>
        <p className="auth-sub">Start monitoring your competitive landscape</p>

        {error && <div className="auth-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Seller / Brand Name</label>
            <input
              placeholder="e.g. boAt Audio"
              value={form.seller_name}
              onChange={set('seller_name')}
              required
            />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              placeholder="you@brand.com"
              value={form.email}
              onChange={set('email')}
              required
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              placeholder="••••••••"
              value={form.password}
              onChange={set('password')}
              required
            />
          </div>
          <button
            className="btn btn-primary"
            style={{ width: '100%', justifyContent: 'center', marginTop: 4 }}
            disabled={loading}
          >
            {loading ? 'Creating account...' : 'Create account →'}
          </button>
        </form>

        <div className="auth-link">
          Already registered? <Link to="/login">Sign in</Link>
        </div>
      </div>
    </div>
  );
}
