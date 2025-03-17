// src/public/App.tsx
import React, { useState } from 'react';

const App: React.FC = () => {
    const [query, setQuery] = useState('');
    const [response, setResponse] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            const res = await fetch(`/api/query?q=${encodeURIComponent(query)}`);
            const data = await res.json();
            setResponse(data.response);
        } catch (error) {
            setResponse('Error: Failed to fetch response');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-800 via-gray-900 to-black">
            <div className="w-full max-w-2xl p-8 bg-gray-800 rounded-xl shadow-2xl border border-gray-700 transform transition-all hover:scale-105">
                <h1 className="text-4xl font-bold text-center text-teal-400 mb-6 animate-pulse">RAG Agent</h1>
                <form onSubmit={handleSubmit} className="space-y-6">
                    <textarea
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Ask me anything..."
                        className="w-full h-32 p-4 bg-gray-700 rounded-lg border border-gray-600 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-teal-500 transition duration-300"
                    />
                    <button
                        type="submit"
                        disabled={loading}
                        className={`w-full py-3 px-6 rounded-lg font-semibold text-lg transition duration-300 ${
                            loading ? 'bg-gray-600 cursor-not-allowed' : 'bg-teal-500 hover:bg-teal-600'
                        }`}
                    >
                        {loading ? 'Processing...' : 'Submit'}
                    </button>
                </form>
                {response && (
                    <div className="mt-6 p-4 bg-gray-700 rounded-lg animate-fade-in">
                        <p className="text-gray-200 whitespace-pre-wrap">{response}</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default App;