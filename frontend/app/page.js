'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { API_BASE } from '../lib/api-base';

export default function HomePage() {
  const router = useRouter();
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const onSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      setError('Choose a log file first.');
      return;
    }

    setError('');
    setLoading(true);

    try {
      const data = new FormData();
      data.append('file', file);

      const response = await fetch(`${API_BASE}/api/upload`, {
        method: 'POST',
        body: data,
      });

      if (!response.ok) {
        throw new Error(`Upload failed (${response.status})`);
      }

      const payload = await response.json();
      router.push(`/uploads/${payload.id}`);
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl items-center px-6 py-12">
      <section className="w-full rounded-2xl border border-slate-200 bg-white/85 p-8 shadow-sm backdrop-blur">
        <h1 className="text-3xl font-semibold tracking-tight text-ink">LogLens</h1>
        <p className="mt-2 text-sm text-slate-600">Upload a production log file and inspect grouped patterns.</p>

        <form onSubmit={onSubmit} className="mt-8 space-y-4">
          <input
            type="file"
            accept=".log,.txt,text/plain"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            className="block w-full cursor-pointer rounded-lg border border-slate-300 bg-surface px-3 py-2 text-sm text-slate-700 file:mr-3 file:rounded-md file:border-0 file:bg-accent file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-white hover:file:bg-teal-700"
          />
          <button
            type="submit"
            disabled={loading}
            className="rounded-lg bg-ink px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? 'Uploading...' : 'Upload log'}
          </button>
        </form>

        {error ? <p className="mt-4 text-sm text-red-600">{error}</p> : null}
      </section>
    </main>
  );
}
