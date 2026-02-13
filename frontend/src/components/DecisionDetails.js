import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

function DecisionDetails() {
  const { id } = useParams();
  const [decision, setDecision] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`/api/v1/trace/${id}`).then(r => { setDecision(r.data); setLoading(false); }).catch(e => setLoading(false));
  }, [id]);

  if (loading) return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div></div>;
  if (!decision) return <div className="text-center py-12">Decision not found</div>;

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold">{decision.decision_id}</h2>
        <p className="text-gray-500">{new Date(decision.timestamp).toLocaleString()}</p>
        <div className="mt-4 grid grid-cols-2 gap-4">
          <div><h3 className="text-sm font-medium text-gray-500">Source</h3><p>{decision.source_system}</p></div>
          <div><h3 className="text-sm font-medium text-gray-500">Risk</h3><p>{decision.risk_level}</p></div>
        </div>
      </div>
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium mb-4">Input</h3>
        <pre className="bg-gray-50 p-4 rounded text-sm overflow-auto">{JSON.stringify(decision.input_payload, null, 2)}</pre>
      </div>
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium mb-4">Output</h3>
        <pre className="bg-gray-50 p-4 rounded text-sm overflow-auto">{JSON.stringify(decision.output, null, 2)}</pre>
      </div>
    </div>
  );
}
export default DecisionDetails;