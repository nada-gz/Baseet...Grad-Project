import React from "react";
import { motion } from "framer-motion";

/**
 * VisualNumberLine Component
 * Provides a concrete spatial representation of numbers.
 */
const VisualNumberLine = ({ target, current, onSelect, range = [0, 10] }) => {
  const [min, max] = range;
  const numbers = Array.from({ length: max - min + 1 }, (_, i) => min + i);

  return (
    <div className="number-line-wrapper" style={styles.wrapper}>
      <div style={styles.line} />
      <div style={styles.marksContainer}>
        {numbers.map((num) => (
          <div key={num} style={styles.markWrapper} onClick={() => onSelect && onSelect(num)}>
            <div style={{
              ...styles.mark,
              height: num % 5 === 0 ? "20px" : "12px",
              backgroundColor: num === current ? "#4F46E5" : "#CBD5E1"
            }} />
            <span style={{
              ...styles.number,
              color: num === current ? "#4F46E5" : "#64748B",
              fontWeight: num === current ? "bold" : "normal"
            }}>
              {num}
            </span>

            {num === target && current !== 0 && (
              <motion.div
                layoutId="target-indicator"
                style={styles.targetIndicator}
                initial={{ y: -20, opacity: 0 }}
                animate={{ y: -45, opacity: 1 }}
              >
                🎯
              </motion.div>
            )}

            {num === current && (
              <motion.div
                layoutId="current-pin"
                style={styles.currentPin}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

const styles = {
  wrapper: {
    width: "100%",
    padding: "60px 20px 20px 20px",
    position: "relative",
    background: "#F8FAFC",
    borderRadius: "15px",
    marginTop: "40px",
  },
  line: {
    position: "absolute",
    top: "80px",
    left: "40px",
    right: "40px",
    height: "4px",
    backgroundColor: "#CBD5E1",
    borderRadius: "2px",
  },
  marksContainer: {
    display: "flex",
    justifyContent: "space-between",
    position: "relative",
    zIndex: 1,
  },
  markWrapper: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    cursor: "pointer",
    width: "30px",
  },
  mark: {
    width: "3px",
    borderRadius: "2px",
    marginBottom: "8px",
    transition: "all 0.2s",
  },
  number: {
    fontSize: "0.9rem",
  },
  targetIndicator: {
    position: "absolute",
    fontSize: "1.5rem",
  },
  currentPin: {
    position: "absolute",
    top: "14px",
    width: "12px",
    height: "12px",
    backgroundColor: "#4F46E5",
    borderRadius: "50%",
    border: "2px solid white",
    boxShadow: "0 2px 4px rgba(0,0,0,0.2)",
  },
};

export default VisualNumberLine;
