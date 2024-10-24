// src/components/SetupUsername.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const SetupUsername = () => {
  const [username, setUsername] = useState('');
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const response = await fetch('/api/users/username', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to set username');
      }

      // Success! Redirect to lobby
      navigate('/');
    } catch (err) {
      setError(err.message || 'An error occurred');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Client-side validation to match server rules
  const validateUsername = (value) => {
    if (value.length < 3 || value.length > 20) {
      return 'Username must be between 3 and 20 characters';
    }
    if (!value.replace('_', '').match(/^[a-zA-Z0-9]+$/)) {
      return 'Username can only contain letters, numbers, and underscores';
    }
    return null;
  };

  const handleChange = (e) => {
    const value = e.target.value;
    setUsername(value);
    setError(validateUsername(value));
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Choose your username
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            This will be your display name in games
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="username" className="sr-only">
              Username
            </label>
            <input
              id="username"
              name="username"
              type="text"
              required
              value={username}
              onChange={handleChange}
              className={`appearance-none rounded-md relative block w-full px-3 py-2 border 
                ${error ? 'border-red-300' : 'border-gray-300'}
                placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 
                focus:border-indigo-500 focus:z-10 sm:text-sm`}
              placeholder="Choose a username"
            />
            {error && (
              <p className="mt-2 text-sm text-red-600">
                {error}
              </p>
            )}
          </div>

          <div>
            <button
              type="submit"
              disabled={!!error || isSubmitting || !username}
              className={`group relative w-full flex justify-center py-2 px-4 border border-transparent 
                text-sm font-medium rounded-md text-white 
                ${!error && username && !isSubmitting
                  ? 'bg-indigo-600 hover:bg-indigo-700'
                  : 'bg-gray-400 cursor-not-allowed'}
                focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500`}
            >
              {isSubmitting ? 'Setting username...' : 'Continue'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SetupUsername;