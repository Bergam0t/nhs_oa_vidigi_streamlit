import streamlit as st

st.set_page_config(page_title="Vidigi Animation Playground", layout="wide")

st.html(
    """
    <style>
    /* ---- Banner across the top navigation bar ---- */
    /* Sized to the viewport width so it spans the content area; the sidebar
       keeps its plain header. */
    header[data-testid="stHeader"] {
        height: 5rem;
        background-image:
            linear-gradient(rgba(0, 0, 0, 0.38), rgba(0, 0, 0, 0.38)),
            url("/app/static/banner.png");
        background-size: 100vw auto;
        background-position: left center;
        background-repeat: no-repeat;
    }

    /* Keep the page tabs and menu readable on top of the banner. */
    header[data-testid="stHeader"] [data-testid="stToolbar"] a,
    header[data-testid="stHeader"] [data-testid="stToolbar"] a span,
    header[data-testid="stHeader"] [data-testid="stToolbar"] button,
    header[data-testid="stHeader"] [data-testid="stToolbar"] svg {
        color: #ffffff !important;
        fill: #ffffff !important;
    }
    header[data-testid="stHeader"] a[data-testid="stTopNavLink"] {
        font-weight: 500;
    }
    header[data-testid="stHeader"] a[data-testid="stTopNavLink"]:hover {
        background: rgba(255, 255, 255, 0.16);
    }
    header[data-testid="stHeader"] a[data-testid="stTopNavLink"][aria-current="page"] {
        background: rgba(255, 255, 255, 0.26);
        font-weight: 700;
    }

    /* ---- Trim the empty space at the top of the sidebar ---- */
    /* This strip only holds the collapse chevron; shrink it and its margin. */
    section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
        height: 2.5rem;
        margin-bottom: 0.25rem;
    }
    </style>
    """
)

pg = st.navigation(
    [
        st.Page("page_code_reorder_exercise.py", title="Exercise 1"),
        st.Page("page_generate_animation.py", title="Exercise 2"),
    ],
    position="top",
)

pg.run()
