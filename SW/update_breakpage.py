import re

break_page_content = """import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import "../../../styles/index.css";
import cuteBaseet from "../../../assets/cute_baseet.png"; 
import { Leaf, Palette, Gamepad2, Timer, Star, Heart, Rocket, Ghost, Eraser, Play, Square, RotateCcw } from "lucide-react";

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
      <Timer size={24} color="#ff5722" className="timer-icon" />
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
  const [isEraser, setIsEraser] = useState(false);

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
    
    ctx.strokeStyle = isEraser ? "white" : color;
    ctx.lineWidth = isEraser ? 20 : 5;
    
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
              className={`color-swatch ${!isEraser && c === color ? 'active' : ''}`}
              style={{ backgroundColor: c }}
              onClick={() => { setColor(c); setIsEraser(false); }}
            />
          ))}
          <div 
            className={`color-swatch eraser-btn ${isEraser ? 'active' : ''}`}
            onClick={() => setIsEraser(true)}
            title="Eraser"
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'white', border: '2px solid #cbd5e1' }}
          >
            <Eraser size={18} color="#64748b" />
          </div>
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
  const [targetType, setTargetType] = useState('baseet');
  const [targetPos, setTargetPos] = useState({ top: '50%', left: '50%' });
  const [gameState, setGameState] = useState('idle'); // idle | playing
  const gameAreaRef = useRef(null);
  const timerRef = useRef(null);

  const shapes = {
    baseet: <img src={cuteBaseet} alt="Baseet" className="full-shape-img" />,
    star: <Star size={48} fill="#facc15" color="#ca8a04" />,
    heart: <Heart size={48} fill="#f43f5e" color="#be123c" />,
    rocket: <Rocket size={48} fill="#3b82f6" color="#1d4ed8" />,
    ghost: <Ghost size={48} fill="#e2e8f0" color="#94a3b8" />
  };
  
  const sidebarShapes = {
    baseet: <img src={cuteBaseet} alt="Baseet" className="small-shape-img" />,
    star: <Star size={24} fill="#facc15" color="#ca8a04" />,
    heart: <Heart size={24} fill="#f43f5e" color="#be123c" />,
    rocket: <Rocket size={24} fill="#3b82f6" color="#1d4ed8" />,
    ghost: <Ghost size={24} fill="#e2e8f0" color="#94a3b8" />
  };

  const spawnTarget = (missed = false) => {
    if (missed) {
      setScore(s => s - 1); // Decrease score if target vanishes
    }
    
    if (gameAreaRef.current) {
      const maxX = gameAreaRef.current.clientWidth - 80;
      const maxY = gameAreaRef.current.clientHeight - 80;
      const newX = Math.max(10, Math.random() * maxX);
      const newY = Math.max(10, Math.random() * maxY);
      setTargetPos({ top: `${newY}px`, left: `${newX}px` });
    }

    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => spawnTarget(true), 1000);
  };

  const startGame = () => {
    setGameState('playing');
    spawnTarget(false);
  };

  const stopGame = () => {
    setGameState('idle');
    if (timerRef.current) clearTimeout(timerRef.current);
  };

  const restartGame = () => {
    setScore(0);
    setGameState('playing');
    spawnTarget(false);
  };

  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []); 

  const handleCatch = (e) => {
    e.stopPropagation();
    if (gameState !== 'playing') return;
    setScore(s => s + 1); 
    spawnTarget(false);   
  };

  return (
    <div className="game-container with-sidebar">
      <div className="game-sidebar">
        <h4>Target Shape</h4>
        <div className="shape-options">
          {Object.keys(sidebarShapes).map(key => (
            <div 
              key={key} 
              className={`shape-option ${targetType === key ? 'active' : ''}`}
              onClick={() => setTargetType(key)}
            >
              {sidebarShapes[key]}
            </div>
          ))}
        </div>
        <div className="score-board">
          <p>Score</p>
          <div className={`score-value ${score < 0 ? 'negative' : ''}`}>{score}</div>
        </div>
      </div>
      
      <div className="game-main">
        <div className="game-header">
          <h3>Catch Game</h3>
          <div className="game-controls">
            {gameState !== 'playing' ? (
              <button className="game-btn start-btn" onClick={startGame}><Play size={18}/> Start</button>
            ) : (
              <button className="game-btn stop-btn" onClick={stopGame}><Square size={18}/> Stop</button>
            )}
            <button className="game-btn restart-btn" onClick={restartGame}><RotateCcw size={18}/> Restart</button>
          </div>
        </div>
        
        <div className="game-area" ref={gameAreaRef}>
          {gameState === 'idle' ? (
            <div className="game-overlay">
              <Gamepad2 size={64} className="game-overlay-icon" />
              <h2>Press Start to Play!</h2>
            </div>
          ) : (
            <div
              className={`game-target dynamic-target ${targetType === 'baseet' ? 'baseet-target' : ''}`}
              style={{ top: targetPos.top, left: targetPos.left }}
              onClick={handleCatch}
              onTouchStart={handleCatch}
            >
              {shapes[targetType]}
            </div>
          )}
        </div>
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
          <button className={`mode-btn ${mode === 'relax' ? 'active' : ''}`} onClick={() => setMode('relax')}>
            <Leaf size={20} /> Relax
          </button>
          <button className={`mode-btn ${mode === 'draw' ? 'active' : ''}`} onClick={() => setMode('draw')}>
            <Palette size={20} /> Draw
          </button>
          <button className={`mode-btn ${mode === 'game' ? 'active' : ''}`} onClick={() => setMode('game')}>
            <Gamepad2 size={20} /> Catch
          </button>
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

with open("/Users/Nada/nada/GRAD/Grad-Project/SW/frontend/src/pages/dashboards/Student/BreakPage.jsx", "w", encoding='utf-8') as f:
    f.write(break_page_content)

css_append = """
/* Game Controls & Overlay */

.game-controls {
  display: flex;
  gap: 10px;
}

.game-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  color: white;
}

.start-btn { background: #10b981; }
.start-btn:hover { background: #059669; }

.stop-btn { background: #ef4444; }
.stop-btn:hover { background: #dc2626; }

.restart-btn { background: #3b82f6; }
.restart-btn:hover { background: #2563eb; }

.game-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255,255,255,0.7);
  backdrop-filter: blur(4px);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
  color: var(--primary-color, #4361ee);
}

.game-overlay-icon {
  margin-bottom: 10px;
  color: #94a3b8;
}

.dynamic-target {
  display: flex;
  justify-content: center;
  align-items: center;
  background: white;
  border-radius: 50%;
  padding: 8px;
}
.dynamic-target.baseet-target {
  border: 3px solid #ff9800;
  padding: 4px;
}
.full-shape-img {
  width: 100%; height: 100%; object-fit: contain;
}

.eraser-btn {
  transition: transform 0.2s;
  cursor: pointer;
}
.eraser-btn:hover { transform: scale(1.15); }
.eraser-btn.active { border-color: #333; transform: scale(1.15); }

"""

with open("/Users/Nada/nada/GRAD/Grad-Project/SW/frontend/src/styles/index.css", "a", encoding='utf-8') as f:
    f.write(css_append)
