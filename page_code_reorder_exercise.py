import streamlit as st
from streamlit_dnd import dnd, apply_move

# Page config and the top-banner styling live in streamlit_app.py (the entrypoint).

st.title("Vidigi Logging Code")

st.caption("""
Let's add the logging steps into our SimPy model.

However, we've simplified it down to just a single-step model where patients wait for a nurse, see them, then leave.

- First, reorder the code snippets in the left-hand column so they appear in the correct order.
- Then drag and drop the code from the right-hand column to the correct position in the left column.

When you are done, check your answer by clicking the 'submit' button.
""")

code_snippets_left = [
    """
class Model:
    def attend_clinic(self, patient):
""",
    """
        start_q_nurse = self.env.now
""",
    """
        with self.nurse.request() as req:

""",
    """
            nurse_obtained = yield req
""",
    """
            end_q_nurse = self.env.now
            patient.q_time_nurse = end_q_nurse - start_q_nurse
            """
    """
            sampled_nurse_act_time = self.nurse_consult_time_dist.sample()
""",
    """
            yield self.env.timeout(sampled_nurse_act_time)
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
            event="nurse_wait_begins"
            )
""",
    """
            self.logger.log_resource_use_start(
                entity_id=patient.id,
                event="being_seen_by_nurse",
                resource_id=nurse_obtained.id_attribute,
            )
""",
    """
            self.logger.log_resource_use_end(
                    entity_id=patient.id,
                    event="nurse_visit_ends",
                    resource_id=nurse_obtained.id_attribute,
                )
""",
    """
        self.logger.log_departure(
            entity_id=patient.id
            )
""",
]

col_original, col_logging_snippets = st.columns([0.55, 0.45])


if "left" not in st.session_state:
    st.session_state.left = code_snippets_left
if "right" not in st.session_state:
    st.session_state.right = code_snippets_right

col_original.subheader("Model Code")
col_original.caption("""
This is part of the SimPy code you worked with in Dan's exercise.
""")

col_logging_snippets.subheader("Vidigi Logging Code")

col_logging_snippets.caption("""
This is the new logging code that goes with
""")

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

button_submit_pressed = st.button("Submit your answer")

if button_submit_pressed:
    st.write("Woohoo!")
    st.write("Head to the next exercise by using the buttons at the top of the page.")
