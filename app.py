import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import uuid
from pathlib import Path
import base64
from template_structure import USE_CASE_COLUMNS, TEMPLATE_STAGES
from consolidated_map_template import CONSOLIDATED_MAP_TEMPLATE
from services.lakebase import lakebase
from config import Config

# Configure Streamlit page
st.set_page_config(
    page_title="Databricks Use Case Map Builder",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data directory
DATA_DIR = Path("use_case_data")
DATA_DIR.mkdir(exist_ok=True)
USERS_FILE = DATA_DIR / "users.json"
USE_CASES_FILE = DATA_DIR / "use_cases.json"

def load_databricks_logo():
    """Load the actual Databricks logo"""
    logo_path = Path("Databricks-Emblem.png")
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            logo_data = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{logo_data}"
    return None

def load_users():
    """Load users from file"""
    if USERS_FILE.exists():
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_use_cases():
    """Load use cases from file"""
    if USE_CASES_FILE.exists():
        with open(USE_CASES_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_use_cases(use_cases):
    """Save use cases to file"""
    with open(USE_CASES_FILE, 'w') as f:
        json.dump(use_cases, f, indent=2, default=str)

def generate_use_case_id():
    """Generate a unique use case ID"""
    return f"UC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

def generate_readable_use_case_id(customer_name):
    """Generate a readable use case ID based on customer name
    Format: {CUSTOMER_CODE}-{YYYY}-{MM}-{SEQ}
    Example: EJ-2025-09-001
    """
    # Extract customer code (first 2-3 chars of customer name, uppercase)
    customer_code = ''.join(c for c in customer_name if c.isalnum())[:3].upper()
    if not customer_code:
        customer_code = "UC"

    # Get current year and month
    now = datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')

    # Generate sequence number (try to get from database, fallback to random)
    try:
        if Config.validate():
            lakebase.connect()
            # Get count of use cases for this customer in this month
            result = lakebase.query(f"""
                SELECT COUNT(*) FROM test.use_case_maps
                WHERE customer_name = %s
                AND EXTRACT(YEAR FROM created_at) = %s
                AND EXTRACT(MONTH FROM created_at) = %s
            """, (customer_name, int(year), int(month)))

            seq = (result[0][0] + 1) if result and result[0] else 1
            lakebase.close()
        else:
            seq = 1
    except:
        # Fallback to random number if query fails
        seq = 1

    return f"{customer_code}-{year}-{month}-{seq:03d}"

def save_use_case_to_lakebase(use_case_data, user_name):
    """Save use case to Lakebase database in test.use_case_maps table"""
    try:
        if not Config.validate():
            return False, "Database configuration not valid"

        lakebase.connect()

        # First ensure the table exists
        lakebase.create_use_case_maps_table()

        # Prepare rows for insertion - one row per activity
        rows = []
        for stage in use_case_data['stages']:
            stage_name = stage['stage_name']

            # Extract stage code (U2-U6)
            import re
            u_stage_match = re.search(r'(U[2-6])', stage_name)
            if u_stage_match:
                stage_code = u_stage_match.group(1)
            else:
                stage_code = stage_name

            for activity in stage['activities']:
                # Calculate dates
                start_date = datetime.fromisoformat(use_case_data['start_date'])
                end_date = start_date + timedelta(days=activity.get('duration_days', 5))

                row = {
                    'use_case_id': use_case_data['use_case_id'],
                    'use_case_name': use_case_data['name'],
                    'customer_name': use_case_data['customer'],
                    'Stage': stage_code,
                    'Outcome': activity['activity'],
                    'Embedded_Questions': activity.get('description', ''),
                    'Owner_Name': activity.get('owner', ''),
                    'Start_Date': start_date.date(),
                    'End_Date': end_date.date(),
                    'Progress': 0.0 if activity.get('status', 'Not Started') == 'Not Started' else 50.0,
                    'Notes': '',
                    'Action': activity['activity'],
                    'solution_architect': use_case_data.get('solution_architect', ''),
                    'account_executive': use_case_data.get('account_executive', ''),
                    'ssa_required': use_case_data.get('ssa_required', False),
                    'poc_required': use_case_data.get('poc_happening', False),
                    'created_by': user_name,
                    'created_at': datetime.now(),
                    'updated_by': user_name,
                    'updated_at': datetime.now()
                }
                rows.append(row)

        # Insert rows using executemany for efficiency
        insert_sql = """
            INSERT INTO test.use_case_maps (
                use_case_id, use_case_name, customer_name, "Stage", "Outcome",
                "Embedded_Questions", "Owner_Name", "Start_Date", "End_Date",
                "Progress", "Notes", "Action", solution_architect, account_executive,
                ssa_required, poc_required, created_by, created_at, updated_by, updated_at
            ) VALUES (
                %(use_case_id)s, %(use_case_name)s, %(customer_name)s, %(Stage)s, %(Outcome)s,
                %(Embedded_Questions)s, %(Owner_Name)s, %(Start_Date)s, %(End_Date)s,
                %(Progress)s, %(Notes)s, %(Action)s, %(solution_architect)s, %(account_executive)s,
                %(ssa_required)s, %(poc_required)s, %(created_by)s, %(created_at)s, %(updated_by)s, %(updated_at)s
            )
        """

        lakebase.execute_many(insert_sql, rows)
        lakebase.close()

        return True, f"Successfully saved {len(rows)} activities to database"

    except Exception as e:
        return False, f"Failed to save to database: {str(e)}"

def load_maps_from_database():
    """Load existing maps from Lakebase database (both test.maps and test.use_case_maps)"""
    try:
        if not Config.validate():
            return []

        lakebase.connect()

        maps_list = []

        # Load from test.maps (original maps)
        try:
            maps_query = lakebase.query("""
                SELECT DISTINCT "ID", COUNT(*) as activity_count,
                       MIN("Start_Date") as start_date,
                       MAX("End_Date") as end_date
                FROM test.maps
                WHERE "ID" IS NOT NULL AND "ID" != '' AND "ID" NOT LIKE '%/%'
                GROUP BY "ID"
                ORDER BY CAST("ID" AS INTEGER)
                LIMIT 25
            """)

            if maps_query:
                for map_data in maps_query:
                    maps_list.append({
                        'id': map_data[0],
                        'activity_count': map_data[1],
                        'start_date': map_data[2],
                        'end_date': map_data[3],
                        'source': 'maps',
                        'editable': False
                    })
        except Exception as e:
            print(f"Error loading from test.maps: {e}")

        # Load from test.use_case_maps (app-created use cases)
        try:
            use_case_maps_query = lakebase.query("""
                SELECT DISTINCT use_case_id, use_case_name, customer_name,
                       COUNT(*) as activity_count,
                       MIN("Start_Date") as start_date,
                       MAX("End_Date") as end_date
                FROM test.use_case_maps
                WHERE use_case_id IS NOT NULL AND use_case_id != ''
                GROUP BY use_case_id, use_case_name, customer_name
                ORDER BY created_at DESC
                LIMIT 25
            """)

            if use_case_maps_query:
                for map_data in use_case_maps_query:
                    maps_list.append({
                        'id': map_data[0],
                        'name': map_data[1],
                        'customer': map_data[2],
                        'activity_count': map_data[3],
                        'start_date': map_data[4],
                        'end_date': map_data[5],
                        'source': 'use_case_maps',
                        'editable': True
                    })
        except Exception as e:
            # Table might not exist yet
            print(f"Note: test.use_case_maps table not found or empty: {e}")

        lakebase.close()
        return maps_list
    except Exception as e:
        print(f"Error loading maps from database: {e}")
        return []

def load_map_details(map_id):
    """Load detailed activities for a specific map ID"""
    try:
        lakebase.connect()

        activities_query = lakebase.query(f"""
            SELECT "Stage", "Outcome", "Embedded_Questions", "Owner_Name",
                   "Start_Date", "End_Date", "Progress", "Notes", "Action"
            FROM test.maps
            WHERE "ID" = '{map_id}'
            ORDER BY p_id
        """)

        activities = []
        if activities_query:
            for activity in activities_query:
                if activity[0]:  # Only include if Stage is not None
                    activities.append({
                        'stage': activity[0],
                        'outcome': activity[1] or activity[8],  # Use Action if Outcome is None
                        'questions': activity[2] or '',
                        'owner': activity[3] or '',
                        'start_date': activity[4],
                        'end_date': activity[5],
                        'progress': activity[6] or 'Not Started',
                        'notes': activity[7] or ''
                    })

        lakebase.close()
        return activities
    except Exception as e:
        print(f"Error loading map details: {e}")
        return []

def load_template_from_database():
    """Load template from Lakebase database"""
    try:
        if not Config.validate():
            return None

        lakebase.connect()

        template_query = lakebase.query("""
            SELECT stage, outcome, asset_podcast, owner_name
            FROM test.template
            ORDER BY id
        """)

        template_data = {}
        if template_query:
            for row in template_query:
                stage = row[0]
                if stage not in template_data:
                    template_data[stage] = []

                template_data[stage].append({
                    'outcome': row[1],
                    'questions': row[2],
                    'owner': row[3] or ''
                })

        lakebase.close()
        return template_data
    except Exception as e:
        print(f"Error loading template from database: {e}")
        return None

def initialize_session_state():
    """Initialize session state variables"""
    if 'users' not in st.session_state:
        st.session_state.users = load_users()
    if 'use_cases' not in st.session_state:
        st.session_state.use_cases = load_use_cases()
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'editing_use_case' not in st.session_state:
        st.session_state.editing_use_case = None
    if 'show_new_use_case_form' not in st.session_state:
        st.session_state.show_new_use_case_form = False
    if 'create_from_map' not in st.session_state:
        st.session_state.create_from_map = None
    if 'create_from_db_template' not in st.session_state:
        st.session_state.create_from_db_template = False

def inject_custom_css():
    """Inject improved Databricks-style CSS with better proportions"""
    logo_url = load_databricks_logo()

    st.markdown("""
    <style>
        /* Databricks official colors - Dark Mode */
        :root {
            --databricks-orange: #FF3621;
            --databricks-navy: #1B3139;
            --databricks-dark: #0B1929;
            --databricks-darker: #050A0F;
            --databricks-light: #FFFFFF;
            --databricks-gray: #2A2F35;
            --databricks-light-gray: #3A4148;
        }

        /* Main app background - Dark Mode */
        .stApp {
            background: linear-gradient(135deg, #0B1929 0%, #050A0F 100%);
            color: #E8E8E8;
        }

        /* Fixed sidebar with better proportions - narrower */
        section[data-testid="stSidebar"] {
            width: 280px !important;
            background: linear-gradient(180deg, #1B3139 0%, #0B1929 100%);
            position: fixed;
            height: 100vh;
            border-right: 3px solid #FF3621;
            padding-top: 0;
            box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
        }

        section[data-testid="stSidebar"] > div {
            width: 280px !important;
            padding: 1rem;
        }

        /* Main content area adjustment for fixed sidebar */
        .main > div {
            margin-left: 280px;
            padding: 1rem 2rem;
        }

        /* Sidebar content styling */
        section[data-testid="stSidebar"] .stMarkdown {
            color: white;
        }

        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: white !important;
        }

        /* Sidebar buttons with better visibility - More specific selectors */
        section[data-testid="stSidebar"] .stButton > button,
        section[data-testid="stSidebar"] button[data-testid="baseButton-primary"],
        section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"] {
            background: white !important;
            color: #1B3139 !important;
            width: 100%;
            border: 2px solid #FF3621 !important;
            padding: 0.5rem;
            margin: 0.25rem 0;
            font-weight: 600;
            border-radius: 4px;
            transition: all 0.3s ease;
        }

        section[data-testid="stSidebar"] .stButton > button:hover,
        section[data-testid="stSidebar"] button[data-testid="baseButton-primary"]:hover,
        section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:hover {
            background: #FF3621 !important;
            color: white !important;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(255, 54, 33, 0.3);
        }

        /* Additional specificity for sidebar buttons */
        [data-testid="stSidebar"] .stButton button {
            background: white !important;
            color: #1B3139 !important;
            border: 2px solid #FF3621 !important;
        }

        [data-testid="stSidebar"] .stButton button:hover {
            background: #FF3621 !important;
            color: white !important;
        }

        /* Expander headers in sidebar - better visibility */
        section[data-testid="stSidebar"] .streamlit-expanderHeader {
            background: rgba(255, 255, 255, 0.9) !important;
            color: #1B3139 !important;
            border-radius: 6px;
            border: 1px solid rgba(255, 54, 33, 0.4);
            font-weight: 600;
            transition: all 0.3s ease;
        }

        section[data-testid="stSidebar"] .streamlit-expanderHeader:hover {
            background: #FFD700 !important;
            color: #1B3139 !important;
            border-color: #FFD700;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
        }

        section[data-testid="stSidebar"] .streamlit-expanderHeader p {
            color: #1B3139 !important;
            font-weight: 600;
        }

        section[data-testid="stSidebar"] .streamlit-expanderHeader:hover p {
            color: #1B3139 !important;
        }

        /* Input fields in sidebar */
        section[data-testid="stSidebar"] .stTextInput > div > div > input,
        section[data-testid="stSidebar"] .stSelectbox > div > div > select {
            background: rgba(255, 255, 255, 0.9) !important;
            color: #1B3139 !important;
            border: 1px solid rgba(255, 54, 33, 0.3);
            border-radius: 4px;
        }

        /* Labels in sidebar */
        section[data-testid="stSidebar"] label {
            color: white !important;
            font-weight: 500;
        }

        /* Headers - Dark Mode */
        h1, h2, h3 {
            color: #FFFFFF !important;
            font-family: 'DM Sans', sans-serif;
        }

        /* Markdown text */
        .main .stMarkdown {
            color: #E8E8E8;
        }

        /* Main content buttons */
        .main .stButton > button {
            background: #FF3621;
            color: white;
            border: none;
            padding: 0.5rem 1.5rem;
            border-radius: 4px;
            font-weight: 600;
            transition: all 0.3s;
        }

        .main .stButton > button:hover {
            background: #E62E1A;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(255, 54, 33, 0.3);
        }

        /* Input fields - Dark Mode */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > div > textarea,
        .stNumberInput > div > div > input {
            background: #1B3139 !important;
            color: #FFFFFF !important;
            border: 1px solid #3A4148 !important;
            border-radius: 4px;
        }

        /* Input labels - Dark Mode */
        .main label {
            color: #E8E8E8 !important;
            font-weight: 500;
        }

        /* Data editor / table - Dark Mode */
        .stDataFrame {
            background: #1B3139 !important;
            border: 1px solid #3A4148 !important;
            border-radius: 8px;
            overflow: hidden;
        }

        [data-testid="stDataFrameContainer"] {
            background: #1B3139 !important;
        }

        /* Table styling - Dark Mode */
        [data-testid="stDataFrameContainer"] table {
            background: #1B3139 !important;
            color: #FFFFFF !important;
        }

        /* Expander in sidebar */
        section[data-testid="stSidebar"] .streamlit-expanderHeader {
            background: rgba(255, 255, 255, 0.1);
            color: white !important;
            border-radius: 4px;
            border: 1px solid rgba(255, 54, 33, 0.3);
        }

        section[data-testid="stSidebar"] .streamlit-expanderContent {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 54, 33, 0.2);
        }

        /* Main area expanders - Dark Mode */
        .main .streamlit-expanderHeader {
            background: #1B3139 !important;
            color: #FFFFFF !important;
            border-radius: 4px;
            font-weight: 600;
            border: 1px solid #3A4148 !important;
        }

        .main .streamlit-expanderContent {
            background: #0B1929 !important;
            border: 1px solid #3A4148 !important;
            color: #E8E8E8 !important;
        }

        /* Info and success boxes - Dark Mode */
        .stAlert {
            background: #1B3139 !important;
            color: #E8E8E8 !important;
            border-radius: 4px;
            border-left: 4px solid #FF3621;
        }

        /* Header section - Dark Mode */
        .main-header {
            background: #1B3139;
            padding: 1.5rem;
            border-bottom: 3px solid #FF3621;
            margin: -1rem -2rem 2rem -2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }

        .header-content {
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }

        .header-content img {
            height: 50px;
        }

        .header-text h1 {
            font-size: 2rem;
            font-weight: 700;
            color: #FFFFFF !important;
            margin: 0;
        }

        .header-text p {
            color: #FF3621;
            font-size: 0.95rem;
            margin: 0.25rem 0 0 0;
            font-weight: 500;
        }

        /* User card in sidebar */
        .user-card {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 54, 33, 0.3);
            border-radius: 6px;
            padding: 0.75rem;
            margin: 0.5rem 0;
            color: white;
            transition: all 0.3s;
        }

        .user-card:hover {
            background: rgba(255, 255, 255, 0.15);
            border-color: #FF3621;
            transform: translateY(-1px);
        }

        .user-card strong {
            color: #FF3621;
            font-weight: 600;
        }

        .user-card small {
            color: rgba(255, 255, 255, 0.8);
        }

        /* Use case cards in sidebar */
        section[data-testid="stSidebar"] .streamlit-expanderHeader p {
            color: white !important;
            font-size: 0.9rem;
        }

        /* Form section styling - Dark Mode */
        .form-section {
            background: #1B3139 !important;
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }

        /* Stage card - Dark Mode */
        .stage-card {
            background: #1B3139 !important;
            border: 1px solid #3A4148 !important;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
        }

        /* Hide Streamlit default elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .viewerBadge_container__1QSob {visibility: hidden;}

        /* Metrics styling - Dark Mode */
        [data-testid="metric-container"] {
            background: #1B3139 !important;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #3A4148 !important;
        }

        [data-testid="stMetricLabel"] {
            color: #B8B8B8 !important;
        }

        [data-testid="stMetricValue"] {
            color: #FFFFFF !important;
        }

        /* Table headers - Dark Mode */
        thead th {
            background: #FF3621 !important;
            color: white !important;
            font-weight: 600;
        }

        /* Date input - Dark Mode */
        .stDateInput > div > div > input {
            background: #1B3139 !important;
            color: #FFFFFF !important;
            border: 1px solid #3A4148 !important;
        }

        /* Number input controls - Dark Mode */
        .stNumberInput button {
            background: #2A2F35 !important;
            color: #FFFFFF !important;
        }

        /* Selectbox dropdown - Dark Mode */
        .stSelectbox [data-baseweb="select"] {
            background: #1B3139 !important;
        }

        /* All text in main area */
        .main p, .main span, .main div {
            color: #E8E8E8;
        }

        /* Column config labels */
        [data-testid="column-header"] {
            color: #FFFFFF !important;
        }

        /* Success message */
        .stSuccess {
            background: rgba(0, 200, 83, 0.15) !important;
            color: #00C853 !important;
        }

        /* Info message */
        .stInfo {
            background: rgba(33, 150, 243, 0.15) !important;
            color: #2196F3 !important;
        }

        /* Warning message */
        .stWarning {
            background: rgba(255, 152, 0, 0.15) !important;
            color: #FF9800 !important;
        }

        /* Error message */
        .stError {
            background: rgba(244, 67, 54, 0.15) !important;
            color: #F44336 !important;
        }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """Render the main header with Databricks logo"""
    logo_url = load_databricks_logo()

    logo_html = f'<img src="{logo_url}" alt="Databricks">' if logo_url else '<span style="color: #FF3621; font-size: 2rem;">🔥</span>'

    st.markdown(f"""
    <div class="main-header">
        <div class="header-content">
            {logo_html}
            <div class="header-text">
                <h1>Use Case Map Builder</h1>
                <p>Create and manage Databricks implementation plans</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the sidebar with user management and use case list"""
    with st.sidebar:
        # Databricks branding at top - clickable logo
        logo_url = load_databricks_logo()
        if logo_url:
            # Make logo clickable to navigate to home
            st.markdown(f'''
            <div style="text-align: center; margin-bottom: 1rem;">
                <a href="#" onclick="window.location.reload(); return false;" style="text-decoration: none;">
                    <img src="{logo_url}" style="height: 40px; cursor: pointer; transition: transform 0.2s;" 
                         onmouseover="this.style.transform='scale(1.05)'" 
                         onmouseout="this.style.transform='scale(1)'" 
                         title="Click to go to Home">
                </a>
            </div>
            ''', unsafe_allow_html=True)
        else:
            # Fallback with emoji logo
            st.markdown('''
            <div style="text-align: center; margin-bottom: 1rem;">
                <a href="#" onclick="window.location.reload(); return false;" style="text-decoration: none;">
                    <span style="color: #FF3621; font-size: 2rem; cursor: pointer; transition: transform 0.2s;" 
                          onmouseover="this.style.transform='scale(1.1)'" 
                          onmouseout="this.style.transform='scale(1)'" 
                          title="Click to go to Home">🔥</span>
                </a>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown("## 👥 Users")

        # Add new user section
        with st.expander("Add New User", expanded=False):
            new_user_name = st.text_input("User Name", key="new_user_name")
            new_user_email = st.text_input("User Email", key="new_user_email")
            new_user_role = st.selectbox("Role",
                ["Solution Architect", "Account Executive", "FE Manager", "FE Leader"],
                key="new_user_role")

            if st.button("Add User", key="add_user_btn"):
                if new_user_name and new_user_email:
                    user_id = str(uuid.uuid4())
                    if 'users' not in st.session_state:
                        st.session_state.users = {}
                    st.session_state.users[user_id] = {
                        "name": new_user_name,
                        "email": new_user_email,
                        "role": new_user_role,
                        "created_at": datetime.now().isoformat()
                    }
                    save_users(st.session_state.users)
                    st.success(f"Added {new_user_name}")
                    st.rerun()
                else:
                    st.error("Fill all fields")

        st.markdown("---")

        # User selection
        if st.session_state.users:
            user_names = ["Select a user..."] + [user["name"] for user in st.session_state.users.values()]
            selected_user_name = st.selectbox("Active User", user_names, key="user_selector")

            if selected_user_name != "Select a user...":
                # Find user ID by name
                for uid, user in st.session_state.users.items():
                    if user["name"] == selected_user_name:
                        st.session_state.current_user = uid
                        break

                # Display user info
                if st.session_state.current_user:
                    user = st.session_state.users[st.session_state.current_user]
                    st.markdown(f"""
                    <div class="user-card">
                        <strong>{user['name']}</strong><br>
                        <small>{user['role']}</small>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("---")
                    st.markdown("### 📋 Use Cases")

                    # New Use Case button (always uses database template)
                    if st.button("➕ New Use Case", key="new_use_case_btn", use_container_width=True):
                        st.session_state.show_new_use_case_form = True
                        st.session_state.editing_use_case = None
                        # Always use database template
                        st.session_state.create_from_db_template = True
                        st.session_state.create_from_map = None
                        st.rerun()

                    # List user's use cases
                    user_use_cases = {k: v for k, v in st.session_state.use_cases.items()
                                     if v.get("user_id") == st.session_state.current_user}

                    if user_use_cases:
                        st.markdown("##### Your Use Cases")
                        for uc_id, uc in user_use_cases.items():
                            with st.expander(f"{uc['use_case_id'][:15]}"):
                                st.write(f"**{uc['name']}**")
                                st.write(f"Customer: {uc['customer']}")
                                st.write(f"Status: {uc.get('status', 'Planning')}")

                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("View", key=f"view_{uc_id}", use_container_width=True):
                                        st.session_state.editing_use_case = uc_id
                                        st.session_state.show_new_use_case_form = False
                                with col2:
                                    if st.button("Delete", key=f"del_{uc_id}", use_container_width=True):
                                        del st.session_state.use_cases[uc_id]
                                        save_use_cases(st.session_state.use_cases)
                                        st.rerun()
                    else:
                        st.info("No use cases yet")

                    # Database Maps Section
                    if Config.validate():
                        st.markdown("---")
                        st.markdown("### 🗄️ Database")

                        # Existing Maps section
                        with st.expander("🗺️ Existing Maps", expanded=False):
                            maps = load_maps_from_database()
                            if maps:
                                # Separate maps by source
                                app_created = [m for m in maps if m['source'] == 'use_case_maps']
                                original_maps = [m for m in maps if m['source'] == 'maps']

                                # Show app-created use cases first
                                if app_created:
                                    st.markdown("**📝 Your Use Cases**")
                                    for map_data in app_created[:10]:
                                        col1, col2 = st.columns([3, 1])
                                        with col1:
                                            st.write(f"**{map_data['id']}**")
                                            st.caption(f"{map_data.get('customer', 'N/A')} • {map_data['activity_count']} activities")
                                        with col2:
                                            if st.button("Use", key=f"use_map_{map_data['id']}", use_container_width=True):
                                                st.session_state.create_from_map = map_data['id']
                                                st.session_state.create_from_db_template = False
                                                st.session_state.show_new_use_case_form = True
                                                st.session_state.editing_use_case = None
                                                st.rerun()

                                # Show original maps
                                if original_maps:
                                    st.markdown("---")
                                    st.markdown("**📋 Template Maps**")
                                    for map_data in original_maps[:10]:
                                        col1, col2 = st.columns([3, 1])
                                        with col1:
                                            st.write(f"Map #{map_data['id']}")
                                            st.caption(f"{map_data['activity_count']} activities")
                                        with col2:
                                            if st.button("Use", key=f"use_map_{map_data['id']}", use_container_width=True):
                                                st.session_state.create_from_map = map_data['id']
                                                st.session_state.create_from_db_template = False
                                                st.session_state.show_new_use_case_form = True
                                                st.session_state.editing_use_case = None
                                                st.rerun()
                            else:
                                st.info("No maps found in database")
        else:
            st.info("Add a user to start")

def render_use_case_form():
    """Render the use case creation/editing form with proper template structure"""
    st.markdown("## 📝 Use Case Configuration")

    # Check if editing existing use case
    if st.session_state.editing_use_case:
        use_case = st.session_state.use_cases[st.session_state.editing_use_case]
        st.info(f"Editing: {use_case['use_case_id']}")
    else:
        use_case = None
        st.success("Creating New Use Case Map")

    # Form sections
    st.markdown('<div class="form-section">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### Basic Information")
        name = st.text_input("Use Case Name", value=use_case['name'] if use_case else "")
        customer = st.text_input("Customer/Organization", value=use_case['customer'] if use_case else "")

    with col2:
        st.markdown("#### Team")
        solution_architect = st.text_input("Solution Architect",
            value=use_case['solution_architect'] if use_case else "")
        account_executive = st.text_input("Account Executive",
            value=use_case['account_executive'] if use_case else "")

    with col3:
        st.markdown("#### Timeline")
        start_date = st.date_input("Start Date",
            value=datetime.fromisoformat(use_case['start_date']) if use_case else datetime.now())
        duration_months = st.number_input("Duration (Months)", min_value=1, max_value=24,
            value=use_case['duration_months'] if use_case else 6)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Conditional Questions Section
    st.markdown("### ❓ Project Requirements")
    st.markdown('<div class="form-section">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        ssa_required = st.checkbox(
            "SSA (Specialized Solutions Architect) Required?",
            value=use_case.get('ssa_required', False) if use_case else False,
            help="Select if SSA activities need to be included in the plan"
        )

    with col2:
        poc_happening = st.checkbox(
            "POC (Proof of Concept) Phase?",
            value=use_case.get('poc_happening', False) if use_case else False,
            help="Select if POC activities need to be included in the plan"
        )

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### 🎯 Implementation Stages")
    st.markdown("Based on Databricks Consolidated MAP Template")

    # Initialize stages from template
    if use_case and 'stages' in use_case:
        stages_data = use_case['stages']
    elif st.session_state.create_from_map:
        # Load from existing database map
        st.info(f"📋 Loading from Map #{st.session_state.create_from_map}")
        map_activities = load_map_details(st.session_state.create_from_map)

        # Group activities by stage
        stages_dict = {}
        for activity in map_activities:
            stage = activity['stage']
            if stage not in stages_dict:
                stages_dict[stage] = []

            # Auto-populate SA and AE names based on owner field
            owner = activity['owner']
            if 'SA' in owner and solution_architect:
                owner = owner.replace('SA', solution_architect)
            if 'AE' in owner and account_executive:
                owner = owner.replace('AE', account_executive)

            stages_dict[stage].append({
                'activity': activity['outcome'],
                'description': activity['questions'],
                'owner': owner,
                'duration_days': 5,
                'status': 'Not Started'
            })

        # Convert to list format
        stages_data = []
        for stage_code in sorted(stages_dict.keys()):
            stages_data.append({
                'stage_name': stage_code,
                'activities': stages_dict[stage_code]
            })

        # Clear the flag after loading
        if stages_data:
            st.session_state.create_from_map = None
    elif st.session_state.create_from_db_template:
        # Load from database template
        st.info("📋 Loading from Database Template")
        db_template = load_template_from_database()

        if db_template:
            stages_data = []
            for stage_code in ['U2', 'U3', 'U4', 'U5']:
                if stage_code in db_template:
                    stage_activities = []
                    for activity in db_template[stage_code]:
                        # Check conditional requirements
                        should_include = True
                        if 'SSA' in activity['outcome'] and not ssa_required:
                            should_include = False
                        elif 'POC' in activity['outcome'] and not poc_happening:
                            should_include = False

                        if should_include:
                            # Auto-populate SA and AE names
                            owner = activity['owner']
                            if 'SA' in owner and solution_architect:
                                owner = owner.replace('SA', solution_architect)
                            if 'AE' in owner and account_executive:
                                owner = owner.replace('AE', account_executive)

                            stage_activities.append({
                                'activity': activity['outcome'],
                                'description': activity['questions'],
                                'owner': owner,
                                'duration_days': 5,
                                'status': 'Not Started'
                            })

                    if stage_activities:
                        stages_data.append({
                            'stage_name': f"{stage_code}",
                            'activities': stage_activities
                        })

            # Clear the flag after loading
            if stages_data:
                st.session_state.create_from_db_template = False
        else:
            st.warning("Could not load database template, using default template")
            stages_data = []
            for stage_code in ['U2', 'U3', 'U4', 'U5']:
                stage_template = CONSOLIDATED_MAP_TEMPLATE[stage_code]
                stage_activities = []
                for activity in stage_template['activities']:
                    conditional = activity.get('conditional', None)
                    should_include = True
                    if conditional == 'ssa' and not ssa_required:
                        should_include = False
                    elif conditional == 'poc' and not poc_happening:
                        should_include = False
                    if should_include:
                        stage_activities.append({
                            'activity': activity['outcome'],
                            'description': activity['questions'],
                            'owner': activity.get('owner', ''),
                            'duration_days': 5,
                            'status': 'Not Started'
                        })
                stages_data.append({
                    'stage_name': f"{stage_code} - {stage_template['name']}",
                    'activities': stage_activities
                })
    else:
        # Load from consolidated MAP template (default)
        stages_data = []
        for stage_code in ['U2', 'U3', 'U4', 'U5']:
            stage_template = CONSOLIDATED_MAP_TEMPLATE[stage_code]
            stage_activities = []

            for activity in stage_template['activities']:
                # Check if activity should be included based on conditional requirements
                conditional = activity.get('conditional', None)

                should_include = True
                if conditional == 'ssa' and not ssa_required:
                    should_include = False
                elif conditional == 'poc' and not poc_happening:
                    should_include = False

                if should_include:
                    # Auto-populate SA and AE names
                    owner = activity.get('owner', '')
                    if 'SA' in owner and solution_architect:
                        owner = owner.replace('SA', solution_architect)
                    if 'AE' in owner and account_executive:
                        owner = owner.replace('AE', account_executive)

                    stage_activities.append({
                        'activity': activity['outcome'],
                        'description': activity['questions'],
                        'owner': owner,
                        'duration_days': 5,
                        'status': 'Not Started'
                    })

            stages_data.append({
                'stage_name': f"{stage_code} - {stage_template['name']}",
                'activities': stage_activities
            })

    # Display stages
    updated_stages = []
    for idx, stage in enumerate(stages_data):
        with st.expander(f"**{stage['stage_name']}**", expanded=(idx == 0)):

            # Stage name editing
            stage_name = st.text_input("Stage Name", value=stage['stage_name'], key=f"stage_{idx}")

            # Activities table
            activities_df = pd.DataFrame(stage['activities'])

            edited_activities = st.data_editor(
                activities_df,
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "activity": st.column_config.TextColumn("Activity", width=200),
                    "description": st.column_config.TextColumn("Description", width=300),
                    "owner": st.column_config.TextColumn("Owner", width=150),
                    "duration_days": st.column_config.NumberColumn("Days", width=80, min_value=1),
                    "status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["Not Started", "In Progress", "Completed", "Blocked"],
                        width=120
                    )
                },
                key=f"activities_{idx}"
            )

            updated_stages.append({
                'stage_name': stage_name,
                'activities': edited_activities.to_dict('records')
            })

    # Add new stage button
    if st.button("➕ Add New Stage"):
        new_stage = {
            'stage_name': f"Stage {len(updated_stages) + 1}: Custom Stage",
            'activities': [
                {'activity': 'New Activity', 'description': 'Description',
                 'owner': '', 'duration_days': 5, 'status': 'Not Started'}
            ]
        }
        updated_stages.append(new_stage)
        st.rerun()

    st.markdown("---")

    # Save/Cancel buttons
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("💾 Save Use Case", type="primary"):
            if name and customer and solution_architect and account_executive:
                # Create or update use case
                use_case_data = {
                    'use_case_id': use_case['use_case_id'] if use_case else generate_readable_use_case_id(customer),
                    'user_id': st.session_state.current_user,
                    'name': name,
                    'customer': customer,
                    'solution_architect': solution_architect,
                    'account_executive': account_executive,
                    'start_date': start_date.isoformat(),
                    'duration_months': duration_months,
                    'ssa_required': ssa_required,
                    'poc_happening': poc_happening,
                    'status': 'Planning',
                    'stages': updated_stages,
                    'created_at': use_case['created_at'] if use_case else datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }

                if st.session_state.editing_use_case:
                    st.session_state.use_cases[st.session_state.editing_use_case] = use_case_data
                else:
                    st.session_state.use_cases[use_case_data['use_case_id']] = use_case_data

                save_use_cases(st.session_state.use_cases)

                # Save to Lakebase database
                success, message = save_use_case_to_lakebase(use_case_data, st.session_state.current_user)
                if success:
                    st.success(f"✅ {message}")
                    st.success(f"💾 Saved locally: {use_case_data['use_case_id']}")
                else:
                    st.warning(f"⚠️ Saved locally but database save failed: {message}")

                st.session_state.show_new_use_case_form = False
                st.session_state.editing_use_case = use_case_data['use_case_id']
                st.rerun()
            else:
                st.error("Please fill in all required fields")

    with col2:
        if st.button("Cancel"):
            st.session_state.show_new_use_case_form = False
            st.session_state.editing_use_case = None
            st.rerun()

def render_use_case_view():
    """Render the Excel-like view of a use case with proper column structure"""
    use_case = st.session_state.use_cases[st.session_state.editing_use_case]

    st.markdown(f"## 📊 {use_case['name']}")
    st.markdown(f"**Use Case ID:** {use_case['use_case_id']}")

    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Customer", use_case['customer'])
    with col2:
        st.metric("Solution Architect", use_case['solution_architect'])
    with col3:
        st.metric("Account Executive", use_case['account_executive'])
    with col4:
        st.metric("Duration", f"{use_case['duration_months']} months")

    st.markdown("---")

    # Create comprehensive Excel-like view with all columns from template
    st.markdown("### 📋 Implementation Plan")
    st.markdown("*Excel-like view based on Consolidated MAP Template*")

    # Prepare data for DataFrame with proper columns
    data = []

    for stage_idx, stage in enumerate(use_case['stages']):
        stage_name = stage['stage_name']

        # Extract stage code from stage name
        # Look for patterns like "U2 -", "U3 -", "Stage 1:", etc.
        import re
        # First try to match U2-U6 format
        u_stage_match = re.search(r'(U[2-6])', stage_name)
        if u_stage_match:
            stage_code = u_stage_match.group(1)
        else:
            # Try to match "Stage N" format
            stage_match = re.search(r'Stage\s+(\d+)', stage_name)
            if stage_match:
                stage_num = int(stage_match.group(1))
                stage_code = f"U{stage_num + 1}"  # Stage 1 -> U2, Stage 2 -> U3, etc.
            else:
                # Fallback: use index-based mapping
                stage_code = f"U{stage_idx + 2}" if stage_idx < 5 else "U6"

        for activity in stage['activities']:
            # Calculate dates based on duration
            if data:
                prev_end = datetime.fromisoformat(data[-1]['End Date'])
                start = prev_end + timedelta(days=1)
            else:
                start = datetime.fromisoformat(use_case['start_date'])

            end = start + timedelta(days=activity.get('duration_days', 5))

            data.append({
                'ID': stage_code,
                'Stage': stage_name,
                'Activity': activity['activity'],
                'Description': activity['description'],
                'Owner': activity.get('owner', ''),
                'Start Date': start.strftime('%Y-%m-%d'),
                'End Date': end.strftime('%Y-%m-%d'),
                'Duration (Days)': activity.get('duration_days', 5),
                'Status': activity.get('status', 'Not Started'),
                'Dependencies': '',
                'Deliverables': '',
                'Notes': ''
            })

    # Create DataFrame
    df = pd.DataFrame(data)

    # Display as editable table
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        height=600,
        column_config={
            "ID": st.column_config.TextColumn("ID", width=60, disabled=True),
            "Stage": st.column_config.TextColumn("Stage", width=200),
            "Activity": st.column_config.TextColumn("Activity", width=180),
            "Description": st.column_config.TextColumn("Description", width=250),
            "Owner": st.column_config.TextColumn("Owner", width=120),
            "Start Date": st.column_config.TextColumn("Start Date", width=100),
            "End Date": st.column_config.TextColumn("End Date", width=100),
            "Duration (Days)": st.column_config.NumberColumn("Days", width=60),
            "Status": st.column_config.SelectboxColumn(
                "Status",
                options=["Not Started", "In Progress", "Completed", "Blocked", "On Hold"],
                width=110
            ),
            "Dependencies": st.column_config.TextColumn("Dependencies", width=120),
            "Deliverables": st.column_config.TextColumn("Deliverables", width=150),
            "Notes": st.column_config.TextColumn("Notes", width=200)
        },
        key="use_case_table"
    )

    # Action buttons
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("✏️ Edit Details"):
            st.session_state.show_new_use_case_form = True
            st.rerun()

    with col2:
        # Export to CSV
        csv = edited_df.to_csv(index=False)
        st.download_button(
            label="📥 Export CSV",
            data=csv,
            file_name=f"{use_case['use_case_id']}_plan.csv",
            mime="text/csv"
        )

    with col3:
        if st.button("📊 Create New"):
            st.session_state.show_new_use_case_form = True
            st.session_state.editing_use_case = None
            st.rerun()

    with col4:
        if st.button("🔙 Back"):
            st.session_state.editing_use_case = None
            st.rerun()

def render_welcome():
    """Render welcome screen"""
    st.markdown("""
    <div style="text-align: center; padding: 3rem;">
        <h2>Welcome to Databricks Use Case Map Builder</h2>
        <p style="font-size: 1.2rem; color: #FF3621;">
            Select or create a user to get started
        </p>
        <br>
        <div style="text-align: left; max-width: 600px; margin: 0 auto;">
            <h4>Features:</h4>
            <ul>
                <li>Create implementation plans based on Databricks templates</li>
                <li>Track stages and activities with proper column structure</li>
                <li>Manage multiple users and their use cases</li>
                <li>Export to CSV for Excel compatibility</li>
                <li>Professional Databricks-branded interface</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application"""
    inject_custom_css()
    initialize_session_state()

    render_sidebar()
    render_header()

    # Main content area
    if st.session_state.current_user:
        if st.session_state.show_new_use_case_form:
            render_use_case_form()
        elif st.session_state.editing_use_case and not st.session_state.show_new_use_case_form:
            render_use_case_view()
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem;">
                <h2>Ready to Build Your Use Case Map</h2>
                <p>Select an action from the sidebar:</p>
                <ul style="text-align: left; display: inline-block;">
                    <li>Create a new use case map</li>
                    <li>View or edit existing use cases</li>
                    <li>Export use cases to CSV</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    else:
        render_welcome()

if __name__ == "__main__":
    main()