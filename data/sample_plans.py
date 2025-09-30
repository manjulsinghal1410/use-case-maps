"""
Sample use case plans data based on analyzed templates
"""

from datetime import datetime, timedelta

def get_sample_users():
    """Get list of sample users"""
    return [
        {"name": "Manjul Singhal", "email": "manjul.singhal@databricks.com"},
        {"name": "Dennis Clark", "email": "dennis.clark@easyjet.com"},
        {"name": "Amelia Russell", "email": "amelia.russell@databricks.com"},
        {"name": "Matt Johnson", "email": "matt.johnson@databricks.com"},
        {"name": "Saket Patel", "email": "saket.patel@databricks.com"},
    ]

def get_sample_templates():
    """Get sample use case plan templates"""
    return [
        {
            "name": "Data Migration Use Case",
            "description": "Template for data migration projects to Databricks",
            "template_data": {
                "stages": ["U2", "U3", "U4", "U5", "U6"],
                "default_actions": [
                    {"stage": "U2", "action": "Enable feature in Sandbox", "duration_days": 7},
                    {"stage": "U2", "action": "Demo with Product Team", "duration_days": 1},
                    {"stage": "U3", "action": "MVP Scoping call with customer", "duration_days": 7},
                    {"stage": "U3", "action": "MVP Documentation", "duration_days": 21},
                    {"stage": "U3", "action": "Workspace and environment setup", "duration_days": 14},
                    {"stage": "U4", "action": "Implementation planning", "duration_days": 7},
                    {"stage": "U4", "action": "Team resource alignment", "duration_days": 7},
                    {"stage": "U5", "action": "Environment setup and configurations", "duration_days": 14},
                    {"stage": "U5", "action": "User training and enablement", "duration_days": 7},
                    {"stage": "U6", "action": "Go Live", "duration_days": 1},
                ]
            }
        },
        {
            "name": "GenAI Use Case",
            "description": "Template for GenAI implementation projects",
            "template_data": {
                "stages": ["U3", "U4", "U5", "U6"],
                "default_actions": [
                    {"stage": "U3", "action": "Find partner to deliver", "duration_days": 14},
                    {"stage": "U4", "action": "Build out delivery plan", "duration_days": 7},
                    {"stage": "U4", "action": "Validate Design document", "duration_days": 3},
                    {"stage": "U5", "action": "Setup AI Guardrails", "duration_days": 10},
                    {"stage": "U5", "action": "App security scanning", "duration_days": 10},
                    {"stage": "U5", "action": "Configure Private Link", "duration_days": 14},
                    {"stage": "U5", "action": "Setup MLOps processes", "duration_days": 21},
                    {"stage": "U6", "action": "Go Live", "duration_days": 1},
                ]
            }
        }
    ]

