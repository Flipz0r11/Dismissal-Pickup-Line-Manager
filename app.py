import datetime
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Pickup Line",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Resilient CSV Loader
csv_filename = "Students.csv" if os.path.exists("Students.csv") else "students.csv"
STUDENT_ROSTER = []

if os.path.exists(csv_filename):
  for encoding in ["utf-8", "cp1252", "latin1", "iso-8859-1"]:
    try:
      df_students = pd.read_csv(csv_filename, encoding=encoding)
      STUDENT_ROSTER = sorted(
          df_students.iloc[:, 0].dropna().astype(str).str.strip().tolist()
      )
      break
    except Exception:
      continue

if not STUDENT_ROSTER:
  STUDENT_ROSTER = ["Sample Student A", "Sample Student B"]

# Initialize Session States
if "spots" not in st.session_state:
  st.session_state.spots = {i: "" for i in range(1, 9)}

if "pickup_log" not in st.session_state:
  st.session_state.pickup_log = []

# Header
st.markdown(
    "### 🚗 School Pickup Line Manager", unsafe_allow_html=True
)

# Render 8 Spots in a compact 2-column layout (4 rows of 2 spots)
grid = [st.columns(2) for _ in range(4)]

for index in range(8):
  spot_num = index + 1
  row_idx = index // 2
  col_idx = index % 2

  with grid[row_idx][col_idx]:
    with st.container(border=True):
      current_student = st.session_state.spots[spot_num]

      if current_student:
        st.markdown(
            f"**Spot {spot_num}:** {current_student}",
            unsafe_allow_html=True,
        )
        if st.button(
            f"✓ Picked Up",
            key=f"dismiss_{spot_num}",
            type="primary",
            use_container_width=True,
        ):
          timestamp = datetime.datetime.now().strftime("%I:%M:%S %p")
          st.session_state.pickup_log.insert(
              0,
              {
                  "Spot": f"Spot {spot_num}",
                  "Student": current_student,
                  "Time": timestamp,
              },
          )
          st.session_state.spots[spot_num] = ""
          st.rerun()
      else:
        st.caption(f"**Spot {spot_num}**")
        selected_name = st.selectbox(
            f"Spot {spot_num}",
            options=["-- Select --"] + STUDENT_ROSTER,
            key=f"select_{spot_num}",
            label_visibility="collapsed",
        )
        if selected_name and selected_name != "-- Select --":
          st.session_state.spots[spot_num] = selected_name
          st.rerun()

st.divider()

# Collapsible Bottom Panel for Pickup Log & Controls
with st.expander(
    f"📋 Today's Pickup Log ({len(st.session_state.pickup_log)} Picked Up)"
):
  col_refresh, col_clear = st.columns(2)
  with col_refresh:
    if st.button("Refresh", use_container_width=True):
      st.rerun()
  with col_clear:
    if st.button(
        "Clear Log",
        type="secondary",
        use_container_width=True,
        disabled=len(st.session_state.pickup_log) == 0,
    ):
      st.session_state.pickup_log = []
      st.rerun()

  if st.session_state.pickup_log:
    df_log = pd.DataFrame(st.session_state.pickup_log)
    st.dataframe(df_log, use_container_width=True, hide_index=True)

    csv_data = df_log.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Log (CSV)",
        data=csv_data,
        file_name=f"pickup_log_{datetime.date.today()}.csv",
        mime="text/csv",
        use_container_width=True,
    )
  else:
    st.info("No pickups recorded yet today.")
