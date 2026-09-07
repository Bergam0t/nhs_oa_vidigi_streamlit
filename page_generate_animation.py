import difflib
import hashlib
import json

import streamlit as st
from vidigi.utils import create_event_position_df, EventPosition
from vidigi.animation import animate_activity_log
from model import Param, Model  # , Trial

# Page config and the top-banner styling live in streamlit_app.py (the entrypoint).

_TOKEN_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.")


def _changed_spans(prev: str, curr: str) -> list[dict]:
    """Character ranges in `curr` that differ from `prev`, each widened out to
    the surrounding ``name=value`` token so the highlight reads cleanly."""
    raw: list[list[int]] = []
    for tag, _i1, _i2, j1, j2 in difflib.SequenceMatcher(
        None, prev, curr, autojunk=False
    ).get_opcodes():
        if tag in ("replace", "insert") and j2 > j1:
            raw.append([j1, j2])

    widened: list[list[int]] = []
    for start, end in raw:
        while start > 0 and curr[start - 1] in _TOKEN_CHARS:
            start -= 1
        if start > 0 and curr[start - 1] == "=":  # pull in the `name=` prefix
            start -= 1
            while start > 0 and (curr[start - 1].isalnum() or curr[start - 1] == "_"):
                start -= 1
        while end < len(curr) and curr[end] in _TOKEN_CHARS:
            end += 1
        widened.append([start, end])

    merged: list[list[int]] = []
    for start, end in sorted(widened):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])

    return [{"start": s, "end": e, "text": curr[s:e]} for s, e in merged]


def flash_on_change(container_key: str, code_text: str) -> None:
    """Highlight (yellow-marker style) the exact tokens in the code block
    ``.st-key-<container_key>`` that changed since the previous run.

    Slider changes trigger a full rerun, so the code re-renders every time.
    We diff against the previous text (kept in session state), hand the changed
    character ranges to a tiny script, and it wraps just those runs in
    ``<mark class="tok-flash">``. The script's body only changes when the code
    changes, so Streamlit re-executes it exactly on those reruns -- and never
    on the first render.
    """
    state_key = f"_flash_prev_{container_key}"
    prev = st.session_state.get(state_key)
    st.session_state[state_key] = code_text

    spans = _changed_spans(prev, code_text) if prev not in (None, code_text) else []
    payload = json.dumps(
        {
            "key": container_key,
            "nonce": hashlib.md5(code_text.encode("utf-8")).hexdigest()[:8],
            "spans": spans,
        }
    )

    st.html(
        f"""
        <script>
        (function () {{
            const DATA = {payload};
            const scope = document.querySelector(".st-key-" + DATA.key + " [data-testid='stCode']");
            if (!scope) return;
            const root = scope.querySelector("code") || scope;

            // clear any previous highlights
            root.querySelectorAll("mark.tok-flash").forEach(function (m) {{
                m.replaceWith(document.createTextNode(m.textContent));
            }});
            root.normalize();
            if (!DATA.spans.length) return;

            const full = root.textContent;
            DATA.spans.forEach(function (span) {{
                let start = span.start, end = span.end;
                if (full.slice(start, end) !== span.text) {{
                    const found = full.indexOf(span.text);   // fall back to a text search
                    if (found < 0) return;
                    start = found;
                    end = found + span.text.length;
                }}
                wrapRange(root, start, end);
            }});

            function wrapRange(el, start, end) {{
                const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
                let pos = 0, node;
                const hits = [];
                while ((node = walker.nextNode())) {{
                    const nStart = pos, nEnd = pos + node.nodeValue.length;
                    if (nEnd > start && nStart < end) {{
                        hits.push([node, Math.max(start, nStart) - nStart, Math.min(end, nEnd) - nStart]);
                    }}
                    pos = nEnd;
                    if (pos >= end) break;
                }}
                for (let i = hits.length - 1; i >= 0; i--) {{
                    const parts = hits[i];
                    const r = document.createRange();
                    r.setStart(parts[0], parts[1]);
                    r.setEnd(parts[0], parts[2]);
                    const mark = document.createElement("mark");
                    mark.className = "tok-flash";
                    try {{ r.surroundContents(mark); }} catch (e) {{}}
                }}
            }}
        }})();
        </script>
        """,
        unsafe_allow_javascript=True,
    )

