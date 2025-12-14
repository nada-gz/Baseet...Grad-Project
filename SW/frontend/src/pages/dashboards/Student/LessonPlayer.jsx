import { useParams } from "react-router-dom";

export default function LessonPlayer() {
  const { lessonId } = useParams();

  return (
    <div className="lesson-player">
      <h1>Lesson {lessonId}</h1>

      {/* Video Section */}
      <div className="lesson-video">
        VIDEO PLAYER HERE
      </div>

      {/* Controls */}
      <div className="lesson-controls">
        <button>Play</button>
        <button>Pause</button>
        <button>Record</button>
      </div>

      {/* Q&A */}
      <div className="lesson-qa">
        <textarea placeholder="Ask Baseet or answer a question..." />
        <button>Send</button>
      </div>
    </div>
  );
}
