import datetime
import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="School Pickup Manager", layout="wide")

# Load student roster from CSV file (case-insensitive check for filename)
csv_filename = "Students.csv" if os.path.exists("Students.csv") else "students.csv"

if os.path.exists(csv_filename):
    try:
        df_students = pd.read_csv(csv_filename)
        # Grab the first column, drop empty rows, convert to string and sort
        STUDENT_ROSTER = sorted(df_students.iloc[:, 0].dropna().astype(str).str.strip().tolist())
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        STUDENT_ROSTER = []
else:
    # Fallback list if CSV isn't found
    STUDENT_ROSTER = ["Sample Student A", "Sample Student B", "Sample Student C"]
    st.warning("`Students.csv` not found in repository. Using sample roster.")

# Initialize Shared State across all users
if "spots" not in st.session_state:
    st.session_state.spots = {i: "" for i in range(1, 9)}

if "pickup_log" not in st.session_state:
    st.session_state.pickup_log = []

st.title("🚗 School Dismissal Pickup Line Manager")
st.write("Live status for Spots 1–8. Updates are visible to all staff.")

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Pickup Spots (1–8)")
    
    # Render Spots in 2 columns of 4
    grid_col1, grid_col2 = st.columns(2)
    
    for spot_num in range(1, 9):
        target_col = grid_col1 if spot_num <= 4 else grid_col2
        
        with target_col:
            st.markdown(f"### Spot {spot_num}")
            current_student = st.session_state.spots[spot_num]
            
            if current_student:
                st.info(f"**Current Student:** {current_student}")
                if st.button(f"Dismiss Spot {spot_num}", key=f"dismiss_{spot_num}", type="primary"):
                    timestamp = datetime.datetime.now().strftime("%I:%M:%S %p")
                    st.session_state.pickup_log.insert(0, {
                        "Spot": f"Spot {spot_num}",
                        "Student": current_student,
                        "Time": timestamp
                    })
                    st.session_state.spots[spot_num] = ""
                    st.rerun()
            else:
                selected_name = st.selectbox(
                    f"Select student for Spot {spot_num}",
                    options=[""] + STUDENT_ROSTER,
                    key=f"select_{spot_num}",
                    label_visibility="collapsed"
                )
                if selected_name:
                    st.session_state.spots[spot_num] = selected_name
                    st.rerun()
            st.divider()

with col_right:
    st.subheader("📋 Today's Pickup Log")
    
    # Control buttons row
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("Refresh Live Data", use_container_width=True):
            st.rerun()
            
    with btn_col2:
        if st.button("Clear Log", type="secondary", use_container_width=True, disabled=len(st.session_state.pickup_log) == 0):
            st.session_state.pickup_log = []
            st.rerun()
            
    st.write("") # Spacing

    if st.session_state.pickup_log:
        df_log = pd.DataFrame(st.session_state.pickup_log)
        st.dataframe(df_log, use_container_width=True, hide_index=True)
        
        # Download button for attendance records
        csv_data = df_log.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Log (CSV)",
            data=csv_data,
            file_name=f"pickup_log_{datetime.date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.write("No pickups recorded yet today.")
