import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Plane, 
  Users, 
  FileText, 
  BarChart3, 
  LogOut,
  Settings,
  Menu
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Sidebar = () => {
  const { user, logout } = useAuth();

  const navItems = [
    {
      group: 'Main',
      items: [
        { path: '/', icon: LayoutDashboard, label: 'Dashboard' }
      ]
    },
    {
      group: 'Travel Management',
      items: [
        { path: '/travel-dashboard', icon: BarChart3, label: 'Travel Dashboard' },
        { path: '/users', icon: Users, label: 'Users Sync' },
        { path: '/bookings', icon: Plane, label: 'Bookings' },
        { path: '/import-logs', icon: FileText, label: 'Import Logs' }
      ]
    }
  ];

  return (
    <div className="w-64 bg-gray-900 text-white flex flex-col h-screen">
      {/* Logo */}
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center space-x-3">
          <div className="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <Menu className="h-5 w-5" />
          </div>
          <span className="text-lg font-bold">DataHub</span>
        </div>
      </div>

      {/* User Info */}
      {user && (
        <div className="p-4 border-b border-gray-800">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 bg-blue-500 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium">
                {user.first_name?.charAt(0) || user.username?.charAt(0) || 'U'}
              </span>
            </div>
            <div>
              <p className="text-sm font-medium">{user.first_name || user.username}</p>
              <p className="text-xs text-gray-400">{user.email || user.username}</p>
            </div>
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4">
        {navItems.map((group, groupIndex) => (
          <div key={groupIndex} className="mb-6">
            <p className="px-6 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
              {group.group}
            </p>
            <ul className="space-y-1">
              {group.items.map((item) => (
                <li key={item.path}>
                  <NavLink
                    to={item.path}
                    className={({ isActive }) =>
                      `flex items-center px-6 py-3 text-sm transition-colors ${
                        isActive
                          ? 'bg-blue-600 text-white border-r-4 border-white'
                          : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                      }`
                    }
                  >
                    <item.icon className="h-5 w-5 mr-3" />
                    {item.label}
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-gray-800 p-4">
        <button
          onClick={logout}
          className="flex items-center w-full px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 hover:text-white rounded-lg transition-colors"
        >
          <LogOut className="h-5 w-5 mr-3" />
          Logout
        </button>
      </div>
    </div>
  );
};

export default Sidebar;