# Use Case Maps

A comprehensive Streamlit application for managing Databricks use case planning and execution using the MAP (Mutual Action Plan) methodology.

## 🎯 Overview

Use Case Maps is a multi-user web application that helps Solution Architects and Account Executives plan, track, and manage Databricks implementation projects through structured stages (U2-U6). The application integrates with Databricks Lakebase for persistent storage and provides a sophisticated planning interface based on the Consolidated MAP Template.

## ✨ Features

### Core Functionality
- **Multi-User Support**: Isolated workspaces for different users with role-based access
- **Database Integration**: Full PostgreSQL/Lakebase integration for persistent storage
- **Template-Based Planning**: Pre-built MAP templates (U2-U6 stages) with customizable activities
- **Readable Use Case IDs**: Auto-generated format: `{CUSTOMER_CODE}-{YYYY}-{MM}-{SEQ}` (e.g., `EAS-2025-09-001`)
- **Dark Mode UI**: Professional Databricks-branded interface with gradient headers

### Planning Features
- **4-Stage MAP Workflow**:
  - **U2 (Uncover)**: Initial discovery and scoping
  - **U3 (Understand)**: Requirements gathering and MVP planning
  - **U4 (Pilot)**: Pilot implementation and testing
  - **U5 (Scale)**: Production deployment and scaling
- **Conditional Activities**: SSA (Specialized Solutions Architect) and POC requirements
- **Auto-Population**: Automatically populate SA/AE names in owner fields
- **Activity Management**: Add, edit, delete activities with duration tracking
- **Progress Tracking**: Status updates and timeline management

### Data Management
- **Dual Table Support**:
  - `test.maps`: Read-only template maps (existing use cases)
  - `test.use_case_maps`: Editable app-created use cases
- **Audit Tracking**: created_by, created_at, updated_by, updated_at fields
- **Export Ready**: Excel-like view of implementation plans

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL/Databricks Lakebase access
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/manjulsinghal1410/use-case-maps.git
cd use-case-maps
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure database connection:
Create a `.env` file or update `config.py` with your Lakebase credentials:
```env
LAKEBASE_HOST=your-instance.cloud.databricks.com
LAKEBASE_PORT=5432
LAKEBASE_DB_NAME=database_use_case
LAKEBASE_DB_USER=your_username
LAKEBASE_DB_PASSWORD=your_password
DB_SSL_MODE=require
```

4. Run the application:
```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## 📋 Usage

### Creating a New Use Case

1. **Add a User**: Click "Add User" in the sidebar and enter user details
2. **Select User**: Choose your user from the dropdown
3. **New Use Case**: Click "➕ New Use Case" button
4. **Fill Details**:
   - Use Case Name
   - Customer/Organization
   - Solution Architect name
   - Account Executive name
   - Start Date and Duration
5. **Configure Requirements**:
   - Check "SSA Required" if Specialized Solutions Architect activities needed
   - Check "POC Phase" if Proof of Concept activities needed
6. **Review Activities**: Edit the pre-populated activities for each stage
7. **Save**: Click "💾 Save Use Case" to save locally and to Lakebase

### Using Existing Maps

1. Open the "🗺️ Existing Maps" expander in the sidebar
2. Browse:
   - **Your Use Cases**: App-created use cases (editable)
   - **Template Maps**: Read-only template maps
3. Click "Use" to create a new use case based on existing map

### Viewing Use Cases

1. Select a use case from "Your Use Cases" list
2. Click "View" to see the Excel-like implementation plan
3. View includes:
   - Stage breakdown (U2-U6)
   - Activity timelines
   - Owner assignments
   - Progress tracking

## 🏗️ Architecture

### Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **Database**: PostgreSQL/Databricks Lakebase
- **Database Drivers**: psycopg2, pg8000, psycopg2cffi (fallback support)
- **Data Processing**: pandas, openpyxl

### Project Structure
```
use-case-maps/
├── app.py                          # Main application
├── config.py                       # Database configuration
├── consolidated_map_template.py    # MAP template definitions
├── template_structure.py           # Template structure helpers
├── services/
│   └── lakebase.py                # Database service layer
├── components/
│   └── plan_form.py               # Plan creation wizard
├── data/
│   └── sample_plans.py            # Sample data
├── use_case_data/                 # Local storage (JSON files)
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

### Database Schema

#### test.use_case_maps
Main table for storing app-created use cases:
- `p_id`: Primary key
- `use_case_id`: Readable use case identifier
- `use_case_name`: Name of the use case
- `customer_name`: Customer organization
- `Stage`: MAP stage (U2-U6)
- `Outcome`: Activity outcome
- `Embedded_Questions`: Activity questions
- `Owner_Name`: Activity owner
- `Start_Date`, `End_Date`: Timeline
- `Progress`: Completion percentage
- `solution_architect`, `account_executive`: Team members
- `ssa_required`, `poc_required`: Conditional flags
- `created_by`, `created_at`, `updated_by`, `updated_at`: Audit fields

#### test.maps
Read-only template maps table for reference use cases.

## 🎨 Databricks Branding

The application uses official Databricks colors and styling:
- Primary: `#FF3621` (Databricks Red)
- Secondary: `#FF8C00` (Orange)
- Dark Background: `#0B1929` to `#050A0F`
- Accent: `#1B3139` (Dark Teal)

## 🔧 Configuration

### Database Fallback
The application gracefully degrades to demo mode if database connection fails, using local JSON files for storage.

### Multi-Driver Support
Supports multiple PostgreSQL drivers for better compatibility:
1. psycopg2 (preferred, best performance)
2. pg8000 (pure Python, cloud-friendly)
3. psycopg2cffi (alternative implementation)

## 📝 Development

### Running Tests
```bash
# Test database connection and new features
python test_new_features.py

# Test connection to Lakebase
python test_connection_simple.py

# Test application functionality
python test_functionality.py
```

### Code Quality
- No syntax errors (verified with `python -m py_compile`)
- Modular architecture with service layer separation
- Comprehensive error handling and logging

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is proprietary software for Databricks use case management.

## 👥 Authors

- **Manjul Singhal** - Initial development and architecture

## 🙏 Acknowledgments

- Databricks MAP (Mutual Action Plan) methodology
- Streamlit framework for rapid web app development
- PostgreSQL/Lakebase for reliable data storage

## 📞 Support

For issues, questions, or suggestions, please contact the development team or open an issue in the repository.

---

**Built with ❤️ for Databricks Solution Architects and Account Executives**
