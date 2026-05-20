import React from "react";
import { CheckCircle2, Circle } from "lucide-react";

/**
 * StepIndicator Component
 * Offloads working memory by showing progress through sub-tasks.
 */
const StepIndicator = ({ steps, currentStep }) => {
  return (
    <div className="step-indicator" style={styles.container}>
      {steps.map((step, index) => {
        const isCompleted = index < currentStep;
        const isActive = index === currentStep;

        return (
          <div key={index} style={styles.stepWrapper}>
            <div style={{
              ...styles.iconWrapper,
              color: isCompleted ? "#22C55E" : isActive ? "#4F46E5" : "#CBD5E1",
              transform: isActive ? "scale(1.2)" : "scale(1)"
            }}>
              {isCompleted ? <CheckCircle2 size={24} /> : <Circle size={24} />}
            </div>
            <div style={{
              ...styles.text,
              color: isActive ? "#1E293B" : "#94A3B8",
              fontWeight: isActive ? "800" : "500"
            }}>
              {step}
            </div>
            {index < steps.length - 1 && <div style={styles.connector} />}
          </div>
        );
      })}
    </div>
  );
};

const styles = {
  container: {
    display: "flex",
    flexDirection: "row-reverse",
    alignItems: "center",
    justifyContent: "center",
    gap: "10px",
    padding: "15px",
    background: "white",
    borderRadius: "15px",
    boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.05)",
    marginBottom: "20px",
    flexWrap: "wrap"
  },
  stepWrapper: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    position: "relative"
  },
  iconWrapper: {
    transition: "all 0.3s ease",
  },
  text: {
    fontSize: "0.95rem",
    whiteSpace: "nowrap"
  },
  connector: {
    width: "20px",
    height: "2px",
    backgroundColor: "#E2E8F0",
    marginLeft: "5px"
  }
};

export default StepIndicator;
