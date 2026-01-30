--
-- PostgreSQL database dump
--

\restrict 1l0nNhRf5daa0neAW7GzdmcMjjVomSVsQnGJu2doSG5rhSlHC1Vnkb7pwDAG3G3

-- Dumped from database version 14.18 (Homebrew)
-- Dumped by pg_dump version 18.0

-- Started on 2026-01-30 21:43:34 EET

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 5 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: mo
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO mo;

--
-- TOC entry 889 (class 1247 OID 25160)
-- Name: lesson_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.lesson_status AS ENUM (
    'locked',
    'in-progress',
    'completed'
);


ALTER TYPE public.lesson_status OWNER TO postgres;

--
-- TOC entry 871 (class 1247 OID 25020)
-- Name: roleenum; Type: TYPE; Schema: public; Owner: mo
--

CREATE TYPE public.roleenum AS ENUM (
    'teacher',
    'parent',
    'student',
    'supervisor',
    'admin'
);


ALTER TYPE public.roleenum OWNER TO mo;

--
-- TOC entry 886 (class 1247 OID 25153)
-- Name: statusenum; Type: TYPE; Schema: public; Owner: mo
--

CREATE TYPE public.statusenum AS ENUM (
    'locked',
    'in_progress',
    'completed'
);


ALTER TYPE public.statusenum OWNER TO mo;

