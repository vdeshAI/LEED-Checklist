import streamlit as st
import pandas as pd

st.set_page_config(page_title="LEED Checklist & Score Estimator", layout="wide")

# -----------------------------
# Basic LEED data model
# -----------------------------
# This demo app uses a simplified score structure aligned to common LEED scorecard
# category totals for BD+C-style projects. Projects must still meet prerequisites,
# documentation, and official review requirements through USGBC/GBCI.

LEED_CATEGORIES = {
    "Integrative Process": {
        "max_points": 1,
        "credits": {
            "Integrative Process": 1,
        },
    },
    "Location and Transportation": {
        "max_points": 16,
        "credits": {
            "LEED for Neighborhood Development Location": 5,
            "Sensitive Land Protection": 1,
            "High Priority Site": 2,
            "Surrounding Density and Diverse Uses": 5,
            "Access to Quality Transit": 5,
            "Bicycle Facilities": 1,
            "Reduced Parking Footprint": 1,
            "Green Vehicles": 1,
        },
    },
    "Sustainable Sites": {
        "max_points": 10,
        "credits": {
            "Construction Activity Pollution Prevention": 0,
            "Site Assessment": 1,
            "Protect or Restore Habitat": 2,
            "Open Space": 1,
            "Rainwater Management": 3,
            "Heat Island Reduction": 2,
            "Light Pollution Reduction": 1,
        },
    },
    "Water Efficiency": {
        "max_points": 11,
        "credits": {
            "Outdoor Water Use Reduction": 2,
            "Indoor Water Use Reduction": 6,
            "Cooling Tower Water Use": 2,
            "Water Metering": 1,
        },
    },
    "Energy and Atmosphere": {
        "max_points": 33,
        "credits": {
            "Enhanced Commissioning": 6,
            "Optimize Energy Performance": 18,
            "Advanced Energy Metering": 1,
            "Grid Harmonization": 2,
            "Renewable Energy": 5,
            "Enhanced Refrigerant Management": 1,
            "Green Power and Carbon Offsets": 2,
        },
    },
    "Materials and Resources": {
        "max_points": 13,
        "credits": {
            "Storage and Collection of Recyclables": 0,
            "Construction and Demolition Waste Management Planning": 0,
            "Building Life-Cycle Impact Reduction": 5,
            "Building Product Disclosure and Optimization - EPDs": 2,
            "Building Product Disclosure and Optimization - Sourcing": 2,
            "Building Product Disclosure and Optimization - Material Ingredients": 2,
            "Construction and Demolition Waste Management": 2,
        },
    },
    "Indoor Environmental Quality": {
        "max_points": 16,
        "credits": {
            "Enhanced Indoor Air Quality Strategies": 2,
            "Low-Emitting Materials": 3,
            "Construction Indoor Air Quality Management Plan": 1,
            "Indoor Air Quality Assessment": 2,
            "Thermal Comfort": 1,
            "Interior Lighting": 2,
            "Daylight": 3,
            "Quality Views": 1,
            "Acoustic Performance": 1,
        },
    },
    "Innovation": {
        "max_points": 6,
        "credits": {
            "Innovation": 5,
            "LEED Accredited Professional": 1,
        },
    },
    "Regional Priority": {
        "max_points": 4,
        "credits": {
            "Regional Priority Credits": 4,
        },
    },
}

CERTIFICATION_LEVELS = [
    (80, "Platinum"),
    (60, "Gold"),
    (50, "Silver"),
    (40, "Certified"),
    (0, "Below Certified"),
]

PREREQUISITES = {
    "General": [
        "Confirm correct LEED rating system and project scope",
        "Register project with USGBC/GBCI",
        "Verify owner goals, budget, and certification target",
        "Create documentation plan and assign responsible team members",
    ],
    "Sustainable Sites": [
        "Construction activity pollution prevention plan in place",
    ],
    "Water Efficiency": [
        "Outdoor water use prerequisite reviewed",
        "Indoor water use prerequisite reviewed",
        "Building-level water metering planned",
    ],
    "Energy and Atmosphere": [
        "Fundamental commissioning scope defined",
        "Minimum energy performance reviewed",
        "Building-level energy metering planned",
        "Fundamental refrigerant management reviewed",
    ],
    "Materials and Resources": [
        "Recyclables collection/storage addressed",
        "Construction and demolition waste management planning completed",
    ],
    "Indoor Environmental Quality": [
        "Minimum indoor air quality performance reviewed",
        "Environmental tobacco smoke control addressed",
    ],
}

