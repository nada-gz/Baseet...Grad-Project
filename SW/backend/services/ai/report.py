import os
from google import genai
from google.genai import types

# الاستدعاء من ملف القوالب الذي أنشأناه
from schemas.ai_reports_schema import (
    SessionTelemetry, 
    StudentReport, 
    TeacherReport, 
    ParentReport, 
    SupervisorReport
)

def generate_baseet_report(api_key: str, role_requested: str, telemetry_data: SessionTelemetry) -> str:
    """
    Analyzes structured session telemetry to generate a formatted JSON report.
    """
    client = genai.Client(api_key=api_key)
    
    schema_mapping = {
        "student": StudentReport,
        "teacher": TeacherReport,
        "parent": ParentReport,
        "supervisor": SupervisorReport
    }

    if role_requested not in schema_mapping:
        raise ValueError(f"Invalid role '{role_requested}'. Valid options are: {list(schema_mapping.keys())}")
    
    target_schema = schema_mapping[role_requested]

    prompt = f"""
    You are the core analytical AI agent for "Baseet," an educational ecosystem designed for autistic and neurodivergent learners.
    Your objective is to parse the following structured session telemetry and generate a JSON report tailored specifically for the '{role_requested}' dashboard.
    
    Instructions:
    1. Extract all relevant metrics from the structured data provided.
    2. Logically infer any missing qualitative assessments based on the interaction counts and stress states.
    3. Ensure the output strictly adheres to the required JSON schema.
    
    Structured Session Telemetry:
    {telemetry_data.model_dump_json(indent=2)}
    """

    print(f"[*] Processing telemetry... Generating '{role_requested}' report.")

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=target_schema,
            temperature=0.2, 
        ),
    )
    
    return response.text