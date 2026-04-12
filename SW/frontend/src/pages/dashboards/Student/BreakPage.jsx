import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../../../styles/index.css";
import cuteBaseet from "../../../assets/cute_baseet.png"; 

export default function BreakPage() {
  const navigate = useNavigate();
  // 5 minutes break = 300 seconds
  const totalTime = 300; 
  const [timeLeft, setTimeLeft] = useState(totalTime);

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
  
  // Follow the gradient of readiness strictly
  let ringColor = "#4caf50"; // Green (70-100%)
  if (percentage <= 20) {
    ringColor = "#f44336"; // Red (0-20%)
  } else if (percentage <= 70) {
    ringColor = "#ff9800"; // Amber (20-70%)
  }

  // SVG Circular progress bar measurements
  const radius = 110;
  const stroke = 12;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="break-page-container">
      <div className="break-content-card">
        
        {/* Dynamic circular degrading strip around Baseet */}
        <div className="break-image-wrapper">
          <svg
            height={radius * 2}
            width={radius * 2}
            className="break-timer-ring"
          >
            {/* Background Track */}
            <circle
              stroke="#e6e6e6"
              fill="transparent"
              strokeWidth={stroke}
              r={normalizedRadius}
              cx={radius}
              cy={radius}
            />
            {/* Shrinking Color Ring */}
            <circle
              stroke={ringColor}
              fill="transparent"
              strokeWidth={stroke}
              strokeDasharray={circumference + ' ' + circumference}
              style={{ strokeDashoffset }}
              className="break-timer-progress"
              r={normalizedRadius}
              cx={radius}
              cy={radius}
            />
          </svg>
          <img src={cuteBaseet} alt="Baseet taking a break" className="floating-baseet" />
        </div>
        
        <h1 className="break-title">Break Time!</h1>
        <p className="break-subtitle">
          Great job! Take {Math.ceil(timeLeft / 60)} minutes to stand up and stretch!
        </p>
        
        <div className="break-actions">
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
