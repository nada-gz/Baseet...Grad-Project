import re

# 1. Update BreakPage.jsx
break_page_content = """import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import "../../../styles/index.css";
import cuteBaseet from "../../../assets/cute_baseet.png"; 

// Relaxation Messages
const relaxationMessages = [
  "Take a deep breath in... and exhale slowly.",
  "Great job studying! Now it's time to rest.",
  "Look away from the screen, maybe out a window.",
  "Stand up and do a quick stretch!",
  "Drink a glass of water to stay hydrated.",
  "Close your eyes for a moment and relax."
];

const SmallTimer = ({ timeLeft }) => {
  const mins = Math.floor(timeLeft / 60);
  const secs = timeLeft % 60;
  return (
    <div className="small-break-timer">
      <span className="timer-icon">⏳</span>
      {mins}:{secs < 10 ? '0' : ''}{secs}
    </div>
  );
};

const RelaxMode = ({ timeLeft, radius, stroke, normalizedRadius, circumference, strokeDashoffset, ringColor }) => {
  const [msgIndex, setMsgIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setMsgIndex(prev => (prev + 1) % relaxationMessages.length);
    }, 20000); // 20 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <div className="break-image-wrapper" style={{ position: 'relative' }}>
        <svg height={radius * 2} width={radius * 2} className="break-timer-ring">
          <circle stroke="#e6e6e6" fill="transparent" strokeWidth={stroke} r={normalizedRadius} cx={radius} cy={radius} />
          <circle
            stroke={ringColor} fill="transparent" strokeWidth={stroke}
            strokeDasharray={circumference + ' ' + circumference}
            style={{ strokeDashoffset, transition: "stroke-dashoffset 1s linear" }}
            className="break-timer-progress" r={normalizedRadius} cx={radius} cy={radius}
          />
        </svg>
        <img src={cuteBaseet} alt="Baseet taking a break" className="floating-baseet" />
        
        {/* Chat Bubble */}
        <div className="baseet-chat-bubble fade-in-out">
          {relaxationMessages[msgIndex]}
        </div>
      </div>
      
      <h1 className="break-title">Break Time!</h1>
      <p className="break-subtitle">
        Great job! Take {Math.ceil(timeLeft / 60)} minutes to stand up and stretch!
      </p>
    </>
  );
};

const WhiteboardMode = () => {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [color, setColor] = useState("#2196F3");
  const brushSize = 5;

  const colors = ["#2196F3", "#F44336", "#4CAF50", "#FFEB3B", "#9C27B0", "#000000"];

  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = "white";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
    }
  }, []);

  const getCoordinates = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    return {
      x: clientX - rect.left,
      y: clientY - rect.top
    };
  };

  const startDrawing = (e) => {
    e.preventDefault();
    if (!canvasRef.current) return;
    const { x, y } = getCoordinates(e);
    const ctx = canvasRef.current.getContext('2d');
    ctx.beginPath();
    ctx.moveTo(x, y);
    setIsDrawing(true);
  };

  const draw = (e) => {
    if (!isDrawing || !canvasRef.current) return;
    e.preventDefault();
    const { x, y } = getCoordinates(e);
    const ctx = canvasRef.current.getContext('2d');
    ctx.strokeStyle = color;
    ctx.lineWidth = brushSize;
    ctx.lineTo(x, y);
    ctx.stroke();
  };

  const stopDrawing = () => {
    if (!canvasRef.current) return;
    const ctx = canvasRef.current.getContext('2d');
    ctx.closePath();
    setIsDrawing(false);
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  };

  return (
    <div className="whiteboard-container">
      <div className="whiteboard-toolbar">
        <div className="color-picker">
          {colors.map(c => (
            <div 
              key={c} 
              className={`color-swatch ${c === color ? 'active' : ''}`}
              style={{ backgroundColor: c }}
              onClick={() => setColor(c)}
            />
          ))}
        </div>
        <button className="clear-btn" onClick={clearCanvas}>Clear Board</button>
      </div>
      <canvas
        ref={canvasRef}
        width={600}
        height={350}
        className="whiteboard-canvas"
        onMouseDown={startDrawing}
        onMouseMove={draw}
        onMouseUp={stopDrawing}
        onMouseLeave={stopDrawing}
        onTouchStart={startDrawing}
        onTouchMove={draw}
        onTouchEnd={stopDrawing}
      />
    </div>
  );
};

const GameMode = () => {
  const [score, setScore] = useState(0);
  const [targetPos, setTargetPos] = useState({ top: '50%', left: '50%' });
  const gameAreaRef = useRef(null);

  const moveTarget = () => {
    if (gameAreaRef.current) {
      const maxX = gameAreaRef.current.clientWidth - 80; // target size+padding
      const maxY = gameAreaRef.current.clientHeight - 80;
      
      const newX = Math.max(10, Math.random() * maxX);
      const newY = Math.max(10, Math.random() * maxY);
      
      setTargetPos({ top: `${newY}px`, left: `${newX}px` });
    }
  };

  useEffect(() => {
    moveTarget();
    const interval = setInterval(() => {
      moveTarget();
    }, 1500); // Move every 1.5s if not clicked
    return () => clearInterval(interval);
  }, []);

  const handleCatch = (e) => {
    e.stopPropagation();
    setScore(s => s + 1);
    moveTarget();
  };

  return (
    <div className="game-container">
      <div className="game-header">
        <h3>Catch Baseet!</h3>
        <p>Score: <strong>{score}</strong></p>
      </div>
      <div className="game-area" ref={gameAreaRef}>
        <img 
          src={cuteBaseet} 
          alt="target Baseet" 
          className="game-target"
          style={{ top: targetPos.top, left: targetPos.left }}
          onClick={handleCatch}
          onTouchStart={handleCatch}
          draggable={false}
        />
      </div>
    </div>
  );
};

export default function BreakPage() {
  const navigate = useNavigate();
  const totalTime = 300; 
  const [timeLeft, setTimeLeft] = useState(totalTime);
  const [mode, setMode] = useState('relax'); // relax | draw | game

  useEffect(() => {
    let interval = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const percentage = Math.max(0, Math.min(100, (timeLeft / totalTime) * 100));
  
  let ringColor = "#4caf50"; 
  if (percentage <= 20) {
    ringColor = "#f44336"; 
  } else if (percentage <= 70) {
    ringColor = "#ff9800"; 
  }

  const radius = 110;
  const stroke = 12;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="break-page-container">
      <div className="break-top-bar">
        <div className="break-mode-selector">
          <button className={`mode-btn ${mode === 'relax' ? 'active' : ''}`} onClick={() => setMode('relax')}>🌿 Relax</button>
          <button className={`mode-btn ${mode === 'draw' ? 'active' : ''}`} onClick={() => setMode('draw')}>🎨 Draw</button>
          <button className={`mode-btn ${mode === 'game' ? 'active' : ''}`} onClick={() => setMode('game')}>🎮 Play</button>
        </div>
        {mode !== 'relax' && <SmallTimer timeLeft={timeLeft} />}
      </div>

      <div className="break-content-card enhanced-card">
        {mode === 'relax' && (
          <RelaxMode 
            timeLeft={timeLeft} 
            radius={radius} stroke={stroke} normalizedRadius={normalizedRadius} 
            circumference={circumference} strokeDashoffset={strokeDashoffset} 
            ringColor={ringColor} 
          />
        )}
        {mode === 'draw' && <WhiteboardMode />}
        {mode === 'game' && <GameMode />}
        
        <div className="break-actions" style={{ marginTop: '30px' }}>
          <button 
            className="return-btn primary"
            onClick={() => navigate("/dashboard/student")}
          >
            {timeLeft === 0 ? "Return to Dashboard" : "End Break Early"}
          </button>
        </div>
      </div>
    </div>
  );
}
"""

