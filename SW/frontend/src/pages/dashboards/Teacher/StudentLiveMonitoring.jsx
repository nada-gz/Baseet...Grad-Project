import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import '../../../styles/index.css';

// Custom SVG Semicircle Gauge
const Gauge = ({ value, min, max, unit, color }) => {
    const radius = 80;
    const stroke = 15;
    const normalizedValue = Math.min(Math.max(value, min), max);
    const percentage = (normalizedValue - min) / (max - min);
    const circumference = radius * Math.PI;
    const strokeDashoffset = circumference - (percentage * circumference);

    return (
        <div className="gauge-chart-container">
            <svg width="200" height="120" viewBox="0 0 200 120" className="overflow-visible">
                {/* Background Arc */}
                <path
                    d="M 20 100 A 80 80 0 0 1 180 100"
                    fill="none"
                    stroke="#e2e8f0"
                    strokeWidth={stroke}
                    strokeLinecap="round"
                />
                {/* Value Arc */}
                <path
                    d="M 20 100 A 80 80 0 0 1 180 100"
                    fill="none"
                    stroke={color}
                    strokeWidth={stroke}
                    strokeDasharray={circumference}
                    strokeDashoffset={strokeDashoffset}
                    strokeLinecap="round"
                    className="transition-all duration-1000 ease-out"
                />
                {/* Min/Max Labels */}
                <text x="20" y="125" textAnchor="middle" className="text-gray-400 text-xs font-bold">{min}</text>
                <text x="180" y="125" textAnchor="middle" className="text-gray-400 text-xs font-bold">{max}</text>
            </svg>
            {/* Centered Value */}
            <div className="absolute top-16 text-center">
                <span className="text-4xl font-bold text-gray-700 block">{value}</span>
            </div>
        </div>
    );
};

export default function StudentLiveMonitoring() {
    const { studentId } = useParams();
    const navigate = useNavigate();

    const [data, setData] = useState({
        temp: 0,
        hr: 0,
        gsr: 0,
        status: "Offline"
    });

    const [controls, setControls] = useState({
        led: false,
        music: true
    });

    const [connected, setConnected] = useState(false);

    // Simulation
    useEffect(() => {
        const fetchData = async () => {
            setConnected(true);
            setData(prev => ({
                temp: parseFloat((35 + Math.random() * 2).toFixed(1)), // 35-37
                hr: Math.floor(60 + Math.random() * 30), // 60-90
                gsr: parseFloat((0 + Math.random() * 2).toFixed(1)),
                status: Math.random() > 0.8 ? "Stressed" : "Relaxed"
            }));
        };

        const interval = setInterval(fetchData, 2000);
        return () => clearInterval(interval);
    }, []);

    const getStatusColor = () => {
        if (data.status === 'Stressed') return '#d9534f'; // Red
        if (data.status === 'Relaxed') return '#5bc0de'; // Blue/Greenish
        return '#94a3b8';
    };

    const getStatusBg = () => {
        // Matching the reference image style (solid block)
        if (data.status === 'Stressed') return '#ef4444';
        if (data.status === 'Relaxed') return '#4f46e5'; // Indigo/Blue from reference
        return '#64748b';
    };

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            {/* Header / Nav */}
            <div className="max-w-6xl mx-auto mb-6 flex items-center gap-4">
                <button
                    onClick={() => navigate(-1)}
                    className="p-2 hover:bg-gray-200 rounded-full transition-colors"
                >
                    <ArrowLeft size={24} className="text-gray-600" />
                </button>
                <h1 className="text-xl font-bold text-gray-700">Child Monitor <span className="text-sm font-normal text-gray-400">• Student #{studentId}</span></h1>
            </div>

            <div className="live-dashboard">

                {/* 1. Status Banner */}
                <div className="status-banner" style={{ backgroundColor: getStatusBg() }}>
                    <div className="status-label">Stress Status</div>
                    <div className="status-value">{data.status}</div>
                </div>

                {/* 2. Controls Row */}
                <div className="controls-row">
                    {/* LED Control */}
                    <div className="control-card">
                        <div className="control-header">LED</div>
                        <div className="toggle-switch-container">
                            <div
                                className={`toggle-switch ${controls.led ? 'active' : ''}`}
                                onClick={() => setControls(prev => ({ ...prev, led: !prev.led }))}
                            >
                                <div className="toggle-slider"></div>
                            </div>
                            <div className="toggle-label">{controls.led ? 'On' : 'Off'}</div>
                        </div>
                    </div>

                    {/* Music Control */}
                    <div className="control-card">
                        <div className="control-header">Music</div>
                        <div className="toggle-switch-container">
                            <div
                                className={`toggle-switch ${controls.music ? 'active' : ''}`}
                                onClick={() => setControls(prev => ({ ...prev, music: !prev.music }))}
                            >
                                <div className="toggle-slider"></div>
                            </div>
                            <div className="toggle-label">{controls.music ? 'Play' : 'Pause'}</div>
                        </div>
                    </div>
                </div>

                {/* 3. Gauges Row */}
                <div className="gauge-grid">
                    <div className="metric-card">
                        <div className="metric-title">Heart Rate - bpm</div>
                        <Gauge value={data.hr} min={40} max={180} unit="BPM" color="#94a3b8" />
                    </div>

                    <div className="metric-card">
                        <div className="metric-title">GSR</div>
                        <Gauge value={data.gsr} min={0} max={10} unit="µS" color="#94a3b8" />
                    </div>

                    <div className="metric-card">
                        <div className="metric-title">Temperature</div>
                        <Gauge value={data.temp} min={20} max={42} unit="°C" color="#d4a373" />
                    </div>
                </div>

            </div>
        </div>
    );
}
