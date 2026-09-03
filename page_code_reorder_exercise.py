import streamlit as st
from streamlit_dnd import dnd, apply_move

st.set_page_config(layout="wide")

code_snippets_left = [
    """
class Model:
    def attend_clinic(self, patient):
""",
    """
        start_q_registration = self.env.now
""",
]


code_snippets_right = [
    """
        self.logger.log_arrival(
            entity_id=patient.id
            )
""",
    """
        self.logger.log_queue(
            entity_id=patient.id,
            event="receptionist_wait_begins"
            )
""",
]

col_original, col_logging_snippets = st.columns(2)


if "left" not in st.session_state:
    st.session_state.left = code_snippets_left
if "right" not in st.session_state:
    st.session_state.right = code_snippets_right

with col_original, st.container(key="left", border=True):
    for i, it_l in enumerate(st.session_state.left):
        with st.container(key=f"item_left_{i}", border=True):
            st.code(it_l)


with col_logging_snippets, st.container(key="right", border=True):
    for j, it_r in enumerate(st.session_state.right):
        with st.container(key=f"item_right_{j}", border=True):
            st.code(it_r)

lists = {"left": st.session_state.left, "right": st.session_state.right}

event = dnd(
    "left", "right", sources=["left", "right"], destinations=["left"], indicator="ghost"
)

if event:
    apply_move(event, lists)
    st.rerun()