def get_sample_plans():
    """Get sample use case plans with actions"""
    base_date = datetime.now().date()

    return [
        {
            "plan": {
                "name": "EasyJet RMS Lakebase Migration",
                "description": "Revenue Management System migration to Databricks Lakebase with Apps OLTP competitive MVP",
                "customer": "EasyJet",
                "status": "In Progress"
            },
            "actions": [
                {
                    "stage": "U2",
                    "action": "Enabling the feature in Sandbox",
                    "owner_name": "Manjul Singhal",
                    "start_date": base_date - timedelta(days=30),
                    "end_date": base_date - timedelta(days=23),
                    "progress": "Complete",
                    "notes": "Decision criteria: Technology should be able to consume data at real-time basis"
                },
                {
                    "stage": "U2",
                    "action": "OLTP Demo with Product Team",
                    "owner_name": "Abbey Russell",
                    "start_date": base_date - timedelta(days=20),
                    "end_date": base_date - timedelta(days=20),
                    "progress": "Complete",
                    "notes": "Demo went well"
                },
                {
                    "stage": "U3",
                    "action": "MVP: Scoping call with EasyJet to discuss Success criteria and Scope",
                    "owner_name": "Amelia / Manjul/ Shiv /Dennis",
                    "start_date": base_date - timedelta(days=18),
                    "end_date": base_date - timedelta(days=11),
                    "progress": "Complete",
                    "notes": "Dennis presented the slides, we discussed on the two phases of POC"
                },
                {
                    "stage": "U3",
                    "action": "MVP Documentation",
                    "owner_name": "Manjul/Matt/Saket",
                    "start_date": base_date - timedelta(days=17),
                    "end_date": base_date + timedelta(days=3),
                    "progress": "Complete",
                    "notes": "Had a meeting with EasyJet on 19th June, working with Saket to document the requirements"
                },
                {
                    "stage": "U4",
                    "action": "Discussion on Proposed Use case Plan and implementation plan",
                    "owner_name": "Amelia / Manjul/ Dennis",
                    "start_date": base_date - timedelta(days=5),
                    "end_date": base_date + timedelta(days=2),
                    "progress": "In Progress",
                    "notes": "Dennis is working with a team of 6 engineers, These are full stack developers"
                },
                {
                    "stage": "U5",
                    "action": "Set up environment and network configurations for implementation",
                    "owner_name": "Manjul",
                    "start_date": base_date + timedelta(days=5),
                    "end_date": base_date + timedelta(days=19),
                    "progress": "Not Started",
                    "notes": ""
                },
                {
                    "stage": "U6",
                    "action": "Launch and Presentation",
                    "owner_name": "Shiv Nayak (EasyJet)",
                    "start_date": base_date + timedelta(days=20),
                    "end_date": base_date + timedelta(days=20),
                    "progress": "Not Started",
                    "notes": ""
                }
            ]
        },
        {
            "plan": {
                "name": "Drax GenAI Corporate Affairs",
                "description": "GenAI implementation for Corporate Affairs use case with security and privacy requirements",
                "customer": "Drax",
                "status": "In Progress"
            },
            "actions": [
                {
                    "stage": "U3",
                    "action": "Find DPP partner to deliver",
                    "owner_name": "Ollie Bird",
                    "start_date": base_date - timedelta(days=25),
                    "end_date": base_date - timedelta(days=11),
                    "progress": "In Progress",
                    "notes": ""
                },
                {
                    "stage": "U4",
                    "action": "Build out delivery plan",
                    "owner_name": "Nagajan Karavadra + Partner",
                    "start_date": base_date - timedelta(days=7),
                    "end_date": base_date + timedelta(days=1),
                    "progress": "In Progress",
                    "notes": "Prepped but waiting on final decision from PoC. 15/9: Scoping call planned on Thursday 18/9"
                },
                {
                    "stage": "U5",
                    "action": "Milestone 1: Setup AI Guardrails",
                    "owner_name": "Linda + Kyra + Romy",
                    "start_date": base_date,
                    "end_date": base_date + timedelta(days=10),
                    "progress": "In Progress",
                    "notes": "15/9: Product bug on AI Guardrail. Support ticket open. Need to confirm with customer if it's a blocker"
                },
                {
                    "stage": "U5",
                    "action": "Configure Private Link for Serverless",
                    "owner_name": "Soham + Dan",
                    "start_date": base_date - timedelta(days=15),
                    "end_date": base_date + timedelta(days=14),
                    "progress": "In Progress",
                    "notes": "15/9 Soham progressing urgently, will raise support for STS enablement"
                },
                {
                    "stage": "U6",
                    "action": "Go Live",
                    "owner_name": "Kate",
                    "start_date": base_date + timedelta(days=35),
                    "end_date": base_date + timedelta(days=35),
                    "progress": "Not Started",
                    "notes": ""
                }
            ]
        }
    ]

STAGE_DEFINITIONS = {
    "U2": {"name": "Uncover", "description": "Initial discovery and scoping"},
    "U3": {"name": "Understand", "description": "Requirements gathering and MVP planning"},
    "U4": {"name": "Pilot", "description": "Pilot implementation and testing"},
    "U5": {"name": "Scale", "description": "Production deployment and scaling"},
    "U6": {"name": "Expand", "description": "Go-live and expansion planning"}
}

PROGRESS_OPTIONS = ["Not Started", "In Progress", "Complete", "Blocked", "On Hold"]