with open("/Users/Nada/nada/GRAD/Grad-Project/SW/frontend/src/pages/dashboards/Student/BreakPage.jsx", "w") as f:
    f.write(break_page_content)

# 2. Append CSS to index.css
css_append = """

/* --- BREAK PAGE ENHANCEMENTS --- */

.break-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  max-width: 800px;
  position: absolute;
  top: 30px;
  left: 50%;
  transform: translateX(-50%);
  padding: 0 20px;
  z-index: 10;
}

@media (max-width: 600px) {
  .break-top-bar {
    flex-direction: column;
    gap: 15px;
    top: 15px;
  }
}

.break-mode-selector {
  display: flex;
  gap: 12px;
  background: rgba(255, 255, 255, 0.9);
  padding: 8px;
  border-radius: 30px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}

.mode-btn {
  padding: 10px 20px;
  border-radius: 20px;
  border: none;
  background: transparent;
  color: #555;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.mode-btn:hover {
  background: rgba(0,0,0,0.05);
}

.mode-btn.active {
  background: var(--primary-color, #4361ee);
  color: white;
  box-shadow: 0 4px 10px rgba(67, 97, 238, 0.3);
}

.small-break-timer {
  background: white;
  padding: 10px 20px;
  border-radius: 20px;
  font-weight: bold;
  color: #ff5722;
  font-size: 18px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  display: flex;
  align-items: center;
  gap: 8px;
}

.enhanced-card {
  max-width: 800px !important;
  margin-top: 80px;
  position: relative;
  transition: all 0.3s ease;
}

.baseet-chat-bubble {
  position: absolute;
  top: -10px;
  right: -50px;
  background: white;
  padding: 12px 20px;
  border-radius: 20px;
  border-bottom-left-radius: 4px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  font-weight: 500;
  color: #333;
  max-width: 220px;
  z-index: 10;
  animation: floatBubble 4s ease-in-out infinite;
  border: 2px solid var(--primary-color, #4361ee);
}

@keyframes floatBubble {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

/* Whiteboard */
.whiteboard-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  width: 100%;
}

.whiteboard-toolbar {
  display: flex;
  justify-content: space-between;
  width: 100%;
  max-width: 600px;
  align-items: center;
}

.color-picker {
  display: flex;
  gap: 10px;
}

.color-swatch {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  cursor: pointer;
  border: 3px solid transparent;
  transition: transform 0.2s;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.color-swatch:hover {
  transform: scale(1.15);
}

.color-swatch.active {
  border-color: #333;
  transform: scale(1.15);
}

.clear-btn {
  padding: 8px 16px;
  background: white;
  border: 2px solid #dee2e6;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  color: #495057;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: #f8f9fa;
  border-color: #adb5bd;
}

.whiteboard-canvas {
  border: 4px dashed #e2e8f0;
  border-radius: 16px;
  background: white;
  cursor: crosshair;
  max-width: 100%;
  box-shadow: inset 0 2px 10px rgba(0,0,0,0.02);
  touch-action: none; /* Prevent scrolling while drawing */
}

/* Game Area */
.game-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  align-items: center;
  gap: 15px;
}

.game-header {
  display: flex;
  justify-content: space-between;
  width: 100%;
  max-width: 600px;
  align-items: center;
  font-size: 20px;
  color: var(--primary-color, #4361ee);
  font-weight: 600;
}

.game-header h3 {
  margin: 0;
}

.game-area {
  width: 100%;
  max-width: 600px;
  height: 400px;
  background: #f1f5f9;
  border-radius: 20px;
  position: relative;
  overflow: hidden;
  border: 4px solid #e2e8f0;
  box-shadow: inset 0 5px 20px rgba(0,0,0,0.05);
}

.game-target {
  position: absolute;
  width: 65px;
  height: 65px;
  cursor: pointer;
  transition: all 0.15s ease-out;
  filter: drop-shadow(0 4px 6px rgba(0,0,0,0.2));
  background: white;
  border-radius: 50%;
  padding: 4px;
  z-index: 5;
  border: 3px solid #ff9800;
}

.game-target:hover {
  transform: scale(1.1);
}
"""

with open("/Users/Nada/nada/GRAD/Grad-Project/SW/frontend/src/styles/index.css", "a") as f:
    f.write(css_append)

print("Files updated successfully!")
