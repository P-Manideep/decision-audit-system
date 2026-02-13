import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

function DecisionSearch() {
  const [searchParams, setSearchParams] = useState({
    source_system: '',
    risk_level: '',
    search_text: ''
  });
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const params = {};
      if (searchParams.source_system) params.source_system = searchParams.source_system;
      if (searchParams.risk_level) params.risk_level = searchParams.risk_level;
      if (searchParams.search_text) params.search_text = searchParams.search_text;
      const response = await axios.get('/api/v1/search', { params });
      setResults(response.data.results);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Search Decision Traces</h2>
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <input type="text" value={searchParams.source_system} onChange={(e) => setSearchParams({ ...searchParams, source_system: e.target.value })} placeholder="Source System" className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3" />
            <select value={searchParams.risk_level} onChange={(e) => setSearchParams({ ...searchParams, risk_level: e.target.value })} className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3">
              <option value="">All Risk Levels</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
            <input type="text" value={searchParams.search_text} onChange={(e) => setSearchParams({ ...searchParams, search_text: e.target.value })} placeholder="Search..." className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3" />
          </div>
          <button type="submit" disabled={loading} className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>
      </div>
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b"><h3 className="text-lg font-medium">Results ({results.length})</h3></div>
        <ul className="divide-y">
          {results.map((d) => (
            <li key={d.decision_id} className="px-6 py-4 hover:bg-gray-50">
              <Link to={`/decision/${d.decision_id}`}>
                <p className="text-sm font-medium text-indigo-600">{d.decision_id}</p>
                <p className="text-sm text-gray-500">{d.source_system} • {new Date(d.timestamp).toLocaleString()}</p>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
export default DecisionSearch;