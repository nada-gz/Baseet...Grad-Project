import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { BookOpen, FileText } from 'lucide-react';
import '../../../styles/index.css';

export default function StudentEducationalProgress() {
    const { studentId } = useParams();
    const navigate = useNavigate();

    // Mock data for now (will replace with API fetch later)
    const student = { username: "Nada Alaa", email: "nada@example.com" };
    const mockProgress = [
        {
            level: 1,
            milestones: [
                {
                    id: 1,
                    number: 1,
                    lessons: [
                        { id: 101, title: "Intro to Algorithms", status: "completed", score: 95 },
                        { id: 102, title: "Variables", status: "in-progress" }
                    ]
                }
            ]
        }
    ];

    return (
        <div className="lesson-prep-container">
            <div className="flex items-center mb-6">
                <button onClick={() => navigate(-1)} className="btn btn-secondary mr-4">
                    &larr; Back
                </button>
                <h1 className="text-2xl font-bold">Academic Progress: {student.username}</h1>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                    <BookOpen className="text-blue-500" /> Course Progress
                </h2>

                {/* Placeholder for future real data implementation */}
                <div className="space-y-4">
                    {mockProgress.map(level => (
                        <div key={level.level} className="border p-4 rounded">
                            <h3 className="font-bold text-lg mb-2">Level {level.level}</h3>
                            {level.milestones.map(m => (
                                <div key={m.id} className="ml-4">
                                    <h4 className="font-medium text-gray-700">Milestone {m.number}</h4>
                                    <ul className="list-disc ml-6 mt-2">
                                        {m.lessons.map(l => (
                                            <li key={l.id} className="mb-1">
                                                <span className="font-semibold">{l.title}</span>
                                                <span className={`ml-2 text-xs px-2 py-0.5 rounded ${l.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                                                    {l.status}
                                                </span>
                                                {l.score && <span className="ml-2 text-sm text-gray-600">Score: {l.score}%</span>}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            ))}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
