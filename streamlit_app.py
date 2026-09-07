import streamlit as st

st.set_page_config(page_title="Vidigi Animation Playground", layout="wide")

# ---- Common chrome for every page ----
# The banner lives in static/banner.png and is served at /app/static/banner.png
# (see .streamlit/config.toml -> server.enableStaticServing).
st.html(
    """
    <style>
    /* ---- Banner across the top navigation bar ---- */
    /* The app header sits to the right of the sidebar; the sidebar header
       covers the top-left corner. Give both the same banner slice, sized to
       the viewport width and anchored the same way, so they line up into one
       continuous full-width strip. */
    header[data-testid="stHeader"],
    [data-testid="stSidebarHeader"] {
        height: 5rem;
        background-image:
            linear-gradient(rgba(0, 0, 0, 0.38), rgba(0, 0, 0, 0.38)),
            url("/app/static/banner.png");
        background-size: 100vw auto;
        background-position: left center;
        background-repeat: no-repeat;
    }

    /* The sidebar collapse chevron now sits on the banner. */
    [data-testid="stSidebarCollapseButton"] svg {
        color: #ffffff !important;
        fill: #ffffff !important;
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