st.html(
    """
    <style>
    /* ---- Tighten the sliders in the sidebar ---- */

    /* Less space between each widget in the sidebar. */
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.6rem;
    }

    /* Trim the large vertical padding baked into every slider. Keep enough
       headroom above for the always-visible value, and enough below the track
       for the min/max range labels that appear on hover. */
    section[data-testid="stSidebar"] [data-testid="stSlider"] > div:last-child > div {
        padding-top: 1.35rem !important;
        padding-bottom: 0.7rem !important;
    }

    /* Pull each slider a little closer to its label (but leave room for the
       value that sits just above the track). */
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
        margin-bottom: 0.35rem;
    }

    /* Tighten the gap above and below the divider between the two groups. */
    section[data-testid="stSidebar"] hr {
        margin-top: 0.8rem;
        margin-bottom: 0.8rem;
    }

    /* ---- Big call-to-action button on the "Run" tab ---- */
    .st-key-animate_button button {
        min-height: 3.5rem;
        font-size: 1.15rem;
        font-weight: 600;
        background-color: #be185d;
        border-color: #be185d;
        color: #ffffff;
    }
    .st-key-animate_button button:hover,
    .st-key-animate_button button:focus:not(:active) {
        background-color: #9d174d;
        border-color: #9d174d;
        color: #ffffff;
    }

    /* ---- Let the ADVANCED section recede until you engage with it ---- */
    .st-key-advanced_section {
        opacity: 0.5;
        transition: opacity 200ms ease;
    }
    .st-key-advanced_section:hover,
    .st-key-advanced_section:focus-within {
        opacity: 1;
    }
    .st-key-advanced_section h3 {
        font-size: 1rem;
        font-weight: 600;
        padding-bottom: 0.25rem;
    }

    /* ---- Highlighter flash on the exact code that a slider just changed ---- */
    .st-key-code_params mark.tok-flash,
    .st-key-code_anim mark.tok-flash {
        color: inherit;
        border-radius: 3px;
        padding: 0 1px;
        box-decoration-break: clone;
        -webkit-box-decoration-break: clone;
        animation: tokFlash 1.6s ease-out forwards;
    }
    @keyframes tokFlash {
        0%, 55% { background-color: #fde047; }
        100%    { background-color: rgba(253, 224, 71, 0); }
    }

    /* The flash helper and the style block above ship as empty html elements. */
    [data-testid="stHtml"] {
        display: none;
    }
    </style>
    """
)

st.title("Animation Playground")

st.write(
    "Let's now generate the animation. This page gives you a chance to try out a range of key vidigi parameters, interactively building up the code for an animation."
)

with st.sidebar:
    st.markdown("**Animation Parameters**")
    time_interval_slider = st.slider(
        "Time between snapshots",
        value=1,
        min_value=1,
        max_value=10,
        persist_state="session",
        key="time_interval_input",
    )
    gap_between_entities_slider = st.slider(
        "Gap between entities",
        value=10,
        min_value=1,
        max_value=100,
        persist_state="session",
        key="gap_between_entities_input",
    )
    gap_between_queue_rows_slider = st.slider(
        "Gap between queue rows",
        value=40,
        min_value=1,
        max_value=100,
        persist_state="session",
        key="gap_between_queue_rows_input",
    )
    gap_between_resources_slider = st.slider(
        "Gap between resources",
        value=10,
        min_value=1,
        max_value=100,
        persist_state="session",
        key="gap_between_resources_input",
    )
    entity_icon_size_slider = st.slider(
        "Entity Icon Size",
        value=20,
        min_value=1,
        max_value=100,
        persist_state="session",
        key="entity_icon_size_input",
    )
    wrap_queues_at = st.slider(
        "Wrap queues at",
        value=10,
        min_value=1,
        max_value=30,
        persist_state="session",
        key="wrap_queues_input",
    )

    maximum_queue = st.slider(
        "Maximum Queue Displayed",
        value=10,
        min_value=0,
        max_value=100,
        persist_state="session",
        key="step_snapshot_max_input",
        help="Best as a multiple of 'Wrap queues at!'",
    )

    st.divider()

    st.markdown("**Simulation Parameters**")
    iat_slider = st.slider(
        "Interarrival Time (mins)",
        value=2.0,
        min_value=0.1,
        max_value=30.0,
        persist_state="session",
        key="iat_input",
        step=0.1,
    )
    num_recep_slider = st.slider(
        "Number of Receptionists",
        value=1,
        min_value=1,
        max_value=10,
        persist_state="session",
        key="num_recep_input",
    )
    num_nurses_slider = st.slider(
        "Number of Nurses",
        value=1,
        min_value=1,
        max_value=10,
        persist_state="session",
        key="num_nurses_input",
    )

    num_specialists_slider = st.slider(
        "Number of Specialists",
        value=1,
        min_value=1,
        max_value=10,
        persist_state="session",
        key="num_specialists_input",
    )


