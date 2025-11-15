import { useState, useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';

interface ModulePage {
  id: string;
  module_id: string;
  module_name: string;
  title: string;
  icon: string | null;
  path: string;
  component_url: string | null;
  order: number;
  enabled: boolean;
}

export function useModulePages() {
  const [pages, setPages] = useState<ModulePage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuthStore();

  useEffect(() => {
    const fetchPages = async () => {
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        // Добавляем timestamp чтобы избежать кэширования
        const response = await fetch(`http://localhost:8001/api/v1/module-pages?t=${Date.now()}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          cache: 'no-store'
        });

        if (!response.ok) {
          throw new Error('Failed to fetch module pages');
        }

        const data = await response.json();
        console.log('[useModulePages] Loaded pages:', data); // Debug
        
        // Фильтруем отключенные встроенные модули
        const disabledModules = JSON.parse(localStorage.getItem('disabledBuiltinModules') || '[]');
        const filteredPages = data.filter((page: ModulePage) => {
          if (page.id.startsWith('builtin-')) {
            return !disabledModules.includes(page.id);
          }
          return true;
        });
        
        setPages(filteredPages);
      } catch (err) {
        console.error('[useModulePages] Error:', err); // Debug
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchPages();
  }, [token]);

  return { pages, loading, error };
}
