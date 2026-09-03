import streamlit as st

pg = st.navigation(
    [
        st.Page("page_code_reorder_exercise.py", title="Exercise 1"),
        st.Page("page_generate_animation.py", title="Exercise 2"),
    ],
    position="top",
)

pg.run()