tab_build, tab_run = st.tabs(["Build your animation", "Run the animation"])

with tab_build:
    st.caption("""
Use the sliders in the sidebar to set the simulation parameters (which feed your `Param` class) and the animation parameters (which feed your `Animation` class). Optionally adjust where each event sits on screen below. The assembled code updates as you make your changes.
""")

    advanced = st.container(key="advanced_section")
    advanced.subheader("ADVANCED: Adjust Event Positions")
    advanced.caption(
        "Want to try changing where each event appears on the screen? You can make those changes here."
    )

    with advanced.expander("Click here to change the Event Positioning Dataframe"):
        cola, colb, colc, cold = st.columns(4)

        with cola, st.container(border=True):
            st.markdown("`arrival`")
            arrival_x = st.number_input(
                "x",
                key="arrival_x_input",
                value=0,
                min_value=0,
                max_value=1000,
                persist_state="session",
            )
            arrival_y = st.number_input(
                "y",
                key="arrival_y_input",
                value=850,
                min_value=0,
                max_value=1000,
                persist_state="session",
            )
            arrival_label = st.text_input(
                "Label",
                key="arrival_label_input",
                value="Entrance",
                persist_state="session",
            )
        with colb, st.container(border=True):
            st.markdown("`receptionist_wait_begins`")
            receptionist_wait_x = st.number_input(
                "x",
                key="receptionist_wait_x_input",
                value=200,
                min_value=0,
                max_value=1000,
                persist_state="session",
            )
            receptionist_wait_y = st.number_input(
                "y",
                key="receptionist_wait_y_input",
                value=800,
                min_value=0,
                max_value=1000,
                persist_state="session",
            )
            receptionist_wait_label = st.text_input(
                "Label",
                key="receptionist_label_input",
                value="Waiting for Receptionist",
                persist_state="session",
            )
        with colc, st.container(border=True):
            st.markdown("`being_seen_by_receptionist`")
            receptionist_seen_x = st.number_input(
                "x",
                key="receptionist_seen_x_input",
                value=200,
                min_value=0,
                max_value=1000,
                persist_state="session",
            )
            receptionist_seen_y = st.number_input(
                "y",
                key="receptionist_seen_y_input",
                value=700,
                min_value=0,
                max_value=1000,
                persist_state="session",
            )
            receptionist_seen_label = st.text_input(
                "Label",
                key="receptionist_seen_input",
                value="Being Seen by Receptionist",
                persist_state="session",
            )
        with cold, st.container(border=True):
            st.markdown("`nurse_wait_begins`")
            nurse_wait_x = st.number_input(
                "x",
                key="nurse_wait_x_input",
                value=200,
                min_value=0,
                max_value=1000,
                persist_state="session",
            )
            nurse_wait_y = st.number_input(
                "y",
                key="nurse_wait_y_input",
                value=550,
                min_value=0,
                max_value=1000,
                persist_state="session",
            )
            nurse_wait_label = st.text_input(
                "Label",
                key="nurse_wait_label_input",
                value="Waiting for Nurse",
                persist_state="session",
            )

        cole, colf, colg, colh = st.columns(4)

        with cole, st.container(border=True):
            st.markdown("`being_seen_by_nurse`")
            nurse_seen_x = st.number_input(
                "x",
                key="nurse_seen_x_input",
                value=200,
                min_value=0,
                max_value=1000,
                persist_state="session",
            )
            nurse_seen_y = st.number_input(
                "y",
                key="nurse_seen_y_input",
                value=450,
                min_value=0,
                max_value=1000,
                persist_state="session",
            )
            nurse_seen_label = st.text_input(
                "Label",
                key="nurse_seen_label_input",
                value="Being Seen By Nurse",
                persist_state="session",
            )
        with colf, st.container(border=True):
            st.markdown("`specialist_wait_begins`")
            specialist_wait_x = st.number_input(
                "x",
                key="specialist_wait_x_input",
                value=75,
                min_value=0,
                max_value=1000,
                persist_state="session",
            )
            specialist_wait_y = st.number_input(
                "y",
                key="specialist_wait_y_input",
                value=300,
                min_value=0,
                max_value=1000,
                persist_state="session",
            )
            specialist_wait_label = st.text_input(
                "Label",
                key="specialist_wait_label_input",
                value="Waiting for Specialist",
                persist_state="session",
            )
        with colg, st.container(border=True):
            st.markdown("`being_seen_by_specialist`")
            specialist_seen_x = st.number_input(
                "x",
                key="specialist_seen_x_input",
                value=75,
                min_value=0,
                max_value=1000,
                persist_state="session",
            )
            specialist_seen_y = st.number_input(
                "y",
                key="specialist_seen_y_input",
                value=200,
                min_value=0,
                max_value=1000,
                persist_state="session",
            )
            specialist_seen_label = st.text_input(
                "Label",
                key="specialist_seen_label_input",
                value="Being Seen By Specialist",
                persist_state="session",
            )
        with colh, st.container(border=True):
            st.markdown("`depart`")
            depart_x = st.number_input(
                "x",
                key="depart_x_input",
                value=200,
                min_value=0,
                max_value=1000,
                persist_state="session",
            )
            depart_y = st.number_input(
                "y",
                key="depart_y_input",
                value=50,
                min_value=0,
                max_value=1000,
                persist_state="session",
            )
            depart_label = st.text_input(
                "Label",
                key="depart_label_input",
                value="Exit",
                persist_state="session",
            )

        event_position_df_generated = f"""
create_event_position_df(
    [
        EventPosition(
            event="arrival", x={arrival_x}, y={arrival_y}, label="{arrival_label}"
            ),
        EventPosition(
            event="receptionist_wait_begins", x={receptionist_wait_x}, y={receptionist_wait_y}, label="{receptionist_wait_label}",
        ),
        EventPosition(
            event="being_seen_by_receptionist", x={receptionist_seen_x}, y={receptionist_seen_y}, label="{receptionist_seen_label}", resource="num_receptionists",
        ),
        EventPosition(
            event="nurse_wait_begins", x={nurse_wait_x}, y={nurse_wait_y}, label="{nurse_wait_label}"
        ),
        EventPosition(
            event="being_seen_by_nurse", x={nurse_seen_x}, y={nurse_seen_y}, label="{nurse_seen_label}", resource="num_nurses",
        ),
        EventPosition(
            event="specialist_wait_begins", x={specialist_wait_x}, y={specialist_wait_y}, label="{specialist_wait_label}",
        ),
        EventPosition(
            event="being_seen_by_specialist", x={specialist_seen_x}, y={specialist_seen_y}, label="{specialist_seen_label}", resource="num_specialists",
        ),
        EventPosition(
            event="depart", x={depart_x}, y={depart_y}, label="{depart_label}"
        ),
    ]
)
    """

        st.code(event_position_df_generated)

    st.subheader("Your code so far")

    params_code = f"""
what_if_params = Param(
    num_nurses={num_nurses_slider},
    num_receptionists={num_recep_slider},
    num_specialists={num_specialists_slider},
    mean_patient_inter={iat_slider},
    mean_nurse_consult_time=10,
    sd_nurse_consult_time=4,
)
"""

    anim_code = f"""
class Animation:
    def __init__(self, event_log, params):
        self.event_log = event_log
        self.params = params
        self.layout = create_event_position_df(...)

    def build_animation(self):
        animate_activity_log(
            event_log=self.event_log, scenario=self.params,
            event_position_df=self.layout, plotly_height=500,
            every_x_time_units={time_interval_slider},
            entity_icon_size={entity_icon_size_slider}, gap_between_entities={gap_between_entities_slider},
             wrap_queues_at={wrap_queues_at}, step_snapshot_max={maximum_queue},
            gap_between_resources={gap_between_resources_slider}, gap_between_queue_rows={gap_between_queue_rows_slider},
        )
"""

    # Strip the leading/trailing newline so the rendered text (and therefore
    # the highlight offsets) line up exactly with these strings.
    params_code = params_code.strip("\n")
    anim_code = anim_code.strip("\n")

    col_params, col_anim = st.columns([0.35, 0.65])

    with col_params, st.container(key="code_params"):
        st.code(params_code)

    with col_anim, st.container(key="code_anim"):
        st.code(anim_code)

    # Flash each block when its slider-driven code actually changes.
    flash_on_change("code_params", params_code)
    flash_on_change("code_anim", anim_code)


