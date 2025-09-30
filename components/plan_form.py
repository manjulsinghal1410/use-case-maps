"""
Sophisticated Add New Use Case Plan functionality
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from data.sample_plans import STAGE_DEFINITIONS, PROGRESS_OPTIONS, get_sample_templates

def render_plan_creation_wizard():
    """Render the sophisticated plan creation wizard"""

    st.header("🚀 Create New Use Case Plan")

    # Progress indicator
    if "wizard_step" not in st.session_state:
        st.session_state.wizard_step = 1

    # Show progress
    progress_cols = st.columns(4)
    steps = [
        "1. Basic Info",
        "2. Template",
        "3. Actions",
        "4. Review"
    ]

    for i, (col, step) in enumerate(zip(progress_cols, steps)):
        with col:
            if i + 1 < st.session_state.wizard_step:
                st.success(f"✅ {step}")
            elif i + 1 == st.session_state.wizard_step:
                st.info(f"🔄 {step}")
            else:
                st.write(f"⏳ {step}")

    st.markdown("---")

    # Initialize plan data in session state
    if "new_plan" not in st.session_state:
        st.session_state.new_plan = {
            "name": "",
            "description": "",
            "customer": "",
            "template": None,
            "actions": []
        }

    # Step 1: Basic Information
    if st.session_state.wizard_step == 1:
        render_basic_info_step()

    # Step 2: Template Selection
    elif st.session_state.wizard_step == 2:
        render_template_step()

    # Step 3: Actions Configuration
    elif st.session_state.wizard_step == 3:
        render_actions_step()

    # Step 4: Review and Create
    elif st.session_state.wizard_step == 4:
        render_review_step()

def render_basic_info_step():
    """Render basic information collection step"""
    st.subheader("📋 Plan Basic Information")

    col1, col2 = st.columns(2)

    with col1:
        plan_name = st.text_input(
            "Plan Name *",
            value=st.session_state.new_plan.get("name", ""),
            placeholder="e.g., Customer GenAI Implementation",
            help="Give your use case plan a descriptive name"
        )

        customer = st.text_input(
            "Customer/Client *",
            value=st.session_state.new_plan.get("customer", ""),
            placeholder="e.g., Acme Corp",
            help="The customer or client for this use case"
        )

    with col2:
        description = st.text_area(
            "Description",
            value=st.session_state.new_plan.get("description", ""),
            placeholder="Describe the use case and objectives...",
            height=100,
            help="Detailed description of the use case and its objectives"
        )

        priority = st.selectbox(
            "Priority",
            ["High", "Medium", "Low"],
            help="Priority level for this use case plan"
        )

    # Validation and navigation
    st.markdown("---")
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("← Back to Plans", key="back_to_plans"):
            st.session_state.show_create_plan = False
            st.session_state.wizard_step = 1
            st.rerun()

    with col2:
        can_proceed = plan_name.strip() and customer.strip()
        if st.button("Next: Template Selection →", disabled=not can_proceed, key="next_template"):
            st.session_state.new_plan.update({
                "name": plan_name,
                "description": description,
                "customer": customer,
                "priority": priority
            })
            st.session_state.wizard_step = 2
            st.rerun()

        if not can_proceed:
            st.warning("Please fill in Plan Name and Customer to continue")

def render_template_step():
    """Render template selection step"""
    st.subheader("📝 Choose a Template")

    templates = get_sample_templates()

    # Template selection
    template_options = ["Start from scratch"] + [t["name"] for t in templates]

    selected_template = st.radio(
        "Select a starting template:",
        template_options,
        help="Choose a template to pre-populate common actions, or start from scratch"
    )

    # Show template details
    if selected_template != "Start from scratch":
        template = next(t for t in templates if t["name"] == selected_template)

        with st.expander(f"📖 Template Details: {selected_template}", expanded=True):
            st.write(f"**Description:** {template['description']}")

            if "default_actions" in template["template_data"]:
                st.write("**Included Actions:**")
                for action in template["template_data"]["default_actions"]:
                    st.write(f"• **{action['stage']}:** {action['action']} ({action['duration_days']} days)")

    # Navigation
    st.markdown("---")
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("← Back: Basic Info", key="back_basic"):
            st.session_state.wizard_step = 1
            st.rerun()

    with col2:
        if st.button("Next: Configure Actions →", key="next_actions"):
            # Set template
            if selected_template == "Start from scratch":
                st.session_state.new_plan["template"] = None
                st.session_state.new_plan["actions"] = []
            else:
                template = next(t for t in templates if t["name"] == selected_template)
                st.session_state.new_plan["template"] = template

                # Generate actions from template
                actions = []
                base_date = datetime.now().date()
                current_date = base_date

                for action in template["template_data"]["default_actions"]:
                    actions.append({
                        "stage": action["stage"],
                        "action": action["action"],
                        "owner_name": "",
                        "start_date": current_date,
                        "end_date": current_date + timedelta(days=action["duration_days"]),
                        "progress": "Not Started",
                        "notes": ""
                    })
                    current_date += timedelta(days=action["duration_days"] + 1)

                st.session_state.new_plan["actions"] = actions

            st.session_state.wizard_step = 3
            st.rerun()

def render_actions_step():
    """Render actions configuration step"""
    st.subheader("⚙️ Configure Actions")

    if not st.session_state.new_plan.get("actions"):
        st.info("No actions from template. Add your first action below.")
        st.session_state.new_plan["actions"] = []

    # Add new action form
    with st.expander("➕ Add New Action", expanded=len(st.session_state.new_plan["actions"]) == 0):
        col1, col2 = st.columns(2)

        with col1:
            new_stage = st.selectbox(
                "Stage",
                list(STAGE_DEFINITIONS.keys()),
                format_func=lambda x: f"{x} - {STAGE_DEFINITIONS[x]['name']}",
                key="new_action_stage"
            )

            new_action = st.text_input(
                "Action Description",
                placeholder="Describe what needs to be done...",
                key="new_action_desc"
            )

            new_owner = st.text_input(
                "Owner",
                placeholder="Who is responsible?",
                key="new_action_owner"
            )

        with col2:
            new_start_date = st.date_input(
                "Start Date",
                value=datetime.now().date(),
                key="new_action_start"
            )

            new_end_date = st.date_input(
                "End Date",
                value=datetime.now().date() + timedelta(days=7),
                key="new_action_end"
            )

            new_progress = st.selectbox(
                "Progress",
                PROGRESS_OPTIONS,
                key="new_action_progress"
            )

        new_notes = st.text_area(
            "Notes (optional)",
            placeholder="Any additional notes or context...",
            key="new_action_notes"
        )

        if st.button("Add Action", key="add_action_btn"):
            if new_action.strip():
                st.session_state.new_plan["actions"].append({
                    "stage": new_stage,
                    "action": new_action,
                    "owner_name": new_owner,
                    "start_date": new_start_date,
                    "end_date": new_end_date,
                    "progress": new_progress,
                    "notes": new_notes
                })
                st.success("Action added!")
                st.rerun()
            else:
                st.warning("Please enter an action description")

    # Display current actions
    if st.session_state.new_plan["actions"]:
        st.write("**Current Actions:**")

        actions_df = pd.DataFrame(st.session_state.new_plan["actions"])
        actions_df["stage_name"] = actions_df["stage"].map(
            lambda x: f"{x} - {STAGE_DEFINITIONS.get(x, {}).get('name', 'Unknown')}"
        )

        # Group by stage
        for stage in ["U2", "U3", "U4", "U5", "U6"]:
            stage_actions = [i for i, action in enumerate(st.session_state.new_plan["actions"]) if action["stage"] == stage]

            if stage_actions:
                stage_info = STAGE_DEFINITIONS[stage]
                st.markdown(f"**{stage} - {stage_info['name']}**")

                for idx in stage_actions:
                    action = st.session_state.new_plan["actions"][idx]

                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])

                        with col1:
                            st.write(f"• {action['action']}")
                            if action.get('owner_name'):
                                st.caption(f"Owner: {action['owner_name']}")

                        with col2:
                            st.caption(f"{action['start_date']} → {action['end_date']}")

                        with col3:
                            if st.button(f"🗑️", key=f"delete_{idx}", help="Delete action"):
                                st.session_state.new_plan["actions"].pop(idx)
                                st.rerun()

                st.write("")  # Add spacing

    # Navigation
    st.markdown("---")
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("← Back: Template", key="back_template"):
            st.session_state.wizard_step = 2
            st.rerun()

    with col2:
        can_proceed = len(st.session_state.new_plan["actions"]) > 0
        if st.button("Next: Review →", disabled=not can_proceed, key="next_review"):
            st.session_state.wizard_step = 4
            st.rerun()

        if not can_proceed:
            st.warning("Please add at least one action to continue")

def render_review_step():
    """Render review and creation step"""
    st.subheader("📊 Review & Create Plan")

    plan = st.session_state.new_plan

    # Plan summary
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Plan Summary:**")
        st.write(f"• **Name:** {plan['name']}")
        st.write(f"• **Customer:** {plan['customer']}")
        st.write(f"• **Priority:** {plan.get('priority', 'Medium')}")
        st.write(f"• **Total Actions:** {len(plan['actions'])}")

        if plan.get('template'):
            st.write(f"• **Template Used:** {plan['template']['name']}")

    with col2:
        st.write("**Description:**")
        st.write(plan.get('description', 'No description provided'))

    # Actions summary
    st.write("**Actions Summary:**")
    actions_df = pd.DataFrame(plan["actions"])

    if not actions_df.empty:
        # Summary by stage
        stage_summary = actions_df.groupby('stage').size().reset_index(name='count')
        stage_summary['stage_name'] = stage_summary['stage'].map(
            lambda x: f"{x} - {STAGE_DEFINITIONS.get(x, {}).get('name', 'Unknown')}"
        )

        for _, row in stage_summary.iterrows():
            st.write(f"• **{row['stage_name']}:** {row['count']} actions")

        # Timeline
        st.write("**Timeline:**")
        start_dates = pd.to_datetime(actions_df['start_date'])
        end_dates = pd.to_datetime(actions_df['end_date'])

        st.write(f"• **Start Date:** {start_dates.min().strftime('%B %d, %Y')}")
        st.write(f"• **End Date:** {end_dates.max().strftime('%B %d, %Y')}")
        st.write(f"• **Duration:** {(end_dates.max() - start_dates.min()).days} days")

    # Final actions
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("← Back: Actions", key="back_actions"):
            st.session_state.wizard_step = 3
            st.rerun()

    with col2:
        if st.button("📋 Save as Draft", key="save_draft"):
            # In a real app, this would save to database
            st.success("Plan saved as draft! (Database integration pending)")
            st.balloons()

    with col3:
        if st.button("🚀 Create Plan", key="create_plan", type="primary"):
            # In a real app, this would save to database and set status to active
            st.success("🎉 Use Case Plan created successfully!")
            st.balloons()

            # Reset wizard
            st.session_state.wizard_step = 1
            st.session_state.new_plan = {
                "name": "",
                "description": "",
                "customer": "",
                "template": None,
                "actions": []
            }
            st.session_state.show_create_plan = False

            # Show success message
            st.info("Your plan has been created! Redirecting to plans overview...")
            st.rerun()

def render_add_plan_button():
    """Render the main Add New Plan button"""
    if st.button("➕ Add New Use Case Plan", type="primary", key="add_plan_main"):
        st.session_state.show_create_plan = True
        st.session_state.wizard_step = 1
        st.rerun()

def handle_plan_creation():
    """Main handler for plan creation functionality"""
    if st.session_state.get("show_create_plan", False):
        render_plan_creation_wizard()
        return True
    else:
        render_add_plan_button()
        return False