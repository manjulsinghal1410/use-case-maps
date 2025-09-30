"""
Consolidated MAP Template based on actual Excel template
This contains the real activities from the Databricks MAP template
"""

CONSOLIDATED_MAP_TEMPLATE = {
    "U2": {
        "name": "Uncover",
        "description": "Initial discovery and scoping",
        "activities": [
            {
                "outcome": "Confirm U1 Exit Criteria Met",
                "questions": "Is this a valid use case that is ready to enter U2? Should we push this back to U1 or de-prioritise?",
                "owner": "SA/SA Manager"
            },
            {
                "outcome": "Build and share this plan",
                "questions": "How will you communicate the plan to all parties and ensure continous agreement?",
                "owner": "SA"
            },
            {
                "outcome": "Confirm Business Strategy Alignment",
                "questions": "How does use case align with the customer's strategy and objectives?",
                "owner": "AE"
            },
            {
                "outcome": "Confirm budget and sign off process",
                "questions": "Who will sign off the additional consumption and implementation costs?",
                "owner": "AE"
            },
            {
                "outcome": "Identify & develop a champion",
                "questions": "Do we have a true Champion who can sell internally? What's their influence level?",
                "owner": "AE/SA"
            },
            {
                "outcome": "Confirm and document business case",
                "questions": "What's the measurable business value (ROI, efficiency, risk)? Is there executive-level urgency?",
                "owner": "AE"
            },
            {
                "outcome": "Discover and document as is architecture",
                "questions": "What is the current state? What are its challenges or limitations?",
                "owner": "SA"
            },
            {
                "outcome": "Document and validate to be architecture",
                "questions": "What will the solution look like? How feasible is it?",
                "owner": "SA"
            },
            {
                "outcome": "Perform initial sizing",
                "questions": "How much data? How many users? How complex is the workload? What mix of workload types is it?",
                "owner": "SA"
            },
            {
                "outcome": "Identify possible help needed from SSA, Product or third parties",
                "questions": "Will we be able to access the expertise when we need it in later stages?",
                "owner": "SA",
                "conditional": "ssa"
            },
            {
                "outcome": "Identify technical/product blockers and dependencies",
                "questions": "What is likely to slow things down? How can we mitigate this?",
                "owner": "SA"
            },
            {
                "outcome": "Agree current view of onboarding and live dates",
                "questions": "Is the customer bought into these dates? How would you assess their sense of urgency and priority?",
                "owner": "AE/SA"
            },
            {
                "outcome": "Agree a cadence with the customer for ongoing review and tracking",
                "questions": "How often will you check in to ensure all parties are on track? Will this be part of a wider account cadence or does it merit a separate activity?",
                "owner": "AE/SA"
            },
            {
                "outcome": "Identify possible implementation strategies and participants",
                "questions": "Will this be delivered by PS, Partner, Customer?",
                "owner": "AE/SA"
            },
            {
                "outcome": "Identify and agree evaluation strategy",
                "questions": "What will happen in U3? Can we use an alternative to a POC?",
                "owner": "SA",
                "conditional": "poc"
            },
            {
                "outcome": "Confirm U2 Exit Criteria Met and move to U3",
                "questions": "Are you ready to enter U3?",
                "owner": "AE/SA/SA Manager"
            }
        ]
    },
    "U3": {
        "name": "Understand",
        "description": "Requirements gathering and MVP planning",
        "activities": [
            {
                "outcome": "Define Evaluation Plan & Success Criteria",
                "questions": "What are the agreed success metrics? What will trigger a go/no-go decision? Will there be a POC?",
                "owner": "SA/AE",
                "conditional": "poc"
            },
            {
                "outcome": "Document POC (if POC Needed)",
                "questions": "Does the POC document include success criteria, a plan that shows who is responsible for what and target timescales",
                "owner": "SA",
                "conditional": "poc"
            },
            {
                "outcome": "Document alternative approach if no POC needed",
                "questions": "Do all parties understand and agree to the alternative approach and the success criteria?",
                "owner": "SA"
            },
            {
                "outcome": "Evaluation Milestones Aligned",
                "questions": "What are the exact steps required to hit success criteria? What could accelerate the timeline?",
                "owner": "SA/SA Manager/AE"
            },
            {
                "outcome": "Recheck product blockers and sign up for previews where needed",
                "questions": "How will you ensure that the customer has access to all the required functionality?",
                "owner": "SA"
            },
            {
                "outcome": "Revalidate sizing based on evaluation",
                "questions": "What has the evaluation process shown that will impact our assumptions about sizing? What are the cost implications?",
                "owner": "SA"
            },
            {
                "outcome": "Identify additional risks found in evaluation and mitigation strategies",
                "questions": "Has the POC or other evaluation approach brought any new technical risks to light?",
                "owner": "SA"
            },
            {
                "outcome": "Learning needs assessment",
                "questions": "What additional skills and knowledge does the customer need to ensure success?",
                "owner": "AE/SA"
            },
            {
                "outcome": "Validate Exec Alignment",
                "questions": "Who is the exec decision maker? What's the strength of the relationship? (Promoter/Neutral/Detractor)",
                "owner": "AE/SA"
            },
            {
                "outcome": "Confirm Post-Eval Path",
                "questions": "If successful, what will the customer do next? Is onboarding resourced and approved? Are we still on track to meet our target dates?",
                "owner": "AE/SA"
            },
            {
                "outcome": "Technical Evaluation Complete",
                "questions": "Were success criteria met? What's blocking a decision or deployment?",
                "owner": "SA"
            },
            {
                "outcome": "Engage all parties",
                "questions": "Are all those who will be involved in onboarding the use case engaged?",
                "owner": "AE/SA"
            },
            {
                "outcome": "This Mutual Action Plan is shared and agreed",
                "questions": "Does the customer agree that the evaluation is complete and understand the high level sequence of events outlined in this plan?",
                "owner": "AE/SA"
            },
            {
                "outcome": "Confirm U3 Exit Criteria Met and move to U4 - Technical Win",
                "questions": "Is this a quality technical win that has a clear path through U4 to U5? What could go wrong or slow things down?",
                "owner": "AE/SA/SA Manager"
            }
        ]
    },
    "U4": {
        "name": "Pilot",
        "description": "Pilot implementation and testing",
        "activities": [
            {
                "outcome": "Confirm Eval Exit Criteria Were Met",
                "questions": "Have success metrics been validated and signed off? Who confirmed success on the customer side?",
                "owner": "AE"
            },
            {
                "outcome": "Confirm Executive Go Decision",
                "questions": "Is the economic buyer aligned and committing to proceed? What's the signed path forward?",
                "owner": "AE"
            },
            {
                "outcome": "Workspace & Project Provisioning",
                "questions": "Have workspaces been provisioned? Is the technical deployment path (e.g. DSA vs. self-serve) locked in?",
                "owner": "AE/SA/DSA"
            },
            {
                "outcome": "Delivery Planning: Who, What, When",
                "questions": "Who is delivering (DSA/partner)? What are the timelines, and who owns delivery internally?",
                "owner": "AE/Delivery Team"
            },
            {
                "outcome": "Final Delivery Logistics Sign-Off",
                "questions": "Have all operational elements been reviewed — data access, PS/CS handoff, success tracking?",
                "owner": "AE/PS/SA/DSA"
            },
            {
                "outcome": "Customer Communication on Kickoff",
                "questions": "Is the customer's team briefed on onboarding plan, success milestones, and delivery roles?",
                "owner": "AE"
            }
        ]
    },
    "U5": {
        "name": "Scale",
        "description": "Production deployment and scaling",
        "activities": [
            {
                "outcome": "Onboarding Kickoff Completed",
                "questions": "Has onboarding occurred with technical leads, project owners, and exec sponsors aligned?",
                "owner": "Delivery Team"
            },
            {
                "outcome": "Success Plan Finalized",
                "questions": "Is the success plan tailored to the agreed use case(s) with KPIs, owners, and timelines defined?",
                "owner": "SA/AE"
            },
            {
                "outcome": "Workspace Operational",
                "questions": "Are required workspaces deployed with access, Unity Catalog, and governance configured?",
                "owner": "SA"
            },
            {
                "outcome": "Data Onboarding Complete",
                "questions": "Has the necessary data been ingested, cleaned, and cataloged for the target use case?",
                "owner": "SA"
            },
            {
                "outcome": "Use Case Build Phase",
                "questions": "Are ETL pipelines, SQL queries, dashboards, or ML models being built against real data?",
                "owner": "Customer/Partner"
            },
            {
                "outcome": "Milestone Review: First Value Delivered",
                "questions": "Has the customer run production-like workflows (e.g., first pipeline, query, or model run)?",
                "owner": "SA"
            },
            {
                "outcome": "Enablement & Handoff to Users",
                "questions": "Are end users enabled on tools like DBSQL, notebooks, dashboards, or ML interfaces?",
                "owner": "SA"
            },
            {
                "outcome": "User Onboarding Plan",
                "questions": "Is there a big bang cutover of users or staged user onboarding? How many in each stage? Are the first tranche of users enabled/trained on Databricks?",
                "owner": "SA/AE"
            },
            {
                "outcome": "Value Confirmation Milestone",
                "questions": "Has the business sponsor confirmed the use case delivered expected results or insights?",
                "owner": "AE"
            },
            {
                "outcome": "Final Project Wrap-Up",
                "questions": "Is there a documented outcomes review, with a clear roadmap for next use cases or expansion?",
                "owner": "AE/SA"
            },
            {
                "outcome": "Transition to CS/Scale Team",
                "questions": "Has ownership formally shifted to the CS/Scale team with context and future growth plan?",
                "owner": "AE"
            }
        ]
    }
}
