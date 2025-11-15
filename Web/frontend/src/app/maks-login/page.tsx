'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function MAKSLoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    console.log('Попытка входа...', { username, password: '***' });

    try {
      console.log('Отправка запроса на:', 'http://localhost:8001/api/v1/maks-auth/login');
      
      // Добавляем таймаут
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 секунд
      
      const response = await fetch('http://localhost:8001/api/v1/maks-auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      console.log('Ответ получен:', response.status, response.statusText);

      if (!response.ok) {
        const data = await response.json();
        console.error('Ошибка входа:', data);
        throw new Error(data.detail || 'Ошибка входа');
      }

      const data = await response.json();
      console.log('Успешный вход:', data);
      
      // Сохранить токен
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      
      console.log('Перенаправление на /dashboard');
      // Перенаправить на дашборд
      router.push('/dashboard');
      
    } catch (err: any) {
      console.error('Ошибка при входе:', err);
      if (err.name === 'AbortError') {
        setError('Превышено время ожидания. Проверьте что backend запущен на http://localhost:8001');
      } else if (err.message.includes('Failed to fetch')) {
        setError('Не удалось подключиться к серверу. Убедитесь что backend запущен.');
      } else {
        setError(err.message || 'Ошибка при входе');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Вход через MAKS
          </h1>
          <p className="text-gray-600">
            Используйте логин и пароль из бота
          </p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Логин
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="eidos_abc123"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Пароль
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Введите пароль"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              required
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Вход...' : 'Войти'}
          </button>
        </form>

        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-800 font-medium mb-2">
            📱 Как получить учетные данные?
          </p>
          <ol className="text-sm text-blue-700 space-y-1 list-decimal list-inside">
            <li>Откройте мессенджер MAKS</li>
            <li>Найдите бота @t33_hakaton_bot</li>
            <li>Отправьте команду /start</li>
            <li>Бот выдаст логин и пароль</li>
          </ol>
        </div>

        <div className="mt-4 text-center">
          <a
            href="/login"
            className="text-sm text-indigo-600 hover:text-indigo-700"
          >
            Войти через email
          </a>
        </div>
      </div>
    </div>
  );
}
