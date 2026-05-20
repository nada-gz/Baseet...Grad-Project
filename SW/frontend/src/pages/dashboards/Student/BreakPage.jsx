import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import "../../../styles/index.css";
import cuteBaseet from "../../../assets/cute_baseet.png"; 
import baseetRun1 from "../../../assets/baseet_run_1.png";
import baseetRun2 from "../../../assets/baseet_run_2.png";
import { Leaf, Palette, Gamepad2, Timer, Star, Heart, Rocket, Ghost, Eraser, Play, Square, RotateCcw, Footprints, Zap } from "lucide-react";

import housePineapple from "../../../assets/house_pineapple.png";
import houseRock from "../../../assets/house_rock.png";
import houseMoai from "../../../assets/house_moai.png";
import houseKrusty from "../../../assets/house_krusty.png";

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
    }, 20000);
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
    if (canvasRef.current) {
      const ctx = canvasRef.current.getContext('2d');
      ctx.fillStyle = "white";
      ctx.fillRect(0, 0, canvasRef.current.width, canvasRef.current.height);
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
    }
  }, []);

  const getCoordinates = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    return { x: clientX - rect.left, y: clientY - rect.top };
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
    canvasRef.current.getContext('2d').closePath();
    setIsDrawing(false);
  };

  const clearCanvas = () => {
    if (!canvasRef.current) return;
    const ctx = canvasRef.current.getContext('2d');
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvasRef.current.width, canvasRef.current.height);
  };

  return (
    <div className="whiteboard-container">
      <div className="whiteboard-toolbar">
        <div className="color-picker">
          {colors.map(c => (
            <div key={c} className={`color-swatch ${!isEraser && c === color ? 'active' : ''}`}
                 style={{ backgroundColor: c }} onClick={() => { setColor(c); setIsEraser(false); }} />
          ))}
          <div className={`color-swatch eraser-btn ${isEraser ? 'active' : ''}`} onClick={() => setIsEraser(true)}
               style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'white', border: '2px solid #cbd5e1' }}>
            <Eraser size={18} color="#64748b" />
          </div>
        </div>
        <button className="clear-btn" onClick={clearCanvas}>Clear Board</button>
      </div>
      <canvas ref={canvasRef} width={600} height={350} className="whiteboard-canvas"
        onMouseDown={startDrawing} onMouseMove={draw} onMouseUp={stopDrawing} onMouseLeave={stopDrawing}
        onTouchStart={startDrawing} onTouchMove={draw} onTouchEnd={stopDrawing} />
    </div>
  );
};

