import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function IngestDecision() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    source_system: '',
    input_payload: '{}',
    output: '{}',
    risk_level: 'medium',
    confidence: '0.95'
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        source_system: formData.source_system,
        input_payload: JSON.parse(formData.input_payload),
        rules_triggered: [],
        output: JSON.parse(formData.output),
        confidence: parseFloat(formData.confidence),
        risk_level: formData.risk_level
      };
      const response = await axios.post('/api/v1/ingest', payload);
      navigate(`/decision/${response.data.decision_id}`);
    } catch (err) {
      alert('Error: ' + (err.response?.data?.detail || 'Failed'));
    }
  };

  return (
    <div className="max-w-3xl mx-auto bg-white shadow rounded-lg p-6">
      <h2 className="text-2xl font-bold mb-6">Ingest New Decision</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div><label className="block text-sm font-medium">Source System</label><input type="text" required value={formData.source_system} onChange={(e) => setFormData({...formData, source_system: e.target.value})} className="mt-1 block w-full border rounded-md py-2 px-3" /></div>
        <div><label className="block text-sm font-medium">Risk Level</label><select value={formData.risk_level} onChange={(e) => setFormData({...formData, risk_level: e.target.value})} className="mt-1 block w-full border rounded-md py-2 px-3"><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="critical">Critical</option></select></div>
        <div><label className="block text-sm font-medium">Confidence</label><input type="number" step="0.01" min="0" max="1" required value={formData.confidence} onChange={(e) => setFormData({...formData, confidence: e.target.value})} className="mt-1 block w-full border rounded-md py-2 px-3" /></div>
        <div><label className="block text-sm font-medium">Input (JSON)</label><textarea required value={formData.input_payload} onChange={(e) => setFormData({...formData, input_payload: e.target.value})} rows={4} className="mt-1 block w-full border rounded-md py-2 px-3 font-mono text-sm" /></div>
        <div><label className="block text-sm font-medium">Output (JSON)</label><textarea required value={formData.output} onChange={(e) => setFormData({...formData, output: e.target.value})} rows={4} className="mt-1 block w-full border rounded-md py-2 px-3 font-mono text-sm" /></div>
        <button type="submit" className="w-full py-2 px-4 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">Ingest Decision</button>
      </form>
    </div>
  );
}
export default IngestDecision;