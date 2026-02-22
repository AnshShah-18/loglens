'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { API_BASE } from '../../../lib/api-base';

export default function UploadPatternsPage({ params }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const sortedPatterns = data
    ? [...data.patterns].sort((a, b) => {
        if (a.is_new !== b.is_new) {
          return a.is_new ? -1 : 1;
        }
        return b.count - a.count;
      })
    : [];

  useEffect(() => {
    const fetchPatterns = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/uploads/${params.id}/patterns`, {
          cache: 'no-store',
        });

        if (!response.ok) {
          throw new Error(`Failed to load upload (${response.status})`);
        }

        const payload = await response.json();
        setData(payload);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : 'Failed to load data');
      }
    };

    fetchPatterns();
  }, [params.id]);

  return (
    <main className="mx-auto min-h-screen w-full max-w-6xl px-6 py-10">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-ink">Upload {params.id}</h1>
          {data ? (
            <p className="mt-1 text-sm text-slate-600">
              {data.filename} · {new Date(data.created_at).toLocaleString()}
            </p>
          ) : null}
        </div>
        <Link href="/" className="rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700">
          New Upload
        </Link>
      </div>

      {error ? <p className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p> : null}
      {!data && !error ? <p className="text-sm text-slate-600">Loading patterns...</p> : null}

      {data ? (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50 text-left text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Count</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Pattern</th>
                <th className="px-4 py-3 font-medium">Sample</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sortedPatterns.map((pattern) => (
                <tr key={pattern.id} className="align-top">
                  <td className="px-4 py-3 font-medium text-ink">{pattern.count}</td>
                  <td className="px-4 py-3">
                    {pattern.is_new ? (
                      <span className="rounded-full bg-emerald-100 px-2 py-1 text-xs font-semibold uppercase tracking-wide text-emerald-700">
                        NEW
                      </span>
                    ) : (
                      <span className="rounded-full bg-slate-200 px-2 py-1 text-xs font-semibold uppercase tracking-wide text-slate-600">
                        existing
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-slate-800 whitespace-pre-wrap break-words">
                    {pattern.pattern_text}
                  </td>
                  <td className="px-4 py-3 text-slate-700">{pattern.sample_line}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </main>
  );
}
