import { useState, useCallback } from 'react';

export function useApi(fn) {
  const [data, setData]     = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]   = useState(null);

  const run = useCallback(async (...args) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fn(...args);
      setData(res.data);
      return res.data;
    } catch (e) {
      const msg = e?.response?.data?.detail || e.message || 'An error occurred';
      setError(msg);
      return null;
    } finally {
      setLoading(false);
    }
  }, [fn]);

  return { data, loading, error, run };
}
