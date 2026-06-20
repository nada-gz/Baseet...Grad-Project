<div align="center">
  
# 🌟 BASEET (بسيط)
**An Agentic AI & Sensor-Integrated Solution for Adaptive Special Education**

[![Live Deployment](https://img.shields.io/badge/Live_Deployment-baseet.tech-success?style=for-the-badge&logo=vercel)](https://baseet.tech)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

</div>

<br />

Welcome to the official repository for **Baseet**, a comprehensive technological ecosystem designed to bridge the gap between clinical therapy, home-based learning, and classroom education for children with Autism Spectrum Disorder (ASD). 

> **Important**: This README serves as a technical guide to navigate, install, and deploy the repository. For the full academic context, literature review, and evaluation metrics, please refer to our accompanying Graduation Thesis.

---

## 👥 The Team
This project was developed as a Senior Project II for the Bachelor’s Degree in Information Technology and Computer Science at **Nile University** (Spring 2026), under the supervision of **Dr. Noha Gamal Eldin**.

* **Hana Elgabry** – CV Engineer
* **Khetam Mohamed** – AI R & D
* **Mona Elsayed** – Software Developer
* **Nada Zaki** – Software Developer
* **Noor Alzoghby** – Agentic AI Developer
* **Zeina Ahmed** – Agentic AI Developer

---

## 🏗️ Repository Structure

The project is architected as a modular ecosystem. Below is a guide to navigating the codebase:

```text
Grad-Project/
│
├── SW/
│   ├── frontend/        # React.js web application (Dashboards for Student, Teacher, Parent, Supervisor)
│   └── backend/         # FastAPI Python server (REST API, WebSockets, Database, AI Orchestration)
│       └── services/ai/ # Includes Video Generation Agent, Explanation Agent, Report Agent, IOT, TTS, STT, and STS
│
├── docs/                # Architecture diagrams, API specs, and project documentation
├── deploy.sh            # Production deployment script for baseet.tech
└── README.md            # You are here!
```

---

## 🛠️ Technology Stack

**Frontend Layer**
* **Framework**: React.js (Create React App)
* **Styling**: Tailwind CSS
* **Animations & UI**: Framer Motion, Lucide React
* **Data Visualization**: Recharts

**Backend & Data Layer**
* **Framework**: FastAPI (Python)
* **Database**: PostgreSQL with SQLModel (ORM)
* **Real-time & IoT**: WebSockets, MQTT (gmqtt)
* **Security**: JWT Authentication, bcrypt, python-jose

**AI & ML Layer**
* **Large Language Models**: Google Gemini, OpenAI
* **Retrieval-Augmented Generation (RAG)**: ChromaDB, SentenceTransformers, PyMuPDF
* **Speech Processing**: Custom TTS pipelines, Egyptian Arabic STT
* **Computer Vision**: OpenCV, Deep Learning pipelines for OCR and biometric mapping

---

## 🚀 Getting Started (Local Development)

Follow these steps to set up the Baseet ecosystem on your local machine for development and testing.

### 1. Prerequisites
* **Node.js** (v18+ recommended)
* **Python** (3.10+ recommended)
* **PostgreSQL** (running locally or via Docker)
* **Git**

### 2. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd SW/backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure your environment variables:
   * Create a `.env` file in the `SW/backend` directory.
   * Add your database URL, JWT secret keys, and AI API keys (Google Gemini, OpenAI, etc.).
5. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   *The backend will now be running at `http://localhost:8000`. You can view the auto-generated API documentation at `http://localhost:8000/docs`.*

### 3. Frontend Setup
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd SW/frontend
   ```
2. Install the Node dependencies:
   ```bash
   npm install
   ```
3. Start the React development server:
   ```bash
   npm start
   ```
   *The web application will open automatically at `http://localhost:3000`.*

---

## 🌍 Production Deployment

The platform is deployed live at **[https://baseet.tech](https://baseet.tech)**. 

The production environment is hosted on an Ubuntu VPS, utilizing **Nginx** as a reverse proxy and **PM2** for process management.

To deploy updates to the production server:
1. Merge your changes into the `main` branch.
2. SSH into the production server.
3. Run the automated deployment script located at the root of the repository:
   ```bash
   bash deploy.sh
   ```
   *This script will automatically pull the latest changes, rebuild the optimized React frontend, install any new Python dependencies, and restart the FastAPI PM2 process seamlessly.*

---

## 🔒 Security & Privacy Notice
Given the sensitive nature of the data handled by Baseet (pediatric emotional states, physiological signals, and academic progress), the system enforces strict role-based access control (RBAC). Passwords are cryptographically hashed, and endpoints are protected via JSON Web Tokens (JWT). All real-world testing data is anonymized and pseudonymized in compliance with standard research ethics protocols.

---

<div align="center">
  <i>"Empowering neurodivergent learners through empathy, intelligence, and technology."</i>
</div>
