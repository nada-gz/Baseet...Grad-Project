import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Activity, Zap, Music, Thermometer, Droplets, User, Heart } from 'lucide-react';
import '../../../styles/index.css';

// Custom SVG Semicircle Gauge
// Advanced Gauge with Ticks & Gradient
const Gauge = ({ value, min, max, unit, color }) => {
    const radius = 80;
    const stroke = 10;
    const normalizedValue = Math.min(Math.max(value, min), max);
    const percentage = (normalizedValue - min) / (max - min);
    const circumference = radius * Math.PI;
    const strokeDashoffset = circumference - (percentage * circumference);

    // Generate ticks
    const ticks = [];
    const totalTicks = 30; // Number of ticks
    for (let i = 0; i <= totalTicks; i++) {
        const angle = Math.PI - (i / totalTicks) * Math.PI; // Semicircle from PI to 0
        // Calculate raw position relative to center (0,0) then shift to (100,100)
        // Note: Math.cos(angle) maps to x, Math.sin(angle) maps to -y (SVG y is down)

        // Wait, standard parametric circle: x = r*cos(t), y = r*sin(t)
        // We want arc from 180 deg (PI) to 0 deg (0).
        // x = 100 + r * cos(angle)
        // y = 100 - r * sin(angle) (since we want "up" to be negative Y relative to center)

        const tickInner = 65;
        const tickOuter = 75;

        const x1 = 100 + tickInner * Math.cos(angle);
        const y1 = 100 - tickInner * Math.sin(angle);
        const x2 = 100 + tickOuter * Math.cos(angle);
        const y2 = 100 - tickOuter * Math.sin(angle);

        ticks.push(
            <line
                key={i}
                x1={x1} y1={y1}
                x2={x2} y2={y2}
                stroke="#e2e8f0"
                strokeWidth={i % 5 === 0 ? 2 : 1} // Thicker major ticks
            />
        );
    }

    return (
        <div className="gauge-wrapper">
            <svg width="240" height="150" viewBox="0 0 200 140" className="gauge-svg">
                <defs>
                    <linearGradient id={`grad-${unit}`} x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor={color} stopOpacity="1" />
                        <stop offset="100%" stopColor={color} stopOpacity="0.6" />
                    </linearGradient>
                    <filter id={`glow-${unit}`} x="-50%" y="-50%" width="200%" height="200%">
                        <feGaussianBlur stdDeviation="3" result="coloredBlur" />
                        <feMerge>
                            <feMergeNode in="coloredBlur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                </defs>

                {/* Tick Marks Ring */}
                <g className="gauge-ticks">
                    {ticks}
                </g>

                {/* Background Track Arc */}
                <path
                    d="M 15 100 A 85 85 0 0 1 185 100"
                    fill="none"
                    stroke="#f1f5f9"
                    strokeWidth={stroke}
                    strokeLinecap="round"
                />

                {/* Value Progress Arc */}
                <path
                    d="M 15 100 A 85 85 0 0 1 185 100"
                    fill="none"
                    stroke={`url(#grad-${unit})`}
                    strokeWidth={stroke}
                    strokeDasharray={radius * Math.PI * (85 / 80)} // Approximate adjusted circumference
                    strokeDashoffset={strokeDashoffset * (85 / 80)}
                    strokeLinecap="round"
                    className="gauge-value-arc transition-all duration-1000 ease-out"
                    style={{ filter: `drop-shadow(0 0 4px ${color})` }}
                />

                {/* Min/Max Labels */}
                <text x="15" y="125" textAnchor="middle" className="gauge-label font-bold">{min}</text>
                <text x="185" y="125" textAnchor="middle" className="gauge-label font-bold">{max}</text>
            </svg>

            {/* Centered Value */}
            <div className="gauge-value-container">
                <span className="gauge-value-text" style={{
                    color: color,
                    textShadow: `0 2px 10px ${color}33` // Subtle text glow 
                }}>
                    {value}
                </span>
                <div className="gauge-unit-pill" style={{ borderColor: color, color: '#64748b' }}>
                    {unit}
                </div>
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

    // Simulation
    useEffect(() => {
        const fetchData = async () => {
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

    // Helper for status class
    const getStatusClass = () => {
        if (data.status === 'Stressed') return 'status-stressed';
        if (data.status === 'Relaxed') return 'status-relaxed';
        return 'status-offline';
    };

    return (
        <div className="monitoring-page">
            {/* Header / Nav - Updated Layout */}
            <div className="monitoring-header-row">
                <div className="header-left">
                    <button
                        onClick={() => navigate(-1)}
                        className="monitoring-back-icon-btn"
                    >
                        <ArrowLeft size={24} />
                    </button>
                    <div className="header-info">
                        <span className="sub-label-header">Live Session</span>
                        <h1 className="header-title">Monitoring <span className="highlight-name">Nada</span></h1>
                    </div>
                </div>

                <div className="header-right">
                    <div className="live-indicator">
                        <span className="dot"></span> System Active
                    </div>
                </div>
            </div>

            <div className="live-dashboard-container">

                {/* 1. Full Width Status Row */}
                <div className={`status-section ${getStatusClass()}`}>
                    <div className="status-content-row">
                        <div className="status-text-group">
                            <span className="status-label-lg">CURRENT PSYCHOLOGICAL STATE</span>
                            <h2 className="status-value-lg">{data.status}</h2>
                        </div>
                        <div className="status-visual">
                            <Activity size={60} className="status-pulse-icon" />
                        </div>
                    </div>
                    {/* Background decoration */}
                    <div className="status-bg-deco"></div>
                </div>

                {/* 2. Metrics Row (3 Columns) */}
                <div className="metrics-section">
                    <div className="metric-card glass-panel">
                        <div className="metric-header">
                            <Heart className="metric-icon heart" size={24} />
                            <span>Heart Rate</span>
                        </div>
                        <Gauge value={data.hr} min={40} max={180} unit="BPM" color="#f43f5e" />
                    </div>

                    <div className="metric-card glass-panel">
                        <div className="metric-header">
                            <Droplets className="metric-icon droplet" size={24} />
                            <span>GSR</span>
                        </div>
                        <Gauge value={data.gsr} min={0} max={10} unit="µS" color="#0ea5e9" />
                    </div>

                    <div className="metric-card glass-panel">
                        <div className="metric-header">
                            <Thermometer className="metric-icon temp" size={24} />
                            <span>Temperature</span>
                        </div>
                        <Gauge value={data.temp} min={20} max={42} unit="°C" color="#f97316" />
                    </div>
                </div>

                {/* 3. Controls Row */}
                <div className="controls-section">
                    {/* LED Control */}
                    <div className="control-card glass-panel">
                        <div className="control-info">
                            <div className={`control-icon-box ${controls.led ? 'active' : ''}`}>
                                <Zap size={24} />
                            </div>
                            <div className="control-text">
                                <h3>LED Light</h3>
                                <span>Visual Stimulus</span>
                            </div>
                        </div>

                        <div className="toggle-wrapper">
                            <div
                                className={`custom-toggle ${controls.led ? 'checked' : ''}`}
                                onClick={() => setControls(prev => ({ ...prev, led: !prev.led }))}
                            >
                                <div className="toggle-circle"></div>
                            </div>
                        </div>
                    </div>

                    {/* Music Control */}
                    <div className="control-card glass-panel">
                        <div className="control-info">
                            <div className={`control-icon-box ${controls.music ? 'active' : ''}`}>
                                <Music size={24} />
                            </div>
                            <div className="control-text">
                                <h3>Calming Music</h3>
                                <span>Audio Stimulus</span>
                            </div>
                        </div>

                        <div className="toggle-wrapper">
                            <div
                                className={`custom-toggle ${controls.music ? 'checked' : ''}`}
                                onClick={() => setControls(prev => ({ ...prev, music: !prev.music }))}
                            >
                                <div className="toggle-circle"></div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
}
