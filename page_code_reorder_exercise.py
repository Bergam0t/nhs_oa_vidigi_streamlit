import random

import streamlit as st
from streamlit_dnd import dnd, apply_move

with open("styles.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

# Page config and the top-banner styling live in streamlit_app.py (the entrypoint).

st.title("Vidigi Logging Code")

st.caption("""
Let's add the logging steps into our SimPy model.

However, we've simplified it down to just a single-step model where patients wait for a nurse, see them, then leave.

- First, reorder the code snippets in the left-hand column so they appear in the correct order.
- Then drag and drop the code from the right-hand column to the correct position in the left column.

When you are done, check your answer by clicking the 'Submit' button.
""")

# ---------------------------------------------------------------------------
# The snippets.
#
# The left column is the model code the learner already wrote in Dan's
# exercise; the right column is the new vidigi logging code that has to be
# woven in. Both are defined here in canonical order (matching the nurse
# section of ``Model.attend_clinic`` in model.py) and shuffled before they
# reach the learner.
#
# The ``class Model:`` / ``def attend_clinic`` header is pinned at the top of
# the left column -- it is rendered outside the draggable container so it
# never moves and never counts toward streamlit-dnd's index math.
# ---------------------------------------------------------------------------

DEF_HEADER = """
class Model:
    def attend_clinic(self, patient):
"""

# Left column -- model code (canonical order, header excluded).
S_STARTQ = """
        start_q_nurse = self.env.now
"""
S_WITH = """
        with self.nurse.request() as req:

"""
S_OBT = """
            nurse_obtained = yield req
"""
S_ENDQ = """
            end_q_nurse = self.env.now
            patient.q_time_nurse = end_q_nurse - start_q_nurse
"""
S_SAMPLE = """
            sampled_nurse_act_time = self.nurse_consult_time_dist.sample()
"""
S_TIMEOUT = """
            yield self.env.timeout(sampled_nurse_act_time)
"""

# Right column -- vidigi logging code (canonical order).
S_ARR = """
        self.logger.log_arrival(
            entity_id=patient.id
            )
"""
S_LOGQ = """
        self.logger.log_queue(
            entity_id=patient.id,
            event="nurse_wait_begins"
            )
"""
S_RUS = """
            self.logger.log_resource_use_start(
                entity_id=patient.id,
                event="being_seen_by_nurse",
                resource_id=nurse_obtained.id_attribute,
            )
"""
S_RUE = """
            self.logger.log_resource_use_end(
                    entity_id=patient.id,
                    event="nurse_visit_ends",
                    resource_id=nurse_obtained.id_attribute,
                )
"""
S_DEP = """
        self.logger.log_departure(
            entity_id=patient.id
            )
"""

CANON_LEFT_MOVABLE = [S_STARTQ, S_WITH, S_OBT, S_ENDQ, S_SAMPLE, S_TIMEOUT]
CANON_RIGHT = [S_ARR, S_LOGQ, S_RUS, S_RUE, S_DEP]


def _norm(snippet: str) -> str:
    """Whitespace-insensitive key for a snippet, so identity survives Streamlit
    re-executing this script (fresh string objects) every rerun."""
    return "\n".join(line.rstrip() for line in snippet.strip().splitlines())


SNIPPET_ID = {
    _norm(s): sid
    for s, sid in {
        S_STARTQ: "STARTQ",
        S_WITH: "WITH",
        S_OBT: "OBT",
        S_ENDQ: "ENDQ",
        S_SAMPLE: "SAMPLE",
        S_TIMEOUT: "TIMEOUT",
        S_ARR: "ARR",
        S_LOGQ: "LOGQ",
        S_RUS: "RUS",
        S_RUE: "RUE",
        S_DEP: "DEP",
    }.items()
}

# (A, B, hint): A must appear before B. Checked top to bottom; the first breach
# is the one reported. These rules admit exactly the acceptable orderings:
# {log_arrival, start_q_nurse, log_queue} may sit in any order that keeps
# log_arrival before log_queue, and the end_q_nurse block may swap with
# log_resource_use_start.
ORDER_RULES = [
    ("ARR", "LOGQ", "`log_arrival` should be logged before `log_queue`."),
    (
        "ARR",
        "WITH",
        "`log_arrival` should come before the patient starts waiting for the nurse.",
    ),
    (
        "STARTQ",
        "WITH",
        "`start_q_nurse = self.env.now` must be recorded before `with self.nurse.request()`.",
    ),
    (
        "LOGQ",
        "WITH",
        "`log_queue` (nurse_wait_begins) should come before `with self.nurse.request()`.",
    ),
    (
        "WITH",
        "OBT",
        "`with self.nurse.request() as req:` must come before `nurse_obtained = yield req`.",
    ),
    (
        "OBT",
        "ENDQ",
        "`end_q_nurse = self.env.now` should come after the nurse has been obtained.",
    ),
    (
        "OBT",
        "RUS",
        (
            "`log_resource_use_start` needs `nurse_obtained.id_attribute`, so it must "
            "come after `nurse_obtained = yield req`."
        ),
    ),
    (
        "ENDQ",
        "SAMPLE",
        "Record the queue time before sampling the consultation length.",
    ),
    (
        "RUS",
        "SAMPLE",
        "Log the start of the nurse visit before sampling the consultation length.",
    ),
    (
        "SAMPLE",
        "TIMEOUT",
        "`yield self.env.timeout(...)` must come after you sample `sampled_nurse_act_time`.",
    ),
    (
        "TIMEOUT",
        "RUE",
        "`log_resource_use_end` should come after the consultation time has elapsed.",
    ),
    ("RUE", "DEP", "`log_departure` should be the very last step."),
]


def _shuffled(canonical: list[str]) -> list[str]:
    """A copy of ``canonical`` that is guaranteed not to be in canonical order."""
    items = list(canonical)
    while items == canonical:
        random.shuffle(items)
    return items


if "left" not in st.session_state:
    st.session_state.left = _shuffled(CANON_LEFT_MOVABLE)
if "right" not in st.session_state:
    st.session_state.right = _shuffled(CANON_RIGHT)


col_original, col_logging_snippets = st.columns([0.55, 0.45])

with col_original:
    st.subheader("Model Code")
    st.caption("""
This is part of the SimPy code you worked with in Dan's exercise.
""")
    st.code(DEF_HEADER)  # pinned -- rendered outside the draggable container
    with st.container(key="left", border=True):
        for i, it_l in enumerate(st.session_state.left):
            with st.container(key=f"item_left_{i}", border=True):
                st.code(it_l)

with col_logging_snippets:
    st.subheader("Vidigi Logging Code")
    st.caption("""
This is the new logging code that needs to be woven into the model above.
""")
    with st.container(key="right", border=True):
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

if st.button("Reset / shuffle again"):
    # Keep _stdnd_seen_stdnd so the last drag event isn't replayed onto the
    # freshly shuffled lists.
    st.session_state.pop("left", None)
    st.session_state.pop("right", None)
    st.rerun()

button_submit_pressed = st.button("Submit your answer", type="primary")

if button_submit_pressed:
    left = st.session_state.left
    remaining = len(st.session_state.right)

    if remaining:
        st.warning(
            f"You still have {remaining} logging snippet"
            f"{'s' if remaining != 1 else ''} in the right column to drag into place."
        )
    elif len(left) != len(SNIPPET_ID) or {
        SNIPPET_ID.get(_norm(x)) for x in left
    } != set(SNIPPET_ID.values()):
        st.error(
            "Something's off with the snippets -- hit 'Reset / shuffle again' and try once more."
        )
    else:
        pos = {SNIPPET_ID[_norm(x)]: idx for idx, x in enumerate(left)}
        breach = next(
            (rule for rule in ORDER_RULES if pos[rule[0]] > pos[rule[1]]), None
        )
        if breach:
            st.error(f"Not quite. {breach[2]}")
        else:
            st.success("Woohoo! That's a valid ordering.")
            st.write(
                "Head to the next exercise by using the buttons at the top of the page."
            )
