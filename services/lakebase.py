"""
Lakebase PostgreSQL connection service for Databricks Use Case Plans app
Supports multiple PostgreSQL drivers for better Databricks compatibility
Based on the EasyJet app architecture with enhancements
"""

from config import config

# Try to import PostgreSQL drivers in order of preference
POSTGRES_DRIVER = None
DB_MODULE = None

# Try psycopg2-binary first (best performance)
try:
    import psycopg2
    POSTGRES_DRIVER = "psycopg2"
    DB_MODULE = psycopg2
except ImportError:
    pass

# Try pg8000 as fallback (pure Python, works well in cloud environments)
if not POSTGRES_DRIVER:
    try:
        import pg8000.dbapi
        POSTGRES_DRIVER = "pg8000"
        DB_MODULE = pg8000.dbapi
    except ImportError:
        pass

# Try any other available PostgreSQL driver
if not POSTGRES_DRIVER:
    try:
        import psycopg2cffi
        POSTGRES_DRIVER = "psycopg2cffi"
        DB_MODULE = psycopg2cffi
    except ImportError:
        pass

class LakebaseService:
    def __init__(self):
        self.connection = None
        self.driver_info = f"Using driver: {POSTGRES_DRIVER}" if POSTGRES_DRIVER else "No PostgreSQL driver available"

    def _is_connection_closed(self):
        """Check if connection is closed, handling different driver APIs"""
        if self.connection is None:
            return True

        try:
            # psycopg2 has .closed attribute
            if hasattr(self.connection, 'closed'):
                return self.connection.closed != 0
            # pg8000 and others might not have .closed
            return False
        except:
            return True

    def connect(self):
        """Establish connection to PostgreSQL database"""
        if not POSTGRES_DRIVER:
            raise ImportError("No PostgreSQL driver available")

        if not config.validate():
            raise Exception("Database configuration not properly set. Please provide connection details.")

        if self.connection is None or self._is_connection_closed():
            try:
                conn_params = config.get_connection_params()

                # Adjust connection parameters based on driver
                if POSTGRES_DRIVER == "pg8000":
                    # pg8000 uses different parameter names
                    if 'sslmode' in conn_params:
                        conn_params['ssl_context'] = conn_params.pop('sslmode') == 'require'

                self.connection = DB_MODULE.connect(**conn_params)
                return True
            except Exception as e:
                raise Exception(f"Database connection failed ({POSTGRES_DRIVER}): {e}")
        return True

    def query(self, sql_query, params=None):
        """Execute a query and return results"""
        try:
            if not self.connect():
                return None

            with self.connection.cursor() as cursor:
                if params:
                    cursor.execute(sql_query, params)
                else:
                    cursor.execute(sql_query)

                # If it's a SELECT query, return results
                if sql_query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    # For INSERT, UPDATE, DELETE, commit the transaction
                    self.connection.commit()
                    return cursor.rowcount

        except Exception as e:
            if self.connection:
                try:
                    self.connection.rollback()
                except:
                    pass  # Some drivers might not support rollback
            raise Exception(f"Query execution failed ({POSTGRES_DRIVER}): {e}")

    def execute_many(self, sql_query, params_list):
        """Execute a query with multiple parameter sets"""
        try:
            if not self.connect():
                return None

            with self.connection.cursor() as cursor:
                cursor.executemany(sql_query, params_list)
                self.connection.commit()
                return cursor.rowcount

        except Exception as e:
            if self.connection:
                try:
                    self.connection.rollback()
                except:
                    pass
            raise Exception(f"Batch execution failed ({POSTGRES_DRIVER}): {e}")

    def create_tables(self):
        """Create the necessary tables for use case plans"""
        try:
            if not self.connect():
                return False

            # Create schema if it doesn't exist
            self.query("""
                CREATE SCHEMA IF NOT EXISTS use_case_plans
            """)

            # Create users table
            self.query("""
                CREATE TABLE IF NOT EXISTS use_case_plans.users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    email VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create use_case_plans table
            self.query("""
                CREATE TABLE IF NOT EXISTS use_case_plans.plans (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES use_case_plans.users(id),
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    customer VARCHAR(255),
                    status VARCHAR(50) DEFAULT 'Draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create plan_actions table
            self.query("""
                CREATE TABLE IF NOT EXISTS use_case_plans.actions (
                    id SERIAL PRIMARY KEY,
                    plan_id INTEGER REFERENCES use_case_plans.plans(id) ON DELETE CASCADE,
                    stage VARCHAR(10) NOT NULL,
                    action TEXT NOT NULL,
                    owner_name VARCHAR(255),
                    start_date DATE,
                    end_date DATE,
                    progress VARCHAR(20) DEFAULT 'Not Started',
                    notes TEXT,
                    sort_order INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create plan_templates table
            self.query("""
                CREATE TABLE IF NOT EXISTS use_case_plans.templates (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    template_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            return True

        except Exception as e:
            print(f"Failed to create tables: {e}")
            return False

    def create_use_case_maps_table(self):
        """Create test.use_case_maps table for storing app-created use cases"""
        try:
            if not self.connect():
                return False

            # Create use_case_maps table matching the structure of test.maps
            # but with additional audit fields
            # Note: Assuming test schema already exists
            self.query("""
                CREATE TABLE IF NOT EXISTS test.use_case_maps (
                    p_id BIGSERIAL PRIMARY KEY,
                    use_case_id TEXT NOT NULL,
                    use_case_name TEXT,
                    customer_name TEXT,
                    "Stage" TEXT,
                    "Outcome" TEXT,
                    "Embedded_Questions" TEXT,
                    "Owner_Name" TEXT,
                    "Start_Date" DATE,
                    "End_Date" DATE,
                    "Progress" DOUBLE PRECISION,
                    "Notes" TEXT,
                    "Action" TEXT,
                    solution_architect TEXT,
                    account_executive TEXT,
                    ssa_required BOOLEAN DEFAULT FALSE,
                    poc_required BOOLEAN DEFAULT FALSE,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_by TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create index on use_case_id for faster lookups
            self.query("""
                CREATE INDEX IF NOT EXISTS idx_use_case_id
                ON test.use_case_maps(use_case_id)
            """)

            # Create index on customer_name for faster filtering
            self.query("""
                CREATE INDEX IF NOT EXISTS idx_customer_name
                ON test.use_case_maps(customer_name)
            """)

            return True

        except Exception as e:
            print(f"Failed to create use_case_maps table: {e}")
            return False

    def close(self):
        """Close database connection"""
        if self.connection and not self._is_connection_closed():
            try:
                self.connection.close()
            except:
                pass  # Connection might already be closed

# Create singleton instance
lakebase = LakebaseService()