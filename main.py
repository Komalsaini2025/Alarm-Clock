import streamlit as st 
import base64
import datetime
import os
import time

# ---- Utility to embed background image ----
def get_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

img_base64 = get_base64("im.jpg")

# ---- Streamlit page config ----
st.set_page_config(page_title="Alarm Clock", page_icon="⏰", layout="wide")

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/webp;base64,{img_base64}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---- Alarm UI ----
st.title("⏰ Multi Alarm Clock with Different Sounds")
st.subheader("Set up to 3 alarms. Each alarm rings with its own sound!")

# ---- Number of alarms ----
num_alarms = 3

# ---- Session State Init ----
for i in range(num_alarms):
    if f"alarm_set_{i}" not in st.session_state:
        st.session_state[f"alarm_set_{i}"] = False
    if f"alarm_time_{i}" not in st.session_state:
        st.session_state[f"alarm_time_{i}"] = None
    if f"alarm_triggered_{i}" not in st.session_state:
        st.session_state[f"alarm_triggered_{i}"] = False

# ---- Sidebar Inputs ----
for i in range(num_alarms):
    st.sidebar.markdown(f"### Alarm {i+1}")
    alarm_hour = st.sidebar.selectbox(f"Hour {i+1}", list(range(24)), key=f"hour_{i}")
    alarm_minute = st.sidebar.selectbox(f"Minute {i+1}", list(range(60)), key=f"minute_{i}")
    alarm_second = st.sidebar.selectbox(f"Second {i+1}", list(range(60)), key=f"second_{i}")

    alarm_time = f"{alarm_hour:02}:{alarm_minute:02}:{alarm_second:02}"
    st.sidebar.success(f"Alarm {i+1} set for: {alarm_time}")

    if st.sidebar.button(f"Start Alarm {i+1}"):
        selected_time = datetime.time(hour=alarm_hour, minute=alarm_minute, second=alarm_second)
        current_time = datetime.datetime.now().time()

        if selected_time <= current_time:
            st.warning(f"⛔ Alarm {i+1}: Please select a future time.")
        else:
            st.session_state[f"alarm_time_{i}"] = selected_time
            st.session_state[f"alarm_set_{i}"] = True
            st.session_state[f"alarm_triggered_{i}"] = False
            st.info(f"✅ Alarm {i+1} set for {alarm_time}")

# ---- Audio HTML (Frontend Playback) ----
def play_audio_html(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    audio_html = f"""
    <audio autoplay hidden>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# ---- Alarm Checking Loop ----
any_alarm_waiting = False  # This flag tracks if any alarm is still waiting

status_list = [st.empty() for _ in range(num_alarms)]  # separate container for each alarm

for i in range(num_alarms):
    if st.session_state[f"alarm_set_{i}"] and not st.session_state[f"alarm_triggered_{i}"]:
        current_time = datetime.datetime.now().time().replace(microsecond=0)
        alarm_time_obj = st.session_state[f"alarm_time_{i}"]
        alarm_time_str = alarm_time_obj.strftime('%H:%M:%S')

        status = status_list[i]

        if current_time >= alarm_time_obj:
            st.session_state[f"alarm_triggered_{i}"] = True
            st.session_state[f"alarm_set_{i}"] = False

            status.markdown(
                f"""
                <div style='font-size:2em; color:black; font-weight:bold; animation: blinker 1s linear infinite;'>
                    ⏰ ALARM {i+1}! It's {alarm_time_str}! ⏰
                </div>
                <style>
                @keyframes blinker {{
                  50% {{ opacity: 0; }}
                }}
                </style>
                """,
                unsafe_allow_html=True
            )

            alarm_file = f"audio/audio{i+1}.mp3"

            if os.path.exists(alarm_file):
                play_audio_html(alarm_file)
            else:
                st.error(f"Missing '{alarm_file}' file! Make sure it is in the 'audio' folder.")

        else:
            status.info(f"⏳ Alarm {i+1} waiting... Current time: {current_time.strftime('%H:%M:%S')}")
            any_alarm_waiting = True  # There is at least one alarm still waiting

# ---- Only rerun once if any alarms are waiting ----
if any_alarm_waiting:
    time.sleep(2)
    st.rerun()



