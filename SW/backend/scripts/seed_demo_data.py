import sys
import os
from datetime import datetime, timedelta
import random

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlmodel import Session, select, text
from db.database import engine
from models.user import User, RoleEnum
from models.student import Student
from models.parent import Parent
from models.classroom import Classroom, ClassroomCourseLink
from models.teacher_student_link import TeacherStudentLink
from models.course import Course
from models.lesson import Lesson
from models.material import Material
from models.assignment import Assignment
from models.submission import Submission
from models.submission_file import SubmissionFile
from models.feedback import Feedback
from models.iot_reading import IOTReading
from models.class_level import ClassLevel
from models.content_course import ContentCourse
from models.content_lesson import ContentLesson
from models.content_material import ContentMaterial
from models.content_assignment import ContentAssignment
from models.content_assignment_file import ContentAssignmentFile
from models.milestone import Milestone
from models.quiz import Quiz
from models.student_math_mastery import StudentMathMastery
from models.student_flag import StudentFlag
from models.supervisor_report import SupervisorReport
from models.supervisor_message import SupervisorMessage
from models.parent_notification import ParentNotification
from models.ask_baseet import AskBaseet
from models.log import Log
from utils.auth import hash_password

def cleanup_demo_data(session: Session):
    """
    Selectively deletes previous demo data (users starting with demo_ or emails ending in @demo.com)
    along with all linked student, parent, submission, telemetry, flag, and notification records.
    All custom data (e.g., student nada, teacher/parent nada, supervisor super) is left completely untouched.
    """
    print("🧹 Starting selective cleanup of old demo data...")
    
    # Get all demo users
    demo_users = session.exec(select(User).where((User.username.like("demo_%")) | (User.email.like("%@demo.com")))).all()
    demo_user_ids = [u.id for u in demo_users]
    
    if not demo_user_ids:
        print("   No old demo users found. Skipping cleanup.")
        return

    # Find demo student IDs
    demo_students = session.exec(select(Student).where(Student.user_id.in_(demo_user_ids))).all()
    demo_student_ids = [s.id for s in demo_students]
    
    # Find demo parent IDs
    demo_parents = session.exec(select(Parent).where(Parent.user_id.in_(demo_user_ids))).all()
    demo_parent_ids = [p.id for p in demo_parents]

    print(f"   Found {len(demo_user_ids)} demo users, {len(demo_student_ids)} demo students, and {len(demo_parents)} demo parents to clean up.")

    if demo_student_ids:
        # Delete student-specific linked data
        session.exec(text("DELETE FROM iot_readings WHERE student_id IN :ids").bindparams(ids=tuple(demo_student_ids)))
        session.exec(text("DELETE FROM quiz_attempts WHERE quiz_id IN (SELECT id FROM quizzes WHERE student_id IN :ids)").bindparams(ids=tuple(demo_student_ids)))
        session.exec(text("DELETE FROM quizzes WHERE student_id IN :ids").bindparams(ids=tuple(demo_student_ids)))
        session.exec(text("DELETE FROM linking_codes WHERE student_id IN :ids").bindparams(ids=tuple(demo_student_ids)))
        session.exec(text("DELETE FROM student_reports WHERE student_id IN :ids").bindparams(ids=tuple(demo_student_ids)))
        session.exec(text("DELETE FROM student_flags WHERE student_id IN :ids").bindparams(ids=tuple(demo_student_ids)))
        session.exec(text("DELETE FROM supervisor_reports WHERE student_id IN :ids").bindparams(ids=tuple(demo_student_ids)))
        session.exec(text("DELETE FROM supervisormessage WHERE student_id IN :ids").bindparams(ids=tuple(demo_student_ids)))
        session.exec(text("DELETE FROM ask_baseet WHERE student_id IN :ids").bindparams(ids=tuple(demo_student_ids)))
        session.exec(text("DELETE FROM student_math_mastery WHERE student_id IN :ids").bindparams(ids=tuple(demo_student_ids)))
        
        # Delete feedback and submission files linked to demo student submissions
        session.exec(text("DELETE FROM feedback WHERE submission_id IN (SELECT id FROM submissions WHERE student_id IN :ids)").bindparams(ids=tuple(demo_student_ids)))
        session.exec(text("DELETE FROM submission_files WHERE submission_id IN (SELECT id FROM submissions WHERE student_id IN :ids)").bindparams(ids=tuple(demo_student_ids)))
        session.exec(text("DELETE FROM submissions WHERE student_id IN :ids").bindparams(ids=tuple(demo_student_ids)))
        
        # Delete assignments and materials linked to demo student lessons
        session.exec(text("DELETE FROM assignments WHERE lesson_id IN (SELECT id FROM lessons WHERE student_id IN :ids)").bindparams(ids=tuple(demo_student_ids)))
        session.exec(text("DELETE FROM materials WHERE lesson_id IN (SELECT id FROM lessons WHERE student_id IN :ids)").bindparams(ids=tuple(demo_student_ids)))
        session.exec(text("DELETE FROM log_table WHERE topic_id IN (SELECT id FROM lessons WHERE student_id IN :ids)").bindparams(ids=tuple(demo_student_ids)))
        session.exec(text("DELETE FROM lessons WHERE student_id IN :ids").bindparams(ids=tuple(demo_student_ids)))
        session.exec(text("DELETE FROM milestones WHERE student_id IN :ids").bindparams(ids=tuple(demo_student_ids)))
        session.exec(text("DELETE FROM teacher_student_links WHERE student_id IN :ids").bindparams(ids=tuple(demo_student_ids)))

    if demo_parent_ids:
        session.exec(text("DELETE FROM parent_notifications WHERE parent_id IN :ids").bindparams(ids=tuple(demo_parent_ids)))

    # Delete teacher links for demo teachers
    session.exec(text("DELETE FROM teacher_student_links WHERE teacher_id IN :ids").bindparams(ids=tuple(demo_user_ids)))

    # Delete main profile records
    if demo_student_ids:
        session.exec(text("DELETE FROM students WHERE id IN :ids").bindparams(ids=tuple(demo_student_ids)))
    if demo_parent_ids:
        session.exec(text("DELETE FROM parents WHERE id IN :ids").bindparams(ids=tuple(demo_parent_ids)))

    # Delete classroom links and classrooms that are demo-related
    demo_class = session.exec(select(Classroom).where(Classroom.name == "Demo Class 1A")).first()
    if demo_class:
        session.exec(text("DELETE FROM classroom_course_links WHERE classroom_id = :cid").bindparams(cid=demo_class.id))
        session.exec(text("DELETE FROM classrooms WHERE id = :cid").bindparams(cid=demo_class.id))
        
    demo_level = session.exec(select(ClassLevel).where(ClassLevel.name == "Demo Level 1")).first()
    if demo_level:
        session.exec(text("DELETE FROM class_levels WHERE id = :lid").bindparams(lid=demo_level.id))

    # Finally delete the users
    session.exec(text("DELETE FROM users WHERE id IN :ids").bindparams(ids=tuple(demo_user_ids)))
    
    session.commit()
    print("   Cleanup of old demo data finished successfully.")

