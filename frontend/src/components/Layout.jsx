import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';

const NAV = [
  { to: '/',           icon: '⚡', label: 'Dashboard',     end: true },
  { to: '/pricing',    icon: '💰', label: 'Pricing Alerts' },
  { to: '/sentiment',  icon: '💬', label: 'Sentiment'      },
  { to: '/gaps',       icon: '🔍', label: 'Gap Analysis'   },
  { to: '/strategy',   icon: '♟️', label: 'Strategy'       },
  { to: '/listing',    icon: '✏️', label: 'Listing Rewriter'},
  { to: '/chat',       icon: '🤖', label: 'AI Chat'        },
  { to: '/competitors',icon: '🏆', label: 'Competitors'    },
];

export default function Layout() {
  const navigate = useNavigate();
  const email = localStorage.getItem('seller_email') || 'Seller';
  const name  = localStorage.getItem('seller_name')  || email;

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login', { replace: true });
  };

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <h2>🛒 Marketlens</h2>
          <p>Competitive Intelligence</p>
        </div>

        <nav className="sidebar-nav">
          {NAV.map(({ to, icon, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
            >
              <span className="nav-icon">{icon}</span>
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-user">
            <strong>{name}</strong>
            {email}
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            Sign out
          </button>
        </div>
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
