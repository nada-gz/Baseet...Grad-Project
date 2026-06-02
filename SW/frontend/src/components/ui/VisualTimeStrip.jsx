import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "../../styles/index.css";

export default function VisualTimeStrip({ initialMinutes = 20 }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [totalSeconds, setTotalSeconds] = useState(initialMinutes * 60);
  const [remainingSeconds, setRemainingSeconds] = useState(initialMinutes * 60);
  const [showModal, setShowModal] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [draftMinutes, setDraftMinutes] = useState(initialMinutes);
  const [topbarHeight, setTopbarHeight] = useState(85);

  useEffect(() => {
    const updateHeight = () => {
      const topbar = document.querySelector('.topbar');
      if (topbar) {
        setTopbarHeight(topbar.offsetHeight);
      }
    };

    // Slight delay to ensure DOM is updated and images are rendered
    setTimeout(updateHeight, 100);
    window.addEventListener('resize', updateHeight);
    return () => window.removeEventListener('resize', updateHeight);
  }, [location.pathname]);

  useEffect(() => {
    // Reset timer when initialMinutes changes (e.g. parent reconfigures)
    setTotalSeconds(initialMinutes * 60);
    setRemainingSeconds(initialMinutes * 60);
    setDraftMinutes(initialMinutes);
    setIsRunning(false);
  }, [initialMinutes]);

  useEffect(() => {
    let interval = null;
    if (isRunning && remainingSeconds > 0) {
      interval = setInterval(() => {
        setRemainingSeconds((prev) => prev - 1);
      }, 1000);
    } else if (isRunning && remainingSeconds === 0) {
      setIsRunning(false);
      // Trigger Break
      navigate("/dashboard/student/break");
    }
    return () => clearInterval(interval);
  }, [remainingSeconds, isRunning, navigate]);

  const handleSetTimer = () => {
    setTotalSeconds(draftMinutes * 60);
    setRemainingSeconds(draftMinutes * 60);
    setIsRunning(false); // Stop when a new time is set
    setShowModal(false);
  };

  const toggleTimer = () => {
    if (remainingSeconds > 0) {
      setIsRunning(!isRunning);
    }
  };

  // Calculate percentage and color
  const percentage = Math.max(0, Math.min(100, (remainingSeconds / totalSeconds) * 100));

  let barColor = "#4caf50"; // Green (70-100%)
  let icon = "🐢"; // Turtle

  if (percentage <= 20) {
    barColor = "#f44336"; // Red (0-20%)
  } else if (percentage <= 70) {
    barColor = "#ff9800"; // Amber (20-70%)
  }

  // Switch icon at 30%
  if (percentage <= 30) {
    icon = "🐇"; // Rabbit
  }

  const presetOptions = [10, 15, 20, 30, 45, 60];

  return (
    <>
      <div
        className="visual-time-strip-container"
        style={{
          marginTop: "0px",
          top: `${topbarHeight + 30}px`
        }}
      >
        <div className="time-strip-wrapper">
          <div
            className="time-strip-progress"
            style={{
              width: `${percentage}%`,
              backgroundColor: barColor
            }}
          >
            {/* The moving icon at the tip of the progress bar */}
            <div className="time-strip-icon" style={{ borderColor: barColor }}>
              {icon}
            </div>
          </div>
        </div>

        {/* Adjusted controls for kids / teacher */}
        <div className="time-strip-controls" style={{ display: 'flex', gap: '8px' }}>
          <button
            className="set-timer-btn"
            onClick={toggleTimer}
            style={{ backgroundColor: isRunning ? '#ff9800' : '#4caf50' }}
          >
            {isRunning ? "Pause" : "Start"}
          </button>
          <button className="set-timer-btn" onClick={() => setShowModal(true)}>
            Set Timer
          </button>
        </div>
      </div>

      {showModal && (
        <div className="timer-modal-overlay">
          <div className="timer-modal-content">
            <h3>Set Lesson Time</h3>
            <div className="timer-modal-options">
              {presetOptions.map((mins) => (
                <button
                  key={mins}
                  className="timer-option-btn"
                  style={{
                    backgroundColor: draftMinutes === mins ? 'var(--primary-color)' : '#f1f4ff',
                    color: draftMinutes === mins ? 'white' : 'var(--primary-color)'
                  }}
                  onClick={() => setDraftMinutes(mins)}
                >
                  {mins} min
                </button>
              ))}
            </div>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', marginTop: '20px' }}>
              <button
                className="timer-modal-close"
                style={{ padding: '8px 16px', background: '#ccc', borderRadius: '12px', border: 'none', color: '#333', cursor: 'pointer', textDecoration: 'none' }}
                onClick={() => setShowModal(false)}
              >
                Cancel
              </button>
              <button
                className="set-timer-btn"
                onClick={handleSetTimer}
              >
                Set
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