def reset_db_sequences(session: Session):
    """
    Resets all PostgreSQL serial sequences to the maximum ID in the corresponding table
    to avoid primary key duplicate key unique violation errors.
    """
    print("🔄 Syncing PostgreSQL primary key sequences...")
    tables = [
        "users", "students", "parents", "class_levels", "classrooms",
        "courses", "content_courses", "lessons", "content_lessons",
        "materials", "content_materials", "assignments", "content_assignments",
        "submissions", "submission_files", "feedback", "parent_notifications",
        "quizzes", "student_flags", "supervisor_reports", "supervisormessage",
        "ask_baseet", "log_table", "milestones", "linking_codes", "student_reports",
        "iot_readings"
    ]
    for table in tables:
        try:
            # Sync sequence to the maximum ID currently in table (or 1 if table is empty)
            session.exec(text(f"""
                SELECT setval(
                    pg_get_serial_sequence('{table}', 'id'),
                    coalesce((SELECT max(id) FROM {table}), 1)
                )
            """))
            session.commit()
        except Exception as e:
            session.rollback()
            # print(f"   Skipped resetting sequence for table {table}: {e}")

def seed_demo_data():
    with Session(engine) as session:
        print("🌱 Starting database seeding process...")

        # 1. Cleanup old demo data to ensure a fresh, consistent seed
        cleanup_demo_data(session)

        # 2. Reset database sequences to fix primary key discrepancies
        reset_db_sequences(session)

        # 3. Re-create Level & Classroom
        level = ClassLevel(name="Demo Level 1")
        session.add(level)
        session.commit()
        session.refresh(level)

        classroom = Classroom(name="Demo Class 1A", level_id=level.id)
        session.add(classroom)
        session.commit()
        session.refresh(classroom)

        # 4. Create Supervisor
        supervisor_user = User(
            username="demo_supervisor",
            email="supervisor@demo.com",
            hashed_password=hash_password("password123"),
            role=RoleEnum.supervisor
        )
        session.add(supervisor_user)

        # 5. Create Teachers
        teacher1 = User(
            username="demo_teacher_1",
            email="teacher1@demo.com",
            hashed_password=hash_password("password123"),
            role=RoleEnum.teacher
        )
        teacher2 = User(
            username="demo_teacher_2",
            email="teacher2@demo.com",
            hashed_password=hash_password("password123"),
            role=RoleEnum.teacher
        )
        session.add(teacher1)
        session.add(teacher2)
        session.commit()
        session.refresh(teacher1)
        session.refresh(teacher2)

        # Assign Teacher 1 to the demo classroom
        classroom.teacher_id = teacher1.id
        session.add(classroom)
        session.commit()

        # 6. Create Parents
        parent1_user = User(
            username="demo_parent_1",
            email="parent1@demo.com",
            hashed_password=hash_password("password123"),
            role=RoleEnum.parent
        )
        parent2_user = User(
            username="demo_parent_2",
            email="parent2@demo.com",
            hashed_password=hash_password("password123"),
            role=RoleEnum.parent
        )
        session.add(parent1_user)
        session.add(parent2_user)
        session.commit()
        session.refresh(parent1_user)
        session.refresh(parent2_user)

        parent1 = Parent(user_id=parent1_user.id)
        parent2 = Parent(user_id=parent2_user.id)
        session.add(parent1)
        session.add(parent2)
        session.commit()
        session.refresh(parent1)
        session.refresh(parent2)

        # 7. Create Demo Students
        student_profiles = [
            {"username": "demo_student_1", "email": "student1@demo.com", "age": 7, "autism_type": "Sensory Sensitive", "sensitivities": "Loud sounds, blinking lights", "learning_style": "Visual", "engagement": 0.85, "parent": parent1, "teacher": teacher1},
            {"username": "demo_student_2", "email": "student2@demo.com", "age": 8, "autism_type": "Highly Focused", "sensitivities": "Complex text, sudden layout changes", "learning_style": "Visual", "engagement": 0.75, "parent": parent1, "teacher": teacher1},
            {"username": "demo_student_3", "email": "student3@demo.com", "age": 7, "autism_type": "Developing Autonomy", "sensitivities": "Repetitive sounds", "learning_style": "Auditory", "engagement": 0.60, "parent": parent2, "teacher": teacher2},
            {"username": "demo_student_4", "email": "student4@demo.com", "age": 9, "autism_type": "Non-verbal tendencies", "sensitivities": "Bright backgrounds", "learning_style": "Visual/Hands-on", "engagement": 0.70, "parent": parent2, "teacher": teacher2},
            {"username": "demo_student_5", "email": "student5@demo.com", "age": 8, "autism_type": "Sensory Sensitive", "sensitivities": "Loud background sound", "learning_style": "Visual", "engagement": 0.80, "parent": parent2, "teacher": teacher1},
        ]

        students = []
        for p in student_profiles:
            su = User(
                username=p["username"],
                email=p["email"],
                hashed_password=hash_password("password123"),
                role=RoleEnum.student
            )
            session.add(su)
            session.commit()
            session.refresh(su)

            s = Student(
                user_id=su.id,
                age=p["age"],
                autism_type=p["autism_type"],
                sensitivities=p["sensitivities"],
                learning_style=p["learning_style"],
                baseline_engagement=p["engagement"],
                classroom_id=classroom.id,
                parent_id=p["parent"].id,
                difficulty_level=5,
                sensory_settings='{"background_color": "#F0F8FF", "speech_rate": 1.0, "reduce_animations": true}',
                is_flagged=(p["username"] == "demo_student_2") # Student 2 is flagged as stressed
            )
            session.add(s)
            session.commit()
            session.refresh(s)
            students.append(s)

            # Link teacher to student
            session.add(TeacherStudentLink(teacher_id=p["teacher"].id, student_id=s.id))
            
        session.commit()

        # 8. Upsert Content Courses and Arabic Lessons
        courses_curriculum = [
            {
                "course_number": 1,
                "title": "العلوم للمبتدئين",
                "subject": "Science",
                "description": "تعلم أساسيات العلوم، الطبيعة، الفضاء وجسم الإنسان بطرق مبسطة",
                "lessons": [
                    {"milestone": 1, "lesson_num": 1, "title": "البناء الضوئي", "desc": "كيف تصنع النباتات غذاءها باستخدام أشعة الشمس والماء؟", "dur": 25},
                    {"milestone": 1, "lesson_num": 2, "title": "أجزاء النبتة", "desc": "التعرف على الجذور، الساق، الأوراق والأزهار ووظائفها", "dur": 20},
                    {"milestone": 1, "lesson_num": 3, "title": "ماذا تحتاج النبتة لتنمو؟", "desc": "أهمية الضوء والماء والهواء والتربة المناسبة لحياة النبات", "dur": 20},
                    {"milestone": 2, "lesson_num": 1, "title": "المجموعة الشمسية", "desc": "الكواكب الثمانية التي تدور حول الشمس ومواقعها", "dur": 30},
                    {"milestone": 2, "lesson_num": 2, "title": "كوكب الأرض والقمر والشمس", "desc": "دوران الأرض حول نفسها وحول الشمس وتعاقب الليل والنهار", "dur": 25},
                    {"milestone": 2, "lesson_num": 3, "title": "النجوم والمجرات", "desc": "استكشاف النجوم المضيئة والمجموعات النجمية في سمائنا", "dur": 30},
                    {"milestone": 3, "lesson_num": 1, "title": "الحواس الخمس", "desc": "كيف نستخدم حواسنا الخمس لاستكشاف العالم من حولنا", "dur": 20},
                    {"milestone": 3, "lesson_num": 2, "title": "الهيكل العظمي", "desc": "العظام ودورها الهام في حماية أعضائنا الداخلية ودعم حركتنا", "dur": 25},
                ]
            },
            {
                "course_number": 3,
                "title": "أساسيات الرياضيات",
                "subject": "Math",
                "description": "تعلم الأرقام، العد، والعمليات الحسابية البسيطة بطرق ممتعة وتفاعلية",
                "lessons": [
                    {"milestone": 1, "lesson_num": 1, "title": "العد من ١ إلى ١٠", "desc": "تعلم نطق الأرقام وكتابتها وعد المجموعات المختلفة", "dur": 15},
                    {"milestone": 1, "lesson_num": 2, "title": "مقارنة الأعداد", "desc": "التعرف على مفاهيم الأكبر، الأصغر، ويساوي بين الأعداد", "dur": 15},
                    {"milestone": 2, "lesson_num": 1, "title": "الجمع البسيط", "desc": "طريقة جمع رقمين صغيرين معاً للحصول على المجموع الكلي", "dur": 20},
                    {"milestone": 2, "lesson_num": 2, "title": "الطرح البسيط", "desc": "طرح عدد من آخر لإيجاد الباقي بطرق مرئية", "dur": 20},
                ]
            }
        ]

        content_courses_map = {}
        for cdata in courses_curriculum:
            # Check if ContentCourse with this course_number already exists
            cc = session.exec(select(ContentCourse).where(ContentCourse.course_number == cdata["course_number"])).first()
            if cc:
                cc.title = cdata["title"]
                cc.subject = cdata["subject"]
                cc.description = cdata["description"]
                cc.teacher_id = teacher1.id
            else:
                cc = ContentCourse(
                    course_number=cdata["course_number"],
                    title=cdata["title"],
                    subject=cdata["subject"],
                    description=cdata["description"],
                    teacher_id=teacher1.id
                )
            session.add(cc)
            session.commit()
            session.refresh(cc)
            content_courses_map[cdata["course_number"]] = cc

            # Upsert legacy/redundant Course model as well to keep routers working
            legacy_c = session.exec(select(Course).where(Course.title == cdata["title"])).first()
            if not legacy_c:
                legacy_c = Course(title=cdata["title"], subject=cdata["subject"], description=cdata["description"])
                session.add(legacy_c)
                session.commit()

            # Seed Content Lessons
            for ldata in cdata["lessons"]:
                cl = session.exec(select(ContentLesson).where(
                    ContentLesson.course_number == cdata["course_number"],
                    ContentLesson.milestone_number == ldata["milestone"],
                    ContentLesson.lesson_number == ldata["lesson_num"]
                )).first()

                if cl:
                    cl.title = ldata["title"]
                    cl.description = ldata["desc"]
                    cl.duration_minutes = ldata["dur"]
                    cl.teacher_id = teacher1.id
                else:
                    cl = ContentLesson(
                        course_number=cdata["course_number"],
                        milestone_number=ldata["milestone"],
                        lesson_number=ldata["lesson_num"],
                        title=ldata["title"],
                        description=ldata["desc"],
                        duration_minutes=ldata["dur"],
                        teacher_id=teacher1.id
                    )
                session.add(cl)
                session.commit()
                session.refresh(cl)

                # Seed Materials for this Content Lesson if not existing
                m_check = session.exec(select(ContentMaterial).where(ContentMaterial.lesson_id == cl.id)).first()
                if not m_check:
                    session.add(ContentMaterial(
                        lesson_id=cl.id,
                        title=f"فيديو الشرح لدرس: {cl.title}",
                        material_type="video",
                        file_url="https://www.youtube.com/watch?v=demo_video"
                    ))
                    session.add(ContentMaterial(
                        lesson_id=cl.id,
                        title=f"ملخص القراءة لدرس: {cl.title}",
                        material_type="pdf",
                        file_url="/uploads/materials/sample.pdf"
                    ))
                    session.commit()

                # Seed Assignment templates for this Content Lesson if not existing
                a_check = session.exec(select(ContentAssignment).where(ContentAssignment.lesson_id == cl.id)).first()
                if not a_check:
                    ca = ContentAssignment(
                        lesson_id=cl.id,
                        title=f"ورقة العمل التفاعلية لدرس: {cl.title}",
                        description=f"الرجاء إكمال الأنشطة والتمارين المطلوبة لدرس {cl.title}.",
                        assignment_type="pdf",
                        deadline=datetime.utcnow() + timedelta(days=5),
                        file_url=""
                    )
                    session.add(ca)
                    session.commit()
                    session.refresh(ca)

                    # Add file to assignment
                    session.add(ContentAssignmentFile(
                        assignment_id=ca.id,
                        file_name="worksheet.pdf",
                        file_url="/uploads/assignments/worksheet.pdf"
                    ))
                    session.commit()

        # 9. Link Classrooms to Content Courses
        for cc_num, cc in content_courses_map.items():
            # Demo Class
            link_demo = session.exec(select(ClassroomCourseLink).where(
                ClassroomCourseLink.classroom_id == classroom.id,
                ClassroomCourseLink.course_id == cc.id
            )).first()
            if not link_demo:
                session.add(ClassroomCourseLink(classroom_id=classroom.id, course_id=cc.id))
            
            # Ensure "Class A" (Classroom 1) is also linked to Course 1 and 3 (which it is)
            link_class_a = session.exec(select(ClassroomCourseLink).where(
                ClassroomCourseLink.classroom_id == 1,
                ClassroomCourseLink.course_id == cc.id
            )).first()
            if not link_class_a:
                session.add(ClassroomCourseLink(classroom_id=1, course_id=cc.id))
        session.commit()

        # 10. Seed Student Progress & Activity (Lessons, Submissions, Quizzes, Telemetry, and Flags)
        for s_idx, s in enumerate(students):
            # Seed Math Mastery profile
            session.add(StudentMathMastery(
                student_id=s.id,
                subitizing=0.9 - (s_idx * 0.15),
                number_line=0.8 - (s_idx * 0.12),
                place_value=0.7 - (s_idx * 0.15),
                fact_retrieval=0.5 - (s_idx * 0.10),
                word_problems=0.3 - (s_idx * 0.08),
                consecutive_errors=0,
                current_node="subitizing",
                last_updated=datetime.utcnow().isoformat()
            ))

            # Create Milestones for the student
            # Science Milestones
            milestone_sci1 = Milestone(student_id=s.id, course_id=content_courses_map[1].id, title="عالم النباتات", number=1, description="دراسة النبات وأجزائه وعملية البناء الضوئي")
            milestone_sci2 = Milestone(student_id=s.id, course_id=content_courses_map[1].id, title="الفضاء والمجموعة الشمسية", number=2, description="استكشاف الكواكب والنجوم والأرض")
            milestone_sci3 = Milestone(student_id=s.id, course_id=content_courses_map[1].id, title="جسم الإنسان", number=3, description="التعرف على الحواس والهيكل العظمي")
            # Math Milestones
            milestone_math1 = Milestone(student_id=s.id, course_id=content_courses_map[3].id, title="الأرقام والعد", number=1, description="العد من ١ إلى ١٠ ومقارنة الأعداد")
            milestone_math2 = Milestone(student_id=s.id, course_id=content_courses_map[3].id, title="العمليات الحسابية البسيطة", number=2, description="عمليات الجمع والطرح البسيطة")
            
            session.add(milestone_sci1)
            session.add(milestone_sci2)
            session.add(milestone_sci3)
            session.add(milestone_math1)
            session.add(milestone_math2)
            session.commit()
            session.refresh(milestone_sci1)
            session.refresh(milestone_sci2)
            session.refresh(milestone_sci3)
            session.refresh(milestone_math1)
            session.refresh(milestone_math2)

            milestones_by_course = {
                1: {1: milestone_sci1, 2: milestone_sci2, 3: milestone_sci3},
                3: {1: milestone_math1, 2: milestone_math2}
            }

            # Query all content lessons to assign student lesson progress
            all_content_lessons = session.exec(select(ContentLesson)).all()
            for cl in all_content_lessons:
                # Set progress profile depending on student index
                # Student 1 & 5: Completed most Science, half Math
                # Student 2 (flagged stressed): Completed Milestone 1 Science, struggling in Milestone 2
                # Student 3 & 4: Moderate progress
                status = "locked"
                progress = 0
                
                if cl.course_number == 1: # Science
                    if cl.milestone_number == 1:
                        status = "completed"
                        progress = 100
                    elif cl.milestone_number == 2:
                        if cl.lesson_number == 1:
                            status = "in_progress" if s_idx != 1 else "completed"
                            progress = 65 if s_idx != 1 else 100
                        elif cl.lesson_number == 2:
                            status = "in_progress" if s_idx == 1 else "locked"
                            progress = 30 if s_idx == 1 else 0
                        else:
                            status = "locked"
                            progress = 0
                    else:
                        status = "locked"
                        progress = 0
                else: # Math (course 3)
                    if cl.milestone_number == 1:
                        if cl.lesson_number == 1:
                            status = "completed"
                            progress = 100
                        else:
                            status = "in_progress"
                            progress = 40
                    else:
                        status = "locked"
                        progress = 0

                m_ref = milestones_by_course[cl.course_number][cl.milestone_number]

                student_lesson = Lesson(
                    student_id=s.id,
                    content_lesson_id=cl.id,
                    milestone_id=m_ref.id,
                    lesson_number=cl.lesson_number,
                    title=cl.title,
                    description=cl.description,
                    progress=progress,
                    status=status
                )
                session.add(student_lesson)
                session.commit()
                session.refresh(student_lesson)

                # Seed student-specific Material records
                cl_materials = session.exec(select(ContentMaterial).where(ContentMaterial.lesson_id == cl.id)).all()
                for cm in cl_materials:
                    session.add(Material(
                        lesson_id=student_lesson.id,
                        title=cm.title,
                        material_type=cm.material_type,
                        file_url=cm.file_url,
                        extracted_text=f"نص مستخرج للدرس {cl.title} للنشاط المرئي والمسموع."
                    ))
                
                # Seed student-specific Assignment records
                cl_assignments = session.exec(select(ContentAssignment).where(ContentAssignment.lesson_id == cl.id)).all()
                for ca_temp in cl_assignments:
                    student_assign = Assignment(
                        lesson_id=student_lesson.id,
                        content_assignment_id=ca_temp.id,
                        title=ca_temp.title,
                        description=ca_temp.description,
                        assignment_type=ca_temp.assignment_type,
                        file_url=ca_temp.file_url or "/uploads/assignments/worksheet.pdf",
                        deadline=ca_temp.deadline
                    )
                    session.add(student_assign)
                    session.commit()
                    session.refresh(student_assign)

                    # If lesson is completed, create a submission and teacher feedback
                    if status == "completed":
                        methods = ["typed", "voice"]
                        method = random.choice(methods)
                        desc_text = f"إجابتي على ورقة العمل لدرس {cl.title}. لقد قمت بحل جميع الأسئلة."
                        
                        sub = Submission(
                            assignment_id=student_assign.id,
                            student_id=s.id,
                            description=desc_text,
                            submission_method=method,
                            story_grammar_score="S,P,E" if cl.course_number == 1 else None, # Setting, Problem, Event
                            causal_connective_count=random.randint(2, 5),
                            audio_url="/uploads/submissions/voice_demo.wav" if method == "voice" else None,
                            submitted_at=datetime.utcnow() - timedelta(days=random.randint(1, 4))
                        )
                        session.add(sub)
                        session.commit()
                        session.refresh(sub)

                        # Create submission file
                        session.add(SubmissionFile(
                            submission_id=sub.id,
                            file_name="my_answers.pdf",
                            file_url="/uploads/submissions/my_answers.pdf"
                        ))

                        # Create Feedback from teacher
                        feedback_comments = [
                            f"عمل رائع وممتاز يا بطل في درس {cl.title}! إجاباتك صحيحة ودقيقة.",
                            f"أحسنت التوضيح! أعجبني جداً تنظيمك لحلول درس {cl.title}.",
                            f"مجهود رائع واستخدام رائع للمفردات في حل ورقة عمل {cl.title}."
                        ]
                        
                        feed = Feedback(
                            submission_id=sub.id,
                            comment=random.choice(feedback_comments),
                            rating=random.choice([4, 5]),
                            created_at=sub.submitted_at + timedelta(hours=2)
                        )
                        session.add(feed)
                        session.commit()

            # Seed Student Quizzes
            quiz_science1 = Quiz(
                student_id=s.id,
                title="اختبار عالم النباتات",
                description="اختبار قصير لتقييم فهم النبات وعملية البناء الضوئي",
                status="completed",
                score=float(random.randint(80, 100)),
                attempts_used=1,
                attempts_allowed=3,
                questions='[]',
                answers='[]',
                completed_at=(datetime.utcnow() - timedelta(days=3)).isoformat(),
                created_at=(datetime.utcnow() - timedelta(days=3, hours=1)).isoformat()
            )
            quiz_math1 = Quiz(
                student_id=s.id,
                title="اختبار الأرقام والعد",
                description="اختبار تقييم فهم العد من ١ إلى ١٠ ومقارنة الأعداد",
                status="completed" if s_idx != 1 else "in_progress",
                score=float(random.randint(70, 95)) if s_idx != 1 else None,
                attempts_used=1,
                attempts_allowed=3,
                questions='[]',
                answers='[]',
                completed_at=(datetime.utcnow() - timedelta(days=2)).isoformat() if s_idx != 1 else None,
                created_at=(datetime.utcnow() - timedelta(days=2, hours=1)).isoformat()
            )
            session.add(quiz_science1)
            session.add(quiz_math1)
            session.commit()

            # Generate 7 Days of Biometric Telemetry (IOT Readings)
            # Create a reading every 30 minutes to look like continuous learning sessions.
            now = datetime.utcnow()
            for day in range(7):
                day_offset = now - timedelta(days=day)
                # Assume study sessions happen between 09:00 and 12:00
                for hour in range(9, 12):
                    for minute in [0, 30]:
                        ts = day_offset.replace(hour=hour, minute=minute, second=0, microsecond=0)
                        
                        # Student 2 is generally more stressed during mathematics study sessions
                        # Generate some stressed periods on Day 1 and Day 3
                        is_stressed_moment = (s_idx == 1) and (day in [1, 3]) and (hour == 10)
                        
                        if is_stressed_moment:
                            status = "stressed"
                            hr = random.randint(98, 115)
                            gsr = round(random.uniform(0.75, 1.20), 3)
                        else:
                            status = random.choice(["focused", "focused", "relaxed", "calm"])
                            hr = random.randint(70, 84)
                            gsr = round(random.uniform(0.15, 0.45), 3)

                        session.add(IOTReading(
                            student_id=s.id,
                            heart_rate=hr,
                            gsr=gsr,
                            temperature=36.6,
                            status=status,
                            timestamp=ts
                        ))
            session.commit()

            # Create Student flags (For Student 2, create an active flag, and some resolved flags for others)
            if s_idx == 1: # Student 2 (demo_student_2)
                # Active Stress Flag
                session.add(StudentFlag(
                    student_id=s.id,
                    source="iot",
                    reason="تم رصد إجهاد حاد ومتكرر عبر المستشعرات (نبضات قلب تجاوزت ١٠٥ وتوصيل جلدي مرتفع) أثناء حل اختبار الرياضيات.",
                    status="active",
                    created_at=datetime.utcnow() - timedelta(hours=18)
                ))
                # Resolved historical flag
                session.add(StudentFlag(
                    student_id=s.id,
                    source="teacher",
                    reason="تشتت حساسي بسبب انعكاس ضوء الشمس على الشاشة.",
                    status="resolved",
                    created_at=datetime.utcnow() - timedelta(days=4),
                    resolved_at=datetime.utcnow() - timedelta(days=4, hours=2),
                    supervisor_id=supervisor_user.id,
                    supervisor_notes="قامت المعلمة بإسدال الستائر وضبط درجة سطوع الشاشة إلى الوضع الداكن. استعاد الطالب تركيزه وهدأ سريعاً."
                ))
            else:
                # Normal resolved flag for variety
                if s_idx % 2 == 0:
                    session.add(StudentFlag(
                        student_id=s.id,
                        source="teacher",
                        reason="تشتت انتباه بسيط من أصوات الجرس الخارجي.",
                        status="resolved",
                        created_at=datetime.utcnow() - timedelta(days=5),
                        resolved_at=datetime.utcnow() - timedelta(days=5, hours=1),
                        supervisor_id=supervisor_user.id,
                        supervisor_notes="تم توجيه الطالب لاستخدام سماعات الرأس المانعة للضوضاء."
                    ))
            session.commit()

            # Create AskBaseet history
            chat_interactions = [
                {"q": "كيف يساعد البناء الضوئي النبات؟", "a": "يساعد البناء الضوئي النبات على صنع السكر، وهو الغذاء الذي يعطيه الطاقة لينمو ويصبح قوياً!"},
                {"q": "ما هي المجموعة الشمسية?‏", "a": "المجموعة الشمسية هي عائلة من 8 كواكب تدور حول نجم كبير مضيء يسمى الشمس. كوكبنا الأرض هو جزء من هذه العائلة!"},
                {"q": "كيف أجمع ٥ و ٣؟", "a": "ابدأ بالعدد ٥، ثم عد ٣ خطوات للأمام: ٦، ٧، ٨. المجموع هو ٨! أحسنت المحاولة."}
            ]
            for chat in chat_interactions:
                session.add(AskBaseet(
                    student_id=s.id,
                    question=chat["q"],
                    answer=chat["a"],
                    context="تعليم العلوم والرياضيات المبسطة",
                    created_at=(datetime.utcnow() - timedelta(days=2)).isoformat(),
                    answered_at=(datetime.utcnow() - timedelta(days=2, minutes=1)).isoformat()
                ))
            session.commit()

            # Create Supervisor Reports
            session.add(SupervisorReport(
                student_id=s.id,
                supervisor_id=supervisor_user.id,
                title="التقرير التقييمي الشامل لمنتصف الشهر",
                content=f"يظهر الطالب تقدماً واعداً في منهج العلوم والرياضيات. الالتزام ممتاز ويستجيب بشكل جيد للتنبيهات والدروس المرئية. معدل التركيز في متوسط {int(s.baseline_engagement*100)}% وهو مؤشر ممتاز.",
                created_at=datetime.utcnow() - timedelta(days=2)
            ))

            # Create Supervisor Messages to teachers discussing students
            session.add(SupervisorMessage(
                supervisor_id=supervisor_user.id,
                teacher_id=teacher1.id if s_idx in [0, 1, 4] else teacher2.id,
                student_id=s.id,
                content=f"يرجى متابعة إعدادات الشاشة وسماعات الرأس للطالب في الحصص القادمة ومقارنتها بقراءات الإجهاد الحيوية.",
                created_at=datetime.utcnow() - timedelta(days=1),
                is_read=False
            ))
            session.commit()

            # Create Parent Notifications
            session.add(ParentNotification(
                parent_id=s.parent_id,
                title="تقييم جديد متاح لدرس العلوم",
                message=f"أضاف المعلم تعليقاً وتقييماً ممتازاً على واجب درس {content_courses_map[1].title} الخاص بطفلك.",
                type="feedback",
                is_read=False,
                is_urgent=False,
                created_at=datetime.utcnow() - timedelta(days=1)
            ))
            if s_idx == 1: # Alert for parent of student 2
                session.add(ParentNotification(
                    parent_id=s.parent_id,
                    title="تنبيه ارتفاع الإجهاد",
                    message="تم رصد مستويات إجهاد مرتفعة أثناء نشاط الرياضيات اليوم. قمنا بتقديم دعم إضافي لتهدئة طفلك.",
                    type="alert",
                    is_read=False,
                    is_urgent=True,
                    created_at=datetime.utcnow() - timedelta(hours=18)
                ))
            session.commit()

        print("🎉 Database successfully seeded with extensive Arabic Science/Math demo data!")
        print("--------------------------------------------------------------------------------")
        print("Demo User Credentials:")
        print("  - Supervisor: supervisor@demo.com  / password123")
        print("  - Teacher 1:  teacher1@demo.com    / password123")
        print("  - Teacher 2:  teacher2@demo.com    / password123")
        print("  - Parent 1:   parent1@demo.com     / password123")
        print("  - Parent 2:   parent2@demo.com     / password123")
        print("  - Students:   student1@demo.com to student5@demo.com  / password123")
        print("--------------------------------------------------------------------------------")
        print("Custom users (nada, Ahmed, NewStudent, etc.) were left completely untouched.")

if __name__ == "__main__":
    seed_demo_data()
