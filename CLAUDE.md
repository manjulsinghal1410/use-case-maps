# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Application
```bash
# Main Streamlit app (production version)
streamlit run app.py

# Alternative versions for testing
streamlit run app_v2.py  # Version 2 with enhanced features
streamlit run app_v3.py  # Version 3 with additional templates
```

### Testing
```bash
# Run functionality tests
python test_functionality.py

# Run V3 app tests (includes template and UI tests)
python test_app_v3.py

# Test sidebar functionality
python test_sidebar.py
```

### Installation
```bash
# Install all dependencies
pip install -r requirements.txt
```

## Architecture Overview

This is a **Streamlit-based multi-user application** for managing Databricks use case plans with PostgreSQL database integration. The application features a sophisticated 4-step plan creation wizard, professional Databricks branding, and comprehensive project tracking.

### Core Components

- **app.py**: Main production application with full database integration
- **services/lakebase.py**: Database service layer handling PostgreSQL connections with multiple driver support (psycopg2, pg8000, psycopg2cffi)
- **components/plan_form.py**: Sophisticated 4-step plan creation wizard component
- **data/sample_plans.py**: Sample data and template definitions for demo mode
- **config.py**: Database configuration and environment settings

### Key Design Patterns

1. **Multi-User Isolation**: Each user has isolated workspace with plans stored in `use_case_data/users.json` and `use_case_data/use_cases.json` in demo mode, or PostgreSQL tables in production

2. **Database Fallback Strategy**: Application gracefully degrades to demo mode with sample data if database connection fails

3. **Template System**: Pre-built templates (Data Migration, GenAI Use Case) stored in `data/sample_plans.py` with extensible structure for adding new templates

4. **Stage Management**: U2-U6 stage progression (Uncover → Understand → Pilot → Scale → Expand) with specific action tracking per stage

### Databricks Branding Implementation

The application implements official Databricks branding through custom CSS:
- Primary colors: #FF3621 (red), #FF8C00 (orange), #1C1C1C (black)
- Gradient headers and hover effects
- Professional card-based UI with stage-specific color coding

### State Management

Streamlit session state is used extensively for:
- User context switching (`st.session_state.selected_user`)
- Plan creation wizard state (`st.session_state.plan_form`)
- View navigation (`st.session_state.view_plan_id`)
- Database connection status

### Database Schema

When connected to PostgreSQL:
- **use_case_plans.users**: User management
- **use_case_plans.plans**: Main plan storage with foreign key to users
- **use_case_plans.actions**: Individual plan actions with stage, owner, dates, progress
- **use_case_plans.templates**: Reusable plan templates

The database service handles automatic table creation and supports connection pooling for performance.