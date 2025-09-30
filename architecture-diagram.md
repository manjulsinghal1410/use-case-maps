# Use Case Maps - Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Streamlit UI<br/>app.py<br/>Dark Mode Interface]
        Sidebar[Sidebar Navigation<br/>User Management<br/>Use Case List<br/>Database Maps]
        Form[Use Case Form<br/>4-Stage Editor<br/>Activity Management]
        View[Excel-like View<br/>Timeline Display<br/>Progress Tracking]
    end

    subgraph "Business Logic Layer"
        UserMgmt[User Management<br/>Multi-user Support<br/>Session State]
        UseCaseMgmt[Use Case Management<br/>CRUD Operations<br/>ID Generation]
        TemplateMgmt[Template Management<br/>MAP Templates<br/>Conditional Loading]
        DataSync[Data Synchronization<br/>Local + Database<br/>Audit Tracking]
    end

    subgraph "Data Access Layer"
        LakebaseService[Lakebase Service<br/>services/lakebase.py<br/>Connection Pool]
        LocalStorage[Local Storage<br/>JSON Files<br/>use_case_data/]
        ConfigMgmt[Configuration<br/>config.py<br/>.env Support]
    end

    subgraph "Database Schema - Lakebase"
        UseCaseMaps[(test.use_case_maps<br/>App-created Use Cases<br/>Editable)]
        Maps[(test.maps<br/>Template Maps<br/>Read-only)]
        Template[(test.template<br/>MAP Templates<br/>U2-U5 Activities)]
    end

    subgraph "Templates & Data"
        MAPTemplate[MAP Template<br/>consolidated_map_template.py<br/>U2-U6 Stages]
        SampleData[Sample Data<br/>data/sample_plans.py<br/>Demo Mode]
    end

    UI --> Sidebar
    UI --> Form
    UI --> View
    
    Sidebar --> UserMgmt
    Form --> UseCaseMgmt
    Form --> TemplateMgmt
    View --> UseCaseMgmt
    
    UserMgmt --> DataSync
    UseCaseMgmt --> DataSync
    TemplateMgmt --> MAPTemplate
    TemplateMgmt --> DataSync
    
    DataSync --> LakebaseService
    DataSync --> LocalStorage
    
    LakebaseService --> ConfigMgmt
    LakebaseService --> UseCaseMaps
    LakebaseService --> Maps
    LakebaseService --> Template
    
    MAPTemplate --> TemplateMgmt
    SampleData --> LocalStorage
    
    style UI fill:#FF3621,stroke:#333,stroke-width:3px,color:#fff
    style LakebaseService fill:#FF8C00,stroke:#333,stroke-width:2px
    style UseCaseMaps fill:#1B3139,stroke:#333,stroke-width:2px,color:#fff
    style Maps fill:#1B3139,stroke:#333,stroke-width:2px,color:#fff
    style Template fill:#1B3139,stroke:#333,stroke-width:2px,color:#fff
    style MAPTemplate fill:#FFE599,stroke:#333,stroke-width:2px
```

## Component Details

### Frontend Layer (Streamlit)
- **UI (app.py)**: Main application entry point, dark mode Databricks-branded interface
- **Sidebar**: User selection, use case list, database maps browser
- **Form**: 4-stage use case creation wizard with activity editor
- **View**: Excel-like implementation plan display

### Business Logic Layer
- **User Management**: Multi-user support with isolated workspaces
- **Use Case Management**: Create, read, update, delete operations with readable ID generation
- **Template Management**: Load MAP templates with SSA/POC conditional logic
- **Data Synchronization**: Dual persistence (local + database) with audit tracking

### Data Access Layer
- **Lakebase Service**: PostgreSQL driver abstraction (psycopg2/pg8000/psycopg2cffi)
- **Local Storage**: JSON-based fallback for demo mode
- **Configuration**: Environment-based database connection management

### Database Schema
- **test.use_case_maps**: Stores app-created use cases (editable)
  - use_case_id, use_case_name, customer_name
  - Stage, Outcome, Embedded_Questions, Owner_Name
  - created_by, created_at, updated_by, updated_at
- **test.maps**: Template maps for reference (read-only)
- **test.template**: MAP template activities (U2-U5)

## Data Flow

### Creating a New Use Case
1. User selects "New Use Case" from sidebar
2. Form loads MAP template from database or consolidated_map_template.py
3. Conditional activities filtered based on SSA/POC requirements
4. SA/AE names auto-populated in owner fields
5. User edits activities and timeline
6. On save:
   - Generate readable use case ID (CUSTOMER-YYYY-MM-SEQ)
   - Save to local JSON file
   - Write to test.use_case_maps table with audit fields
   - Update session state and refresh UI

### Loading Existing Maps
1. Sidebar queries both test.maps and test.use_case_maps
2. Displays categorized lists:
   - "Your Use Cases" (editable, from use_case_maps)
   - "Template Maps" (read-only, from maps)
3. User clicks "Use" to create new use case from template
4. Activities loaded and populated with current user's SA/AE names

## Technology Stack
- **Frontend**: Streamlit 1.x
- **Database**: PostgreSQL/Databricks Lakebase
- **Languages**: Python 3.8+
- **Data Processing**: pandas, openpyxl
- **Drivers**: psycopg2, pg8000, psycopg2cffi

