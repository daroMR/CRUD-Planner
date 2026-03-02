import React, { useState } from 'react';
import { LayoutGrid, RefreshCw, Save, Database, ShieldCheck, Activity, Cpu } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const App = () => {
  const [tasks, setTasks] = useState([
    { id: '1', title: 'Unit_Alpha_Sync', status: 'Active', customFields: { Cost: '520.45', Latency: '12ms', Priority: 'Critical' } },
    { id: '2', title: 'BETA_Protocol_Init', status: 'Stable', customFields: { Cost: '102.00', Latency: '45ms', Priority: 'Standard' } },
    { id: '3', title: 'Gamma_Data_Stitch', status: 'Syncing', customFields: { Cost: '340.10', Latency: '28ms', Priority: 'High' } }
  ]);
  const [syncing, setSyncing] = useState(false);

  const handleSync = () => {
    setSyncing(true);
    setTimeout(() => setSyncing(false), 1500);
  };

  return (
    <div className="min-h-screen bg-[#F0F2F5] text-[#1A1C1E] font-sans antialiased text-[13px] leading-tight">
      {/* Top Navigation Bar - Scientific Thin */}
      <nav className="h-12 bg-white border-b border-gray-200 flex items-center justify-between px-4 sticky top-0 z-50 shadow-sm">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-[#0B57D0] rounded flex items-center justify-center">
            <Cpu className="text-white w-5 h-5" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold tracking-tight text-[#0B57D0]">STITCH_LAB</span>
            <span className="text-[10px] text-gray-400 font-mono -mt-1">v2.1.0_STABLE</span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1 bg-green-50 rounded-full border border-green-100">
            <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
            <span className="text-[11px] font-medium text-green-700 uppercase tracking-widest">System_Online</span>
          </div>
          <button
            onClick={handleSync}
            disabled={syncing}
            className={`flex items-center gap-2 px-4 py-1.5 rounded text-[12px] font-semibold transition-all
              ${syncing ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-[#0B57D0] text-white hover:bg-[#0842a0] active:scale-95 shadow-sm'}`}
          >
            <RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'PROCESSING...' : 'RUN_SYNC'}
          </button>
        </div>
      </nav>

      <div className="max-w-[1400px] mx-auto p-4 space-y-4">
        {/* Bento Metrics - High Density */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <MetricBox icon={<Activity size={16} />} label="THROUGHPUT" value="4.2 GB/s" trend="+0.4%" />
          <MetricBox icon={<Database size={16} />} label="SYNC_OBJECTS" value="1,024" trend="Stable" />
          <MetricBox icon={<ShieldCheck size={16} />} label="SECURITY_LAYER" value="AES-256" trend="Active" />
          <MetricBox icon={<LayoutGrid size={16} />} label="GRID_NODES" value="168" trend="+12" />
        </div>

        {/* Scientific Data Grid */}
        <div className="bg-white rounded border border-gray-200 shadow-sm overflow-hidden">
          <div className="px-4 py-2.5 bg-gray-50 border-b border-gray-200 flex justify-between items-center text-[11px] font-bold text-gray-500 uppercase tracking-widest">
            <span>Core_Registry // Data_Stitching_Engine</span>
            <span className="text-[#0B57D0]">Filter: All_Active</span>
          </div>
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-white border-b border-gray-100 text-gray-400 text-[11px] font-bold uppercase tracking-wider">
                <th className="px-4 py-3 border-r border-gray-50">NODE_IDENTIFIER</th>
                <th className="px-4 py-3 border-r border-gray-50">STATUS</th>
                <th className="px-4 py-3 border-r border-gray-50 text-right">QUANTUM_COST</th>
                <th className="px-4 py-3 border-r border-gray-50">LATENCY</th>
                <th className="px-4 py-3 border-r border-gray-50">PRIORITY</th>
                <th className="px-4 py-3 text-center">CMD</th>
              </tr>
            </thead>
            <tbody className="text-gray-700 divide-y divide-gray-50 font-mono text-[12px]">
              {tasks.map((task) => (
                <tr key={task.id} className="hover:bg-blue-50/20 transition-colors group">
                  <td className="px-4 py-2 font-semibold text-[#0B57D0]">{task.title}</td>
                  <td className="px-4 py-2 text-[11px]">
                    <span className={`px-2 py-0.5 rounded-sm font-bold border ${task.status === 'Syncing' ? 'bg-blue-50 text-blue-600 border-blue-100' : 'bg-gray-50 text-gray-500 border-gray-200'}`}>
                      {task.status.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-right text-gray-900 tabular-nums">${task.customFields.Cost}</td>
                  <td className="px-4 py-2 text-gray-400">{task.customFields.Latency}</td>
                  <td className="px-4 py-2">
                    <span className={`text-[10px] font-black px-1.5 py-0.5 rounded ${task.customFields.Priority === 'Critical' ? 'bg-red-50 text-red-600' : 'bg-blue-50 text-blue-600'}`}>
                      {task.customFields.Priority.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-center">
                    <button className="p-1 text-gray-300 hover:text-[#0B57D0] hover:bg-white border border-transparent rounded transition-all">
                      <Save size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Footer Stats - Scientific Fine Print */}
        <footer className="flex justify-between items-center px-1 text-[10px] text-gray-400 font-mono uppercase tracking-widest pt-2">
          <div className="flex gap-4">
            <span>MEM: 12.4GB</span>
            <span>Uptime: 99.98%</span>
          </div>
          <div className="flex gap-4">
            <span>Auth: MS_GRAPH_v1.0</span>
            <span className="text-[#0B57D0]">Bento_Grid_Enabled</span>
          </div>
        </footer>
      </div>
    </div>
  );
};

const MetricBox = ({ icon, label, value, trend }) => (
  <div className="bg-white p-3 rounded border border-gray-200 shadow-sm flex flex-col justify-between">
    <div className="flex justify-between items-start mb-2">
      <span className="text-[10px] font-bold text-gray-400 uppercase tracking-tighter">{label}</span>
      <div className="text-gray-300">{icon}</div>
    </div>
    <div className="flex justify-between items-end">
      <span className="text-xl font-bold text-gray-900 tracking-tighter">{value}</span>
      <span className={`text-[10px] font-bold ${trend.startsWith('+') ? 'text-green-500' : 'text-blue-500'}`}>{trend}</span>
    </div>
  </div>
);

export default App;