class Animation:
    def __init__(self, event_log, params):
        self.event_log = event_log
        self.params = params

        self.layout = create_event_position_df(
            [
                EventPosition(
                    event="arrival",
                    x=arrival_x,
                    y=arrival_y,
                    label=arrival_label,
                ),
                EventPosition(
                    event="receptionist_wait_begins",
                    x=receptionist_wait_x,
                    y=receptionist_wait_y,
                    label=receptionist_wait_label,
                ),
                EventPosition(
                    event="being_seen_by_receptionist",
                    x=receptionist_seen_x,
                    y=receptionist_seen_y,
                    label=receptionist_seen_label,
                    resource="num_receptionists",
                ),
                EventPosition(
                    event="nurse_wait_begins",
                    x=nurse_wait_x,
                    y=nurse_wait_y,
                    label=nurse_wait_label,
                ),
                EventPosition(
                    event="being_seen_by_nurse",
                    x=nurse_seen_x,
                    y=nurse_seen_y,
                    label=nurse_seen_label,
                    resource="num_nurses",
                ),
                EventPosition(
                    event="specialist_wait_begins",
                    x=specialist_wait_x,
                    y=specialist_wait_y,
                    label=specialist_wait_label,
                ),
                EventPosition(
                    event="being_seen_by_specialist",
                    x=specialist_seen_x,
                    y=specialist_seen_y,
                    label=specialist_seen_label,
                    resource="num_specialists",
                ),
                EventPosition(
                    event="depart", x=depart_x, y=depart_y, label=depart_label
                ),
            ]
        )

    def build_animation(self, time_interval=1):
        return animate_activity_log(
            event_log=self.event_log,
            event_position_df=self.layout,
            every_x_time_units=time_interval,
            scenario=self.params,
            gap_between_entities=gap_between_entities_slider,
            step_snapshot_max=maximum_queue,
            gap_between_resources=gap_between_resources_slider,
            plotly_height=500,
            entity_icon_size=entity_icon_size_slider,
            gap_between_queue_rows=gap_between_queue_rows_slider,
            wrap_queues_at=wrap_queues_at,
        )