# -----------------------------
# Helpers
# -----------------------------
def certification_label(score: int) -> str:
    for min_score, label in CERTIFICATION_LEVELS:
        if score >= min_score:
            return label
    return "Below Certified"


def score_color(score: int) -> str:
    if score >= 80:
        return "#6f42c1"
    if score >= 60:
        return "#d4a017"
    if score >= 50:
        return "#9aa0a6"
    if score >= 40:
        return "#2e8b57"
    return "#c0392b"


# -----------------------------
# Session state init
# -----------------------------
if "selected_points" not in st.session_state:
    st.session_state.selected_points = {}
    for category, cat_data in LEED_CATEGORIES.items():
        for credit in cat_data["credits"]:
            st.session_state.selected_points[f"{category}::{credit}"] = 0

if "checked_prereqs" not in st.session_state:
    st.session_state.checked_prereqs = {}
    for group, items in PREREQUISITES.items():
        for item in items:
            st.session_state.checked_prereqs[f"{group}::{item}"] = False

# -----------------------------
# UI
# -----------------------------
st.title("LEED Checklist & Score Estimator")
st.caption("A Streamlit starter app to manage a LEED-style project checklist and estimate certification score.")

with st.sidebar:
    st.header("Project Setup")
    project_name = st.text_input("Project name", "My LEED Project")
    project_type = st.selectbox(
        "Project type",
        [
            "BD+C: New Construction",
            "BD+C: Core and Shell",
            "ID+C: Commercial Interiors",
            "O+M: Existing Buildings",
            "Custom / Early Feasibility",
        ],
    )
    target_level = st.selectbox("Target certification", ["Certified", "Silver", "Gold", "Platinum"])
    st.markdown("---")
    st.info("This app is for planning and early scoring. Official certification depends on the exact rating system, prerequisites, documentation, and GBCI review.")

# Calculate totals
category_rows = []
for category, cat_data in LEED_CATEGORIES.items():
    subtotal = 0
    for credit, max_pts in cat_data["credits"].items():
        subtotal += st.session_state.selected_points[f"{category}::{credit}"]
    category_rows.append(
        {
            "Category": category,
            "Earned": subtotal,
            "Available": cat_data["max_points"],
            "Remaining": cat_data["max_points"] - subtotal,
        }
    )

summary_df = pd.DataFrame(category_rows)
total_earned = int(summary_df["Earned"].sum())
total_available = int(summary_df["Available"].sum())
cert_level = certification_label(total_earned)

prereq_total = sum(len(v) for v in PREREQUISITES.values())
prereq_done = sum(1 for v in st.session_state.checked_prereqs.values() if v)
prereq_pct = prereq_done / prereq_total if prereq_total else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Project", project_name)
col2.metric("Estimated LEED Score", f"{total_earned} / {total_available}")
col3.metric("Estimated Level", cert_level)
col4.metric("Checklist Complete", f"{prereq_done}/{prereq_total}")

st.progress(min(total_earned / 110, 1.0), text=f"Score progress toward 110-point scale: {total_earned} points")
st.progress(prereq_pct, text=f"Checklist completion: {prereq_done} of {prereq_total} prerequisite/planning items")

# Tabs
score_tab, checklist_tab, dashboard_tab, export_tab = st.tabs([
    "Score Estimator",
    "Checklist",
    "Dashboard",
    "Export",
])

with score_tab:
    st.subheader("Credit-by-credit score selection")
    st.write("For each credit, choose the points you realistically expect to achieve.")

    for category, cat_data in LEED_CATEGORIES.items():
        with st.expander(f"{category} (max {cat_data['max_points']} pts)", expanded=False):
            cat_total = 0
            for credit, max_pts in cat_data["credits"].items():
                key = f"{category}::{credit}"
                if max_pts == 0:
                    st.checkbox(
                        f"{credit} (prerequisite / required item)",
                        key=f"req_display::{key}",
                        value=False,
                        disabled=True,
                        help="Shown as a reminder. This item does not directly add points in this demo score model.",
                    )
                    continue
                chosen = st.slider(
                    f"{credit}",
                    min_value=0,
                    max_value=max_pts,
                    value=st.session_state.selected_points[key],
                    key=f"slider::{key}",
                )
                st.session_state.selected_points[key] = chosen
                cat_total += chosen
            st.markdown(f"**Category subtotal:** {cat_total} / {cat_data['max_points']} points")

