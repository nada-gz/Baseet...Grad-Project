from pydantic import BaseModel, Field
from typing import List, Any

# ==========================================
# 1. INCOMING DATA SCHEMAS (Inputs from Backend)
# ==========================================
class EngagementModelInput(BaseModel):
    engagement_score_percentage: int
    engagement_state: str  # e.g., "Highly Engaged", "Distracted"

class StressModelInput(BaseModel):
    average_heart_rate: int
    average_gsr: float
    stress_classification: str  # e.g., "Calm", "Stressed"
    stress_peaks_count: int

class WebTrackerInput(BaseModel):
    video_watch_time_minutes: float
    chat_interaction_count: int
    lessons_completed: int
    current_topic: str

class SessionTelemetry(BaseModel):
    """The master object combining all 3 data sources your backend will pass to the AI."""
    student_id: int
    student_name: str
    organization_id: str = "school_01"
    class_level: str = "Grade 1-A"
    engagement_data: EngagementModelInput
    stress_data: StressModelInput
    website_tracking_data: WebTrackerInput

# ==========================================
# 2. OUTPUT SCHEMAS (Dashboards)
# ==========================================
# --- Student Schema Sub-models ---
class Identity(BaseModel):
    id: int
    name: str
    level: str

class TimeMetrics(BaseModel):
    hours_today: float
    hours_this_week: float
    hours_this_month: float
    focus_percentage: int

class Stats(BaseModel):
    total_xp: int
    current_streak: int
    lessons_completed_this_week: int
    achievements_unlocked: int

class RadarData(BaseModel):
    subject: str
    score: int
    fullMark: int = 100

class MoodData(BaseModel):
    time: str
    emoji: str
    label: str

class DailyGoal(BaseModel):
    progress: int
    target: int
    message: str

class StudentReport(BaseModel):
    role: str = "student"
    identity: Identity
    time_metrics: TimeMetrics
    stats: Stats
    radar_chart_data: List[RadarData]
    mood_timeline: List[MoodData]
    daily_goal: DailyGoal

# --- Teacher Schema Sub-models ---
class UsageHours(BaseModel):
    today: float
    week: float
    month: float

class EngagementProfile(BaseModel):
    focused: int
    stressed: int
    distracted: int

class TimeAnalytics(BaseModel):
    usage_hours: UsageHours
    engagement_profile: EngagementProfile

class PerformanceSummary(BaseModel):
    avg_accuracy: int
    lessons_completed: int
    assignments_submitted: int

class StoryGrammar(BaseModel):
    setting: int
    problem: int
    event: int
    response: int
    consequence: int

class ConnectiveUsage(BaseModel):
    word: str
    count: int

class SkillGapAnalysis(BaseModel):
    story_grammar: StoryGrammar
    connective_usage: List[ConnectiveUsage]

class BiometricData(BaseModel):
    timestamp: str
    hr: int
    gsr: float
    status: str
    task: str

class AiOrchestratorLogs(BaseModel):
    total_prompts_needed: int
    autonomy_score: int
    preferred_topic: str

class TeacherReport(BaseModel):
    role: str = "teacher"
    student_id: int
    time_analytics: TimeAnalytics
    performance_summary: PerformanceSummary
    skill_gap_analysis: SkillGapAnalysis
    biometric_correlation_chart: List[BiometricData]
    ai_orchestrator_logs: AiOrchestratorLogs

# --- Parent Schema Sub-models ---
class TimeWellSpent(BaseModel):
    study_hours_today: str
    focus_score: str
    calm_percentage: str

class DailySnapshot(BaseModel):
    overall_mood: str
    energy_level: str
    social_engagement: str

class JourneyMap(BaseModel):
    stage: str
    activity: str
    success: Any

class SentimentTrend(BaseModel):
    values: List[int]
    labels: List[str]

class ParentToolkit(BaseModel):
    discuss_today: str
    suggested_activity: str
    new_words: List[str]

class ParentReport(BaseModel):
    role: str = "parent"
    child_name: str
    time_well_spent: TimeWellSpent
    daily_snapshot: DailySnapshot
    learning_journey_map: List[JourneyMap]
    sentiment_trend: SentimentTrend
    parent_toolkit: ParentToolkit

# --- Supervisor Schema Sub-models ---
class OrgTimeMetrics(BaseModel):
    avg_hours_per_student_daily: float
    total_hours_this_month: int
    org_focus_avg: int
    org_stress_avg: int

class KpiCards(BaseModel):
    total_students: int
    total_lessons_completed: int
    system_uptime: float
    avg_org_progress: int

class ClassComparison(BaseModel):
    class_name: str = Field(alias="class") 
    progress: int
    stress_index: int

class ResourceUtil(BaseModel):
    module: str
    usage: int

class SafetyWellness(BaseModel):
    stress_alerts_weekly: int
    resolved_cases: int
    critical_alerts: int

class SupervisorReport(BaseModel):
    role: str = "supervisor"
    org_id: str
    org_time_metrics: OrgTimeMetrics
    kpi_cards: KpiCards
    class_comparison_chart: List[ClassComparison]
    resource_utilization: List[ResourceUtil]
    safety_and_wellness: SafetyWellness