const CatchGameMode = () => {
  const [score, setScore] = useState(0);
  const [targetType, setTargetType] = useState('baseet');
  const [targetPos, setTargetPos] = useState({ top: '50%', left: '50%' });
  const [gameState, setGameState] = useState('idle'); 
  const gameAreaRef = useRef(null);
  const timerRef = useRef(null);
  const spawnRef = useRef(null);

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
    if (missed) setScore(s => s - 1); 
    
    if (gameAreaRef.current) {
      const maxX = gameAreaRef.current.clientWidth - 80;
      const maxY = gameAreaRef.current.clientHeight - 80;
      setTargetPos({ top: `${Math.max(10, Math.random() * maxY)}px`, left: `${Math.max(10, Math.random() * maxX)}px` });
    }
    
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      // Use latest ref to prevent stale closures failing to decrement correctly
      if (spawnRef.current) spawnRef.current(true);
    }, 1000);
  };

  useEffect(() => {
    spawnRef.current = spawnTarget;
  });

  useEffect(() => {
    if (gameState === 'playing') {
      if (score <= -5) {
        setGameState('gameover');
        if (timerRef.current) clearTimeout(timerRef.current);
      } else if (score >= 20) {
        setGameState('win');
        if (timerRef.current) clearTimeout(timerRef.current);
      }
    }
  }, [score, gameState]);

  const startGame = () => { setGameState('playing'); setScore(0); spawnTarget(false); };
  const stopGame = () => { setGameState('idle'); if (timerRef.current) clearTimeout(timerRef.current); };
  const restartGame = () => { setScore(0); setGameState('playing'); spawnTarget(false); };

  useEffect(() => () => { if (timerRef.current) clearTimeout(timerRef.current); }, []);

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
            <div key={key} className={`shape-option ${targetType === key ? 'active' : ''}`} onClick={() => setTargetType(key)}>
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
            {gameState !== 'playing' ? <button className="game-btn start-btn" onClick={startGame}><Play size={18}/> Start</button> : <button className="game-btn stop-btn" onClick={stopGame}><Square size={18}/> Stop</button>}
            <button className="game-btn restart-btn" onClick={restartGame}><RotateCcw size={18}/> Restart</button>
          </div>
        </div>
        <div className="game-area" ref={gameAreaRef}>
          {gameState === 'idle' && (
            <div className="game-overlay"><Gamepad2 size={64} className="game-overlay-icon" /><h2>Press Start to Play!</h2></div>
          )}
          {gameState === 'gameover' && (
            <div className="game-overlay" style={{ background: 'rgba(255,255,255,0.85)' }}>
              <h2 style={{ color: '#ef4444', fontSize: '32px' }}>Oops! Game Over</h2>
              <p style={{ fontSize: '20px', margin: '10px 0 20px 0' }}>Score: {score}</p>
              <button className="game-btn restart-btn" style={{ fontSize: '18px', padding: '10px 24px', margin: 0 }} onClick={restartGame}>
                <RotateCcw size={20}/> Play Again
              </button>
            </div>
          )}
          {gameState === 'win' && (
            <div className="game-overlay" style={{ background: 'rgba(255,255,255,0.85)', overflow: 'hidden' }}>
              <div className="balloons-container">
                <div className="balloon r1">🎈</div>
                <div className="balloon r2">🎈</div>
                <div className="balloon r3">🎈</div>
                <div className="balloon r4">🎈</div>
                <div className="balloon r5">🎉</div>
              </div>
              <h2 style={{ color: '#10b981', fontSize: '40px', zIndex: 2 }}>YOU WIN..!</h2>
              <p style={{ fontSize: '20px', margin: '10px 0 20px 0', zIndex: 2, fontWeight: 'bold' }}>Final Score: {score}</p>
              <button className="game-btn start-btn" style={{ fontSize: '18px', padding: '10px 24px', margin: 0, zIndex: 2 }} onClick={restartGame}>
                <RotateCcw size={20}/> Play Again
              </button>
            </div>
          )}
          {gameState === 'playing' && (
            <div className={`game-target dynamic-target ${targetType === 'baseet' ? 'baseet-target' : ''}`} style={{ top: targetPos.top, left: targetPos.left }} onMouseDown={handleCatch} onTouchStart={handleCatch}>
              {shapes[targetType]}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};


// RUNNER GAME COMPONENT

const RunnerGameMode = () => {
  const canvasRef = useRef(null);
  const [gameState, setGameState] = useState('idle'); // idle, playing, gameover
  const [score, setScore] = useState(0);
  
  const imgRun1 = useRef(new Image());
  const imgRun2 = useRef(new Image());
  const imgPineapple = useRef(new Image());
  const imgRock = useRef(new Image());
  const imgMoai = useRef(new Image());
  const imgKrusty = useRef(new Image());
  
  useEffect(() => {
    imgRun1.current.src = baseetRun1;
    imgRun2.current.src = baseetRun2;
    imgPineapple.current.src = housePineapple;
    imgRock.current.src = houseRock;
    imgMoai.current.src = houseMoai;
    imgKrusty.current.src = houseKrusty;
  }, []);

  const gameData = useRef({
    score: 0,
    speed: 5,
    obstacles: [],
    bubbles: [],
    bgObjects: [],
    bgQueue: ['pineapple', 'rock', 'moai', 'krab', 'krusty'],
    bgTimer: 0,
    dino: { x: 50, y: 150, width: 60, height: 60, yVelocity: 0, isJumping: false, frame: 1 },
    lastFrameTime: 0,
    speedTimer: 0,
    animationId: 0,
    lastSpeedIncreaseScore: 0
  });

  const gravity = 0.85;
  const jumpStrength = 14;
  const groundY = 220; // 300 total height, ground at 220

  const jump = () => {
    if (gameState === 'playing' && !gameData.current.dino.isJumping) {
      gameData.current.dino.yVelocity = -jumpStrength;
      gameData.current.dino.isJumping = true;
    }
  };

  const handleInteraction = (e) => {
    e.preventDefault(); 
    if (gameState === 'idle' || gameState === 'gameover') {
      startGame();
    } else if (gameState === 'playing') {
      jump();
    }
  };
  
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.code === 'Space' || e.code === 'ArrowUp') {
        e.preventDefault();
        handleInteraction(e);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [gameState]);

  const startGame = () => {
    setGameState('playing');
    setScore(0);
    gameData.current = {
      score: 0,
      speed: 8.5,
      obstacles: [],
      bubbles: [],
      bgQueue: ['rock', 'moai', 'krab', 'krusty', 'pineapple'], // Cycle queue
      bgObjects: [
        {
          x: 400, // Spawn one immediately on screen at the start!
          type: 'pineapple',
          img: imgPineapple.current,
          width: 140,
          height: 180
        }
      ],
      bgTimer: 0,
      dino: { x: 50, y: groundY - 60, width: 60, height: 60, yVelocity: 0, isJumping: false, frame: 1 },
      lastFrameTime: Date.now(),
      speedTimer: 0,
      animationId: 0,
      lastSpeedIncreaseScore: 0
    };
    gameLoop();
  };

  const stopGameRunner = () => {
    setGameState('idle');
    if (gameData.current.animationId) {
      cancelAnimationFrame(gameData.current.animationId);
    }
  };

  const gameLoop = () => {
    if (!canvasRef.current) return;
    const ctx = canvasRef.current.getContext('2d');
    const state = gameData.current;
    
    // Clear canvas entirely to reveal scrolling CSS background
    ctx.clearRect(0, 0, 600, 300);
    
    // Draw Sandy Sea Floor
    ctx.fillStyle = "#eab308"; // Beautiful warm sand
    ctx.beginPath();
    ctx.roundRect(0, groundY + 15, 600, 300 - groundY, 15);
    ctx.fill();
    ctx.fillStyle = "#facc15"; // Top sand highlight
    ctx.fillRect(0, groundY, 600, 30);

    // Dynamic Bubbles
    if (Math.random() < 0.06) {
      state.bubbles.push({
        x: Math.random() * 600,
        y: 320,
        radius: 3 + Math.random() * 6,
        speed: 1 + Math.random() * 2,
        wobble: Math.random() * Math.PI * 2
      });
    }

    ctx.fillStyle = "rgba(255, 255, 255, 0.45)"; // Soft bubbles
    state.bubbles.forEach((b) => {
      b.y -= b.speed;
      b.x += Math.sin(b.y * 0.05 + b.wobble) * 1.5;
      
      // Parallax move bubbles slightly backwards so baseet feels fast
      b.x -= state.speed * 0.15;

      ctx.beginPath();
      ctx.arc(b.x, b.y, b.radius, 0, Math.PI * 2);
      ctx.fill();
    });
    // Cull offscreen
    state.bubbles = state.bubbles.filter(b => b.y + b.radius > 0 && b.x > -20);

    // Dynamic Parallax Houses (Background Objects)
    state.bgTimer++;
    // Spawn houses or seaweed with controlled pacing to look like a real neighborhood
    if (state.bgTimer > 100 && (state.bgObjects.length === 0 || 600 - state.bgObjects[state.bgObjects.length - 1].x > 250)) {
         state.bgTimer = 0;
         
         let type = 'seaweed';
         if (Math.random() < 0.6) {
             type = state.bgQueue.shift();
             state.bgQueue.push(type);
         }
         
         let houseImg = null;
         let w = 140, h = 180;
         
         if (type === 'pineapple') { houseImg = imgPineapple.current; w = 150; h = 240; } // Adjusted for exact real PNG aspect ratio
         else if (type === 'moai') { houseImg = imgMoai.current; w = 150; h = 210; } // Adjusted for exact real PNG aspect ratio
         else if (type === 'krusty') { houseImg = imgKrusty.current; w = 140; h = 210; } // The green pickle house
         else if (type === 'seaweed') { w = 40; h = 80; }

         state.bgObjects.push({
           x: 600, // Spawn off screen right
           type: type,
           img: houseImg,
           width: w,
           height: h
         });
    }

    state.bgObjects.forEach((bg) => {
      bg.x -= state.speed * 0.35; // Parallax effect
      
      if (bg.type === 'pineapple') {
          if (bg.img && bg.img.complete && bg.img.naturalHeight > 1) {
              ctx.drawImage(bg.img, bg.x, groundY - bg.height + 20, bg.width, bg.height);
          }
      } else if (bg.type === 'moai') {
          if (bg.img && bg.img.complete && bg.img.naturalHeight > 1) {
              ctx.drawImage(bg.img, bg.x, groundY - bg.height + 20, bg.width, bg.height);
          } else {
              ctx.font = "140px Arial";
              ctx.textBaseline = "bottom";
              ctx.fillText("🗿", bg.x, groundY + 30);
          }
      } else if (bg.type === 'krusty') {
          if (bg.img && bg.img.complete && bg.img.naturalHeight > 1) {
              ctx.drawImage(bg.img, bg.x, groundY - bg.height + 20, bg.width, bg.height);
          } else {
              ctx.font = "160px Arial";
              ctx.textBaseline = "bottom";
              ctx.fillText("🥒", bg.x, groundY + 30); // Pickle fallback for green house
          }
      } else if (bg.type === 'rock') {
          ctx.font = "140px Arial";
          ctx.textBaseline = "bottom";
          ctx.fillText("🪨", bg.x, groundY + 30);
      } else if (bg.type === 'krab') {
          ctx.font = "100px Arial";
          ctx.textBaseline = "bottom";
          ctx.fillText("🍔", bg.x, groundY + 20); 
      } else if (bg.type === 'seaweed') {
        // Draw native Canvas Seaweed
        ctx.fillStyle = "#15803d";
        ctx.beginPath();
        ctx.roundRect(bg.x, groundY - 60, 16, 80, 8);
        ctx.fill();
        ctx.fillStyle = "#16a34a";
        ctx.beginPath();
        ctx.roundRect(bg.x - 12, groundY - 45, 12, 65, 6);
        ctx.fill();
        ctx.fillStyle = "#22c55e";
        ctx.beginPath();
        ctx.roundRect(bg.x + 16, groundY - 30, 10, 50, 5);
        ctx.fill();
      }
    });
    state.bgObjects = state.bgObjects.filter(bg => bg.x + bg.width > -150);

    // Update Dino
    state.dino.yVelocity += gravity;
    state.dino.y += state.dino.yVelocity;

    if (state.dino.y > groundY - state.dino.height) {
      state.dino.y = groundY - state.dino.height;
      state.dino.isJumping = false;
      state.dino.yVelocity = 0;
    }

    // Animation frame for Sprite
    const now = Date.now();
    if (!state.dino.isJumping && now - state.lastFrameTime > 400) { // Changed from 250 to 400 for even slower, pronounced leg switch
      state.dino.frame = state.dino.frame === 1 ? 2 : 1;
      state.lastFrameTime = now;
    } else if (state.dino.isJumping) {
      state.dino.frame = 1; // static frame while jumping
    }

    // Draw Dino Sprite
    const currentImg = state.dino.frame === 1 ? imgRun1.current : imgRun2.current;
    if (currentImg.complete && currentImg.naturalHeight !== 0) {
        ctx.drawImage(currentImg, state.dino.x, state.dino.y, state.dino.width, state.dino.height);
    } else {
        // Fallback drawing if image fails
        ctx.fillStyle = "#ff9800";
        ctx.fillRect(state.dino.x, state.dino.y, state.dino.width, state.dino.height);
    }

    // Manage Obstacles
    if (state.obstacles.length === 0 || (600 - state.obstacles[state.obstacles.length - 1].x > (180 + Math.random() * 250))) {
      if (Math.random() < 0.02) {
         // Create obstacle
         state.obstacles.push({
           x: 600,
           y: groundY - 30, // Shorter rock
           width: 45,       // Wider rock
           height: 30,
           color: ["#94a3b8", "#a8a29e", "#a78bfa"][Math.floor(Math.random()*3)] // gray, warm gray, soft purple
         });
      }
    }

    // Move & Draw Obstacles, Collision Check
    let isHit = false;
    for (let i = 0; i < state.obstacles.length; i++) {
       let obs = state.obstacles[i];
       obs.x -= state.speed;
       
       // Draw Smooth, Cute Pebble
       ctx.fillStyle = obs.color;
       
       // Very soft shadow for separation
       ctx.shadowColor = "rgba(0,0,0,0.4)"; 
       ctx.shadowBlur = 8;
       ctx.shadowOffsetY = 4;
       
       ctx.beginPath();
       ctx.roundRect(obs.x, obs.y, obs.width, obs.height, 15); // Super soft, round corners
       ctx.fill();
       
       ctx.shadowColor = "transparent";
       ctx.shadowBlur = 0;
       ctx.shadowOffsetY = 0;

       // Cute shiny highlight on top (makes it pop clearly without harsh lines!)
       ctx.fillStyle = "rgba(255, 255, 255, 0.4)";
       ctx.beginPath();
       ctx.roundRect(obs.x + 6, obs.y + 4, obs.width - 18, obs.height * 0.3, 8);
       ctx.fill();

       // Hit Check (AABB Collision)
       // Giving a small buffer (5px) to be generous to kids
       const buffer = 10;
       if (
         state.dino.x < obs.x + obs.width - buffer &&
         state.dino.x + state.dino.width - buffer > obs.x &&
         state.dino.y < obs.y + obs.height - buffer &&
         state.dino.y + state.dino.height - buffer > obs.y
       ) {
         isHit = true;
       }
    }

    // Clean up off-screen
    state.obstacles = state.obstacles.filter(o => o.x + o.width > 0);

    // Score and Speed Up
    state.score += 0.1;
    
    // Increase speed distinctly every 100 points
    const currentScoreLevel = Math.floor(state.score / 100) * 100;
    if (currentScoreLevel > state.lastSpeedIncreaseScore && currentScoreLevel > 0) {
       state.speed += 1.5;
       state.lastSpeedIncreaseScore = currentScoreLevel;
    }
    
    // Sync React state for display every few frames
    if (Math.floor(state.score) % 5 === 0) setScore(Math.floor(state.score));

    // Game Over 
    if (isHit) {
       setGameState('gameover');
       ctx.fillStyle = "rgba(0,0,0,0.5)";
       ctx.fillRect(0,0,600,300);
       return; // Stop loop
    }
    
    // Win Condition
    if (state.score >= 1000) {
       setGameState('win');
       return; // Stop loop
    }

    state.animationId = requestAnimationFrame(gameLoop);
  };

  return (
    <div className="game-container runner-container">
      <div className="game-header runner-header">
        <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', margin: 0, color: 'var(--primary-color, #4361ee)' }}>
          <Zap size={24} color="#f59e0b" fill="#f59e0b" /> Baseet Runner!
        </h3>
        
        <div className="runner-stats-panel">
          <div className="game-controls runner-controls">
            {gameState !== 'playing' ? (
              <button className="game-btn start-btn start-running" onClick={startGame}><Play size={18}/> Start</button>
            ) : (
              <button className="game-btn stop-btn" onClick={stopGameRunner}><Square size={18}/> Stop</button>
            )}
          </div>
          
          <div className="runner-score-badge">
            <span className="runner-score-label">Score</span>
            <span className="runner-score-number">{Math.floor(score)}</span>
          </div>
        </div>
      </div>
      
      <div className="game-area runner-area" style={{ height: '300px', cursor: 'pointer', overflow: 'hidden' }}
           onMouseDown={handleInteraction} onTouchStart={handleInteraction}>
        <canvas ref={canvasRef} width={600} height={300} className="runner-canvas" style={{ width: '100%', height: '100%' }} />
        
        {gameState === 'idle' && (
          <div className="game-overlay">
            <Footprints size={64} className="game-overlay-icon" />
            <h2>Tap Screen or Press Space to Start!</h2>
          </div>
        )}
        
        {gameState === 'gameover' && (
          <div className="game-overlay" style={{ background: 'rgba(255,255,255,0.85)' }}>
            <h2 style={{ color: '#ef4444', fontSize: '32px' }}>Oops! Game Over</h2>
            <p style={{ fontSize: '20px', margin: '10px 0 20px 0' }}>Score: {Math.floor(score)}</p>
            <button className="game-btn restart-btn" style={{ fontSize: '18px', padding: '10px 24px', margin: 0 }} onClick={startGame}>
              <RotateCcw size={20}/> Play Again
            </button>
          </div>
        )}

        {gameState === 'win' && (
          <div className="game-overlay" style={{ background: 'rgba(255,255,255,0.85)', overflow: 'hidden' }}>
            <div className="balloons-container">
              <div className="balloon r1">🎈</div>
              <div className="balloon r2">🎈</div>
              <div className="balloon r3">🎈</div>
              <div className="balloon r4">🎈</div>
              <div className="balloon r5">🎉</div>
            </div>
            <h2 style={{ color: '#10b981', fontSize: '40px', zIndex: 2 }}>YOU SURVIVED!</h2>
            <p style={{ fontSize: '20px', margin: '10px 0 20px 0', zIndex: 2, fontWeight: 'bold' }}>Final Score: {Math.floor(score)}</p>
            <button className="game-btn restart-btn" style={{ fontSize: '18px', padding: '10px 24px', margin: 0, zIndex: 2 }} onClick={startGame}>
              <RotateCcw size={20}/> Play Again
            </button>
          </div>
        )}
      </div>
    </div>
  );
};


export default function BreakPage() {
  const navigate = useNavigate();
  const totalTime = 300; 
  const [timeLeft, setTimeLeft] = useState(totalTime);
  const [mode, setMode] = useState('relax'); // relax | draw | game | run

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
  if (percentage <= 20) ringColor = "#f44336"; 
  else if (percentage <= 70) ringColor = "#ff9800"; 

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
          <button className={`mode-btn ${mode === 'run' ? 'active' : ''}`} onClick={() => setMode('run')}>
            <Footprints size={20} /> Run
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
        {mode === 'game' && <CatchGameMode />}
        {mode === 'run' && <RunnerGameMode />}
        
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
