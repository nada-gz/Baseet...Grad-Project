import React from "react";
import { motion, AnimatePresence } from "framer-motion";

/**
 * Manipulatives Component
 * Renders concrete visual blocks for a given number to support Dyscalculia.
 */
const Manipulatives = ({ count, color = "#4F46E5" }) => {
  // Create an array of length 'count'
  const blocks = Array.from({ length: count }, (_, i) => i);

  return (
    <div className="manipulatives-container" style={styles.container}>
      <AnimatePresence>
        <div style={styles.grid}>
          {blocks.map((id) => (
            <motion.div
              key={id}
              initial={{ scale: 0, rotate: -45 }}
              animate={{ scale: 1, rotate: 0 }}
              exit={{ scale: 0 }}
              whileHover={{ scale: 1.1 }}
              style={{
                ...styles.block,
                backgroundColor: color,
              }}
            />
          ))}
        </div>
      </AnimatePresence>
    </div>
  );
};

const styles = {
  container: {
    padding: "20px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "15px",
    background: "rgba(255, 255, 255, 0.5)",
    borderRadius: "20px",
    border: "2px dashed #CBD5E1",
  },
  grid: {
    display: "flex",
    flexWrap: "wrap",
    justifyContent: "center",
    gap: "10px",
    maxWidth: "400px",
  },
  block: {
    width: "50px",
    height: "50px",
    borderRadius: "8px",
    boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
  },
  label: {
    fontSize: "1.2rem",
    fontWeight: "bold",
    color: "#64748B",
  },
};

export default Manipulatives;
