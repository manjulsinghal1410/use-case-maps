"""
Template structure based on the Consolidated MAP Excel template
This defines the proper column structure and stages for use cases
"""

# Standard columns from the Excel template for use case mapping
USE_CASE_COLUMNS = [
    "ID",
    "Stage",
    "Activity",
    "Description",
    "Owner",
    "Start Date",
    "End Date",
    "Duration (Days)",
    "Status",
    "Dependencies",
    "Deliverables",
    "Notes"
]

# Template stages based on typical Databricks implementations
TEMPLATE_STAGES = {
    "standard": [
        {
            "stage": "Stage 1: Assessment & Planning",
            "default_duration": 14,
            "activities": [
                {"activity": "Current State Analysis", "description": "Analyze existing infrastructure and data landscape"},
                {"activity": "Requirements Gathering", "description": "Collect business and technical requirements"},
                {"activity": "Stakeholder Alignment", "description": "Align stakeholders on objectives and success criteria"},
                {"activity": "Risk Assessment", "description": "Identify potential risks and mitigation strategies"},
                {"activity": "Resource Planning", "description": "Define team structure and resource allocation"}
            ]
        },
        {
            "stage": "Stage 2: Architecture & Design",
            "default_duration": 21,
            "activities": [
                {"activity": "Solution Architecture", "description": "Design target architecture on Databricks"},
                {"activity": "Data Model Design", "description": "Define data models and schemas"},
                {"activity": "Security Architecture", "description": "Design security and governance framework"},
                {"activity": "Integration Design", "description": "Plan integrations with existing systems"},
                {"activity": "Migration Strategy", "description": "Define migration approach and phases"}
            ]
        },
        {
            "stage": "Stage 3: Development & Build",
            "default_duration": 42,
            "activities": [
                {"activity": "Environment Setup", "description": "Set up Databricks workspaces and clusters"},
                {"activity": "Data Pipeline Development", "description": "Build data ingestion and processing pipelines"},
                {"activity": "Data Transformation", "description": "Implement ETL/ELT processes"},
                {"activity": "Feature Development", "description": "Build required features and capabilities"},
                {"activity": "Unit Testing", "description": "Test individual components"}
            ]
        },
        {
            "stage": "Stage 4: Testing & Validation",
            "default_duration": 21,
            "activities": [
                {"activity": "Integration Testing", "description": "Test end-to-end data flows"},
                {"activity": "Performance Testing", "description": "Validate performance and scalability"},
                {"activity": "Security Testing", "description": "Verify security controls and compliance"},
                {"activity": "UAT Preparation", "description": "Prepare for user acceptance testing"},
                {"activity": "User Acceptance Testing", "description": "Conduct UAT with business users"}
            ]
        },
        {
            "stage": "Stage 5: Deployment & Migration",
            "default_duration": 14,
            "activities": [
                {"activity": "Production Preparation", "description": "Prepare production environment"},
                {"activity": "Data Migration", "description": "Migrate data to production"},
                {"activity": "Cutover Planning", "description": "Plan and execute cutover"},
                {"activity": "Go-Live", "description": "Launch production system"},
                {"activity": "Hypercare", "description": "Provide intensive support post go-live"}
            ]
        },
        {
            "stage": "Stage 6: Optimization & Handover",
            "default_duration": 28,
            "activities": [
                {"activity": "Performance Optimization", "description": "Optimize performance and costs"},
                {"activity": "Documentation", "description": "Complete technical and user documentation"},
                {"activity": "Knowledge Transfer", "description": "Transfer knowledge to support team"},
                {"activity": "Training", "description": "Train end users and administrators"},
                {"activity": "Support Transition", "description": "Transition to BAU support"}
            ]
        }
    ]
}