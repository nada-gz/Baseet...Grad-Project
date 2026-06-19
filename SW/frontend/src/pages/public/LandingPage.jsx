import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
  Laptop, MonitorPlay, Smartphone, ArrowRight, 
  PlayCircle, BrainCircuit, Activity, Eye, Thermometer, 
  HeartPulse, Layers, ShieldCheck, Users, Camera
} from 'lucide-react';
import Logo from '../../components/ui/logo';

export default function LandingPage() {
  const navigate = useNavigate();

  useEffect(() => {
    // Set both html and body background to white to prevent yellow overscroll (top and bottom)
    const originalBodyBg = document.body.style.backgroundColor;
    const originalHtmlBg = document.documentElement.style.backgroundColor;
    
    document.body.style.backgroundColor = '#ffffff';
    document.documentElement.style.backgroundColor = '#ffffff';
    
    return () => {
      document.body.style.backgroundColor = originalBodyBg;
      document.documentElement.style.backgroundColor = originalHtmlBg;
    };
  }, []);

  const handleScroll = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  const fadeInUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } }
  };

  const staggerContainer = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.15 } }
  };

  return (
    <div className="landing-wrapper">
      <style>{`
        /* Global Reset for Landing */
        .landing-wrapper {
          font-family: 'Nunito', sans-serif;
          background-color: #ffffff;
          color: #2D3436;
          overflow-x: hidden;
          scroll-behavior: smooth;
        }

        h1, h2, h3, h4, .logo-text {
          font-family: 'Lexend', sans-serif;
        }

        /* --- Navbar --- */
        .l-navbar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px 5% 20px 180px; /* 180px left padding to accommodate the fixed logo */
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(10px);
          position: sticky;
          top: 0;
          z-index: 100;
          border-bottom: 1px solid #f1f2f6;
        }

        .l-navbar .logo-fixed {
          top: -52px !important;
        }
        
        .logo-text {
          font-size: 1.8rem;
          font-weight: 800;
          color: #6C63FF;
          cursor: pointer;
        }
        .l-nav-links {
          display: flex;
          gap: 32px;
          align-items: center;
        }
        .l-nav-links a {
          text-decoration: none;
          color: #636E72;
          font-weight: 600;
          font-size: 1rem;
          transition: color 0.2s;
          cursor: pointer;
        }
        .l-nav-links a:hover {
          color: #6C63FF;
        }

        /* --- Buttons --- */
        .l-btn {
          padding: 12px 28px;
          border-radius: 12px;
          font-family: 'Lexend', sans-serif;
          font-weight: 600;
          font-size: 1rem;
          cursor: pointer;
          border: none;
          display: inline-flex;
          align-items: center;
          gap: 8px;
          transition: all 0.2s ease;
        }
        .l-btn-primary {
          background-color: #6C63FF;
          color: #fff;
          box-shadow: 0 4px 14px rgba(108, 99, 255, 0.25);
        }
        .l-btn-primary:hover {
          background-color: #584ff0;
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(108, 99, 255, 0.35);
        }
        .l-btn-outline {
          background-color: transparent;
          color: #6C63FF;
          border: 2px solid #6C63FF;
        }
        .l-btn-outline:hover {
          background-color: rgba(108, 99, 255, 0.05);
        }
        .l-btn-demo {
          padding: 8px 16px;
          border-radius: 8px;
          background-color: #f1f2f6;
          color: #2D3436;
          font-size: 0.9rem;
          font-weight: 600;
          text-decoration: none;
          transition: background 0.2s;
        }
        .l-btn-demo:hover {
          background-color: #DFE6E9;
        }

        /* --- Hero Section --- */
        .l-hero {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 100px 5%;
          min-height: 85vh;
          background: linear-gradient(135deg, #f9faff 0%, #ffffff 100%);
          position: relative;
        }
        .l-hero-content {
          flex: 1;
          max-width: 600px;
          z-index: 2;
        }
        .l-hero-title {
          font-size: 3.5rem;
          font-weight: 800;
          color: #2D3436;
          line-height: 1.15;
          margin-bottom: 24px;
        }
        .l-hero-title span {
          color: #6C63FF;
        }
        .l-hero-subtitle {
          font-size: 1.15rem;
          color: #636E72;
          line-height: 1.6;
          margin-bottom: 40px;
        }
        .l-hero-actions {
          display: flex;
          gap: 16px;
        }
        .l-hero-image-wrap {
          flex: 1;
          display: flex;
          justify-content: flex-end;
          align-items: center;
          position: relative;
        }
        .l-hero-image {
          max-width: 90%;
          width: 500px;
          object-fit: cover;
          border-radius: 32px;
          border: 6px solid #ffffff;
          box-shadow: 0 25px 50px rgba(108, 99, 255, 0.15);
          transform: perspective(1000px) rotateY(-5deg);
          transition: transform 0.5s ease;
        }
        .l-hero-image:hover {
          transform: perspective(1000px) rotateY(0deg) translateY(-10px);
        }

        /* --- Sections --- */
        .l-section {
          padding: 100px 5%;
        }
        .l-section-alt {
          background-color: #fafbfc;
          border-top: 1px solid #f1f2f6;
          border-bottom: 1px solid #f1f2f6;
        }
        .l-section-header {
          text-align: center;
          max-width: 700px;
          margin: 0 auto 60px auto;
        }
        .l-section-title {
          font-size: 2.5rem;
          font-weight: 700;
          color: #2D3436;
          margin-bottom: 20px;
        }
        .l-section-subtitle {
          font-size: 1.1rem;
          color: #636E72;
          line-height: 1.6;
        }

        /* --- Info Grid (How it works) --- */
        .l-grid-3 {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 40px;
          max-width: 1200px;
          margin: 0 auto;
        }
        .l-info-card {
          text-align: center;
          padding: 30px;
        }
        .l-info-icon {
          width: 70px;
          height: 70px;
          background: rgba(108, 99, 255, 0.1);
          color: #6C63FF;
          border-radius: 20px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 24px auto;
        }
        .l-info-title {
          font-size: 1.3rem;
          font-weight: 700;
          margin-bottom: 16px;
        }
        .l-info-text {
          color: #636E72;
          line-height: 1.6;
        }

        /* --- Ecosystem Cards --- */
        .l-eco-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
          gap: 30px;
          max-width: 1200px;
          margin: 0 auto;
        }
        .l-eco-card {
          background: #fff;
          border: 1px solid #f1f2f6;
          border-radius: 24px;
          padding: 40px 30px;
          box-shadow: 0 10px 30px rgba(0,0,0,0.03);
          transition: transform 0.3s, box-shadow 0.3s;
          display: flex;
          flex-direction: column;
        }
        .l-eco-card:hover {
          transform: translateY(-8px);
          box-shadow: 0 20px 40px rgba(108, 99, 255, 0.08);
          border-color: rgba(108, 99, 255, 0.2);
        }
        .l-eco-icon {
          color: #2D3436;
          margin-bottom: 24px;
        }
        .l-eco-title {
          font-size: 1.4rem;
          font-weight: 700;
          margin-bottom: 16px;
        }
        .l-eco-text {
          color: #636E72;
          line-height: 1.6;
          margin-bottom: 30px;
          flex: 1;
        }

        /* --- Wearables --- */
        .l-wearables-wrap {
          display: flex;
          flex-wrap: wrap;
          gap: 40px;
          justify-content: center;
          max-width: 1000px;
          margin: 0 auto;
        }
        .l-wearable-box {
          flex: 1;
          min-width: 300px;
          background: #fff;
          border: 1px solid #f1f2f6;
          border-radius: 20px;
          padding: 30px;
        }
        .l-wearable-header {
          font-size: 1.2rem;
          font-weight: 700;
          margin-bottom: 24px;
          display: flex;
          align-items: center;
          gap: 10px;
        }
        .l-wearable-header.current { color: #3A86FF; }
        .l-wearable-header.future { color: #FF006E; }
        
        .l-w-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        .l-w-item {
          display: flex;
          align-items: center;
          gap: 16px;
          padding: 16px;
          background: #f9faff;
          border-radius: 12px;
          border: 1px solid #f1f2f6;
        }
        .l-w-item-text {
          font-weight: 600;
          color: #2D3436;
        }

        /* --- Footer --- */
        .l-footer {
          padding: 60px 5% 40px;
          background: #2D3436;
          color: #fff;
          text-align: center;
        }
        .l-footer-logo {
          font-size: 2rem;
          font-family: 'Lexend', sans-serif;
          font-weight: 800;
          color: #fff;
          margin-bottom: 20px;
        }
        .l-footer-text {
          color: #94a3b8;
          max-width: 500px;
          margin: 0 auto 40px auto;
          line-height: 1.6;
        }
        .l-footer-bottom {
          border-top: 1px solid rgba(255,255,255,0.1);
          padding-top: 20px;
          color: #94a3b8;
          font-size: 0.9rem;
          display: flex;
          justify-content: space-between;
        }

        @media (max-width: 968px) {
          .l-hero { flex-direction: column; text-align: center; padding-top: 140px; }
          .l-hero-actions { justify-content: center; }
          .l-hero-image-wrap { margin-top: 60px; justify-content: center; }
          .l-nav-links { display: none; }
        }
      `}</style>

      {/* ──── Navbar ──── */}
      <nav className="l-navbar">
        <div className="sidebar-logo" style={{ cursor: 'pointer', margin: 0, padding: 0 }} onClick={() => navigate('/')}>
          <Logo />
        </div>
        <div className="l-nav-links">
          <a onClick={() => handleScroll('about-us')}>About Us</a>
          <a onClick={() => handleScroll('about')}>Our Mission</a>
          <a onClick={() => handleScroll('how-it-works')}>How it Works</a>
          <a onClick={() => handleScroll('ecosystem')}>Ecosystem</a>
          <a onClick={() => handleScroll('technology')}>Technology</a>
        </div>
        <div style={{ display: 'flex', gap: '16px' }}>
          <button className="l-btn l-btn-outline" onClick={() => navigate('/login')}>
            Log In
          </button>
        </div>
      </nav>

      {/* ──── Hero ──── */}
      <section className="l-hero">
        <motion.div 
          className="l-hero-content"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={staggerContainer}
        >
          <motion.h1 variants={fadeInUp} className="l-hero-title">
            Adaptive Education for <span>Special Needs</span>
          </motion.h1>
          <motion.p variants={fadeInUp} className="l-hero-subtitle">
            An Egyptian initiative delivering a deeply personalized, stress-free learning environment. Baseet dynamically adapts to every student's emotional and cognitive state in real-time.
          </motion.p>
          <motion.div variants={fadeInUp} className="l-hero-actions">
            <button className="l-btn l-btn-primary" onClick={() => navigate('/register')}>
              Join the Waitlist <ArrowRight size={20} />
            </button>
            <button className="l-btn l-btn-outline" onClick={() => navigate('/login')}>
              Log In
            </button>
          </motion.div>
        </motion.div>

        <motion.div 
          className="l-hero-image-wrap"
          initial={{ opacity: 0, scale: 0.9, y: 30 }}
          whileInView={{ opacity: 1, scale: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          {/* Using the cute Baseet studying image as it fits an EdTech vibe better than a floating head */}
          <img src={require("../../assets/baseet_studying_banner.png")} className="l-hero-image" alt="Student learning with Baseet" />
        </motion.div>
      </section>

      {/* ──── About Us ──── */}
      <section id="about-us" className="l-section">
        <motion.div className="l-section-header" initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeInUp}>
          <h2 className="l-section-title">About Us</h2>
          <p className="l-section-subtitle">
            We are a passionate team dedicated to revolutionizing education in Egypt. 
            Baseet was born out of a deep desire to provide children with special needs the individualized, empathetic learning environment they deserve. 
            Our project bridges the gap between advanced AI orchestrators, wearable biometrics, and engaging digital content to empower both students and educators.
          </p>
        </motion.div>
      </section>

      {/* ──── About Mission ──── */}
      <section id="about" className="l-section l-section-alt">
        <motion.div className="l-section-header" initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeInUp}>
          <h2 className="l-section-title">Why Baseet?</h2>
          <p className="l-section-subtitle">
            Traditional, one-size-fits-all education often leaves students with special needs feeling overwhelmed or disconnected. 
            Baseet was built in Egypt to solve this by creating an AI orchestrator that acts as an empathetic tutor—detecting frustration before it happens and pivoting the lesson strategy instantly.
          </p>
        </motion.div>
      </section>

      {/* ──── How It Works ──── */}
      <section id="how-it-works" className="l-section">
        <motion.div className="l-section-header" initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeInUp}>
          <h2 className="l-section-title">How It Works</h2>
          <p className="l-section-subtitle">
            A seamless loop of data, analysis, and educational adaptation.
          </p>
        </motion.div>

        <motion.div className="l-grid-3" initial="hidden" whileInView="visible" viewport={{ once: true }} variants={staggerContainer}>
          <motion.div className="l-info-card" variants={fadeInUp}>
            <div className="l-info-icon"><Activity size={32} /></div>
            <h3 className="l-info-title">1. Connect</h3>
            <p className="l-info-text">
              Students wear comfortable, non-intrusive biometrics sensors (like smartwatches) that monitor physiological indicators such as heart rate and skin response.
            </p>
          </motion.div>
          <motion.div className="l-info-card" variants={fadeInUp}>
            <div className="l-info-icon"><BrainCircuit size={32} /></div>
            <h3 className="l-info-title">2. Analyze</h3>
            <p className="l-info-text">
              Our AI Orchestrator processes this data in real-time to accurately determine the student's current cognitive load, stress, and engagement levels.
            </p>
          </motion.div>
          <motion.div className="l-info-card" variants={fadeInUp}>
            <div className="l-info-icon"><Layers size={32} /></div>
            <h3 className="l-info-title">3. Adapt</h3>
            <p className="l-info-text">
              The platform dynamically adjusts lesson difficulty, changes teaching methods, or triggers guided breaks to maintain the optimal learning zone.
            </p>
          </motion.div>
        </motion.div>
      </section>

      {/* ──── Ecosystem ──── */}
      <section id="ecosystem" className="l-section l-section-alt">
        <motion.div className="l-section-header" initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeInUp}>
          <h2 className="l-section-title">The Baseet Ecosystem</h2>
          <p className="l-section-subtitle">
            A fully integrated suite of applications connecting students, parents, teachers, and supervisors across multiple platforms.
          </p>
        </motion.div>

        <motion.div className="l-eco-grid" initial="hidden" whileInView="visible" viewport={{ once: true }} variants={staggerContainer}>
          <motion.div className="l-eco-card" variants={fadeInUp}>
            <Laptop size={40} className="l-eco-icon" />
            <h3 className="l-eco-title">Web Platform</h3>
            <p className="l-eco-text">
              The core hub. Students access interactive lessons, teachers manage curriculum and track progress, and supervisors oversee organization-wide health and analytics.
            </p>
            <div>
              <a href="#" className="l-btn-demo"><PlayCircle size={16} style={{display: 'inline', verticalAlign: 'middle', marginRight: 4}}/> View Demo</a>
            </div>
          </motion.div>

          <motion.div className="l-eco-card" variants={fadeInUp}>
            <MonitorPlay size={40} className="l-eco-icon" />
            <h3 className="l-eco-title">Desktop VR Game</h3>
            <p className="l-eco-text">
              An immersive, distraction-free 3D environment. Students explore concepts through engaging, interactive gamification built specifically for neurodivergent focus.
            </p>
            <div>
              <a href="#" className="l-btn-demo"><PlayCircle size={16} style={{display: 'inline', verticalAlign: 'middle', marginRight: 4}}/> View Demo</a>
            </div>
          </motion.div>

          <motion.div className="l-eco-card" variants={fadeInUp}>
            <Smartphone size={40} className="l-eco-icon" />
            <h3 className="l-eco-title">Caretaker Mobile App</h3>
            <p className="l-eco-text">
              Real-time peace of mind. Parents and caretakers receive instant alerts regarding the student's emotional state, milestone achievements, and learning session summaries.
            </p>
            <div>
              <a href="#" className="l-btn-demo"><PlayCircle size={16} style={{display: 'inline', verticalAlign: 'middle', marginRight: 4}}/> View Demo</a>
            </div>
          </motion.div>
        </motion.div>
      </section>

      {/* ──── Wearables ──── */}
      <section id="technology" className="l-section">
        <motion.div className="l-section-header" initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeInUp}>
          <h2 className="l-section-title">Hardware Integrations</h2>
          <p className="l-section-subtitle">
            Seamless integration with biometrics to feed our AI orchestrator with highly accurate emotional data.
          </p>
        </motion.div>

        <motion.div className="l-wearables-wrap" initial="hidden" whileInView="visible" viewport={{ once: true }} variants={staggerContainer}>
          <motion.div className="l-wearable-box" variants={fadeInUp}>
            <h4 className="l-wearable-header current"><ShieldCheck size={24} /> Currently Supported</h4>
            <div className="l-w-list">
              <div className="l-w-item">
                <HeartPulse size={24} color="#FF006E" />
                <span className="l-w-item-text">Heart Rate Sensors</span>
              </div>
              <div className="l-w-item">
                <Activity size={24} color="#3A86FF" />
                <span className="l-w-item-text">Galvanic Skin Response (GSR)</span>
              </div>
              <div className="l-w-item">
                <Thermometer size={24} color="#FFBE0B" />
                <span className="l-w-item-text">Temperature Sensors</span>
              </div>
              <div className="l-w-item">
                <Camera size={24} color="#6C63FF" />
                <span className="l-w-item-text">Camera for Facial Expressions</span>
              </div>
            </div>
          </motion.div>

          <motion.div className="l-wearable-box" variants={fadeInUp}>
            <h4 className="l-wearable-header future"><Eye size={24} /> Future Roadmap</h4>
            <div className="l-w-list">
              <div className="l-w-item" style={{opacity: 0.7}}>
                <BrainCircuit size={24} color="#2D3436" />
                <span className="l-w-item-text">EEG Brainwave Headbands</span>
              </div>
              <div className="l-w-item" style={{opacity: 0.7}}>
                <Eye size={24} color="#2D3436" />
                <span className="l-w-item-text">Eye-Tracking Hardware</span>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </section>

      {/* ──── Footer ──── */}
      <footer className="l-footer">
        <div className="l-footer-logo">Baseet</div>
        <p className="l-footer-text">
          An Egyptian EdTech initiative dedicated to revolutionizing education for special needs students through artificial intelligence, adaptive learning, and empathy.
        </p>
        <div className="l-footer-bottom">
          <span>&copy; {new Date().getFullYear()} Baseet. All rights reserved.</span>
          <div style={{display: 'flex', gap: '20px'}}>
            <a href="#" style={{color: '#94a3b8', textDecoration: 'none'}}>Privacy Policy</a>
            <a href="#" style={{color: '#94a3b8', textDecoration: 'none'}}>Terms of Service</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