@st.fragment
def render_anim():
    button_run_pressed = st.button(
        "Animate simulation",
        key="animate_button",
        type="primary",
        icon=":material/play_arrow:",
        width="stretch",
    )

    if button_run_pressed:
        # base_case_params = Param()
        # base_case_trial = Trial(base_case_params)
        # base_case_trial.run_trial()
        # base_case_trial.calculate_trial_results()
        # my_event_log = base_case_trial.trial_logger.get_log_by_run(run=0, as_df=True)

        with st.spinner("Running the simulation and building the animation..."):
            base_case_params = Param(
                num_nurses=num_nurses_slider,
                num_receptionists=num_recep_slider,
                num_specialists=num_specialists_slider,
                mean_patient_inter=iat_slider,
                mean_nurse_consult_time=10,
                sd_nurse_consult_time=4,
            )

            base_case_model_run = Model(base_case_params, replication_id=1)
            base_case_model_run.run_model()
            my_event_log = base_case_model_run.get_vidigi_event_log()

            my_animation = Animation(my_event_log, base_case_params)

            fig = my_animation.build_animation()

        st.plotly_chart(fig)


with tab_run:
    st.write("""
Finished tweaking the settings? Click the button to see how the changes you've made affect the final animation. You can rerun this as many times as you like!
""")

    render_anim()