--
-- TOC entry 257 (class 1255 OID 25639)
-- Name: update_lesson_progress(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_lesson_progress() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_lesson_progress() OWNER TO postgres;

--
-- TOC entry 269 (class 1255 OID 25180)
-- Name: update_lesson_status(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_lesson_status() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    next_milestone INTEGER;
BEGIN
    -- 1️⃣ Update status of the current lesson
    IF NEW.progress = 100 THEN
        NEW.status := 'completed';
    ELSE
        NEW.status := 'in-progress';
    END IF;

    -- 2️⃣ Check if all lessons in the current milestone are completed
    IF (SELECT bool_and(progress = 100)
        FROM lessons
        WHERE student_id = NEW.student_id
          AND milestone_id = NEW.milestone_id) THEN

        -- 3️⃣ Unlock next milestone lessons
        next_milestone := NEW.milestone_id + 1;

        UPDATE lessons
        SET status = 'in-progress'
        WHERE student_id = NEW.student_id
          AND milestone_id = next_milestone
          AND status = 'locked';
    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_lesson_status() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 216 (class 1259 OID 25125)
-- Name: ask_baseet; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.ask_baseet (
    id integer NOT NULL,
    student_id integer NOT NULL,
    question character varying NOT NULL,
    answer character varying,
    context character varying,
    created_at character varying,
    answered_at character varying
);


ALTER TABLE public.ask_baseet OWNER TO mo;

--
-- TOC entry 215 (class 1259 OID 25124)
-- Name: ask_baseet_id_seq; Type: SEQUENCE; Schema: public; Owner: mo
--

CREATE SEQUENCE public.ask_baseet_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ask_baseet_id_seq OWNER TO mo;

--
-- TOC entry 3949 (class 0 OID 0)
-- Dependencies: 215
-- Name: ask_baseet_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mo
--

ALTER SEQUENCE public.ask_baseet_id_seq OWNED BY public.ask_baseet.id;


--
-- TOC entry 224 (class 1259 OID 25260)
-- Name: assignments; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.assignments (
    id integer NOT NULL,
    lesson_id integer NOT NULL,
    title character varying,
    description character varying,
    assignment_type character varying NOT NULL,
    file_url character varying NOT NULL,
    deadline timestamp without time zone,
    content_assignment_id integer
);


ALTER TABLE public.assignments OWNER TO mo;

--
-- TOC entry 223 (class 1259 OID 25259)
-- Name: assignments_id_seq; Type: SEQUENCE; Schema: public; Owner: mo
--

CREATE SEQUENCE public.assignments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.assignments_id_seq OWNER TO mo;

--
-- TOC entry 3950 (class 0 OID 0)
-- Dependencies: 223
-- Name: assignments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mo
--

ALTER SEQUENCE public.assignments_id_seq OWNED BY public.assignments.id;


--
-- TOC entry 240 (class 1259 OID 25496)
-- Name: class_levels; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.class_levels (
    id integer NOT NULL,
    name character varying NOT NULL,
    teacher_id integer
);


ALTER TABLE public.class_levels OWNER TO mo;

--
-- TOC entry 239 (class 1259 OID 25495)
-- Name: class_levels_id_seq; Type: SEQUENCE; Schema: public; Owner: mo
--

CREATE SEQUENCE public.class_levels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.class_levels_id_seq OWNER TO mo;

--
-- TOC entry 3951 (class 0 OID 0)
-- Dependencies: 239
-- Name: class_levels_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mo
--

ALTER SEQUENCE public.class_levels_id_seq OWNED BY public.class_levels.id;


--
-- TOC entry 243 (class 1259 OID 25518)
-- Name: classroom_course_links; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.classroom_course_links (
    classroom_id integer NOT NULL,
    course_id integer NOT NULL
);


ALTER TABLE public.classroom_course_links OWNER TO mo;

--
-- TOC entry 242 (class 1259 OID 25505)
-- Name: classrooms; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.classrooms (
    id integer NOT NULL,
    name character varying NOT NULL,
    level_id integer NOT NULL,
    teacher_id integer
);


ALTER TABLE public.classrooms OWNER TO mo;

--
-- TOC entry 241 (class 1259 OID 25504)
-- Name: classrooms_id_seq; Type: SEQUENCE; Schema: public; Owner: mo
--

CREATE SEQUENCE public.classrooms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.classrooms_id_seq OWNER TO mo;

--
-- TOC entry 3952 (class 0 OID 0)
-- Dependencies: 241
-- Name: classrooms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mo
--

ALTER SEQUENCE public.classrooms_id_seq OWNED BY public.classrooms.id;


--
-- TOC entry 254 (class 1259 OID 25727)
-- Name: content_assignment_files; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.content_assignment_files (
    id integer NOT NULL,
    assignment_id integer NOT NULL,
    file_url character varying NOT NULL,
    file_name character varying NOT NULL
);


ALTER TABLE public.content_assignment_files OWNER TO mo;

--
-- TOC entry 253 (class 1259 OID 25726)
-- Name: content_assignment_files_id_seq; Type: SEQUENCE; Schema: public; Owner: mo
--

CREATE SEQUENCE public.content_assignment_files_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.content_assignment_files_id_seq OWNER TO mo;

--
-- TOC entry 3953 (class 0 OID 0)
-- Dependencies: 253
-- Name: content_assignment_files_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mo
--

ALTER SEQUENCE public.content_assignment_files_id_seq OWNED BY public.content_assignment_files.id;


--
-- TOC entry 252 (class 1259 OID 25710)
-- Name: content_assignments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.content_assignments (
    id integer NOT NULL,
    lesson_id integer,
    title character varying NOT NULL,
    description text,
    assignment_type character varying DEFAULT 'unknown'::character varying,
    file_url character varying DEFAULT ''::character varying,
    deadline timestamp without time zone
);


ALTER TABLE public.content_assignments OWNER TO postgres;

--
-- TOC entry 251 (class 1259 OID 25709)
-- Name: content_assignments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.content_assignments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.content_assignments_id_seq OWNER TO postgres;

--
-- TOC entry 3954 (class 0 OID 0)
-- Dependencies: 251
-- Name: content_assignments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.content_assignments_id_seq OWNED BY public.content_assignments.id;


--
-- TOC entry 238 (class 1259 OID 25486)
-- Name: content_courses; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.content_courses (
    id integer NOT NULL,
    course_number integer NOT NULL,
    description character varying,
    title character varying,
    teacher_id integer
);


ALTER TABLE public.content_courses OWNER TO mo;

--
-- TOC entry 246 (class 1259 OID 25605)
-- Name: content_lessons; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.content_lessons (
    id integer NOT NULL,
    course_number integer NOT NULL,
    milestone_number integer NOT NULL,
    lesson_number integer NOT NULL,
    title character varying NOT NULL,
    description character varying,
    teacher_id integer
);


ALTER TABLE public.content_lessons OWNER TO mo;

--
-- TOC entry 245 (class 1259 OID 25604)
-- Name: content_lessons_id_seq; Type: SEQUENCE; Schema: public; Owner: mo
--

CREATE SEQUENCE public.content_lessons_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.content_lessons_id_seq OWNER TO mo;

--
-- TOC entry 3955 (class 0 OID 0)
-- Dependencies: 245
-- Name: content_lessons_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mo
--

ALTER SEQUENCE public.content_lessons_id_seq OWNED BY public.content_lessons.id;


--
-- TOC entry 237 (class 1259 OID 25485)
-- Name: content_levels_id_seq; Type: SEQUENCE; Schema: public; Owner: mo
--

CREATE SEQUENCE public.content_levels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.content_levels_id_seq OWNER TO mo;

--
-- TOC entry 3956 (class 0 OID 0)
-- Dependencies: 237
-- Name: content_levels_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mo
--

ALTER SEQUENCE public.content_levels_id_seq OWNED BY public.content_courses.id;


--
-- TOC entry 248 (class 1259 OID 25614)
-- Name: content_materials; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.content_materials (
    id integer NOT NULL,
    lesson_id integer NOT NULL,
    title character varying NOT NULL,
    file_url character varying NOT NULL,
    material_type character varying NOT NULL
);


ALTER TABLE public.content_materials OWNER TO mo;

--
-- TOC entry 247 (class 1259 OID 25613)
-- Name: content_materials_id_seq; Type: SEQUENCE; Schema: public; Owner: mo
--

CREATE SEQUENCE public.content_materials_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.content_materials_id_seq OWNER TO mo;

--
-- TOC entry 3957 (class 0 OID 0)
-- Dependencies: 247
-- Name: content_materials_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mo
--

ALTER SEQUENCE public.content_materials_id_seq OWNED BY public.content_materials.id;


--
-- TOC entry 250 (class 1259 OID 25676)
-- Name: courses; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.courses (
    id integer NOT NULL,
    title character varying NOT NULL,
    description character varying,
    image_url character varying
);


ALTER TABLE public.courses OWNER TO mo;

--
-- TOC entry 249 (class 1259 OID 25675)
-- Name: courses_id_seq; Type: SEQUENCE; Schema: public; Owner: mo
--

CREATE SEQUENCE public.courses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.courses_id_seq OWNER TO mo;

--
-- TOC entry 3958 (class 0 OID 0)
-- Dependencies: 249
-- Name: courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mo
--

ALTER SEQUENCE public.courses_id_seq OWNED BY public.courses.id;


--
-- TOC entry 222 (class 1259 OID 25244)
-- Name: feedback; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.feedback (
    id integer NOT NULL,
    submission_id integer NOT NULL,
    comment character varying NOT NULL,
    rating integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.feedback OWNER TO mo;

--
-- TOC entry 221 (class 1259 OID 25243)
-- Name: feedback_id_seq; Type: SEQUENCE; Schema: public; Owner: mo
--

CREATE SEQUENCE public.feedback_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.feedback_id_seq OWNER TO mo;

--
-- TOC entry 3959 (class 0 OID 0)
-- Dependencies: 221
-- Name: feedback_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mo
--

ALTER SEQUENCE public.feedback_id_seq OWNED BY public.feedback.id;


--
-- TOC entry 256 (class 1259 OID 25742)
-- Name: iot_readings; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.iot_readings (
    id integer NOT NULL,
    student_id integer,
    heart_rate double precision NOT NULL,
    gsr double precision NOT NULL,
    temperature double precision NOT NULL,
    status character varying NOT NULL,
    "timestamp" timestamp without time zone NOT NULL
);


ALTER TABLE public.iot_readings OWNER TO mo;

--
-- TOC entry 255 (class 1259 OID 25741)
-- Name: iot_readings_id_seq; Type: SEQUENCE; Schema: public; Owner: mo
--

CREATE SEQUENCE public.iot_readings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.iot_readings_id_seq OWNER TO mo;

--
-- TOC entry 3960 (class 0 OID 0)
-- Dependencies: 255
-- Name: iot_readings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mo
--

ALTER SEQUENCE public.iot_readings_id_seq OWNED BY public.iot_readings.id;


--
-- TOC entry 214 (class 1259 OID 25055)
-- Name: lessons; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.lessons (
    id integer NOT NULL,
    title character varying,
    description character varying,
    lesson_number integer,
    student_id integer,
    progress integer DEFAULT 0,
    status character varying(20) DEFAULT 'locked'::character varying,
    milestone_id integer,
    content_lesson_id integer
);


ALTER TABLE public.lessons OWNER TO mo;

--
-- TOC entry 213 (class 1259 OID 25054)
-- Name: lessons_id_seq; Type: SEQUENCE; Schema: public; Owner: mo
--

CREATE SEQUENCE public.lessons_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.lessons_id_seq OWNER TO mo;

--
-- TOC entry 3961 (class 0 OID 0)
-- Dependencies: 213
-- Name: lessons_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mo
--

ALTER SEQUENCE public.lessons_id_seq OWNED BY public.lessons.id;


--
-- TOC entry 244 (class 1259 OID 25554)
-- Name: level_course_links; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.level_course_links (
    level_id integer NOT NULL,
    course_id integer NOT NULL
);


ALTER TABLE public.level_course_links OWNER TO mo;

--
-- TOC entry 236 (class 1259 OID 25426)
-- Name: log_table; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.log_table (
    id integer NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    user_input character varying,
    intent character varying,
    topic character varying,
    question character varying,
    correct boolean,
    correct_answer character varying,
    user_choice character varying,
    topic_id integer
);


ALTER TABLE public.log_table OWNER TO mo;

--
-- TOC entry 235 (class 1259 OID 25425)
-- Name: log_table_id_seq; Type: SEQUENCE; Schema: public; Owner: mo
--

CREATE SEQUENCE public.log_table_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.log_table_id_seq OWNER TO mo;

--
-- TOC entry 3962 (class 0 OID 0)
-- Dependencies: 235
-- Name: log_table_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mo
--

ALTER SEQUENCE public.log_table_id_seq OWNED BY public.log_table.id;


--
-- TOC entry 234 (class 1259 OID 25412)
-- Name: materials; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.materials (
    id integer NOT NULL,
    lesson_id integer NOT NULL,
    title character varying NOT NULL,
    description character varying,
    material_type character varying NOT NULL,
    file_url character varying NOT NULL,
    extracted_text character varying
);


ALTER TABLE public.materials OWNER TO mo;

--
-- TOC entry 233 (class 1259 OID 25411)
-- Name: materials_id_seq; Type: SEQUENCE; Schema: public; Owner: mo
--

CREATE SEQUENCE public.materials_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.materials_id_seq OWNER TO mo;

--
-- TOC entry 3963 (class 0 OID 0)
-- Dependencies: 233
-- Name: materials_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mo
--

ALTER SEQUENCE public.materials_id_seq OWNED BY public.materials.id;


--
-- TOC entry 230 (class 1259 OID 25383)
-- Name: milestones; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.milestones (
    id integer NOT NULL,
    title character varying NOT NULL,
    number integer NOT NULL,
    description character varying,
    student_id integer,
    course_id integer
);


ALTER TABLE public.milestones OWNER TO mo;

--
-- TOC entry 229 (class 1259 OID 25382)
-- Name: milestones_id_seq; Type: SEQUENCE; Schema: public; Owner: mo
--

CREATE SEQUENCE public.milestones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.milestones_id_seq OWNER TO mo;

--
-- TOC entry 3964 (class 0 OID 0)
-- Dependencies: 229
-- Name: milestones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mo
--

ALTER SEQUENCE public.milestones_id_seq OWNED BY public.milestones.id;


--
-- TOC entry 228 (class 1259 OID 25359)
-- Name: quiz; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.quiz (
    id integer NOT NULL,
    student_id integer NOT NULL,
    lesson_id integer,
    milestone_id integer,
    title character varying NOT NULL,
    quiz_type character varying NOT NULL,
    max_attempts integer NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.quiz OWNER TO mo;

--
-- TOC entry 226 (class 1259 OID 25347)
-- Name: quiz_attempts; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.quiz_attempts (
    id integer NOT NULL,
    quiz_id integer NOT NULL,
    score double precision,
    submitted_at timestamp without time zone NOT NULL
);


ALTER TABLE public.quiz_attempts OWNER TO mo;

--
-- TOC entry 225 (class 1259 OID 25346)
-- Name: quiz_attempts_id_seq; Type: SEQUENCE; Schema: public; Owner: mo
--

CREATE SEQUENCE public.quiz_attempts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quiz_attempts_id_seq OWNER TO mo;

--
-- TOC entry 3965 (class 0 OID 0)
-- Dependencies: 225
-- Name: quiz_attempts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mo
--

ALTER SEQUENCE public.quiz_attempts_id_seq OWNED BY public.quiz_attempts.id;


--
-- TOC entry 227 (class 1259 OID 25358)
-- Name: quiz_id_seq; Type: SEQUENCE; Schema: public; Owner: mo
--

CREATE SEQUENCE public.quiz_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quiz_id_seq OWNER TO mo;

--
-- TOC entry 3966 (class 0 OID 0)
-- Dependencies: 227
-- Name: quiz_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mo
--

ALTER SEQUENCE public.quiz_id_seq OWNED BY public.quiz.id;


--
-- TOC entry 232 (class 1259 OID 25398)
-- Name: quizzes; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.quizzes (
    id integer NOT NULL,
    student_id integer NOT NULL,
    title character varying NOT NULL,
    description character varying,
    lesson_id integer,
    status character varying NOT NULL,
    score double precision,
    attempts_used integer NOT NULL,
    attempts_allowed integer NOT NULL,
    questions character varying,
    answers character varying,
    completed_at character varying,
    created_at character varying
);


ALTER TABLE public.quizzes OWNER TO mo;

--
-- TOC entry 231 (class 1259 OID 25397)
-- Name: quizzes_id_seq; Type: SEQUENCE; Schema: public; Owner: mo
--

CREATE SEQUENCE public.quizzes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quizzes_id_seq OWNER TO mo;

--
-- TOC entry 3967 (class 0 OID 0)
-- Dependencies: 231
-- Name: quizzes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mo
--

ALTER SEQUENCE public.quizzes_id_seq OWNED BY public.quizzes.id;


--
-- TOC entry 212 (class 1259 OID 25041)
-- Name: students; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.students (
    id integer NOT NULL,
    user_id integer NOT NULL,
    age integer,
    autism_type character varying,
    sensitivities character varying,
    learning_style character varying,
    baseline_engagement double precision,
    course_number integer,
    classroom_id integer
);


ALTER TABLE public.students OWNER TO mo;

--
-- TOC entry 211 (class 1259 OID 25040)
-- Name: students_id_seq; Type: SEQUENCE; Schema: public; Owner: mo
--

CREATE SEQUENCE public.students_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.students_id_seq OWNER TO mo;

--
-- TOC entry 3968 (class 0 OID 0)
-- Dependencies: 211
-- Name: students_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mo
--

ALTER SEQUENCE public.students_id_seq OWNED BY public.students.id;


--
-- TOC entry 220 (class 1259 OID 25230)
-- Name: submission_files; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.submission_files (
    id integer NOT NULL,
    submission_id integer NOT NULL,
    file_name character varying NOT NULL,
    file_url character varying NOT NULL
);


ALTER TABLE public.submission_files OWNER TO mo;

--
-- TOC entry 219 (class 1259 OID 25229)
-- Name: submission_files_id_seq; Type: SEQUENCE; Schema: public; Owner: mo
--

CREATE SEQUENCE public.submission_files_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.submission_files_id_seq OWNER TO mo;

--
-- TOC entry 3969 (class 0 OID 0)
-- Dependencies: 219
-- Name: submission_files_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mo
--

ALTER SEQUENCE public.submission_files_id_seq OWNED BY public.submission_files.id;


--
-- TOC entry 218 (class 1259 OID 25216)
-- Name: submissions; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.submissions (
    id integer NOT NULL,
    assignment_id integer NOT NULL,
    student_id integer NOT NULL,
    description character varying,
    submitted_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.submissions OWNER TO mo;

--
-- TOC entry 217 (class 1259 OID 25215)
-- Name: submissions_id_seq; Type: SEQUENCE; Schema: public; Owner: mo
--

CREATE SEQUENCE public.submissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.submissions_id_seq OWNER TO mo;

--
-- TOC entry 3970 (class 0 OID 0)
-- Dependencies: 217
-- Name: submissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mo
--

ALTER SEQUENCE public.submissions_id_seq OWNED BY public.submissions.id;


--
-- TOC entry 210 (class 1259 OID 25032)
-- Name: users; Type: TABLE; Schema: public; Owner: mo
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying NOT NULL,
    email character varying NOT NULL,
    hashed_password character varying NOT NULL,
    role public.roleenum NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.users OWNER TO mo;

--
-- TOC entry 209 (class 1259 OID 25031)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: mo
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO mo;

--
-- TOC entry 3971 (class 0 OID 0)
-- Dependencies: 209
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mo
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 3650 (class 2604 OID 25655)
-- Name: ask_baseet id; Type: DEFAULT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.ask_baseet ALTER COLUMN id SET DEFAULT nextval('public.ask_baseet_id_seq'::regclass);


--
-- TOC entry 3655 (class 2604 OID 25656)
-- Name: assignments id; Type: DEFAULT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.assignments ALTER COLUMN id SET DEFAULT nextval('public.assignments_id_seq'::regclass);


--
-- TOC entry 3663 (class 2604 OID 25657)
-- Name: class_levels id; Type: DEFAULT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.class_levels ALTER COLUMN id SET DEFAULT nextval('public.class_levels_id_seq'::regclass);


--
-- TOC entry 3664 (class 2604 OID 25658)
-- Name: classrooms id; Type: DEFAULT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.classrooms ALTER COLUMN id SET DEFAULT nextval('public.classrooms_id_seq'::regclass);


--
-- TOC entry 3671 (class 2604 OID 25730)
-- Name: content_assignment_files id; Type: DEFAULT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.content_assignment_files ALTER COLUMN id SET DEFAULT nextval('public.content_assignment_files_id_seq'::regclass);


--
-- TOC entry 3668 (class 2604 OID 25713)
-- Name: content_assignments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.content_assignments ALTER COLUMN id SET DEFAULT nextval('public.content_assignments_id_seq'::regclass);


--
-- TOC entry 3662 (class 2604 OID 25659)
-- Name: content_courses id; Type: DEFAULT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.content_courses ALTER COLUMN id SET DEFAULT nextval('public.content_levels_id_seq'::regclass);


--
-- TOC entry 3665 (class 2604 OID 25660)
-- Name: content_lessons id; Type: DEFAULT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.content_lessons ALTER COLUMN id SET DEFAULT nextval('public.content_lessons_id_seq'::regclass);


--
-- TOC entry 3666 (class 2604 OID 25661)
-- Name: content_materials id; Type: DEFAULT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.content_materials ALTER COLUMN id SET DEFAULT nextval('public.content_materials_id_seq'::regclass);


--
-- TOC entry 3667 (class 2604 OID 25679)
-- Name: courses id; Type: DEFAULT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.courses ALTER COLUMN id SET DEFAULT nextval('public.courses_id_seq'::regclass);


--
-- TOC entry 3653 (class 2604 OID 25662)
-- Name: feedback id; Type: DEFAULT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.feedback ALTER COLUMN id SET DEFAULT nextval('public.feedback_id_seq'::regclass);


--
-- TOC entry 3672 (class 2604 OID 25745)
-- Name: iot_readings id; Type: DEFAULT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.iot_readings ALTER COLUMN id SET DEFAULT nextval('public.iot_readings_id_seq'::regclass);


--
-- TOC entry 3647 (class 2604 OID 25663)
-- Name: lessons id; Type: DEFAULT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.lessons ALTER COLUMN id SET DEFAULT nextval('public.lessons_id_seq'::regclass);


--
-- TOC entry 3661 (class 2604 OID 25664)
-- Name: log_table id; Type: DEFAULT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.log_table ALTER COLUMN id SET DEFAULT nextval('public.log_table_id_seq'::regclass);


--
-- TOC entry 3660 (class 2604 OID 25665)
-- Name: materials id; Type: DEFAULT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.materials ALTER COLUMN id SET DEFAULT nextval('public.materials_id_seq'::regclass);


--
-- TOC entry 3658 (class 2604 OID 25666)
-- Name: milestones id; Type: DEFAULT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.milestones ALTER COLUMN id SET DEFAULT nextval('public.milestones_id_seq'::regclass);


--
-- TOC entry 3657 (class 2604 OID 25667)
-- Name: quiz id; Type: DEFAULT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.quiz ALTER COLUMN id SET DEFAULT nextval('public.quiz_id_seq'::regclass);


--
-- TOC entry 3656 (class 2604 OID 25668)
-- Name: quiz_attempts id; Type: DEFAULT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.quiz_attempts ALTER COLUMN id SET DEFAULT nextval('public.quiz_attempts_id_seq'::regclass);


--
-- TOC entry 3659 (class 2604 OID 25669)
-- Name: quizzes id; Type: DEFAULT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.quizzes ALTER COLUMN id SET DEFAULT nextval('public.quizzes_id_seq'::regclass);


--
-- TOC entry 3646 (class 2604 OID 25670)
-- Name: students id; Type: DEFAULT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.students ALTER COLUMN id SET DEFAULT nextval('public.students_id_seq'::regclass);


--
-- TOC entry 3652 (class 2604 OID 25671)
-- Name: submission_files id; Type: DEFAULT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.submission_files ALTER COLUMN id SET DEFAULT nextval('public.submission_files_id_seq'::regclass);


--
-- TOC entry 3651 (class 2604 OID 25672)
-- Name: submissions id; Type: DEFAULT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.submissions ALTER COLUMN id SET DEFAULT nextval('public.submissions_id_seq'::regclass);


--
-- TOC entry 3645 (class 2604 OID 25673)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 3902 (class 0 OID 25125)
-- Dependencies: 216
-- Data for Name: ask_baseet; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.ask_baseet (id, student_id, question, answer, context, created_at, answered_at) FROM stdin;
\.


--
-- TOC entry 3910 (class 0 OID 25260)
-- Dependencies: 224
-- Data for Name: assignments; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.assignments (id, lesson_id, title, description, assignment_type, file_url, deadline, content_assignment_id) FROM stdin;
1	6	1_IMG_7756.jpeg		unknown		\N	2
8	7	hi.docx		unknown		\N	3
9	8	واجب درس النجوم.docx		unknown		\N	5
\.


--
-- TOC entry 3926 (class 0 OID 25496)
-- Dependencies: 240
-- Data for Name: class_levels; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.class_levels (id, name, teacher_id) FROM stdin;
1	Level 1	12
6	Level 3	12
\.


--
-- TOC entry 3929 (class 0 OID 25518)
-- Dependencies: 243
-- Data for Name: classroom_course_links; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.classroom_course_links (classroom_id, course_id) FROM stdin;
1	1
1	3
\.


--
-- TOC entry 3928 (class 0 OID 25505)
-- Dependencies: 242
-- Data for Name: classrooms; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.classrooms (id, name, level_id, teacher_id) FROM stdin;
1	Class A	1	12
2	Class B	1	12
4	Class C	6	12
\.


--
-- TOC entry 3940 (class 0 OID 25727)
-- Dependencies: 254
-- Data for Name: content_assignment_files; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.content_assignment_files (id, assignment_id, file_url, file_name) FROM stdin;
4	4	/uploads/content/assign_4_واجب_درس_النجوم.docx	واجب درس النجوم.docx
5	5	/uploads/content/assign_5_واجب_درس_النجوم.docx	واجب درس النجوم.docx
\.


--
-- TOC entry 3938 (class 0 OID 25710)
-- Dependencies: 252
-- Data for Name: content_assignments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.content_assignments (id, lesson_id, title, description, assignment_type, file_url, deadline) FROM stdin;
4	\N	واجب درس النجوم.docx		unknown		2026-02-10 23:59:00
5	9	واجب درس النجوم.docx		unknown		2026-02-10 23:40:00
\.


--
-- TOC entry 3924 (class 0 OID 25486)
-- Dependencies: 238
-- Data for Name: content_courses; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.content_courses (id, course_number, description, title, teacher_id) FROM stdin;
5	1	Introduction to Science	Course 112	13
3	3		\N	12
4	4		\N	12
1	1	Introduction to Science	Course 112	12
6	5		\N	12
7	6		\N	12
\.


--
-- TOC entry 3932 (class 0 OID 25605)
-- Dependencies: 246
-- Data for Name: content_lessons; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.content_lessons (id, course_number, milestone_number, lesson_number, title, description, teacher_id) FROM stdin;
1	1	1	1	الطاقة		12
2	1	1	2	البناء الضوئي		12
9	1	2	1	النجوم		12
\.


--
-- TOC entry 3934 (class 0 OID 25614)
-- Dependencies: 248
-- Data for Name: content_materials; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.content_materials (id, lesson_id, title, file_url, material_type) FROM stdin;
11	9	درس النجوم.jpeg	/uploads/content/9_درس_النجوم.jpeg	jpeg
12	1	الطاقة.docx	/uploads/content/1_الطاقة.docx	docx
13	2	البناء الضوئي.docx	/uploads/content/2_البناء_الضوئي.docx	docx
\.


--
-- TOC entry 3936 (class 0 OID 25676)
-- Dependencies: 250
-- Data for Name: courses; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.courses (id, title, description, image_url) FROM stdin;
1	Course 1	Science	\N
2	Course 2	Math	\N
\.


--
-- TOC entry 3908 (class 0 OID 25244)
-- Dependencies: 222
-- Data for Name: feedback; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.feedback (id, submission_id, comment, rating, created_at) FROM stdin;
6	10	bravoo..shatooor	5	2026-01-30 18:53:43.164326
\.


--
-- TOC entry 3942 (class 0 OID 25742)
-- Dependencies: 256
-- Data for Name: iot_readings; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.iot_readings (id, student_id, heart_rate, gsr, temperature, status, "timestamp") FROM stdin;
1	1	148	50.14	27.1	relaxed	2026-01-28 22:22:15.970082
2	1	118	50.14	27.2	relaxed	2026-01-28 22:22:36.011899
3	1	140	50.14	27.2	relaxed	2026-01-28 22:22:56.02979
4	1	141	50.14	27.2	relaxed	2026-01-28 22:23:16.150237
5	1	132	50.14	27.2	relaxed	2026-01-28 22:24:21.910384
6	1	115	50.14	27.2	relaxed	2026-01-28 22:24:41.933841
7	1	135	50.14	27.2	relaxed	2026-01-28 22:25:01.950001
8	1	127	50.16	27.2	relaxed	2026-01-28 22:25:21.960624
9	1	118	50.17	27.2	relaxed	2026-01-28 22:25:41.994397
10	1	141	50.16	27.2	relaxed	2026-01-28 22:26:02.007649
11	1	133	50.16	27.2	relaxed	2026-01-28 22:26:22.027413
12	1	132	50.15	27.2	relaxed	2026-01-28 22:26:42.036712
13	1	140	50.16	27.2	relaxed	2026-01-28 22:27:02.045797
14	1	128	50.16	27.2	relaxed	2026-01-28 22:27:22.0527
15	1	0	50.17	27.5	relaxed	2026-01-28 22:27:42.061686
16	1	114	49.11	32.3	relaxed	2026-01-28 22:29:30.096709
17	1	101	48.91	32.8	stressed	2026-01-28 22:29:50.122349
18	1	102	48.85	33.2	stressed	2026-01-28 22:30:10.131876
19	1	102	49.52	33.7	relaxed	2026-01-28 22:30:30.155997
20	1	101	49.08	34.1	relaxed	2026-01-28 22:30:50.179815
21	1	93	43.84	34.2	stressed	2026-01-28 22:31:10.191795
22	1	101	46.39	34.3	stressed	2026-01-28 22:31:30.215351
23	1	102	44.83	34.4	stressed	2026-01-28 22:31:50.261727
24	1	104	46.24	34.5	stressed	2026-01-28 22:32:10.274321
25	1	104	46.2	34.6	stressed	2026-01-28 22:32:30.283358
26	1	108	45.49	34.7	stressed	2026-01-28 22:32:50.297531
27	1	105	44.9	34.8	stressed	2026-01-28 22:33:10.311559
28	1	97	45.22	34.8	stressed	2026-01-28 22:33:30.334532
29	1	101	45.44	34.9	stressed	2026-01-28 22:33:50.349751
30	1	147	50.59	33.8	relaxed	2026-01-28 22:37:36.290765
31	1	138	50.59	33.4	relaxed	2026-01-28 22:37:57.115835
32	1	139	50.59	33.1	relaxed	2026-01-28 22:38:17.189201
33	1	132	50.59	32.8	relaxed	2026-01-28 22:38:37.237539
34	1	133	50.59	32.6	relaxed	2026-01-28 22:38:57.250184
35	1	131	50.59	32.3	relaxed	2026-01-28 22:39:17.262058
36	1	132	50.59	32.1	relaxed	2026-01-28 22:39:37.288633
37	1	121	50.59	31.9	relaxed	2026-01-28 22:39:57.298041
38	1	133	50.59	31.7	relaxed	2026-01-28 22:40:17.304415
39	1	140	50.59	31.5	relaxed	2026-01-28 22:40:37.313939
40	1	130	50.59	31.3	relaxed	2026-01-28 22:40:57.324882
41	1	143	50.58	31.2	relaxed	2026-01-28 22:41:17.333067
42	1	127	50.59	31	relaxed	2026-01-28 22:41:37.348046
43	1	132	50.55	30.9	relaxed	2026-01-28 22:41:57.354762
44	1	138	50.6	30.8	relaxed	2026-01-28 22:42:17.363838
45	1	137	50.59	30.6	relaxed	2026-01-28 22:42:37.372213
46	1	134	50.59	30.4	relaxed	2026-01-28 22:42:57.390394
47	1	128	50.59	30.2	relaxed	2026-01-28 22:43:17.407711
48	1	0	50.49	30	relaxed	2026-01-28 22:43:37.417906
49	1	121	50.63	29.9	relaxed	2026-01-28 22:43:57.42328
50	1	106	50.81	29.8	relaxed	2026-01-28 22:44:17.438116
51	1	103	50.98	29.4	relaxed	2026-01-28 22:44:37.444564
52	1	103	50.34	31.8	relaxed	2026-01-28 22:44:57.454215
53	1	90	50.39	32.8	relaxed	2026-01-28 22:45:17.475414
54	1	97	50.43	33.3	relaxed	2026-01-28 22:45:37.505518
55	1	107	50.33	33.6	relaxed	2026-01-28 22:45:57.525046
56	1	102	50.31	33.9	relaxed	2026-01-28 22:46:17.539378
57	1	120	50.4	34.2	relaxed	2026-01-28 22:46:37.545579
58	1	102	50.32	34.4	relaxed	2026-01-28 22:46:57.552298
59	1	104	50.44	34.7	relaxed	2026-01-28 22:47:17.562942
60	1	103	50.25	36.2	relaxed	2026-01-28 22:48:55.993666
61	1	99	50.26	36.3	relaxed	2026-01-28 22:49:16.018463
62	1	112	50.27	36.4	relaxed	2026-01-28 22:49:36.043953
63	1	106	50.21	36.4	relaxed	2026-01-28 22:49:56.06009
64	1	100	50.69	36.4	relaxed	2026-01-28 22:50:16.091702
65	1	96	50.49	36.4	relaxed	2026-01-28 22:50:36.104229
66	1	108	50.48	36.4	relaxed	2026-01-28 22:50:56.125037
67	1	109	50.49	36.4	relaxed	2026-01-28 22:51:16.133561
68	1	94	50.53	36.4	relaxed	2026-01-28 22:51:36.252182
69	1	99	50.47	36.4	relaxed	2026-01-28 22:51:56.262223
70	1	99	50.46	36.5	relaxed	2026-01-28 22:52:16.274882
71	1	101	51.74	37.1	relaxed	2026-01-28 22:53:52.231655
72	1	94	51.43	37.1	relaxed	2026-01-28 22:54:12.257551
73	1	110	52.29	36.9	relaxed	2026-01-28 22:54:32.265923
74	1	101	51.96	37.1	relaxed	2026-01-28 22:54:52.275583
75	1	94	51.91	37.2	relaxed	2026-01-28 22:55:12.291541
76	1	100	51.32	37.1	relaxed	2026-01-28 22:55:32.3014
77	1	107	51.59	37.2	relaxed	2026-01-28 22:55:52.313146
78	1	103	51.44	37.1	relaxed	2026-01-28 22:56:12.332832
79	1	110	51.39	37.1	relaxed	2026-01-28 22:56:39.125503
80	1	100	51.87	37	relaxed	2026-01-28 22:56:59.186664
81	1	108	52.15	36.9	relaxed	2026-01-28 22:57:28.934919
82	1	104	52.29	36.9	relaxed	2026-01-28 22:57:48.952275
83	1	109	51.48	36.9	relaxed	2026-01-28 22:58:08.95905
84	1	111	51.97	36.9	relaxed	2026-01-28 22:58:28.969617
85	1	107	52.53	37.1	relaxed	2026-01-28 22:59:31.119529
86	1	104	52.75	37.3	relaxed	2026-01-28 22:59:51.150659
87	1	109	50.05	36.7	relaxed	2026-01-28 23:05:39.195345
88	1	94	50.05	36.6	relaxed	2026-01-28 23:06:22.817131
89	1	107	49.97	36.6	relaxed	2026-01-28 23:06:42.861906
90	1	107	49.39	35.2	relaxed	2026-01-28 23:07:44.185017
91	1	109	49.46	34.3	relaxed	2026-01-28 23:08:10.7342
92	1	103	50.36	33.8	relaxed	2026-01-28 23:08:30.749321
93	1	109	50.61	33.2	relaxed	2026-01-28 23:08:50.756083
94	1	116	50.84	32.7	relaxed	2026-01-28 23:09:10.768656
95	1	135	50.69	32.3	relaxed	2026-01-28 23:09:30.775522
96	1	144	50.7	32	relaxed	2026-01-28 23:09:50.786479
97	1	120	50.72	31.7	relaxed	2026-01-28 23:10:10.79863
98	1	143	50.72	31.4	relaxed	2026-01-28 23:10:30.805382
99	1	128	50.74	30.8	relaxed	2026-01-28 23:11:28.369342
100	1	130	50.76	30.4	relaxed	2026-01-28 23:12:02.69778
101	1	128	50.73	30.2	relaxed	2026-01-28 23:12:22.933514
102	1	134	50.7	30.1	relaxed	2026-01-28 23:12:42.945121
103	1	116	50.72	29.9	relaxed	2026-01-28 23:13:06.138957
104	1	141	50.72	29.8	relaxed	2026-01-28 23:13:26.151669
105	1	141	50.93	29.7	relaxed	2026-01-28 23:13:46.159856
106	1	132	51.22	29.6	relaxed	2026-01-28 23:14:43.359258
107	1	132	51.22	29.6	relaxed	2026-01-28 23:15:03.399732
108	1	132	51.22	29.6	relaxed	2026-01-28 23:15:44.487439
109	1	132	51.22	29.6	relaxed	2026-01-28 23:16:06.002169
110	1	132	51.22	29.6	relaxed	2026-01-28 23:16:26.02874
111	1	132	51.22	29.6	relaxed	2026-01-28 23:16:46.041411
112	1	132	51.22	29.6	relaxed	2026-01-28 23:17:06.077466
113	1	132	51.22	29.6	relaxed	2026-01-28 23:17:26.096938
114	1	132	51.22	29.6	relaxed	2026-01-28 23:17:46.109
115	1	132	51.22	29.6	relaxed	2026-01-28 23:18:06.118625
116	1	132	51.22	29.6	relaxed	2026-01-28 23:18:26.146153
117	1	132	51.22	29.6	relaxed	2026-01-28 23:18:46.155112
118	1	132	51.22	29.6	relaxed	2026-01-28 23:19:06.171197
119	1	132	51.22	29.6	relaxed	2026-01-28 23:19:26.201008
120	1	64	0	34.5	relaxed	2026-01-30 14:26:59.349565
121	1	75	0	34.3	relaxed	2026-01-30 14:27:19.379426
122	1	90	51.44	34.2	relaxed	2026-01-30 14:27:39.39277
123	1	113	51.34	34.1	relaxed	2026-01-30 14:27:59.403712
124	1	112	51.23	34	relaxed	2026-01-30 14:28:25.594533
125	1	103	51.4	34.1	relaxed	2026-01-30 14:28:45.602329
126	1	89	51.37	34	relaxed	2026-01-30 14:29:05.610595
127	1	86	51.64	34	relaxed	2026-01-30 14:29:25.620355
128	1	106	51.73	34	relaxed	2026-01-30 14:29:45.630745
129	1	89	53.94	33.9	relaxed	2026-01-30 14:30:05.639794
130	1	87	50.82	34	relaxed	2026-01-30 14:30:25.650118
131	1	105	51.52	34.5	relaxed	2026-01-30 14:30:45.659977
132	1	104	51.84	34.4	relaxed	2026-01-30 14:31:05.672257
133	1	110	51.85	34.3	relaxed	2026-01-30 14:31:25.682611
134	1	97	51.62	34.2	relaxed	2026-01-30 14:31:45.690281
135	1	101	52.05	34.2	relaxed	2026-01-30 14:32:05.700794
136	1	103	0	34.2	relaxed	2026-01-30 14:32:25.708548
137	1	0	51.9	34.2	relaxed	2026-01-30 14:32:45.719103
138	1	106	52.44	34.1	relaxed	2026-01-30 14:33:05.726305
139	1	93	52.52	34.1	relaxed	2026-01-30 14:33:25.734736
140	1	84	52.52	34.2	relaxed	2026-01-30 14:33:45.745112
141	1	88	52.33	34.3	relaxed	2026-01-30 14:34:05.754626
142	1	94	52.09	34.2	relaxed	2026-01-30 14:34:25.7647
143	1	105	52.3	34.3	relaxed	2026-01-30 14:34:45.773288
144	1	112	6.81	34.6	stressed	2026-01-30 14:35:05.782315
145	1	115	0	34.4	relaxed	2026-01-30 14:35:25.791118
146	1	0	0	34.2	relaxed	2026-01-30 14:35:45.799894
147	1	108	1.5	36.7	stressed	2026-01-30 14:36:05.805787
148	1	107	6.26	37.3	stressed	2026-01-30 14:36:25.81214
149	1	87	11.22	37.9	stressed	2026-01-30 14:36:45.831423
150	1	84	11.5	38.1	stressed	2026-01-30 14:37:05.841989
151	1	84	11.5	38.1	stressed	2026-01-30 14:37:25.851886
152	1	84	11.5	38.1	stressed	2026-01-30 14:37:45.861375
153	1	84	11.5	38.1	stressed	2026-01-30 14:38:05.871735
154	1	84	11.5	38.1	stressed	2026-01-30 14:38:25.879514
155	1	84	11.5	38.1	stressed	2026-01-30 14:38:45.888299
156	1	84	11.5	38.1	stressed	2026-01-30 14:39:05.893257
157	1	84	11.5	38.1	stressed	2026-01-30 14:39:25.902115
158	1	84	11.5	38.1	stressed	2026-01-30 14:39:45.912375
159	1	84	11.5	38.1	stressed	2026-01-30 14:40:05.921984
160	1	84	11.5	38.1	stressed	2026-01-30 14:40:25.928653
161	1	84	11.5	38.1	stressed	2026-01-30 14:40:45.937452
162	1	84	11.5	38.1	stressed	2026-01-30 14:41:05.950251
163	1	84	11.5	38.1	stressed	2026-01-30 14:41:25.958016
164	1	84	11.5	38.1	stressed	2026-01-30 14:41:45.96691
165	1	84	11.5	38.1	stressed	2026-01-30 14:42:05.977981
166	1	84	11.5	38.1	stressed	2026-01-30 14:42:26.011564
167	1	84	11.5	38.1	stressed	2026-01-30 14:42:46.025239
168	1	84	11.5	38.1	stressed	2026-01-30 14:43:06.035239
169	1	84	11.5	38.1	stressed	2026-01-30 14:43:26.047572
170	1	84	11.5	38.1	stressed	2026-01-30 14:43:46.057387
171	1	84	11.5	38.1	stressed	2026-01-30 14:44:06.064243
172	1	84	11.5	38.1	stressed	2026-01-30 14:44:26.074208
173	1	84	11.5	38.1	stressed	2026-01-30 14:44:46.081778
174	1	84	11.5	38.1	stressed	2026-01-30 14:45:06.287964
175	1	84	11.5	38.1	stressed	2026-01-30 14:45:26.297033
176	1	84	11.5	38.1	stressed	2026-01-30 14:45:46.306123
177	1	84	11.5	38.1	stressed	2026-01-30 14:46:06.308108
178	1	84	11.5	38.1	stressed	2026-01-30 14:46:26.748411
179	1	84	11.5	38.1	stressed	2026-01-30 14:46:46.759821
180	1	84	11.5	38.1	stressed	2026-01-30 14:47:06.977004
181	1	84	11.5	38.1	stressed	2026-01-30 14:47:26.983311
182	1	84	11.5	38.1	stressed	2026-01-30 14:47:46.989409
183	1	84	11.5	38.1	stressed	2026-01-30 14:48:06.997362
184	1	84	11.5	38.1	stressed	2026-01-30 14:48:27.003985
185	1	84	11.5	38.1	stressed	2026-01-30 14:48:47.009242
186	1	84	11.5	38.1	stressed	2026-01-30 14:49:07.015461
187	1	84	11.5	38.1	stressed	2026-01-30 14:49:27.024848
188	1	101	50.83	33.8	relaxed	2026-01-30 14:50:23.325135
189	1	101	50.83	33.8	relaxed	2026-01-30 14:50:43.354578
190	1	101	50.83	33.8	relaxed	2026-01-30 14:51:03.363717
191	1	101	50.83	33.8	relaxed	2026-01-30 14:51:23.372533
192	1	101	50.83	33.8	relaxed	2026-01-30 14:51:43.379068
193	1	101	50.83	33.8	relaxed	2026-01-30 14:52:03.396981
194	1	101	50.83	33.8	relaxed	2026-01-30 14:52:23.409117
195	1	101	50.83	33.8	relaxed	2026-01-30 14:52:43.417772
196	1	135	50.96	33.7	relaxed	2026-01-30 14:54:03.588796
197	1	108	0	33.7	relaxed	2026-01-30 14:54:23.606134
198	1	113	0	33.7	relaxed	2026-01-30 14:54:43.613913
199	1	111	52.37	33.7	relaxed	2026-01-30 14:55:03.621309
200	1	129	0	33.7	relaxed	2026-01-30 14:55:23.625663
201	1	96	50.17	33.7	relaxed	2026-01-30 14:55:43.63216
202	1	86	49.73	33.8	relaxed	2026-01-30 14:56:03.645414
203	1	95	51.3	33.8	relaxed	2026-01-30 14:56:23.656372
204	1	100	49.82	33.8	relaxed	2026-01-30 14:57:33.092569
205	1	100	49.82	33.8	relaxed	2026-01-30 14:57:53.106695
206	1	100	49.82	33.8	relaxed	2026-01-30 14:58:13.111641
207	1	100	49.82	33.8	relaxed	2026-01-30 14:58:33.116118
208	1	100	49.82	33.8	relaxed	2026-01-30 14:58:53.12191
209	1	100	49.82	33.8	relaxed	2026-01-30 14:59:13.12834
210	1	100	49.82	33.8	relaxed	2026-01-30 14:59:33.135215
211	1	100	49.82	33.8	relaxed	2026-01-30 14:59:53.142306
212	1	100	49.82	33.8	relaxed	2026-01-30 15:00:13.147304
213	1	100	49.82	33.8	relaxed	2026-01-30 15:00:33.152215
214	1	100	49.82	33.8	relaxed	2026-01-30 15:00:53.157733
215	1	100	49.82	33.8	relaxed	2026-01-30 15:01:13.163345
216	1	100	49.82	33.8	relaxed	2026-01-30 15:01:33.170396
217	1	100	49.82	33.8	relaxed	2026-01-30 15:02:13.137161
218	1	100	49.82	33.8	relaxed	2026-01-30 15:02:33.141532
219	1	100	49.82	33.8	relaxed	2026-01-30 15:02:53.14655
220	1	100	49.82	33.8	relaxed	2026-01-30 15:03:13.153853
221	1	100	49.82	33.8	relaxed	2026-01-30 15:03:33.160702
222	1	100	49.82	33.8	relaxed	2026-01-30 15:03:53.170096
223	1	145	50.2	32.9	relaxed	2026-01-30 15:05:30.168563
224	1	145	50.2	32.9	relaxed	2026-01-30 15:05:50.189629
225	1	145	50.2	32.9	relaxed	2026-01-30 15:06:10.199232
226	1	145	50.2	32.9	relaxed	2026-01-30 15:06:30.210257
227	1	145	50.2	32.9	relaxed	2026-01-30 15:06:50.26256
228	1	145	50.2	32.9	relaxed	2026-01-30 15:07:10.270217
229	1	145	50.2	32.9	relaxed	2026-01-30 15:07:30.280206
230	1	145	50.2	32.9	relaxed	2026-01-30 15:07:50.28897
231	1	145	50.2	32.9	relaxed	2026-01-30 15:08:10.298549
232	1	145	50.2	32.9	relaxed	2026-01-30 15:08:30.307747
233	1	145	50.2	32.9	relaxed	2026-01-30 15:08:50.316806
234	1	145	50.2	32.9	relaxed	2026-01-30 15:09:10.32618
235	1	145	50.2	32.9	relaxed	2026-01-30 15:09:30.334984
236	1	145	50.2	32.9	relaxed	2026-01-30 15:09:50.342734
237	1	145	50.2	32.9	relaxed	2026-01-30 15:10:10.351123
238	1	145	50.2	32.9	relaxed	2026-01-30 15:10:30.360654
239	1	145	50.2	32.9	relaxed	2026-01-30 15:10:50.380405
240	1	145	50.2	32.9	relaxed	2026-01-30 15:11:10.387794
241	1	145	50.2	32.9	relaxed	2026-01-30 15:11:30.397266
242	1	145	50.2	32.9	relaxed	2026-01-30 15:11:50.407004
243	1	145	50.2	32.9	relaxed	2026-01-30 15:12:10.41708
244	1	145	50.2	32.9	relaxed	2026-01-30 15:12:30.433573
245	1	145	50.2	32.9	relaxed	2026-01-30 15:12:50.442362
246	1	145	50.2	32.9	relaxed	2026-01-30 15:13:10.451917
247	1	145	50.2	32.9	relaxed	2026-01-30 15:13:30.463034
248	1	145	50.2	32.9	relaxed	2026-01-30 15:13:50.474813
249	1	145	50.2	32.9	relaxed	2026-01-30 15:14:10.483057
250	1	145	50.2	32.9	relaxed	2026-01-30 15:14:30.504621
251	1	145	50.2	32.9	relaxed	2026-01-30 15:14:50.513911
252	1	145	50.2	32.9	relaxed	2026-01-30 15:15:10.522485
253	1	145	50.2	32.9	relaxed	2026-01-30 15:15:30.531519
254	1	145	50.2	32.9	relaxed	2026-01-30 15:15:50.541394
255	1	145	50.2	32.9	relaxed	2026-01-30 15:16:10.551001
256	1	145	50.2	32.9	relaxed	2026-01-30 15:16:30.562514
257	1	145	50.2	32.9	relaxed	2026-01-30 15:16:50.572722
258	1	145	50.2	32.9	relaxed	2026-01-30 15:17:10.582589
259	1	145	50.2	32.9	relaxed	2026-01-30 15:17:30.592192
260	1	145	50.2	32.9	relaxed	2026-01-30 15:17:50.600963
261	1	145	50.2	32.9	relaxed	2026-01-30 15:18:10.61104
262	1	145	50.2	32.9	relaxed	2026-01-30 15:18:30.624525
263	1	145	50.2	32.9	relaxed	2026-01-30 15:18:50.66074
264	1	145	50.2	32.9	relaxed	2026-01-30 15:19:10.678282
265	1	145	50.2	32.9	relaxed	2026-01-30 15:19:30.69168
266	1	145	50.2	32.9	relaxed	2026-01-30 15:19:50.703084
267	1	145	50.2	32.9	relaxed	2026-01-30 15:20:10.713332
268	1	145	50.2	32.9	relaxed	2026-01-30 15:20:30.722235
269	1	145	50.2	32.9	relaxed	2026-01-30 15:20:50.731204
270	1	145	50.2	32.9	relaxed	2026-01-30 15:21:10.741186
271	1	145	50.2	32.9	relaxed	2026-01-30 15:21:30.749896
272	1	145	50.2	32.9	relaxed	2026-01-30 15:21:50.760341
273	1	145	50.2	32.9	relaxed	2026-01-30 15:22:10.770348
274	1	145	50.2	32.9	relaxed	2026-01-30 15:22:30.78153
275	1	145	50.2	32.9	relaxed	2026-01-30 15:22:50.79223
276	1	145	50.2	32.9	relaxed	2026-01-30 15:23:10.800281
277	1	145	50.2	32.9	relaxed	2026-01-30 15:23:30.810281
278	1	145	50.2	32.9	relaxed	2026-01-30 15:23:50.82125
279	1	145	50.2	32.9	relaxed	2026-01-30 15:24:10.830704
280	1	145	50.2	32.9	relaxed	2026-01-30 15:24:30.84379
281	1	145	50.2	32.9	relaxed	2026-01-30 15:24:50.852746
282	1	145	50.2	32.9	relaxed	2026-01-30 15:25:10.862083
283	1	145	50.2	32.9	relaxed	2026-01-30 15:25:30.87157
284	1	145	50.2	32.9	relaxed	2026-01-30 15:25:50.87843
285	1	145	50.2	32.9	relaxed	2026-01-30 15:26:10.891711
286	1	145	50.2	32.9	relaxed	2026-01-30 15:26:30.902767
287	1	145	50.2	32.9	relaxed	2026-01-30 15:26:50.912692
288	1	145	50.2	32.9	relaxed	2026-01-30 15:27:10.923755
289	1	145	50.2	32.9	relaxed	2026-01-30 15:27:30.93211
290	1	145	50.2	32.9	relaxed	2026-01-30 15:27:50.94105
291	1	145	50.2	32.9	relaxed	2026-01-30 15:28:10.952775
292	1	145	50.2	32.9	relaxed	2026-01-30 15:28:30.961816
293	1	145	50.2	32.9	relaxed	2026-01-30 15:28:50.972537
294	1	145	50.2	32.9	relaxed	2026-01-30 15:29:10.979703
295	1	145	50.2	32.9	relaxed	2026-01-30 15:29:30.989759
296	1	145	50.2	32.9	relaxed	2026-01-30 15:29:50.999458
297	1	145	50.2	32.9	relaxed	2026-01-30 15:30:11.009088
298	1	145	50.2	32.9	relaxed	2026-01-30 15:30:31.016188
299	1	145	50.2	32.9	relaxed	2026-01-30 15:30:51.026514
300	1	145	50.2	32.9	relaxed	2026-01-30 15:31:11.036808
301	1	145	50.2	32.9	relaxed	2026-01-30 15:31:31.047661
302	1	145	50.2	32.9	relaxed	2026-01-30 15:31:51.055778
303	1	145	50.2	32.9	relaxed	2026-01-30 15:32:11.064666
304	1	145	50.2	32.9	relaxed	2026-01-30 15:32:31.070319
305	1	145	50.2	32.9	relaxed	2026-01-30 15:32:51.07916
306	1	145	50.2	32.9	relaxed	2026-01-30 15:33:11.08783
307	1	145	50.2	32.9	relaxed	2026-01-30 15:33:31.095636
308	1	145	50.2	32.9	relaxed	2026-01-30 15:33:51.103636
309	1	145	50.2	32.9	relaxed	2026-01-30 15:34:11.11197
310	1	145	50.2	32.9	relaxed	2026-01-30 15:34:31.120941
311	1	145	50.2	32.9	relaxed	2026-01-30 15:34:51.130094
312	1	145	50.2	32.9	relaxed	2026-01-30 15:35:11.140526
313	1	145	50.2	32.9	relaxed	2026-01-30 15:35:51.085281
314	1	145	50.2	32.9	relaxed	2026-01-30 15:36:11.093648
315	1	145	50.2	32.9	relaxed	2026-01-30 15:36:31.099673
316	1	145	50.2	32.9	relaxed	2026-01-30 15:36:51.103989
317	1	145	50.2	32.9	relaxed	2026-01-30 15:37:11.11057
318	1	145	50.2	32.9	relaxed	2026-01-30 15:37:31.123286
319	1	145	50.2	32.9	relaxed	2026-01-30 15:37:51.136593
320	1	145	50.2	32.9	relaxed	2026-01-30 15:38:11.144559
321	1	145	50.2	32.9	relaxed	2026-01-30 15:38:31.152229
322	1	145	50.2	32.9	relaxed	2026-01-30 15:38:51.163763
323	1	145	50.2	32.9	relaxed	2026-01-30 15:39:11.172725
324	1	145	50.2	32.9	relaxed	2026-01-30 15:39:31.180447
325	1	145	50.2	32.9	relaxed	2026-01-30 15:39:51.191029
326	1	145	50.2	32.9	relaxed	2026-01-30 15:40:11.200767
327	1	145	50.2	32.9	relaxed	2026-01-30 15:40:31.208715
328	1	145	50.2	32.9	relaxed	2026-01-30 15:40:51.217181
329	1	145	50.2	32.9	relaxed	2026-01-30 15:41:11.23186
330	1	145	50.2	32.9	relaxed	2026-01-30 15:41:31.239725
331	1	145	50.2	32.9	relaxed	2026-01-30 15:41:51.24888
332	1	145	50.2	32.9	relaxed	2026-01-30 15:42:11.257274
333	1	145	50.2	32.9	relaxed	2026-01-30 15:42:31.266824
334	1	145	50.2	32.9	relaxed	2026-01-30 15:42:51.277258
335	1	145	50.2	32.9	relaxed	2026-01-30 15:43:11.286466
336	1	145	50.2	32.9	relaxed	2026-01-30 15:43:31.29701
337	1	145	50.2	32.9	relaxed	2026-01-30 15:43:51.310348
338	1	145	50.2	32.9	relaxed	2026-01-30 15:44:11.322358
339	1	145	50.2	32.9	relaxed	2026-01-30 15:44:31.330589
340	1	145	50.2	32.9	relaxed	2026-01-30 15:44:51.339477
341	1	145	50.2	32.9	relaxed	2026-01-30 15:45:11.348452
342	1	145	50.2	32.9	relaxed	2026-01-30 15:45:31.357195
343	1	145	50.2	32.9	relaxed	2026-01-30 15:45:51.368517
344	1	145	50.2	32.9	relaxed	2026-01-30 15:46:11.378712
345	1	145	50.2	32.9	relaxed	2026-01-30 15:46:31.390256
346	1	145	50.2	32.9	relaxed	2026-01-30 15:46:51.400696
347	1	145	50.2	32.9	relaxed	2026-01-30 15:47:11.409318
348	1	145	50.2	32.9	relaxed	2026-01-30 15:47:31.422844
349	1	145	50.2	32.9	relaxed	2026-01-30 15:47:51.436429
350	1	145	50.2	32.9	relaxed	2026-01-30 15:48:11.455877
351	1	145	50.2	32.9	relaxed	2026-01-30 15:48:31.470204
352	1	145	50.2	32.9	relaxed	2026-01-30 15:48:51.481776
353	1	145	50.2	32.9	relaxed	2026-01-30 15:49:11.491758
354	1	145	50.2	32.9	relaxed	2026-01-30 15:49:31.506325
355	1	145	50.2	32.9	relaxed	2026-01-30 15:49:51.521856
356	1	145	50.2	32.9	relaxed	2026-01-30 15:50:11.527858
357	1	145	50.2	32.9	relaxed	2026-01-30 15:50:31.537658
358	1	145	50.2	32.9	relaxed	2026-01-30 15:50:51.549219
359	1	145	50.2	32.9	relaxed	2026-01-30 15:51:11.561409
360	1	145	50.2	32.9	relaxed	2026-01-30 15:51:31.57234
361	1	145	50.2	32.9	relaxed	2026-01-30 15:51:51.583266
362	1	145	50.2	32.9	relaxed	2026-01-30 15:52:11.598504
363	1	145	50.2	32.9	relaxed	2026-01-30 15:52:31.612078
364	1	145	50.2	32.9	relaxed	2026-01-30 15:52:51.622499
365	1	145	50.2	32.9	relaxed	2026-01-30 15:53:11.632332
366	1	145	50.2	32.9	relaxed	2026-01-30 15:53:31.642964
367	1	145	50.2	32.9	relaxed	2026-01-30 15:53:51.650903
368	1	145	50.2	32.9	relaxed	2026-01-30 15:54:11.663345
369	1	145	50.2	32.9	relaxed	2026-01-30 15:54:31.682526
370	1	145	50.2	32.9	relaxed	2026-01-30 15:54:51.696557
371	1	145	50.2	32.9	relaxed	2026-01-30 15:55:11.707134
372	1	145	50.2	32.9	relaxed	2026-01-30 15:55:31.719438
373	1	145	50.2	32.9	relaxed	2026-01-30 15:55:51.734899
374	1	145	50.2	32.9	relaxed	2026-01-30 15:56:11.742544
375	1	145	50.2	32.9	relaxed	2026-01-30 15:56:31.824525
376	1	145	50.2	32.9	relaxed	2026-01-30 15:56:51.837807
377	1	145	50.2	32.9	relaxed	2026-01-30 15:57:11.847528
378	1	145	50.2	32.9	relaxed	2026-01-30 15:57:31.854804
379	1	145	50.2	32.9	relaxed	2026-01-30 15:57:51.859258
380	1	145	50.2	32.9	relaxed	2026-01-30 15:58:11.869384
381	1	145	50.2	32.9	relaxed	2026-01-30 15:58:31.879294
382	1	145	50.2	32.9	relaxed	2026-01-30 15:58:51.888674
383	1	145	50.2	32.9	relaxed	2026-01-30 15:59:11.898194
384	1	145	50.2	32.9	relaxed	2026-01-30 15:59:31.907858
385	1	145	50.2	32.9	relaxed	2026-01-30 15:59:51.925466
386	1	145	50.2	32.9	relaxed	2026-01-30 16:00:11.934379
387	1	145	50.2	32.9	relaxed	2026-01-30 16:00:31.942236
388	1	145	50.2	32.9	relaxed	2026-01-30 16:00:51.953313
389	1	145	50.2	32.9	relaxed	2026-01-30 16:01:11.963577
390	1	145	50.2	32.9	relaxed	2026-01-30 16:01:31.970618
391	1	145	50.2	32.9	relaxed	2026-01-30 16:01:51.979875
392	1	145	50.2	32.9	relaxed	2026-01-30 16:02:12.009053
393	1	145	50.2	32.9	relaxed	2026-01-30 16:02:32.024226
394	1	145	50.2	32.9	relaxed	2026-01-30 16:02:52.036583
395	1	0	51.13	36.4	relaxed	2026-01-30 16:03:51.686392
396	1	114	51.15	36.4	relaxed	2026-01-30 16:04:11.706229
397	1	0	51.16	36.4	relaxed	2026-01-30 16:04:31.717982
398	1	107	51.16	36.4	relaxed	2026-01-30 16:04:51.755385
399	1	0	23.93	37.4	relaxed	2026-01-30 16:05:11.766293
400	1	116	23.84	37.4	stressed	2026-01-30 16:05:31.776604
401	1	118	23.84	37.4	stressed	2026-01-30 16:05:51.786265
402	1	107	51.27	36.4	relaxed	2026-01-30 16:06:11.796611
403	1	121	51.3	36.4	relaxed	2026-01-30 16:06:31.805275
404	1	0	51.32	36.4	relaxed	2026-01-30 16:06:51.812495
405	1	0	51.32	36.3	relaxed	2026-01-30 16:07:11.818812
406	1	0	51.32	36.3	relaxed	2026-01-30 16:07:31.828639
407	1	112	51.36	36.3	relaxed	2026-01-30 16:07:51.839471
408	1	119	51.34	36.3	relaxed	2026-01-30 16:08:11.846027
409	1	115	51.37	36.3	relaxed	2026-01-30 16:08:31.85649
410	1	114	51.41	36.2	relaxed	2026-01-30 16:08:51.864699
411	1	108	23.95	37.2	stressed	2026-01-30 16:09:11.873149
412	1	103	51.41	36.2	relaxed	2026-01-30 16:09:31.879594
413	1	100	51.42	36.2	relaxed	2026-01-30 16:09:51.885363
414	1	108	51.37	36.2	relaxed	2026-01-30 16:10:11.894505
415	1	140	51.39	37.2	relaxed	2026-01-30 16:12:20.793418
416	1	127	23.93	37.1	stressed	2026-01-30 16:17:54.091665
417	1	0	23.68	37.1	relaxed	2026-01-30 16:18:14.111402
418	1	127	23.69	37	stressed	2026-01-30 16:18:34.123705
419	1	127	23.65	37	stressed	2026-01-30 16:18:54.137008
420	1	133	23.9	36.9	stressed	2026-01-30 16:19:14.146706
421	1	0	23.64	36.9	relaxed	2026-01-30 16:19:34.159056
422	1	137	23.61	37	stressed	2026-01-30 16:19:54.16942
423	1	137	23.74	36.9	stressed	2026-01-30 16:20:14.223265
424	1	138	23.98	36.9	stressed	2026-01-30 16:20:34.256841
425	1	149	23.99	36.9	stressed	2026-01-30 16:20:54.269886
426	1	0	23.71	37	relaxed	2026-01-30 16:21:14.279836
427	1	153	23.62	37	stressed	2026-01-30 16:21:34.293581
428	1	151	23.77	37	stressed	2026-01-30 16:21:54.320466
429	1	0	23.74	37	relaxed	2026-01-30 16:22:14.330056
430	1	142	23.64	37	stressed	2026-01-30 16:22:34.337787
431	1	0	23.64	37	relaxed	2026-01-30 16:22:54.351665
432	1	140	23.68	37	stressed	2026-01-30 16:23:14.362106
433	1	0	23.81	37.1	relaxed	2026-01-30 16:23:34.37029
434	1	138	23.99	37	stressed	2026-01-30 16:23:54.379394
435	1	138	23.62	37	stressed	2026-01-30 16:24:14.393222
436	1	140	23.66	37	stressed	2026-01-30 16:24:34.402778
437	1	140	23.95	37.1	stressed	2026-01-30 16:24:54.410892
438	1	140	23.95	37.1	stressed	2026-01-30 16:25:14.420127
439	1	140	23.95	37.1	stressed	2026-01-30 16:25:34.431503
440	1	146	51.23	36.1	relaxed	2026-01-30 16:27:05.944073
441	1	146	51.1	36.1	relaxed	2026-01-30 16:27:25.959143
442	1	144	51.25	36.2	relaxed	2026-01-30 16:27:45.966704
443	1	146	51.12	36.2	relaxed	2026-01-30 16:28:05.986686
444	1	108	51.19	35.7	relaxed	2026-01-30 16:28:25.999294
445	1	99	51.2	35.2	relaxed	2026-01-30 16:28:46.011331
446	1	94	51.27	34.9	relaxed	2026-01-30 16:29:06.020609
447	1	102	51.43	34.7	relaxed	2026-01-30 16:29:26.031958
448	1	108	33.69	34.6	stressed	2026-01-30 16:29:46.041184
449	1	106	23.25	34.6	stressed	2026-01-30 16:30:06.05257
450	1	116	23.55	34.7	stressed	2026-01-30 16:30:26.061694
451	1	92	24.98	34.8	stressed	2026-01-30 16:30:46.069532
452	1	96	24.59	34.9	stressed	2026-01-30 16:31:06.079299
453	1	85	23.24	34.9	stressed	2026-01-30 16:31:26.088507
454	1	0	51.21	35.2	relaxed	2026-01-30 16:32:06.082744
455	1	112	19.23	35.2	stressed	2026-01-30 16:32:26.105253
456	1	126	18.07	35.3	stressed	2026-01-30 16:32:46.11247
457	1	126	18.07	35.3	stressed	2026-01-30 16:33:06.118947
458	1	101	17.55	37.6	stressed	2026-01-30 16:33:26.129142
459	1	125	16.81	37.8	stressed	2026-01-30 16:33:46.139809
460	1	111	16.43	37.9	stressed	2026-01-30 16:34:06.149689
461	1	116	51.41	37.9	relaxed	2026-01-30 16:34:26.161204
462	1	109	51.26	38.1	relaxed	2026-01-30 16:34:46.173445
463	1	112	51.33	38	relaxed	2026-01-30 16:35:06.180161
464	1	121	50.9	38	relaxed	2026-01-30 16:35:26.186742
465	1	124	51.27	38	relaxed	2026-01-30 16:35:46.193064
466	1	136	50.86	38	relaxed	2026-01-30 16:36:06.203406
467	1	133	51.24	38	relaxed	2026-01-30 16:36:26.217515
468	1	143	51.33	38.1	relaxed	2026-01-30 16:36:46.223976
469	1	133	51.04	38.1	relaxed	2026-01-30 16:37:06.234229
470	1	129	51.27	38.1	relaxed	2026-01-30 16:37:26.243144
471	1	130	51.26	38.1	relaxed	2026-01-30 16:37:46.251828
472	1	135	50.93	38.1	relaxed	2026-01-30 16:38:06.274434
473	1	135	50.93	38.1	relaxed	2026-01-30 16:38:26.283843
474	1	0	50.84	38.1	relaxed	2026-01-30 16:38:46.293846
475	1	0	51.48	38.2	relaxed	2026-01-30 16:39:06.304071
476	1	0	50.89	38.2	relaxed	2026-01-30 16:39:26.311221
477	1	0	51.2	38.2	relaxed	2026-01-30 16:39:46.318839
478	1	0	51.02	38.2	relaxed	2026-01-30 16:40:06.327475
479	1	0	51.48	38.2	relaxed	2026-01-30 16:40:26.338943
480	1	0	51.37	38.2	relaxed	2026-01-30 16:40:46.347559
481	1	0	52.32	37.8	relaxed	2026-01-30 16:41:06.358341
482	1	125	52.04	37.4	relaxed	2026-01-30 16:41:26.368834
483	1	125	52.04	37.4	relaxed	2026-01-30 16:41:46.378618
484	1	125	52.04	37.4	relaxed	2026-01-30 16:42:06.386059
485	1	125	52.04	37.4	relaxed	2026-01-30 16:42:26.394693
486	1	125	52.04	37.4	relaxed	2026-01-30 16:42:46.401871
487	1	125	52.04	37.4	relaxed	2026-01-30 16:43:06.41057
488	1	125	52.04	37.4	relaxed	2026-01-30 16:43:26.419027
489	1	125	52.04	37.4	relaxed	2026-01-30 16:43:46.425543
490	1	125	52.04	37.4	relaxed	2026-01-30 16:44:06.434342
491	1	125	52.04	37.4	relaxed	2026-01-30 16:44:26.442528
492	1	125	52.04	37.4	relaxed	2026-01-30 16:44:46.451539
493	1	125	52.04	37.4	relaxed	2026-01-30 16:45:06.460506
494	1	125	52.04	37.4	relaxed	2026-01-30 16:45:26.469229
495	1	125	52.04	37.4	relaxed	2026-01-30 16:45:46.477655
496	1	125	52.04	37.4	relaxed	2026-01-30 16:46:06.487868
497	1	125	52.04	37.4	relaxed	2026-01-30 16:46:26.497213
498	1	125	52.04	37.4	relaxed	2026-01-30 16:46:46.507054
499	1	125	52.04	37.4	relaxed	2026-01-30 16:47:06.516286
500	1	125	52.04	37.4	relaxed	2026-01-30 16:47:26.52556
501	1	125	52.04	37.4	relaxed	2026-01-30 16:47:46.535452
502	1	125	52.04	37.4	relaxed	2026-01-30 16:48:06.62155
503	1	125	52.04	37.4	relaxed	2026-01-30 16:48:26.633189
504	1	125	52.04	37.4	relaxed	2026-01-30 16:48:46.663208
505	1	125	52.04	37.4	relaxed	2026-01-30 16:49:06.671382
506	1	125	52.04	37.4	relaxed	2026-01-30 16:49:26.680956
507	1	125	52.04	37.4	relaxed	2026-01-30 16:49:46.696616
508	1	127	51.36	33.6	Relaxed	2026-01-30 17:06:36.485318
509	1	126	51.27	33.6	Relaxed	2026-01-30 17:06:41.422907
510	1	123	50.96	33.6	Relaxed	2026-01-30 17:06:46.432895
511	1	121	51.35	33.6	Relaxed	2026-01-30 17:06:51.4234
512	1	124	51.38	33.6	Relaxed	2026-01-30 17:06:56.433858
513	1	129	51.04	33.6	Relaxed	2026-01-30 17:07:01.421858
514	1	125	50.98	33.6	Relaxed	2026-01-30 17:07:06.421541
515	1	123	51	33.6	Relaxed	2026-01-30 17:07:11.477345
516	1	126	51.34	33.6	Relaxed	2026-01-30 17:07:16.452837
517	1	121	51.36	33.6	Relaxed	2026-01-30 17:07:21.472246
518	1	114	51.37	33.6	Relaxed	2026-01-30 17:07:26.462267
519	1	107	51.34	33.6	Relaxed	2026-01-30 17:07:31.442803
520	1	101	51.25	33.6	Relaxed	2026-01-30 17:07:36.442125
521	1	102	51.38	33.6	Relaxed	2026-01-30 17:07:41.441916
522	1	102	51.36	33.6	Relaxed	2026-01-30 17:07:46.452953
523	1	103	51.4	33.6	Relaxed	2026-01-30 17:07:51.441777
524	1	114	51.24	33.6	Relaxed	2026-01-30 17:07:56.451783
525	1	115	51.26	33.6	Relaxed	2026-01-30 17:08:01.444899
526	1	121	50.97	33.6	Relaxed	2026-01-30 17:08:06.572484
527	1	113	51.24	33.6	Relaxed	2026-01-30 17:08:11.483695
528	1	108	51.37	33.6	Relaxed	2026-01-30 17:08:16.470922
529	1	106	51.4	33.6	Relaxed	2026-01-30 17:08:21.476343
530	1	105	51.39	33.6	Relaxed	2026-01-30 17:08:26.461385
531	1	120	51.37	33.6	Relaxed	2026-01-30 17:08:31.457047
532	1	128	51.34	33.6	Relaxed	2026-01-30 17:08:37.236919
533	1	130	51.27	33.6	Relaxed	2026-01-30 17:08:41.482934
534	1	135	51.16	33.6	Relaxed	2026-01-30 17:08:46.652112
535	1	129	51.13	33.6	Relaxed	2026-01-30 17:08:51.679974
536	1	129	51.01	33.6	Relaxed	2026-01-30 17:08:56.503133
537	1	129	50.97	33.6	Relaxed	2026-01-30 17:09:01.554266
538	1	130	51.21	33.6	Relaxed	2026-01-30 17:09:06.580889
539	1	127	51.23	33.6	Relaxed	2026-01-30 17:09:11.59429
540	1	130	51.4	33.6	Relaxed	2026-01-30 17:09:16.605953
541	1	124	51.26	33.6	Relaxed	2026-01-30 17:09:21.624385
542	1	119	51.38	33.6	Relaxed	2026-01-30 17:09:26.52241
543	1	115	51.41	33.6	Relaxed	2026-01-30 17:09:31.531999
544	1	112	51.34	33.6	Relaxed	2026-01-30 17:09:36.541439
545	1	103	51.31	33.6	Relaxed	2026-01-30 17:09:41.561988
546	1	108	51.01	33.6	Relaxed	2026-01-30 17:09:46.882417
547	1	102	50.93	33.6	Relaxed	2026-01-30 17:09:51.623709
548	1	111	50.96	33.6	Relaxed	2026-01-30 17:09:56.57504
549	1	111	50.99	33.6	Relaxed	2026-01-30 17:10:01.562188
550	1	124	51.22	33.6	Relaxed	2026-01-30 17:10:06.587649
551	1	114	51.23	33.6	Relaxed	2026-01-30 17:10:11.58425
552	1	114	51.37	33.6	Relaxed	2026-01-30 17:10:17.60339
553	1	108	51.37	33.6	Relaxed	2026-01-30 17:10:21.592151
554	1	107	51.39	33.6	Relaxed	2026-01-30 17:10:26.654197
555	1	115	51.14	33.6	Relaxed	2026-01-30 17:10:31.664637
556	1	122	51.13	33.6	Relaxed	2026-01-30 17:10:36.684743
557	1	121	50.97	33.6	Relaxed	2026-01-30 17:10:41.592385
558	1	139	50.97	33.6	Relaxed	2026-01-30 17:10:46.633067
559	1	139	50.93	33.6	Relaxed	2026-01-30 17:10:51.602327
560	1	141	50.93	33.6	Relaxed	2026-01-30 17:10:56.641245
561	1	135	50.97	33.6	Relaxed	2026-01-30 17:11:01.62267
562	1	135	51.2	33.6	Relaxed	2026-01-30 17:11:06.622008
563	1	136	51.13	33.6	Relaxed	2026-01-30 17:11:11.70509
564	1	131	51.12	33.6	Relaxed	2026-01-30 17:11:18.881181
565	1	135	51	33.6	Relaxed	2026-01-30 17:11:22.308393
566	1	123	51.14	33.6	Relaxed	2026-01-30 17:11:28.884642
567	1	115	51.17	33.6	Relaxed	2026-01-30 17:11:31.836865
568	1	115	51.12	33.6	Relaxed	2026-01-30 17:11:36.82483
569	1	115	50.98	33.6	Relaxed	2026-01-30 17:11:41.924831
570	1	121	51.11	33.6	Relaxed	2026-01-30 17:11:46.661937
571	1	129	51.36	33.6	Relaxed	2026-01-30 17:11:52.955879
572	1	128	51.36	33.6	Relaxed	2026-01-30 17:11:57.174715
573	1	127	51.34	33.6	Relaxed	2026-01-30 17:12:01.893121
574	1	134	51.23	33.6	Relaxed	2026-01-30 17:12:06.823785
575	1	123	51.27	33.6	relaxed	2026-01-30 17:13:47.408454
576	1	114	51.16	33.6	relaxed	2026-01-30 17:14:07.426922
577	1	127	51.03	33.6	relaxed	2026-01-30 17:14:27.437079
578	1	125	51.4	33.6	relaxed	2026-01-30 17:14:47.518399
579	1	118	50.96	33.6	relaxed	2026-01-30 17:15:07.533346
580	1	130	51.36	33.6	relaxed	2026-01-30 17:15:27.565013
581	1	133	51.37	33.6	relaxed	2026-01-30 17:15:47.576195
582	1	129	51.23	33.6	relaxed	2026-01-30 17:16:07.585182
583	1	122	50.93	33.7	relaxed	2026-01-30 17:16:27.599288
584	1	110	51.37	33.6	relaxed	2026-01-30 17:16:47.612062
585	1	126	51.06	33.6	relaxed	2026-01-30 17:17:07.621381
586	1	133	51.06	33.6	relaxed	2026-01-30 17:17:27.634271
587	1	0	51.36	33.6	relaxed	2026-01-30 17:17:47.644795
588	1	0	51.27	33.6	relaxed	2026-01-30 17:18:07.657003
589	1	0	51.4	33.6	relaxed	2026-01-30 17:18:27.66669
590	1	0	51.36	33.6	relaxed	2026-01-30 17:18:47.674967
591	1	0	51.05	33.6	relaxed	2026-01-30 17:19:07.684015
592	1	0	51.09	33.6	relaxed	2026-01-30 17:19:27.694302
593	1	0	50.93	33.6	relaxed	2026-01-30 17:19:47.704228
594	1	0	50.95	33.6	relaxed	2026-01-30 17:20:07.710123
595	1	0	50.92	33.6	relaxed	2026-01-30 17:20:27.720551
596	1	0	51.17	33.6	relaxed	2026-01-30 17:20:47.734111
597	1	0	51.2	33.6	relaxed	2026-01-30 17:21:07.74318
598	1	0	51.34	33.6	relaxed	2026-01-30 17:21:27.749416
599	1	0	51.3	33.6	relaxed	2026-01-30 17:21:47.758213
600	1	0	50.93	33.6	relaxed	2026-01-30 17:22:07.76736
601	1	0	51.34	33.6	relaxed	2026-01-30 17:22:27.777636
602	1	0	51.33	33.6	relaxed	2026-01-30 17:22:47.786487
603	1	0	51.1	33.6	relaxed	2026-01-30 17:23:07.795589
604	1	0	50.93	33.6	relaxed	2026-01-30 17:23:27.810445
605	1	0	51.16	33.6	relaxed	2026-01-30 17:23:47.836648
606	1	0	50.98	33.6	relaxed	2026-01-30 17:24:07.845484
607	1	0	51.12	33.6	relaxed	2026-01-30 17:24:27.855454
608	1	0	51.26	33.6	relaxed	2026-01-30 17:24:47.865068
609	1	0	50.91	33.6	relaxed	2026-01-30 17:25:07.872909
610	1	0	51.31	33.6	relaxed	2026-01-30 17:25:27.881441
611	1	0	51.35	33.6	relaxed	2026-01-30 17:25:47.892879
612	1	0	51.06	33.5	relaxed	2026-01-30 17:26:07.900371
613	1	0	51.3	33.6	relaxed	2026-01-30 17:26:27.907912
614	1	0	51.37	33.6	relaxed	2026-01-30 17:26:47.912853
615	1	0	51.3	33.6	relaxed	2026-01-30 17:27:07.92222
616	1	0	50.93	33.5	relaxed	2026-01-30 17:27:27.932981
617	1	0	50.93	33.5	relaxed	2026-01-30 17:27:47.943797
618	1	0	51.36	33.6	relaxed	2026-01-30 17:28:07.952547
619	1	0	51.17	33.5	relaxed	2026-01-30 17:28:27.961857
620	1	0	50.96	33.5	relaxed	2026-01-30 17:28:47.971466
621	1	0	50.98	33.5	relaxed	2026-01-30 17:29:07.979324
622	1	0	51.06	33.5	relaxed	2026-01-30 17:29:27.986186
623	1	0	50.94	33.5	relaxed	2026-01-30 17:29:47.996562
624	1	0	50.92	33.5	relaxed	2026-01-30 17:30:08.00418
625	1	0	50.92	33.5	relaxed	2026-01-30 17:30:28.010481
626	1	0	50.92	33.5	relaxed	2026-01-30 17:30:48.019313
627	1	0	50.92	33.5	relaxed	2026-01-30 17:31:08.026453
628	1	0	50.92	33.5	relaxed	2026-01-30 17:31:28.036841
629	1	0	50.92	33.5	relaxed	2026-01-30 17:31:48.04838
630	1	0	50.92	33.5	relaxed	2026-01-30 17:32:08.057075
631	1	0	51.01	33.4	relaxed	2026-01-30 17:32:28.069939
632	1	0	51.26	33.4	relaxed	2026-01-30 17:32:48.079284
633	1	0	51.26	33.4	relaxed	2026-01-30 17:33:08.087355
634	1	0	51.26	33.4	relaxed	2026-01-30 17:33:28.0971
635	1	0	51.26	33.4	relaxed	2026-01-30 17:33:48.107392
636	1	0	51.26	33.4	relaxed	2026-01-30 17:34:08.118746
637	1	0	51.26	33.4	relaxed	2026-01-30 17:34:28.126796
638	1	0	51.26	33.4	relaxed	2026-01-30 17:34:48.138326
639	1	0	51.26	33.4	relaxed	2026-01-30 17:35:08.148096
640	1	0	51.26	33.4	relaxed	2026-01-30 17:35:28.15671
641	1	0	51.26	33.4	relaxed	2026-01-30 17:35:48.16376
642	1	0	51.25	26.4	Offline	2026-01-30 17:36:08.175899
643	1	0	51.06	26.4	Offline	2026-01-30 17:36:28.188496
644	1	151	50.94	26.4	Relaxed	2026-01-30 17:36:48.199469
645	1	146	50.99	26.4	Relaxed	2026-01-30 17:37:08.208374
646	1	144	50.93	26.4	Relaxed	2026-01-30 17:37:28.216372
647	1	152	51.06	26.4	Relaxed	2026-01-30 17:37:48.225247
648	1	89	51.36	26.4	Relaxed	2026-01-30 17:38:08.234735
649	1	89	51.34	26.4	Relaxed	2026-01-30 17:38:28.245282
650	1	105	51	26.4	Relaxed	2026-01-30 17:38:48.256778
651	1	152	51.25	33.4	relaxed	2026-01-30 17:39:08.265759
652	1	148	51.21	26.4	Relaxed	2026-01-30 17:39:28.284471
653	1	151	51.2	26.4	Relaxed	2026-01-30 17:39:48.300365
654	1	153	51.02	26.4	Relaxed	2026-01-30 17:40:08.310673
655	1	154	51.3	26.4	Relaxed	2026-01-30 17:40:28.320335
656	1	148	50.86	26.4	Relaxed	2026-01-30 17:40:48.331323
657	1	148	51.09	33.4	relaxed	2026-01-30 17:41:08.340769
658	1	133	51.15	33.4	relaxed	2026-01-30 17:41:28.352863
659	1	139	50.94	33.4	relaxed	2026-01-30 17:41:48.38319
660	1	132	51.37	33.4	relaxed	2026-01-30 17:42:08.395201
661	1	157	50.95	26.4	Relaxed	2026-01-30 17:42:28.406848
662	1	148	51.29	26.4	Relaxed	2026-01-30 17:42:48.438366
663	1	145	51.35	26.4	Relaxed	2026-01-30 17:43:08.448357
664	1	152	51.16	26.4	Relaxed	2026-01-30 17:43:28.472649
665	1	129	51.15	26.4	Relaxed	2026-01-30 17:43:48.494039
666	1	139	51.3	26.4	Relaxed	2026-01-30 17:44:08.507477
667	1	140	51.35	26.4	Relaxed	2026-01-30 17:44:28.520546
668	1	135	51.01	33.4	relaxed	2026-01-30 17:44:48.532641
669	1	130	51.34	33.4	relaxed	2026-01-30 17:45:08.543043
670	1	115	51.33	33.4	relaxed	2026-01-30 17:45:28.551975
671	1	117	50.92	33.4	relaxed	2026-01-30 17:45:48.561244
672	1	134	51.08	33.4	relaxed	2026-01-30 17:46:08.571965
673	1	132	51.24	33.4	relaxed	2026-01-30 17:46:28.586448
674	1	142	51.14	33.4	relaxed	2026-01-30 17:46:48.59495
675	1	120	51.07	33.4	relaxed	2026-01-30 17:47:08.608881
676	1	119	51.09	33.4	relaxed	2026-01-30 17:47:28.619993
677	1	132	51.16	33.4	relaxed	2026-01-30 17:47:48.62972
678	1	130	50.98	33.4	relaxed	2026-01-30 17:48:08.638914
679	1	138	51.37	33.4	relaxed	2026-01-30 17:48:28.648098
680	1	134	51.06	33.4	relaxed	2026-01-30 17:48:48.654531
681	1	132	51.34	33.4	relaxed	2026-01-30 17:49:08.661151
682	1	130	50.94	33.4	relaxed	2026-01-30 17:49:28.666931
683	1	131	51.34	33.4	relaxed	2026-01-30 17:49:48.674837
684	1	128	50.95	33.4	relaxed	2026-01-30 17:50:08.683469
685	1	130	51.22	33.4	relaxed	2026-01-30 17:50:28.688944
686	1	129	51.2	33.4	relaxed	2026-01-30 17:50:48.699093
687	1	129	51.3	33.4	relaxed	2026-01-30 17:51:08.711955
688	1	0	51.18	26.4	Offline	2026-01-30 17:56:11.097067
689	1	129	50.93	26.4	Relaxed	2026-01-30 17:56:15.623158
690	1	135	50.93	26.4	Relaxed	2026-01-30 17:56:22.39072
691	1	134	51.09	26.4	Relaxed	2026-01-30 17:56:25.918794
692	1	132	51.38	26.4	Relaxed	2026-01-30 17:56:30.722292
693	1	132	51.25	26.4	Relaxed	2026-01-30 17:56:35.650748
694	1	0	51.12	26.4	Offline	2026-01-30 17:56:40.661048
695	1	0	51.07	26.4	Offline	2026-01-30 17:56:45.710266
696	1	114	51.12	26.4	Relaxed	2026-01-30 17:56:50.640275
697	1	104	51.13	26.4	Relaxed	2026-01-30 17:56:55.678299
698	1	102	0	26.4	Relaxed	2026-01-30 17:57:02.930585
699	1	93	0	26.4	Relaxed	2026-01-30 17:57:06.081684
700	1	86	0	26.4	Relaxed	2026-01-30 17:57:11.17154
701	1	79	0	26.4	Relaxed	2026-01-30 17:57:15.923158
702	1	76	43.21	26.4	Stressed	2026-01-30 17:57:20.909304
703	1	83	0	26.4	Relaxed	2026-01-30 17:57:25.950676
704	1	87	9.63	26.4	Stressed	2026-01-30 17:57:30.949901
705	1	90	0	26.5	Relaxed	2026-01-30 17:57:35.990187
706	1	97	4.61	26.5	Stressed	2026-01-30 17:57:41.04874
707	1	107	51.34	26.6	Relaxed	2026-01-30 17:57:46.078628
708	1	117	0.49	26.6	Relaxed	2026-01-30 17:57:51.109333
709	1	128	0	26.6	Relaxed	2026-01-30 17:57:56.219374
710	1	132	0	26.6	Relaxed	2026-01-30 17:58:01.261552
711	1	133	0	26.7	Relaxed	2026-01-30 17:58:06.334551
712	1	135	0	26.7	Relaxed	2026-01-30 17:58:11.472753
713	1	135	0	26.7	Relaxed	2026-01-30 17:58:16.910199
714	1	123	0	26.7	Relaxed	2026-01-30 17:58:21.619681
715	1	0	0	35.1	Offline	2026-01-30 17:58:36.999389
716	1	0	0	36.8	Offline	2026-01-30 17:58:42.028052
717	1	131	0	37.6	Relaxed	2026-01-30 17:58:48.92774
718	1	112	0	38.4	Relaxed	2026-01-30 17:58:53.622071
719	1	116	0	38.9	Relaxed	2026-01-30 17:59:06.301155
720	1	122	0	38.3	Relaxed	2026-01-30 17:59:16.889029
721	1	121	0	38.1	Relaxed	2026-01-30 17:59:17.062841
722	1	135	0	37.7	Relaxed	2026-01-30 17:59:17.278149
723	1	138	43.87	37.5	Stressed	2026-01-30 17:59:17.390863
724	1	138	51.06	37.4	Relaxed	2026-01-30 17:59:23.981186
725	1	122	50.94	37.1	Relaxed	2026-01-30 17:59:27.361632
726	1	118	49.37	36.8	Relaxed	2026-01-30 17:59:32.382382
727	1	117	23.67	36.7	Stressed	2026-01-30 17:59:37.502383
728	1	119	23.8	36.6	Stressed	2026-01-30 17:59:44.464361
729	1	116	23.87	36.4	Stressed	2026-01-30 17:59:48.757519
730	1	117	23.25	36.3	Stressed	2026-01-30 18:00:04.909839
731	1	137	23.24	36.1	Stressed	2026-01-30 18:00:05.268856
732	1	142	23.35	36	Stressed	2026-01-30 18:00:05.385186
733	1	144	23.25	35.9	Stressed	2026-01-30 18:00:07.712925
734	1	142	23.7	35.8	Stressed	2026-01-30 18:00:12.933132
735	1	141	23.8	35.6	Stressed	2026-01-30 18:00:27.930786
736	1	140	23.92	35.4	Stressed	2026-01-30 18:00:28.71376
737	1	138	23.94	35.4	Stressed	2026-01-30 18:00:29.586119
738	1	136	23.94	35.4	Stressed	2026-01-30 18:00:34.672896
739	1	138	23.94	35.2	Stressed	2026-01-30 18:00:38.249873
740	1	136	23.95	35.2	Stressed	2026-01-30 18:00:43.258649
741	1	133	23.86	35.1	Stressed	2026-01-30 18:00:48.300389
742	1	131	23.22	35	Stressed	2026-01-30 18:00:53.382256
743	1	134	23.36	35	Stressed	2026-01-30 18:00:58.392464
744	1	129	23.36	34.9	Stressed	2026-01-30 18:01:03.411128
745	1	130	23.57	34.9	Stressed	2026-01-30 18:01:08.528756
746	1	127	23.94	34.9	Stressed	2026-01-30 18:01:14.049769
747	1	130	23.93	34.8	Stressed	2026-01-30 18:01:19.639736
748	1	135	23.94	34.8	Stressed	2026-01-30 18:01:23.601544
749	1	135	23.63	34.8	Stressed	2026-01-30 18:01:29.789927
750	1	138	23.89	34.7	Stressed	2026-01-30 18:01:37.798969
751	1	132	23.79	34.7	Stressed	2026-01-30 18:01:39.375068
752	1	133	23.8	34.6	Stressed	2026-01-30 18:01:44.079766
753	1	130	23.81	34.6	Stressed	2026-01-30 18:01:49.129452
754	1	136	23.38	34.6	Stressed	2026-01-30 18:01:54.240392
755	1	135	23.2	34.5	Stressed	2026-01-30 18:01:59.290724
756	1	137	23.22	34.5	Stressed	2026-01-30 18:02:04.279464
757	1	137	23.21	34.4	Stressed	2026-01-30 18:02:09.568021
758	1	138	23.95	34.4	Stressed	2026-01-30 18:02:17.651434
759	1	124	23.92	34.4	Relaxed	2026-01-30 18:02:24.26255
760	1	116	23.78	34.5	Stressed	2026-01-30 18:02:25.363627
761	1	113	23.72	34.6	Stressed	2026-01-30 18:02:30.100202
762	1	122	23.25	34.6	Stressed	2026-01-30 18:02:34.560015
763	1	120	23.26	34.6	Stressed	2026-01-30 18:02:39.668467
764	1	123	23.39	34.6	Stressed	2026-01-30 18:02:44.790093
765	1	117	23.19	34.6	Stressed	2026-01-30 18:02:51.709475
766	1	134	23.19	34.7	Stressed	2026-01-30 18:02:54.830341
767	1	125	23.2	34.7	Stressed	2026-01-30 18:02:59.870554
768	1	130	23.3	34.7	Stressed	2026-01-30 18:03:05.991477
769	1	0	50.05	34.7	Offline	2026-01-30 18:03:21.045609
770	1	114	49.82	34.6	Relaxed	2026-01-30 18:03:25.832772
771	1	123	49.8	34.6	Offline	2026-01-30 18:03:30.659648
772	1	124	50.33	34.6	Offline	2026-01-30 18:03:35.485114
773	1	122	50.02	34.6	Offline	2026-01-30 18:03:40.501682
774	1	129	49.82	34.5	Offline	2026-01-30 18:03:45.511822
775	1	125	49.97	34.5	Offline	2026-01-30 18:03:50.631924
776	1	132	50.1	34.5	Offline	2026-01-30 18:03:55.552464
777	1	134	50.11	34.5	Offline	2026-01-30 18:04:00.610763
778	1	138	47.19	34.5	Stressed	2026-01-30 18:04:05.683532
779	1	132	48.75	34.5	Stressed	2026-01-30 18:04:10.813369
780	1	130	14.89	34.5	Stressed	2026-01-30 18:04:15.821534
781	1	132	0	34.5	Relaxed	2026-01-30 18:04:20.680455
782	1	132	1.36	34.4	Relaxed	2026-01-30 18:04:25.720142
783	1	131	2.24	34.6	Relaxed	2026-01-30 18:04:30.759553
784	1	129	1.44	35.6	Relaxed	2026-01-30 18:04:35.901595
785	1	129	0	35.9	Relaxed	2026-01-30 18:04:41.122968
786	1	0	14.04	36.1	Offline	2026-01-30 18:04:47.002068
787	1	119	13.12	36.4	Stressed	2026-01-30 18:04:51.050038
788	1	103	11.33	36.5	Stressed	2026-01-30 18:04:55.970378
789	1	102	10.77	36.7	Relaxed	2026-01-30 18:05:01.069913
790	1	93	9.96	36.8	Stressed	2026-01-30 18:05:06.131321
791	1	90	10.05	36.9	Relaxed	2026-01-30 18:05:11.232387
792	1	93	9.96	37	Stressed	2026-01-30 18:05:16.245619
793	1	89	9.61	37.1	Relaxed	2026-01-30 18:05:21.301763
794	1	88	9.14	37.2	Relaxed	2026-01-30 18:05:26.594285
795	1	93	8.5	37.3	Relaxed	2026-01-30 18:05:31.37997
796	1	98	8.25	37.4	Relaxed	2026-01-30 18:05:36.500337
797	1	94	7.78	37.4	Relaxed	2026-01-30 18:05:42.472016
798	1	95	7.82	37.6	Relaxed	2026-01-30 18:05:46.552568
799	1	97	7.84	37.6	Relaxed	2026-01-30 18:05:51.540031
800	1	99	7.2	37.7	Relaxed	2026-01-30 18:05:58.744126
801	1	99	7.54	37.8	Relaxed	2026-01-30 18:06:01.623499
802	1	96	7.54	37.8	Relaxed	2026-01-30 18:06:07.963003
803	1	96	7.73	37.8	Relaxed	2026-01-30 18:06:11.684609
804	1	96	7.83	37.9	Relaxed	2026-01-30 18:06:16.750696
805	1	95	7.88	38	Relaxed	2026-01-30 18:06:21.854187
806	1	120	6.81	38.4	Relaxed	2026-01-30 18:07:07.642301
807	1	122	7.11	38.4	Relaxed	2026-01-30 18:07:11.942437
808	1	93	6.72	38.4	Relaxed	2026-01-30 18:07:17.976713
809	1	93	6.26	38.4	Relaxed	2026-01-30 18:07:28.386047
810	1	93	6.61	38.6	Relaxed	2026-01-30 18:07:32.190946
811	1	97	7.27	38.6	Relaxed	2026-01-30 18:07:32.571691
812	1	94	1.41	38.9	Relaxed	2026-01-30 18:09:07.543041
813	1	91	1.3	39	Relaxed	2026-01-30 18:09:12.442802
814	1	85	1.2	39	Relaxed	2026-01-30 18:09:17.393057
815	1	82	1.65	39.1	Relaxed	2026-01-30 18:09:23.103141
816	1	83	1.79	39.1	Relaxed	2026-01-30 18:09:28.256428
817	1	87	1.77	39.1	Relaxed	2026-01-30 18:09:32.490914
818	1	91	1.65	39.2	Relaxed	2026-01-30 18:09:37.566702
819	1	93	1.37	39.2	Relaxed	2026-01-30 18:09:42.592093
820	1	98	1.58	39.2	Relaxed	2026-01-30 18:09:48.054195
821	1	98	1.56	39.3	Relaxed	2026-01-30 18:09:52.701394
822	1	97	0.96	39.4	Relaxed	2026-01-30 18:09:57.8458
823	1	95	1.07	39.4	Relaxed	2026-01-30 18:10:02.865201
824	1	107	0	39.5	Relaxed	2026-01-30 18:10:18.16349
825	1	105	0	39.6	Relaxed	2026-01-30 18:11:13.519696
826	1	101	0	39.6	Relaxed	2026-01-30 18:11:13.598205
827	1	99	0	39.6	Relaxed	2026-01-30 18:11:13.600655
828	1	96	0	39.6	Relaxed	2026-01-30 18:11:13.603006
829	1	97	0	39.7	Relaxed	2026-01-30 18:11:13.605318
830	1	101	0	39.7	Relaxed	2026-01-30 18:11:13.607533
831	1	106	0	39.8	Relaxed	2026-01-30 18:11:13.610438
832	1	107	0	39.8	Relaxed	2026-01-30 18:11:13.613622
833	1	106	0	39.9	Relaxed	2026-01-30 18:11:13.616504
834	1	109	39.28	39.9	Stressed	2026-01-30 18:11:13.618748
835	1	106	46.31	40	Stressed	2026-01-30 18:11:13.723943
836	1	102	49.96	40.1	Relaxed	2026-01-30 18:11:19.21137
837	1	100	48.71	40.1	Stressed	2026-01-30 18:11:31.744682
838	1	101	48.47	40.2	Stressed	2026-01-30 18:11:31.9338
839	1	104	48.53	40.2	Stressed	2026-01-30 18:11:33.825893
840	1	114	48.78	40.3	Stressed	2026-01-30 18:11:51.20823
841	1	106	48.91	40.3	Stressed	2026-01-30 18:11:53.96419
842	1	111	49.17	40.4	Relaxed	2026-01-30 18:11:58.983047
843	1	109	49.32	40.4	Relaxed	2026-01-30 18:12:03.924638
844	1	112	49.26	40.4	Relaxed	2026-01-30 18:12:09.228069
845	1	112	49.31	40.4	Relaxed	2026-01-30 18:12:14.004891
846	1	113	49.32	40.4	Relaxed	2026-01-30 18:12:19.102526
847	1	0	49.13	40.4	Offline	2026-01-30 18:12:56.995624
848	1	122	49.33	40.4	Relaxed	2026-01-30 18:12:57.007562
849	1	122	49.41	40.5	Relaxed	2026-01-30 18:12:57.01145
850	1	124	49.42	40.4	Relaxed	2026-01-30 18:12:57.019358
851	1	125	49.21	40.4	Relaxed	2026-01-30 18:12:57.02474
852	1	123	50.08	40.4	Relaxed	2026-01-30 18:12:59.122285
853	1	107	50.19	40.4	Relaxed	2026-01-30 18:13:04.624295
854	1	104	34.36	40.4	Stressed	2026-01-30 18:13:08.928926
855	1	98	27.77	40.4	Stressed	2026-01-30 18:13:13.832809
856	1	97	36.91	40.3	Stressed	2026-01-30 18:13:18.821412
857	1	105	36.92	40.3	Relaxed	2026-01-30 18:13:23.975885
858	1	103	36.92	40.3	Stressed	2026-01-30 18:13:29.603408
859	1	109	36.93	40.3	Stressed	2026-01-30 18:13:41.712966
860	1	110	37.15	40.3	Stressed	2026-01-30 18:13:41.72083
861	1	104	37.17	37.4	Stressed	2026-01-30 18:13:52.956697
862	1	112	36.87	37.4	Stressed	2026-01-30 18:13:58.073341
863	1	101	36.92	37.4	Stressed	2026-01-30 18:14:03.09269
864	1	101	37.03	37.3	Stressed	2026-01-30 18:14:08.088782
865	1	99	36.94	37.4	Stressed	2026-01-30 18:14:13.151636
866	1	113	1.55	37.4	Relaxed	2026-01-30 18:14:18.221724
867	1	107	50.13	37.4	Relaxed	2026-01-30 18:14:23.141636
868	1	114	45.41	37.3	Stressed	2026-01-30 18:14:28.227812
869	1	115	44.98	37.3	Stressed	2026-01-30 18:14:33.263019
870	1	115	50.13	37.2	Relaxed	2026-01-30 18:14:38.275537
871	1	0	50.18	37.2	Offline	2026-01-30 18:14:43.261235
872	1	0	50.27	37.1	Offline	2026-01-30 18:14:48.351425
873	1	114	50.28	37.1	Relaxed	2026-01-30 18:14:53.311236
874	1	115	48.82	37.1	Relaxed	2026-01-30 18:14:58.361256
875	1	130	20.48	37	Stressed	2026-01-30 18:15:03.362318
876	1	126	9.05	37	Relaxed	2026-01-30 18:15:08.411531
877	1	112	8.71	37.1	Relaxed	2026-01-30 18:15:13.45163
878	1	108	3.3	37	Relaxed	2026-01-30 18:15:18.610785
879	1	106	17.43	36.9	Stressed	2026-01-30 18:15:27.782243
880	1	106	1.69	36.8	Relaxed	2026-01-30 18:15:38.00274
881	1	114	1.06	36.9	Relaxed	2026-01-30 18:15:41.332447
882	1	113	1.18	36.8	Relaxed	2026-01-30 18:15:42.274694
883	1	119	1.88	36.9	Relaxed	2026-01-30 18:15:43.752503
884	1	112	1.55	36.9	Relaxed	2026-01-30 18:15:48.763004
885	1	105	0.6	37	Relaxed	2026-01-30 18:15:56.083531
886	1	107	0	37.1	Relaxed	2026-01-30 18:16:00.385806
887	1	110	0	37.2	Relaxed	2026-01-30 18:16:04.526836
888	1	108	0	37.2	Relaxed	2026-01-30 18:16:20.757117
889	1	108	0	37.3	Relaxed	2026-01-30 18:16:20.78449
890	1	109	0	37.4	Relaxed	2026-01-30 18:16:20.788871
891	1	105	0	37.5	Relaxed	2026-01-30 18:16:24.206852
892	1	105	0	37.6	Relaxed	2026-01-30 18:16:29.163416
893	1	95	0	37.6	Relaxed	2026-01-30 18:16:34.803081
894	1	91	0	37.6	Relaxed	2026-01-30 18:16:39.284983
895	1	88	0	37.7	Relaxed	2026-01-30 18:16:44.374022
896	1	93	0	37.8	Relaxed	2026-01-30 18:16:49.425574
897	1	100	0	37.8	Relaxed	2026-01-30 18:16:54.461968
898	1	92	50.21	37.9	Relaxed	2026-01-30 18:16:59.452763
899	1	0	1.1	37.2	Offline	2026-01-30 18:19:28.848415
900	1	0	2.03	37.2	Offline	2026-01-30 18:19:33.828956
901	1	0	1.78	37.1	Offline	2026-01-30 18:19:38.878778
902	1	0	1.58	37.2	Offline	2026-01-30 18:19:43.883935
903	1	0	1.53	37.2	Offline	2026-01-30 18:19:48.791796
904	1	0	2.64	37.2	Offline	2026-01-30 18:19:53.924692
905	1	0	0	37.3	Offline	2026-01-30 18:19:58.801857
906	1	0	0	37.2	Offline	2026-01-30 18:20:03.853782
907	1	83	0	36.9	Relaxed	2026-01-30 18:20:08.97981
908	1	85	0	36.8	Relaxed	2026-01-30 18:20:14.094278
909	1	86	15.68	36.6	Stressed	2026-01-30 18:20:19.022032
910	1	86	1.55	36.4	Relaxed	2026-01-30 18:20:24.133693
911	1	93	0	36.2	Relaxed	2026-01-30 18:20:29.152994
912	1	98	0	36.1	Relaxed	2026-01-30 18:20:34.378012
913	1	99	49.52	36.1	Relaxed	2026-01-30 18:20:39.285663
914	1	100	0	35.9	Relaxed	2026-01-30 18:20:44.304156
915	1	123	4.49	35.8	Relaxed	2026-01-30 18:20:49.302635
916	1	129	14.36	35.6	Stressed	2026-01-30 18:20:54.444557
917	1	121	14.03	35.5	Stressed	2026-01-30 18:20:59.655171
918	1	125	14.47	35.3	Stressed	2026-01-30 18:21:04.593908
919	1	114	15.94	35.1	Stressed	2026-01-30 18:21:09.622017
920	1	114	12.95	34.9	Stressed	2026-01-30 18:21:14.633056
921	1	111	15.06	34.8	Stressed	2026-01-30 18:21:19.726737
922	1	111	0	34.6	Relaxed	2026-01-30 18:21:24.822113
923	1	0	0	34.5	Offline	2026-01-30 18:21:29.863235
924	1	0	0	34.4	Offline	2026-01-30 18:21:43.984571
925	1	0	0	34.4	Offline	2026-01-30 18:21:48.365502
926	1	0	0	34.4	Offline	2026-01-30 18:21:51.632834
927	1	0	0	34.4	Offline	2026-01-30 18:22:05.495
928	1	0	0	34.4	Offline	2026-01-30 18:22:21.558962
929	1	0	0	34.4	Offline	2026-01-30 18:22:27.863545
930	1	0	0	34.4	Offline	2026-01-30 18:22:32.176528
931	1	0	0	34.4	Offline	2026-01-30 18:22:37.249795
932	1	123	49.89	34.3	Relaxed	2026-01-30 18:22:41.991666
933	1	114	49.62	34.3	Relaxed	2026-01-30 18:22:47.071012
934	1	117	0	34.4	Relaxed	2026-01-30 18:22:52.086345
935	1	119	14.64	34.3	Stressed	2026-01-30 18:22:57.094222
936	1	118	3.94	34.3	Relaxed	2026-01-30 18:23:02.115408
937	1	119	48.77	34.2	Relaxed	2026-01-30 18:23:07.132695
938	1	110	50.02	34.2	Relaxed	2026-01-30 18:23:12.151603
939	1	110	50.4	34.2	Relaxed	2026-01-30 18:23:17.098248
940	1	105	50.22	34.1	Relaxed	2026-01-30 18:23:22.100375
941	1	105	49.73	34.1	Relaxed	2026-01-30 18:23:27.225075
942	1	106	50.02	34.1	Relaxed	2026-01-30 18:23:44.962779
943	1	111	50.39	34	Relaxed	2026-01-30 18:23:46.35175
944	1	112	50.26	33.9	Relaxed	2026-01-30 18:23:46.619487
945	1	106	50.19	33.9	Relaxed	2026-01-30 18:23:47.626162
946	1	110	50.23	33.9	Relaxed	2026-01-30 18:23:52.151551
947	1	109	50.39	33.9	Relaxed	2026-01-30 18:23:57.210029
948	1	96	50.36	33.8	Relaxed	2026-01-30 18:24:02.219619
949	1	89	50.39	33.8	Relaxed	2026-01-30 18:24:07.447728
950	1	103	50.4	33.8	Relaxed	2026-01-30 18:24:12.199795
951	1	102	50.36	33.8	Relaxed	2026-01-30 18:24:18.55897
952	1	97	50.29	33.8	Relaxed	2026-01-30 18:24:22.289531
953	1	113	50.37	33.8	Relaxed	2026-01-30 18:24:27.20957
954	1	108	50.33	33.8	Relaxed	2026-01-30 18:24:32.241733
955	1	108	49.67	33.8	Relaxed	2026-01-30 18:24:37.240984
956	1	109	49.7	33.8	Relaxed	2026-01-30 18:24:42.259874
957	1	106	49.84	33.8	Relaxed	2026-01-30 18:24:47.431506
958	1	102	49.96	33.8	Relaxed	2026-01-30 18:24:52.29862
959	1	108	50.12	33.8	Relaxed	2026-01-30 18:24:57.309071
960	1	122	50.3	33.8	Relaxed	2026-01-30 18:25:02.227297
961	1	123	50.08	33.8	Relaxed	2026-01-30 18:25:07.349558
962	1	132	50.4	33.8	Offline	2026-01-30 18:25:12.369043
963	1	133	50.37	33.8	Offline	2026-01-30 18:25:17.257533
964	1	133	50.38	33.9	Offline	2026-01-30 18:25:22.298843
965	1	115	50.39	33.9	Relaxed	2026-01-30 18:25:27.298872
966	1	108	50.27	33.9	Relaxed	2026-01-30 18:25:32.269094
967	1	108	50.05	33.9	Relaxed	2026-01-30 18:25:37.297784
968	1	108	50	33.9	Relaxed	2026-01-30 18:25:42.369198
969	1	108	49.7	33.9	Relaxed	2026-01-30 18:25:47.328369
970	1	107	50.36	33.9	Relaxed	2026-01-30 18:25:52.410148
971	1	106	50.34	33.9	Relaxed	2026-01-30 18:25:57.531191
972	1	107	50.27	33.9	Relaxed	2026-01-30 18:26:02.313383
973	1	107	50.32	33.9	Relaxed	2026-01-30 18:26:07.298548
974	1	107	50.3	33.9	Relaxed	2026-01-30 18:26:12.628283
975	1	108	50.33	33.9	Relaxed	2026-01-30 18:26:17.389854
976	1	108	50.02	33.9	Relaxed	2026-01-30 18:26:22.348271
977	1	118	49.75	33.9	Relaxed	2026-01-30 18:26:27.429536
978	1	135	49.68	33.9	Offline	2026-01-30 18:26:32.606161
979	1	140	49.89	33.9	Offline	2026-01-30 18:26:37.458127
980	1	134	50.23	33.9	Offline	2026-01-30 18:26:42.379489
981	1	127	49.96	33.9	Relaxed	2026-01-30 18:26:48.891092
982	1	128	49.83	33.9	Relaxed	2026-01-30 18:26:52.39189
983	1	126	49.68	33.9	Relaxed	2026-01-30 18:26:57.387242
984	1	129	50.01	33.9	Relaxed	2026-01-30 18:27:02.401836
985	1	141	50.38	33.9	Offline	2026-01-30 18:27:07.619459
986	1	141	50.02	33.9	Offline	2026-01-30 18:27:12.388003
987	1	136	49.69	33.8	Offline	2026-01-30 18:27:17.397051
988	1	136	50.1	33.8	Offline	2026-01-30 18:27:22.398798
989	1	133	50.36	33.8	Offline	2026-01-30 18:27:27.44448
990	1	133	50.4	33.6	Offline	2026-01-30 18:27:32.386663
991	1	142	50.3	33.6	Offline	2026-01-30 18:27:37.57985
992	1	144	50.13	33.6	Offline	2026-01-30 18:27:42.437372
993	1	143	49.93	33.5	Offline	2026-01-30 18:27:48.250647
994	1	139	49.91	33.4	Offline	2026-01-30 18:27:52.59415
995	1	136	50.17	33.4	Offline	2026-01-30 18:27:57.6586
996	1	133	50.36	33.4	Offline	2026-01-30 18:28:02.45184
997	1	132	50.38	33.3	Offline	2026-01-30 18:28:07.482131
998	1	132	50.26	33.2	Offline	2026-01-30 18:28:13.008563
999	1	131	50.08	33.2	Offline	2026-01-30 18:28:17.510122
1000	1	127	49.97	33.1	Relaxed	2026-01-30 18:28:22.51144
1001	1	128	50.3	33.1	Relaxed	2026-01-30 18:28:27.517148
1002	1	127	50.23	33	Relaxed	2026-01-30 18:28:32.648407
1003	1	131	49.97	33	Offline	2026-01-30 18:28:38.301938
1004	1	139	49.93	32.9	Offline	2026-01-30 18:28:43.658081
1005	1	139	50.34	32.9	Offline	2026-01-30 18:28:53.371636
1006	1	136	50.21	32.8	Offline	2026-01-30 18:29:01.434561
1007	1	137	50.17	32.8	Offline	2026-01-30 18:29:04.527675
1008	1	132	50	32.8	Offline	2026-01-30 18:29:05.341429
1009	1	136	49.94	32.7	Offline	2026-01-30 18:29:07.788335
1010	1	135	50.38	32.6	Offline	2026-01-30 18:29:12.931291
1011	1	133	50.33	32.6	Offline	2026-01-30 18:29:17.620724
1012	1	138	50.11	32.5	Offline	2026-01-30 18:29:23.662091
1013	1	138	50.02	32.5	Offline	2026-01-30 18:29:35.886752
1014	1	139	49.98	32.4	Offline	2026-01-30 18:29:45.369072
1015	1	144	49.95	32.3	Offline	2026-01-30 18:29:55.295913
1016	1	138	50.05	32.2	Offline	2026-01-30 18:29:57.148853
1017	1	136	50.16	32.2	Offline	2026-01-30 18:29:57.719761
1018	1	138	50.28	32.1	Offline	2026-01-30 18:29:57.97871
1019	1	133	50.38	32.1	Offline	2026-01-30 18:29:59.947221
1020	1	132	50.39	32.1	Offline	2026-01-30 18:30:03.559814
1021	1	133	50.39	32	Offline	2026-01-30 18:30:09.063939
1022	1	132	50.35	32	Offline	2026-01-30 18:30:16.400553
1023	1	128	50.2	31.9	Relaxed	2026-01-30 18:30:17.833404
1024	1	128	49.97	31.9	Relaxed	2026-01-30 18:30:24.366271
1025	1	127	49.96	31.9	Relaxed	2026-01-30 18:30:29.272263
1026	1	132	50.03	31.8	Offline	2026-01-30 18:30:45.54607
1027	1	134	50.16	31.8	Offline	2026-01-30 18:30:49.625344
1028	1	134	50.15	31.8	Offline	2026-01-30 18:30:50.340088
1029	1	137	50.27	31.7	Offline	2026-01-30 18:30:50.557082
1030	1	137	50.24	31.6	Offline	2026-01-30 18:30:55.752093
1031	1	133	50.37	31.7	Offline	2026-01-30 18:30:58.903041
1032	1	131	50.39	31.6	Offline	2026-01-30 18:31:04.232097
1033	1	131	49.98	31.6	Offline	2026-01-30 18:31:07.988163
1034	1	136	50.03	31.5	Offline	2026-01-30 18:31:16.134276
1035	1	143	50.34	31.5	Offline	2026-01-30 18:31:20.049453
1036	1	145	50.37	31.4	Offline	2026-01-30 18:31:22.993292
1037	1	148	48.27	31.4	Relaxed	2026-01-30 18:31:27.776123
1038	1	131	0	31.4	Relaxed	2026-01-30 18:31:33.408676
1039	1	106	6.9	31.2	Relaxed	2026-01-30 18:31:45.504152
1040	1	102	6.13	31.3	Relaxed	2026-01-30 18:31:45.559721
1041	1	102	10.57	31.3	Stressed	2026-01-30 18:31:48.046589
1042	1	102	14.07	31.3	Stressed	2026-01-30 18:31:53.101113
1043	1	99	16	31.3	Relaxed	2026-01-30 18:31:58.137078
1044	1	0	13.51	31.3	Offline	2026-01-30 18:32:07.571575
1045	1	0	11.63	31.3	Offline	2026-01-30 18:32:08.528044
1046	1	0	5.89	31.3	Offline	2026-01-30 18:32:14.284073
1047	1	0	0	31.3	Offline	2026-01-30 18:32:18.655693
1048	1	0	24.37	31.3	Offline	2026-01-30 18:32:23.26928
1049	1	0	0.43	31.3	Offline	2026-01-30 18:32:28.202197
1050	1	95	0	31.3	Relaxed	2026-01-30 18:32:33.227258
1051	1	83	0	31.4	Relaxed	2026-01-30 18:32:38.228157
1052	1	88	0	31.5	Relaxed	2026-01-30 18:32:43.35044
1053	1	90	0	31.5	Relaxed	2026-01-30 18:32:48.276403
1054	1	89	47.32	31.6	Relaxed	2026-01-30 18:32:53.316463
1055	1	87	0	31.6	Relaxed	2026-01-30 18:32:58.337929
1056	1	87	0	31.6	Relaxed	2026-01-30 18:33:07.350694
1057	1	87	0	31.5	Relaxed	2026-01-30 18:33:08.425663
1058	1	87	0	31.5	Relaxed	2026-01-30 18:33:13.458547
1059	1	0	24.18	31.4	Offline	2026-01-30 18:33:20.111764
1060	1	0	23.57	31.4	Offline	2026-01-30 18:33:23.85717
1061	1	0	0	31.5	Offline	2026-01-30 18:33:40.921587
1062	1	0	0	31.5	Offline	2026-01-30 18:33:43.538372
1063	1	0	0	31.4	Offline	2026-01-30 18:33:45.093276
1064	1	0	5.84	31.4	Offline	2026-01-30 18:33:45.249324
1065	1	95	4.37	31.3	Relaxed	2026-01-30 18:33:48.634707
1066	1	95	2.39	31.4	Relaxed	2026-01-30 18:33:53.609351
1067	1	0	1.03	31.4	Offline	2026-01-30 18:33:58.71119
1068	1	0	0	31.4	Offline	2026-01-30 18:34:03.611426
1069	1	0	0	31.4	Offline	2026-01-30 18:34:08.649489
1070	1	0	0	31.3	Offline	2026-01-30 18:34:13.668817
1071	1	0	0	31.2	Offline	2026-01-30 18:34:18.67799
1072	1	0	23.36	31.2	Offline	2026-01-30 18:34:23.706817
1073	1	99	15.94	31.2	Stressed	2026-01-30 18:34:28.625508
1074	1	99	1.33	31.1	Relaxed	2026-01-30 18:34:33.73949
1075	1	104	50.05	31.1	Relaxed	2026-01-30 18:34:38.667998
1076	1	106	50.08	31	Relaxed	2026-01-30 18:34:43.707938
1077	1	0	50.23	28.9	Offline	2026-01-30 19:26:06.758789
1078	1	0	50.4	28.9	Offline	2026-01-30 19:26:13.181389
1079	1	142	50.39	28.9	Offline	2026-01-30 19:26:18.101351
1080	1	141	50.36	28.9	Offline	2026-01-30 19:26:18.852633
1081	1	139	50.4	28.9	Offline	2026-01-30 19:26:19.211909
1082	1	137	50.22	28.9	Offline	2026-01-30 19:26:19.525443
1083	1	137	49.94	28.9	Offline	2026-01-30 19:26:19.976145
1084	1	138	50.01	28.9	Offline	2026-01-30 19:26:21.013906
1085	1	135	49.98	28.9	Offline	2026-01-30 19:26:29.952839
1086	1	132	49.99	28.9	Offline	2026-01-30 19:26:30.723963
1087	1	137	50.33	28.9	Offline	2026-01-30 19:26:35.610953
1088	1	134	50.4	28.9	Offline	2026-01-30 19:26:40.670543
1089	1	136	50.05	28.9	Offline	2026-01-30 19:26:51.085826
1090	1	135	50.29	28.9	Offline	2026-01-30 19:26:52.179339
1091	1	135	50.4	28.9	Offline	2026-01-30 19:26:58.909672
1092	1	134	50.22	28.9	Offline	2026-01-30 19:27:04.570525
1093	1	134	50.2	28.9	Offline	2026-01-30 19:27:05.65994
1094	1	137	50.05	28.9	Offline	2026-01-30 19:27:10.677988
1095	1	134	50.11	28.9	Offline	2026-01-30 19:27:15.728934
1096	1	134	49.95	28.9	Offline	2026-01-30 19:27:20.81534
1097	1	135	50.09	28.9	Offline	2026-01-30 19:27:25.770381
1098	1	131	49.98	28.9	Offline	2026-01-30 19:27:30.738124
1099	1	130	49.95	28.9	Relaxed	2026-01-30 19:27:35.658148
1100	1	129	49.98	28.9	Relaxed	2026-01-30 19:27:40.727333
1101	1	129	49.95	28.9	Relaxed	2026-01-30 19:28:01.802904
1102	1	134	49.94	28.9	Offline	2026-01-30 19:28:02.546992
1103	1	135	49.95	28.9	Offline	2026-01-30 19:28:02.68341
1104	1	140	49.98	28.9	Offline	2026-01-30 19:28:03.034811
1105	1	138	50.32	28.9	Offline	2026-01-30 19:28:06.346915
1106	1	142	50.33	28.9	Offline	2026-01-30 19:28:10.716607
1107	1	145	49.95	28.9	Offline	2026-01-30 19:28:16.616227
1108	1	144	50.37	28.9	Offline	2026-01-30 19:28:20.686343
1109	1	149	50.14	28.9	Offline	2026-01-30 19:28:25.896427
1110	1	150	50.02	28.9	Offline	2026-01-30 19:28:31.934265
1111	1	151	50.17	28.9	Offline	2026-01-30 19:28:35.744073
1112	1	150	50.4	28.9	Offline	2026-01-30 19:28:40.774793
1113	1	150	50.1	28.9	Offline	2026-01-30 19:28:45.885206
1114	1	145	49.95	28.9	Offline	2026-01-30 19:28:51.387124
1115	1	135	50.4	28.9	Offline	2026-01-30 19:28:55.095914
1116	1	140	50.23	28.9	Offline	2026-01-30 19:28:55.734813
1117	1	135	50.35	28.9	Offline	2026-01-30 19:29:03.255064
1118	1	139	50.39	28.9	Offline	2026-01-30 19:29:03.404417
1119	1	139	50.33	28.9	Offline	2026-01-30 19:29:05.106483
1120	1	139	50.39	28.9	Offline	2026-01-30 19:29:05.823946
1121	1	140	50.17	28.9	Offline	2026-01-30 19:29:10.564731
1122	1	142	50.37	28.9	Offline	2026-01-30 19:29:11.296319
1123	1	139	50.14	28.9	Offline	2026-01-30 19:29:15.124696
1124	1	143	50.31	28.9	Offline	2026-01-30 19:29:15.903915
1125	1	141	50.07	28.9	Offline	2026-01-30 19:29:21.145713
1126	1	145	50.03	28.9	Offline	2026-01-30 19:29:21.282268
1127	1	143	50.07	28.9	Offline	2026-01-30 19:29:25.809872
1128	1	149	50.03	28.9	Offline	2026-01-30 19:29:27.909818
1129	1	142	50.3	28.9	Offline	2026-01-30 19:29:30.332791
1130	1	146	50.03	29	Offline	2026-01-30 19:29:31.07121
1131	1	143	50.23	28.9	Offline	2026-01-30 19:29:35.649236
1132	1	146	50.05	28.9	Offline	2026-01-30 19:29:36.200805
1133	1	145	50.31	29	Offline	2026-01-30 19:29:42.125848
1134	1	149	50.14	29	Offline	2026-01-30 19:29:42.154261
1135	1	146	50.3	29	Offline	2026-01-30 19:29:45.553852
1136	1	148	50.29	29	Offline	2026-01-30 19:29:46.573937
1137	1	147	50.4	29	Offline	2026-01-30 19:30:03.673335
1138	1	148	50.27	29	Offline	2026-01-30 19:30:03.712802
1139	1	144	50.4	29	Offline	2026-01-30 19:30:05.925562
1140	1	146	50.33	29	Offline	2026-01-30 19:30:05.973813
1141	1	147	50.36	29	Offline	2026-01-30 19:30:06.738624
1142	1	144	50.14	29	Offline	2026-01-30 19:30:06.742694
1143	1	146	50.32	29	Offline	2026-01-30 19:30:08.453553
1144	1	145	50.05	29	Offline	2026-01-30 19:30:10.392023
1145	1	146	50.2	29	Offline	2026-01-30 19:30:27.165335
1146	1	146	50.02	29	Offline	2026-01-30 19:30:27.328897
1147	1	142	50.1	29	Offline	2026-01-30 19:30:28.15032
1148	1	145	49.98	29	Offline	2026-01-30 19:30:28.241131
1149	1	142	50.08	29	Offline	2026-01-30 19:30:28.877301
1150	1	145	50.06	29	Offline	2026-01-30 19:30:29.010681
1151	1	145	50.01	29	Offline	2026-01-30 19:30:37.555555
1152	1	147	50.02	29	Offline	2026-01-30 19:30:37.577202
1153	1	144	49.94	29	Offline	2026-01-30 19:30:41.06345
1154	1	147	50.05	29	Offline	2026-01-30 19:30:41.752174
1155	1	142	49.94	29	Offline	2026-01-30 19:30:49.617128
1156	1	143	50.06	29	Offline	2026-01-30 19:30:51.795603
1157	1	146	50.08	29	Offline	2026-01-30 19:30:53.496824
1158	1	146	50.33	29	Offline	2026-01-30 19:30:53.517284
1159	1	142	50.4	30.6	Offline	2026-01-30 19:38:38.899875
1160	1	142	50.18	30.6	Offline	2026-01-30 19:38:42.524199
1161	1	142	50.04	30.6	Offline	2026-01-30 19:38:47.179343
1162	1	141	49.95	30.5	Offline	2026-01-30 19:38:52.565985
1163	1	139	50.04	30.4	Offline	2026-01-30 19:38:58.79027
1164	1	140	50.17	30.4	Offline	2026-01-30 19:39:02.537077
1165	1	140	50.4	30.4	Offline	2026-01-30 19:39:07.511739
1166	1	140	50.36	30.3	Offline	2026-01-30 19:39:12.42328
1167	1	141	50.07	30.3	Offline	2026-01-30 19:39:17.626985
1168	1	143	50.02	30.3	Offline	2026-01-30 19:39:22.36872
1169	1	145	49.98	30.2	Offline	2026-01-30 19:39:28.89129
1170	1	145	50.34	30.2	Offline	2026-01-30 19:39:32.371774
1171	1	145	50.36	30.2	Offline	2026-01-30 19:39:38.532578
1172	1	148	50.4	30.2	Offline	2026-01-30 19:39:43.271603
1173	1	148	50.4	30.2	Offline	2026-01-30 19:39:47.267456
1174	1	142	50.39	30.2	Offline	2026-01-30 19:39:52.210974
1175	1	142	50.34	30.1	Offline	2026-01-30 19:39:57.931489
1176	1	143	50.02	30.2	Offline	2026-01-30 19:40:02.188003
1177	1	138	50.28	30.1	Offline	2026-01-30 19:40:02.290953
1178	1	142	50.23	30.1	Offline	2026-01-30 19:40:28.434251
1179	1	138	50.23	30.1	Offline	2026-01-30 19:40:28.467555
1180	1	139	50.22	30.1	Offline	2026-01-30 19:40:28.614525
1181	1	137	50.21	30.1	Offline	2026-01-30 19:40:28.618708
1182	1	134	50.3	30.1	Offline	2026-01-30 19:40:29.061102
1183	1	139	50.19	30.1	Offline	2026-01-30 19:40:29.067256
1184	1	135	50.3	30.1	Offline	2026-01-30 19:40:29.07207
1185	1	141	50.18	30.1	Offline	2026-01-30 19:40:29.076784
1186	1	134	50.31	30.1	Offline	2026-01-30 19:40:29.081905
1187	1	140	50.16	30.1	Offline	2026-01-30 19:40:29.087789
1188	1	134	50.31	30.1	Offline	2026-01-30 19:40:32.608412
1189	1	140	50.3	30.1	Offline	2026-01-30 19:40:32.966043
1190	1	136	50.34	30.1	Offline	2026-01-30 19:40:44.688192
1191	1	143	50.28	30.1	Offline	2026-01-30 19:40:44.834872
1192	1	140	50.27	30.1	Offline	2026-01-30 19:40:45.242888
1193	1	141	50.33	30.1	Offline	2026-01-30 19:40:45.391463
1194	1	140	50.21	30	Offline	2026-01-30 19:40:47.306598
1195	1	138	50.32	30	Offline	2026-01-30 19:40:47.360289
1196	1	139	50.19	30	Offline	2026-01-30 19:40:51.669668
1197	1	136	50.3	30	Offline	2026-01-30 19:40:52.727515
1198	1	139	50.3	30	Offline	2026-01-30 19:40:57.390138
1199	1	137	50.28	30	Offline	2026-01-30 19:40:57.646569
1200	1	138	50.3	30	Offline	2026-01-30 19:41:02.740445
1201	1	137	50.29	30	Offline	2026-01-30 19:41:02.779044
1202	1	137	50.31	30	Offline	2026-01-30 19:41:20.269867
1203	1	138	50.28	29.9	Offline	2026-01-30 19:41:20.345586
1204	1	137	50.33	30	Offline	2026-01-30 19:41:21.250235
1205	1	137	50.24	29.9	Offline	2026-01-30 19:41:21.275499
1206	1	138	50.32	29.9	Offline	2026-01-30 19:41:21.452601
1207	1	140	50.19	29.9	Offline	2026-01-30 19:41:21.505038
1208	1	139	50.32	29.9	Offline	2026-01-30 19:41:22.946368
1209	1	138	50.17	29.9	Offline	2026-01-30 19:41:22.999195
1210	1	140	50.3	29.9	Offline	2026-01-30 19:41:28.840804
1211	1	140	50.17	29.9	Offline	2026-01-30 19:41:29.315012
1212	1	139	50.3	29.9	Offline	2026-01-30 19:41:31.525125
1213	1	140	50.19	29.9	Offline	2026-01-30 19:41:33.080352
1214	1	141	50.32	29.9	Offline	2026-01-30 19:41:38.938768
1215	1	138	50.23	29.9	Offline	2026-01-30 19:41:38.988292
1216	1	142	50.32	29.9	Offline	2026-01-30 19:41:43.666866
1217	1	141	50.2	29.9	Offline	2026-01-30 19:41:44.218775
1218	1	143	50.3	29.9	Offline	2026-01-30 19:41:59.91296
1219	1	141	50.2	29.9	Offline	2026-01-30 19:42:00.338648
1220	1	115	50.39	29.9	Relaxed	2026-01-30 19:42:01.844558
1221	1	114	48.68	29.9	Relaxed	2026-01-30 19:42:01.848989
1222	1	103	26.86	29.9	Relaxed	2026-01-30 19:42:02.432217
1223	1	101	20.55	29.9	Relaxed	2026-01-30 19:42:02.5243
1224	1	103	23.32	30.6	Relaxed	2026-01-30 19:42:02.750228
1225	1	101	22.34	30.9	Stressed	2026-01-30 19:42:05.620022
1226	1	98	17.98	31.4	Stressed	2026-01-30 19:42:07.672814
1227	1	97	18.71	31.5	Relaxed	2026-01-30 19:42:07.873163
1228	1	93	18.74	31.9	Stressed	2026-01-30 19:42:12.46814
1229	1	95	16.3	31.9	Stressed	2026-01-30 19:42:12.595139
1230	1	93	42.83	32.9	Stressed	2026-01-30 19:42:19.621435
1231	1	95	50.24	33.1	Relaxed	2026-01-30 19:42:19.645532
1232	1	0	50.29	33.4	Offline	2026-01-30 19:42:24.375942
1233	1	0	50.2	33.4	Offline	2026-01-30 19:42:25.063042
1234	1	93	50.27	33.3	Relaxed	2026-01-30 19:42:36.556603
1235	1	94	50.17	33.2	Relaxed	2026-01-30 19:42:36.615967
1236	1	93	50.32	33.1	Relaxed	2026-01-30 19:42:36.867555
1237	1	93	50.2	33.1	Relaxed	2026-01-30 19:42:37.097533
1238	1	113	50.26	32.9	Relaxed	2026-01-30 19:42:37.541811
1239	1	114	50.25	32.9	Relaxed	2026-01-30 19:42:38.360661
1240	1	113	50.2	32.8	Relaxed	2026-01-30 19:42:42.62991
1241	1	114	50.27	32.8	Relaxed	2026-01-30 19:42:44.012568
1242	1	120	50.22	32.7	Relaxed	2026-01-30 19:42:47.965531
1243	1	111	50.26	32.7	Relaxed	2026-01-30 19:42:48.91637
1244	1	122	50.25	32.6	Relaxed	2026-01-30 19:42:52.442196
1245	1	123	50.21	32.6	Relaxed	2026-01-30 19:42:53.431419
1246	1	114	50.27	32.4	Relaxed	2026-01-30 19:42:57.235773
1247	1	109	50.18	32.4	Relaxed	2026-01-30 19:42:57.621569
1248	1	109	50.27	32.4	Relaxed	2026-01-30 19:43:02.206035
1249	1	107	50.18	32.4	Relaxed	2026-01-30 19:43:03.051004
1250	1	111	50.32	32.3	Relaxed	2026-01-30 19:43:07.642383
1251	1	118	50.17	32.3	Relaxed	2026-01-30 19:43:08.611534
1252	1	104	50.24	32.2	Relaxed	2026-01-30 19:43:12.036476
1253	1	101	50.17	32.2	Relaxed	2026-01-30 19:43:12.502373
1254	1	109	50.2	32.1	Relaxed	2026-01-30 19:43:17.283794
1255	1	115	50.19	32.1	Relaxed	2026-01-30 19:43:17.526251
1256	1	110	50.27	32.1	Relaxed	2026-01-30 19:43:21.938153
1257	1	111	50.24	32	Relaxed	2026-01-30 19:43:23.05906
1258	1	103	50.23	31.9	Relaxed	2026-01-30 19:43:27.145591
1259	1	102	50.15	31.9	Relaxed	2026-01-30 19:43:27.886362
1260	1	116	50.18	31.9	Relaxed	2026-01-30 19:43:33.834705
1261	1	117	50.27	31.9	Relaxed	2026-01-30 19:43:33.90628
\.


--
-- TOC entry 3900 (class 0 OID 25055)
-- Dependencies: 214
-- Data for Name: lessons; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.lessons (id, title, description, lesson_number, student_id, progress, status, milestone_id, content_lesson_id) FROM stdin;
6	الطاقة		1	1	100	completed	1	1
7	البناء الضوئي		2	1	100	completed	1	2
8	النجوم		1	1	100	completed	2	9
\.


--
-- TOC entry 3930 (class 0 OID 25554)
-- Dependencies: 244
-- Data for Name: level_course_links; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.level_course_links (level_id, course_id) FROM stdin;
\.


--
-- TOC entry 3922 (class 0 OID 25426)
-- Dependencies: 236
-- Data for Name: log_table; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.log_table (id, "timestamp", user_input, intent, topic, question, correct, correct_answer, user_choice, topic_id) FROM stdin;
105	2026-01-17 10:03:07.875682	SYSTEM_START	Lesson_Start	الطاقة: 	\N	\N	\N	\N	6
106	2026-01-17 10:03:19.981341	SYSTEM_START	Lesson_Start	الطاقة: 	\N	\N	\N	\N	6
107	2026-01-21 02:06:35.65566	٢	Quiz	الطاقة: 	إيه اللي بيخلي الحاجات تحصل وتتحرك؟	t	\N	\N	6
108	2026-01-23 13:54:31.943859	1	Quiz	البناء الضوئي: 	النبات الأخضر بيستخدم إيه عشان يعمل أكله؟	t	\N	\N	7
109	2026-01-23 15:38:56.002948	1	Quiz	الطاقة: 	مين اللي بيدي طاقة للنبات في الأول؟	t	\N	\N	6
110	2026-01-29 01:08:56.82428	١	Quiz	النجوم	إيه الأداة اللي بتخلينا نشوف النجوم البعيدة قريبة وواضحة؟	t	\N	\N	8
111	2026-01-29 01:56:45.627135	١	Quiz	النجوم	إيه الأداة اللي بتخلي النجوم البعيدة تبان قريبة وواضحة؟	f	\N	\N	8
112	2026-01-29 01:57:16.349476	١	Quiz	النجوم	النجوم لما بتكون كتير مع بعض في السما، بنشوفها كأنها عاملة إيه؟	t	\N	\N	8
113	2026-01-30 20:12:28.30506	٢	Quiz	النجوم	إيه الأداة اللي بتخلينا نشوف النجوم البعيدة قريبة وواضحة؟	f	\N	\N	8
114	2026-01-30 20:13:31.057318	١	Quiz	النجوم	النجوم اللي بنشوفها مع بعض في السما، ممكن شكلها يكون عامل زي إيه؟	t	\N	\N	8
\.


--
-- TOC entry 3920 (class 0 OID 25412)
-- Dependencies: 234
-- Data for Name: materials; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.materials (id, lesson_id, title, description, material_type, file_url, extracted_text) FROM stdin;
\.


--
-- TOC entry 3916 (class 0 OID 25383)
-- Dependencies: 230
-- Data for Name: milestones; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.milestones (id, title, number, description, student_id, course_id) FROM stdin;
1	Milestone 1	1	decimalsssssssssss	1	1
2	Milestone 2	2	رررر	1	1
3	Milestone 1	1	بيبيبيبي	1	2
4	Milestone 2	2	بثبصثبق	1	2
5	Milestone 3	3	صثبصثبصب	1	2
6	Milestone 4	4	صثلصقلثفل	1	2
\.


--
-- TOC entry 3914 (class 0 OID 25359)
-- Dependencies: 228
-- Data for Name: quiz; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.quiz (id, student_id, lesson_id, milestone_id, title, quiz_type, max_attempts, created_at) FROM stdin;
\.


--
-- TOC entry 3912 (class 0 OID 25347)
-- Dependencies: 226
-- Data for Name: quiz_attempts; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.quiz_attempts (id, quiz_id, score, submitted_at) FROM stdin;
\.


--
-- TOC entry 3918 (class 0 OID 25398)
-- Dependencies: 232
-- Data for Name: quizzes; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.quizzes (id, student_id, title, description, lesson_id, status, score, attempts_used, attempts_allowed, questions, answers, completed_at, created_at) FROM stdin;
\.


--
-- TOC entry 3898 (class 0 OID 25041)
-- Dependencies: 212
-- Data for Name: students; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.students (id, user_id, age, autism_type, sensitivities, learning_style, baseline_engagement, course_number, classroom_id) FROM stdin;
1	1	\N	\N	\N	\N	\N	1	1
6	15	\N	\N	\N	\N	\N	\N	\N
\.


--
-- TOC entry 3906 (class 0 OID 25230)
-- Dependencies: 220
-- Data for Name: submission_files; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.submission_files (id, submission_id, file_name, file_url) FROM stdin;
14	9	hi.docx	/uploads/submissions/9_hi.docx
15	8	hi.docx	/uploads/submissions/8_hi.docx
16	10	واجب درس النجوم.docx	/uploads/submissions/10_واجب_درس_النجوم.docx
\.


--
-- TOC entry 3904 (class 0 OID 25216)
-- Dependencies: 218
-- Data for Name: submissions; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.submissions (id, assignment_id, student_id, description, submitted_at, updated_at) FROM stdin;
9	8	1		2026-01-19 10:51:46.432471	2026-01-19 10:53:41.749227
8	1	1		2026-01-18 16:27:17.015729	2026-01-19 10:57:37.949752
10	9	1		2026-01-29 00:12:05.435651	\N
\.


--
-- TOC entry 3896 (class 0 OID 25032)
-- Dependencies: 210
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: mo
--

COPY public.users (id, username, email, hashed_password, role, created_at) FROM stdin;
1	nada	nada.g.zaki.25@gmail.com	$2b$12$eEwnLrfnyxT/n0Glhtzx8eDouwWBswK0WzjdpsyQ1cpCXjc90KTya	student	2025-12-13 19:01:14.993914
11	nada	n.gamal2229@nu.edu.eg	$2b$12$wTCtAASDX6rAJMerdS5e/e3KQKbkGygAspck7sjZRmD5SbmBbzZ.G	parent	2025-12-14 00:36:40.032098
12	nada	nada.g.z@gmail.com	$2b$12$Ae/5rWieN7VKfdrdubm2CeEjG8SXK7H0zzaCprkfnY4CIfrwQaMUa	teacher	2026-01-10 16:39:08.822716
13	Ahmed	ahmed.12345@gmail.com	$2b$12$tQF7a5e2WmZVhaQOFwWy7.KlxmXetbaj3MdDU1uFpoOGlie0sN54u	teacher	2026-01-28 21:13:40.797391
15	NewStudent	new@student.com	123	student	2026-01-29 00:21:17.626487
16	user_izp7fn8ufm	test_ptqs19l4pi@example.com	$2b$12$bfVP/s85Xuz3VSBR98KyuuegPts.xY1ve664AIIaugbobyE6lhQJK	teacher	2026-01-28 23:25:25.471831
17	user_d7zu21gtv8	test_e77v9wh1q9@example.com	$2b$12$RA5wj2FwOat5UiDXmUntZeAo4D5Z64I6uIjS2QnYkWHzQJCOOBjk2	teacher	2026-01-28 23:37:16.239321
18	user_3murhn56h4	test_q4qxkp4ww5@example.com	$2b$12$lCgyEG6g0yfPYJzY5OGjZulPT2wYYnz3uURYHNGcs9DtwxBujmrNG	teacher	2026-01-28 23:39:45.033448
\.


--
-- TOC entry 3972 (class 0 OID 0)
-- Dependencies: 215
-- Name: ask_baseet_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mo
--

SELECT pg_catalog.setval('public.ask_baseet_id_seq', 1, false);


--
-- TOC entry 3973 (class 0 OID 0)
-- Dependencies: 223
-- Name: assignments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mo
--

SELECT pg_catalog.setval('public.assignments_id_seq', 9, true);


--
-- TOC entry 3974 (class 0 OID 0)
-- Dependencies: 239
-- Name: class_levels_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mo
--

SELECT pg_catalog.setval('public.class_levels_id_seq', 8, true);


--
-- TOC entry 3975 (class 0 OID 0)
-- Dependencies: 241
-- Name: classrooms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mo
--

SELECT pg_catalog.setval('public.classrooms_id_seq', 4, true);


--
-- TOC entry 3976 (class 0 OID 0)
-- Dependencies: 253
-- Name: content_assignment_files_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mo
--

SELECT pg_catalog.setval('public.content_assignment_files_id_seq', 5, true);


--
-- TOC entry 3977 (class 0 OID 0)
-- Dependencies: 251
-- Name: content_assignments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.content_assignments_id_seq', 5, true);


--
-- TOC entry 3978 (class 0 OID 0)
-- Dependencies: 245
-- Name: content_lessons_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mo
--

SELECT pg_catalog.setval('public.content_lessons_id_seq', 9, true);


--
-- TOC entry 3979 (class 0 OID 0)
-- Dependencies: 237
-- Name: content_levels_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mo
--

SELECT pg_catalog.setval('public.content_levels_id_seq', 7, true);


--
-- TOC entry 3980 (class 0 OID 0)
-- Dependencies: 247
-- Name: content_materials_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mo
--

SELECT pg_catalog.setval('public.content_materials_id_seq', 13, true);


--
-- TOC entry 3981 (class 0 OID 0)
-- Dependencies: 249
-- Name: courses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mo
--

SELECT pg_catalog.setval('public.courses_id_seq', 1, false);


--
-- TOC entry 3982 (class 0 OID 0)
-- Dependencies: 221
-- Name: feedback_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mo
--

SELECT pg_catalog.setval('public.feedback_id_seq', 6, true);


--
-- TOC entry 3983 (class 0 OID 0)
-- Dependencies: 255
-- Name: iot_readings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mo
--

SELECT pg_catalog.setval('public.iot_readings_id_seq', 1261, true);


--
-- TOC entry 3984 (class 0 OID 0)
-- Dependencies: 213
-- Name: lessons_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mo
--

SELECT pg_catalog.setval('public.lessons_id_seq', 8, true);


--
-- TOC entry 3985 (class 0 OID 0)
-- Dependencies: 235
-- Name: log_table_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mo
--

SELECT pg_catalog.setval('public.log_table_id_seq', 114, true);


--
-- TOC entry 3986 (class 0 OID 0)
-- Dependencies: 233
-- Name: materials_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mo
--

SELECT pg_catalog.setval('public.materials_id_seq', 7, true);


--
-- TOC entry 3987 (class 0 OID 0)
-- Dependencies: 229
-- Name: milestones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mo
--

SELECT pg_catalog.setval('public.milestones_id_seq', 1, false);


--
-- TOC entry 3988 (class 0 OID 0)
-- Dependencies: 225
-- Name: quiz_attempts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mo
--

SELECT pg_catalog.setval('public.quiz_attempts_id_seq', 1, false);


--
-- TOC entry 3989 (class 0 OID 0)
-- Dependencies: 227
-- Name: quiz_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mo
--

SELECT pg_catalog.setval('public.quiz_id_seq', 1, false);


--
-- TOC entry 3990 (class 0 OID 0)
-- Dependencies: 231
-- Name: quizzes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mo
--

SELECT pg_catalog.setval('public.quizzes_id_seq', 1, false);


--
-- TOC entry 3991 (class 0 OID 0)
-- Dependencies: 211
-- Name: students_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mo
--

SELECT pg_catalog.setval('public.students_id_seq', 6, true);


--
-- TOC entry 3992 (class 0 OID 0)
-- Dependencies: 219
-- Name: submission_files_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mo
--

SELECT pg_catalog.setval('public.submission_files_id_seq', 16, true);


--
-- TOC entry 3993 (class 0 OID 0)
-- Dependencies: 217
-- Name: submissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mo
--

SELECT pg_catalog.setval('public.submissions_id_seq', 10, true);


--
-- TOC entry 3994 (class 0 OID 0)
-- Dependencies: 209
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mo
--

SELECT pg_catalog.setval('public.users_id_seq', 18, true);


--
-- TOC entry 3680 (class 2606 OID 25132)
-- Name: ask_baseet ask_baseet_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.ask_baseet
    ADD CONSTRAINT ask_baseet_pkey PRIMARY KEY (id);


--
-- TOC entry 3690 (class 2606 OID 25267)
-- Name: assignments assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.assignments
    ADD CONSTRAINT assignments_pkey PRIMARY KEY (id);


--
-- TOC entry 3707 (class 2606 OID 25503)
-- Name: class_levels class_levels_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.class_levels
    ADD CONSTRAINT class_levels_pkey PRIMARY KEY (id);


--
-- TOC entry 3713 (class 2606 OID 25522)
-- Name: classroom_course_links classroom_course_links_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.classroom_course_links
    ADD CONSTRAINT classroom_course_links_pkey PRIMARY KEY (classroom_id, course_id);


--
-- TOC entry 3710 (class 2606 OID 25512)
-- Name: classrooms classrooms_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.classrooms
    ADD CONSTRAINT classrooms_pkey PRIMARY KEY (id);


--
-- TOC entry 3725 (class 2606 OID 25734)
-- Name: content_assignment_files content_assignment_files_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.content_assignment_files
    ADD CONSTRAINT content_assignment_files_pkey PRIMARY KEY (id);


--
-- TOC entry 3723 (class 2606 OID 25719)
-- Name: content_assignments content_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.content_assignments
    ADD CONSTRAINT content_assignments_pkey PRIMARY KEY (id);


--
-- TOC entry 3717 (class 2606 OID 25612)
-- Name: content_lessons content_lessons_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.content_lessons
    ADD CONSTRAINT content_lessons_pkey PRIMARY KEY (id);


--
-- TOC entry 3704 (class 2606 OID 25493)
-- Name: content_courses content_levels_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.content_courses
    ADD CONSTRAINT content_levels_pkey PRIMARY KEY (id);


--
-- TOC entry 3719 (class 2606 OID 25621)
-- Name: content_materials content_materials_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.content_materials
    ADD CONSTRAINT content_materials_pkey PRIMARY KEY (id);


--
-- TOC entry 3721 (class 2606 OID 25683)
-- Name: courses courses_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (id);


--
-- TOC entry 3686 (class 2606 OID 25251)
-- Name: feedback feedback_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_pkey PRIMARY KEY (id);


--
-- TOC entry 3688 (class 2606 OID 25253)
-- Name: feedback feedback_submission_id_key; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_submission_id_key UNIQUE (submission_id);


--
-- TOC entry 3727 (class 2606 OID 25749)
-- Name: iot_readings iot_readings_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.iot_readings
    ADD CONSTRAINT iot_readings_pkey PRIMARY KEY (id);


--
-- TOC entry 3678 (class 2606 OID 25062)
-- Name: lessons lessons_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.lessons
    ADD CONSTRAINT lessons_pkey PRIMARY KEY (id);


--
-- TOC entry 3715 (class 2606 OID 25558)
-- Name: level_course_links level_course_links_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.level_course_links
    ADD CONSTRAINT level_course_links_pkey PRIMARY KEY (level_id, course_id);


--
-- TOC entry 3702 (class 2606 OID 25433)
-- Name: log_table log_table_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.log_table
    ADD CONSTRAINT log_table_pkey PRIMARY KEY (id);


--
-- TOC entry 3700 (class 2606 OID 25419)
-- Name: materials materials_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_pkey PRIMARY KEY (id);


--
-- TOC entry 3696 (class 2606 OID 25390)
-- Name: milestones milestones_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.milestones
    ADD CONSTRAINT milestones_pkey PRIMARY KEY (id);


--
-- TOC entry 3692 (class 2606 OID 25352)
-- Name: quiz_attempts quiz_attempts_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.quiz_attempts
    ADD CONSTRAINT quiz_attempts_pkey PRIMARY KEY (id);


--
-- TOC entry 3694 (class 2606 OID 25366)
-- Name: quiz quiz_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.quiz
    ADD CONSTRAINT quiz_pkey PRIMARY KEY (id);


--
-- TOC entry 3698 (class 2606 OID 25405)
-- Name: quizzes quizzes_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.quizzes
    ADD CONSTRAINT quizzes_pkey PRIMARY KEY (id);


--
-- TOC entry 3676 (class 2606 OID 25048)
-- Name: students students_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_pkey PRIMARY KEY (id);


--
-- TOC entry 3684 (class 2606 OID 25237)
-- Name: submission_files submission_files_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.submission_files
    ADD CONSTRAINT submission_files_pkey PRIMARY KEY (id);


--
-- TOC entry 3682 (class 2606 OID 25223)
-- Name: submissions submissions_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_pkey PRIMARY KEY (id);


--
-- TOC entry 3674 (class 2606 OID 25039)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 3708 (class 1259 OID 25756)
-- Name: ix_class_levels_teacher_id; Type: INDEX; Schema: public; Owner: mo
--

CREATE INDEX ix_class_levels_teacher_id ON public.class_levels USING btree (teacher_id);


--
-- TOC entry 3711 (class 1259 OID 25757)
-- Name: ix_classrooms_teacher_id; Type: INDEX; Schema: public; Owner: mo
--

CREATE INDEX ix_classrooms_teacher_id ON public.classrooms USING btree (teacher_id);


--
-- TOC entry 3705 (class 1259 OID 25755)
-- Name: ix_content_courses_teacher_id; Type: INDEX; Schema: public; Owner: mo
--

CREATE INDEX ix_content_courses_teacher_id ON public.content_courses USING btree (teacher_id);


--
-- TOC entry 3753 (class 2620 OID 25184)
-- Name: lessons lesson_progress_insert_trigger; Type: TRIGGER; Schema: public; Owner: mo
--

CREATE TRIGGER lesson_progress_insert_trigger AFTER INSERT ON public.lessons FOR EACH ROW EXECUTE FUNCTION public.update_lesson_status();


--
-- TOC entry 3754 (class 2620 OID 25674)
-- Name: lessons lesson_progress_trigger; Type: TRIGGER; Schema: public; Owner: mo
--

CREATE TRIGGER lesson_progress_trigger BEFORE UPDATE OF progress ON public.lessons FOR EACH ROW EXECUTE FUNCTION public.update_lesson_status();


--
-- TOC entry 3755 (class 2620 OID 25640)
-- Name: lessons lesson_progress_update_trigger; Type: TRIGGER; Schema: public; Owner: mo
--

CREATE TRIGGER lesson_progress_update_trigger AFTER UPDATE ON public.lessons FOR EACH ROW EXECUTE FUNCTION public.update_lesson_progress();


--
-- TOC entry 3733 (class 2606 OID 25133)
-- Name: ask_baseet ask_baseet_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.ask_baseet
    ADD CONSTRAINT ask_baseet_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id);


--
-- TOC entry 3736 (class 2606 OID 25268)
-- Name: assignments assignments_lesson_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.assignments
    ADD CONSTRAINT assignments_lesson_id_fkey FOREIGN KEY (lesson_id) REFERENCES public.lessons(id);


--
-- TOC entry 3745 (class 2606 OID 25523)
-- Name: classroom_course_links classroom_course_links_classroom_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.classroom_course_links
    ADD CONSTRAINT classroom_course_links_classroom_id_fkey FOREIGN KEY (classroom_id) REFERENCES public.classrooms(id);


--
-- TOC entry 3746 (class 2606 OID 25528)
-- Name: classroom_course_links classroom_course_links_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.classroom_course_links
    ADD CONSTRAINT classroom_course_links_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.content_courses(id);


--
-- TOC entry 3744 (class 2606 OID 25513)
-- Name: classrooms classrooms_level_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.classrooms
    ADD CONSTRAINT classrooms_level_id_fkey FOREIGN KEY (level_id) REFERENCES public.class_levels(id);


--
-- TOC entry 3751 (class 2606 OID 25735)
-- Name: content_assignment_files content_assignment_files_assignment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.content_assignment_files
    ADD CONSTRAINT content_assignment_files_assignment_id_fkey FOREIGN KEY (assignment_id) REFERENCES public.content_assignments(id);


--
-- TOC entry 3750 (class 2606 OID 25720)
-- Name: content_assignments content_assignments_lesson_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.content_assignments
    ADD CONSTRAINT content_assignments_lesson_id_fkey FOREIGN KEY (lesson_id) REFERENCES public.content_lessons(id);


--
-- TOC entry 3749 (class 2606 OID 25622)
-- Name: content_materials content_materials_lesson_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.content_materials
    ADD CONSTRAINT content_materials_lesson_id_fkey FOREIGN KEY (lesson_id) REFERENCES public.content_lessons(id);


--
-- TOC entry 3735 (class 2606 OID 25254)
-- Name: feedback feedback_submission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES public.submissions(id);


--
-- TOC entry 3730 (class 2606 OID 25694)
-- Name: lessons fk_lessons_milestones; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.lessons
    ADD CONSTRAINT fk_lessons_milestones FOREIGN KEY (milestone_id) REFERENCES public.milestones(id);


--
-- TOC entry 3739 (class 2606 OID 25684)
-- Name: milestones fk_milestones_courses; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.milestones
    ADD CONSTRAINT fk_milestones_courses FOREIGN KEY (course_id) REFERENCES public.courses(id);


--
-- TOC entry 3752 (class 2606 OID 25750)
-- Name: iot_readings iot_readings_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.iot_readings
    ADD CONSTRAINT iot_readings_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id);


--
-- TOC entry 3731 (class 2606 OID 25699)
-- Name: lessons lessons_content_lesson_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.lessons
    ADD CONSTRAINT lessons_content_lesson_id_fkey FOREIGN KEY (content_lesson_id) REFERENCES public.content_lessons(id);


--
-- TOC entry 3732 (class 2606 OID 25634)
-- Name: lessons lessons_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.lessons
    ADD CONSTRAINT lessons_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- TOC entry 3747 (class 2606 OID 25564)
-- Name: level_course_links level_course_links_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.level_course_links
    ADD CONSTRAINT level_course_links_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.content_courses(id);


--
-- TOC entry 3748 (class 2606 OID 25559)
-- Name: level_course_links level_course_links_level_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.level_course_links
    ADD CONSTRAINT level_course_links_level_id_fkey FOREIGN KEY (level_id) REFERENCES public.class_levels(id);


--
-- TOC entry 3743 (class 2606 OID 25434)
-- Name: log_table log_table_topic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.log_table
    ADD CONSTRAINT log_table_topic_id_fkey FOREIGN KEY (topic_id) REFERENCES public.lessons(id);


--
-- TOC entry 3742 (class 2606 OID 25420)
-- Name: materials materials_lesson_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_lesson_id_fkey FOREIGN KEY (lesson_id) REFERENCES public.lessons(id);


--
-- TOC entry 3740 (class 2606 OID 25627)
-- Name: milestones milestones_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.milestones
    ADD CONSTRAINT milestones_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- TOC entry 3737 (class 2606 OID 25372)
-- Name: quiz quiz_lesson_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.quiz
    ADD CONSTRAINT quiz_lesson_id_fkey FOREIGN KEY (lesson_id) REFERENCES public.lessons(id);


--
-- TOC entry 3738 (class 2606 OID 25367)
-- Name: quiz quiz_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.quiz
    ADD CONSTRAINT quiz_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id);


--
-- TOC entry 3741 (class 2606 OID 25406)
-- Name: quizzes quizzes_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.quizzes
    ADD CONSTRAINT quizzes_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id);


--
-- TOC entry 3728 (class 2606 OID 25535)
-- Name: students students_classroom_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_classroom_id_fkey FOREIGN KEY (classroom_id) REFERENCES public.classrooms(id);


--
-- TOC entry 3729 (class 2606 OID 25049)
-- Name: students students_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 3734 (class 2606 OID 25238)
-- Name: submission_files submission_files_submission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mo
--

ALTER TABLE ONLY public.submission_files
    ADD CONSTRAINT submission_files_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES public.submissions(id);


--
-- TOC entry 3948 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: mo
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2026-01-30 21:43:34 EET

--
-- PostgreSQL database dump complete
--

\unrestrict 1l0nNhRf5daa0neAW7GzdmcMjjVomSVsQnGJu2doSG5rhSlHC1Vnkb7pwDAG3G3