with checklist_tab:
    st.subheader("Prerequisite and action checklist")
    st.write("Use this section to track required items and project-management tasks.")

    for group, items in PREREQUISITES.items():
        st.markdown(f"### {group}")
        for item in items:
            pkey = f"{group}::{item}"
            st.session_state.checked_prereqs[pkey] = st.checkbox(
                item,
                value=st.session_state.checked_prereqs[pkey],
                key=f"chk::{pkey}",
            )

    st.markdown("### Custom action items")
    custom_items = st.text_area(
        "Add custom tasks (one per line)",
        placeholder="Example:\nCollect commissioning report\nConfirm low-emitting materials submittals\nUpload transit maps",
    )

with dashboard_tab:
    st.subheader("Score dashboard")

    left, right = st.columns([1.2, 1])
    with left:
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        st.bar_chart(summary_df.set_index("Category")[["Earned", "Remaining"]])

    with right:
        target_min = {
            "Certified": 40,
            "Silver": 50,
            "Gold": 60,
            "Platinum": 80,
        }[target_level]
        gap = max(target_min - total_earned, 0)

        st.markdown(
            f"""
            <div style="padding: 1rem; border-radius: 12px; background: {score_color(total_earned)}22; border: 1px solid {score_color(total_earned)};">
                <h4 style="margin:0;">Estimated Certification Outcome</h4>
                <p style="font-size: 1.15rem; margin: 0.3rem 0 0.5rem 0;"><strong>{cert_level}</strong></p>
                <p style="margin:0;">Target selected: <strong>{target_level}</strong></p>
                <p style="margin:0.3rem 0 0 0;">Points needed to reach target: <strong>{gap}</strong></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### Suggested next steps")
        if total_earned < 40:
            st.warning("Project is currently below the usual LEED certification threshold. Focus on prerequisites first, then target high-value points in Energy, Water, and Location categories.")
        elif total_earned < 50:
            st.info("Project appears near Certified. Review easy-to-capture points in Innovation, Regional Priority, and commissioning/documentation quality.")
        elif total_earned < 60:
            st.info("Project appears near Silver. Focus on energy optimization, water reduction, and material transparency credits to move up.")
        elif total_earned < 80:
            st.success("Project appears in Gold range. Fine-tune documentation and identify remaining Innovation and Regional Priority opportunities.")
        else:
            st.success("Project appears in Platinum range. Carefully validate all prerequisites and documentation assumptions before submission.")

with export_tab:
    st.subheader("Export summary")

    export_df = summary_df.copy()
    export_df.loc[len(export_df)] = {
        "Category": "TOTAL",
        "Earned": total_earned,
        "Available": total_available,
        "Remaining": total_available - total_earned,
    }

    st.download_button(
        label="Download score summary as CSV",
        data=export_df.to_csv(index=False).encode("utf-8"),
        file_name="leed_score_summary.csv",
        mime="text/csv",
    )

    checklist_df = pd.DataFrame(
        [
            {
                "Section": key.split("::")[0],
                "Item": key.split("::")[1],
                "Completed": value,
            }
            for key, value in st.session_state.checked_prereqs.items()
        ]
    )

    st.download_button(
        label="Download checklist as CSV",
        data=checklist_df.to_csv(index=False).encode("utf-8"),
        file_name="leed_checklist.csv",
        mime="text/csv",
    )

    st.markdown("### Notes")
    st.write(f"Project Type: {project_type}")
    st.write(f"Target Level: {target_level}")
    st.write(f"Estimated Score: {total_earned}")
    st.write(f"Estimated Certification: {cert_level}")
    if custom_items.strip():
        st.text_area("Custom action items captured", custom_items, height=180)

st.markdown("---")
st.caption("Planning tool only. Verify the exact LEED version, rating system, prerequisites, and credit requirements through current USGBC/GBCI documentation before using this for real project decisions.")
