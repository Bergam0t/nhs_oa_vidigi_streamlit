import streamlit as st
from vidigi.utils import create_event_position_df, EventPosition
from vidigi.animation import animate_activity_log
from model import Param, Model  # , Trial

st.set_page_config(layout="wide")

st.title("Animation Playground")

st.write(
    "Let's now generate the animation. This page gives you a chance to try out a range of key vidigi parameters, interactively building up the code for an animation."
)

st.subheader("Set Simulation and Animation Parameters")

st.caption("""
Use the sliders in the sidebar to adjust the simulation parameters (which will affect your `Param` class) and the animation parameters (which will affect your `Animation` class). See how the code below updates as you make your changes.
""")

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


col_params, col_anim = st.columns([0.35, 0.65])

with col_params:
    st.code(f"""
what_if_params = Param(
    num_nurses={num_nurses_slider},
    num_receptionists={num_recep_slider},
    num_specialists={num_specialists_slider},
    mean_patient_inter={iat_slider},
    mean_nurse_consult_time=10,
    sd_nurse_consult_time=4,
)
""")

with col_anim:
    st.code(f"""
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
""")


st.subheader("ADVANCED: Adjust Event Positions")

st.caption(
    "Want to try changing where each event appears on the screen? You can make those changes here."
)

with st.expander("Click here to change the Event Positioning Dataframe"):
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


st.write("""
Finished tweaking the settings? Click the "Animate Simulation" button below to see how the changes you've made affect the final animation. You can rerun this as many times as you like!
""")


@st.fragment
def render_anim():
    button_run_pressed = st.button("Animate simulation")

    if button_run_pressed:
        # base_case_params = Param()
        # base_case_trial = Trial(base_case_params)
        # base_case_trial.run_trial()
        # base_case_trial.calculate_trial_results()
        # my_event_log = base_case_trial.trial_logger.get_log_by_run(run=0, as_df=True)

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

        return st.plotly_chart(fig)


render_anim()
