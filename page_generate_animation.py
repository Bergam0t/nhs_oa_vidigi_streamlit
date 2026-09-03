import streamlit as st


st.subheader("Set Event Positions")

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
        st.markdown("`waiting_for_nurse`")
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

    st.code(f"""
create_event_position_df(
    [
        EventPosition(
            event="arrival", x={arrival_x}, y={arrival_y}, label="{arrival_label}"
            ),
        EventPosition(
            event="receptionist_wait_begins", x={receptionist_wait_x}, y={receptionist_wait_y}, label="{receptionist_wait_label}",
        ),
        EventPosition(
            event="being_seen_by_receptionist", x={receptionist_seen_x}, y={receptionist_seen_y}, label="Being Seen By Receptionist", resource="num_receptionists",
        ),
        EventPosition(
            event="nurse_wait_begins", x={nurse_wait_x}, y={nurse_wait_y}, label="{nurse_wait_label}"
        ),
        EventPosition(
            event="being_seen_by_nurse",
            x=200,
            y=450,
            label="Being Seen By Nurse",
            resource="num_nurses",
        ),
        EventPosition(
            event="specialist_wait_begins",
            x=75,
            y=300,
            label="Waiting for Specialist",
        ),
        EventPosition(
            event="being_seen_by_specialist",
            x=75,
            y=200,
            label="Being Seen By Specialist",
            resource="num_specialists",
        ),
        EventPosition(event="depart", x=200, y=50, label="Exit"),
    ]
)
    """)


col1, col2, col3 = st.columns(3)


button_run_pressed = st.button("Run simulation")

if button_run_pressed:
    pass
