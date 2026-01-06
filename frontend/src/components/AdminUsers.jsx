import React, { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

const AdminUsers = () => {
  const [users, setUsers] = useState([]);

  const fetchUsers = useCallback(async () => {
    try {
      const response = await api.get('/users/');
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  }, []);

  const promoteUser = useCallback(async (userId) => {
    try {
      await api.post(`/users/${userId}/promote/`);
      fetchUsers(); // Refresh the user list
    } catch (error) {
      console.error('Error promoting user:', error);
    }
  }, [fetchUsers]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  return (
    <div className="admin-users">
      <h3>User Management</h3>
      <div className="card">
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid var(--border)', textAlign: 'left' }}>
              <th style={{ padding: '10px' }}>Email</th>
              <th style={{ padding: '10px' }}>Role</th>
              <th style={{ padding: '10px' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} style={{ borderBottom: '1px solid var(--border)' }}>
                <td style={{ padding: '10px' }}>{user.email}</td>
                <td style={{ padding: '10px' }}>
                  <span
                    style={{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      backgroundColor: user.role === 'admin' ? '#E0E7FF' : '#F3F4F6',
                      color: user.role === 'admin' ? '#4338CA' : '#374151',
                      fontSize: '0.875rem',
                      fontWeight: '500'
                    }}
                  >
                    {user.role}
                  </span>
                </td>
                <td style={{ padding: '10px' }}>
                  {user.role !== 'admin' && (
                    <button
                      onClick={() => promoteUser(user.id)}
                      className="secondary"
                      style={{ fontSize: '0.875rem', padding: '4px 8px' }}
                    >
                      Promote to Admin
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AdminUsers;
