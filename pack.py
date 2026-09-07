from stlitepack import pack

pack(
    app_file="streamlit_app.py",
    extra_files_to_embed=[
        "model.py",
    ],
    prepend_github_path="bergam0t/nhs_oa_vidigi_streamlit",
    extra_files_to_link=[
        "static/banner.png",
        "page_code_reorder_exercise.py",
        "page_generate_animation.py",
        # Vendored streamlit-dnd (see streamlit_dnd/__init__.py for why). Linked
        # rather than pip-installed: the PyPI wheel pins streamlit>=1.58, which
        # micropip refuses under stlite (bundled Streamlit is 1.57.0). These
        # files are fetched from GitHub raw at runtime, so they must be
        # committed and pushed to `main` for the packed app to load them.
        "streamlit_dnd/__init__.py",
        "streamlit_dnd/frontend/index.html",
        "streamlit_dnd/frontend/main.js",
        "streamlit_dnd/frontend/streamlit-protocol.js",
    ],
    run_preview_server=True,
    requirements=["vidigi", "simpy", "sim-tools"],
    stylesheet_version="1.8.1",
    js_bundle_version="1.8.1",
)
