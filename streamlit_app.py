import streamlit as st
import re
import random
import pandas as pd

from classes.get_data import GetData
from classes.plot_charts import PlotCharts


# Creating instances of classes
get_data = GetData()
plot_charts = PlotCharts()

# Initialise session state variables if not already initialised
def init_session_state():
    default_values = {
        'user_pokemon_name': None,
        'user_pokemon_number': 1,
        'opponent_pokemon': None,
        'user_pokemon_health': None,
        'opponent_pokemon_health': None,
        'user_attack_selected': None,
        'battle_in_progress': False
    }

    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Streamlit app title
st.title("Pokémon Battle Simulator")

# Simple persistent state: The dictionary returned by `get_state()` will be persistent across browser sessions.
@st.cache_resource()
def get_state() -> dict:
    """Get the current session state."""
    return {}

# Function to display Pokémon selection widgets
def display_widgets() -> tuple:
    """Display widgets for Pokémon selection."""
    options = [f"{name.capitalize()} ({i+1})" for i, name in enumerate(get_data.get_all_pokemon_names())]
    index = state.get("selection_index", 0)
    return (
        number_placeholder.slider("Select your favourite Pokémon by number", 1, 151, state.get("selection_number", 1)),
        option_placeholder.selectbox("Or select your favourite Pokémon by name", options, index=index),
    )

# Initialise session state
state = get_state()
if "selection_number" not in state:
    state["selection_number"] = 1
if "selection_name" not in state:
    state["selection_name"] = get_data.get_all_pokemon_names()[0]
if "selection_index" not in state:
    state["selection_index"] = 0

# Initial layout
number_placeholder = st.empty()
option_placeholder = st.empty()

# Display Pokémon selection widgets and handle input changes
selected_number, selected_option = display_widgets()

input_changed = False

# Handle changes in slider
if selected_number != state["selection_number"] and not input_changed:
    state["selection_number"] = selected_number
    state["selection_name"] = get_data.get_all_pokemon_names()[selected_number - 1]
    state["selection_index"] = selected_number - 1
    input_changed = True
    selected_number, selected_option = display_widgets()

# Handle changes in select box
selected_option_id = int(re.match(r".* \((\d+)\)", selected_option).group(1))
if selected_option_id != state["selection_number"] and not input_changed:
    state["selection_number"] = selected_option_id
    state["selection_name"] = get_data.get_all_pokemon_names()[selected_option_id - 1]
    state["selection_index"] = selected_option_id - 1
    input_changed = True
    selected_number, selected_option = display_widgets()

# Get user Pokémon data
user_pokemon = get_data.get_pokemon_data(state["selection_name"])
if st.session_state.user_pokemon_health is None:
    st.session_state.user_pokemon_health = user_pokemon['stats'][0]['base_stat']

# Display user Pokémon data and moves
pokemon_attacks = get_data.attacks(user_pokemon)
df_attacks = pd.DataFrame(pokemon_attacks)
with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        get_data.display_pokemon_data(user_pokemon, f"{user_pokemon['name'].capitalize()} I choose you!", "front", fight = False)
    with col2:
        st.subheader(f"{user_pokemon['name'].capitalize()} Moves")
        st.dataframe(df_attacks)

# Button to initiate battle with a wild Pokémon
if st.button("Wild Pokémon appeared!") or (st.session_state.battle_in_progress and not st.session_state.opponent_pokemon):
    opponent_pokemon_name = get_data.get_random_pokemon_name()
    st.session_state.opponent_pokemon = get_data.get_pokemon_data(opponent_pokemon_name)
    st.session_state.opponent_pokemon_health = st.session_state.opponent_pokemon['stats'][0]['base_stat']
    st.session_state.battle_in_progress = True

# Display opponent Pokémon data and start battle if opponent exists
if st.session_state.opponent_pokemon:
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            get_data.display_pokemon_data(user_pokemon, f"Go! {user_pokemon['name'].upper()}", "back", fight = True)
    with col2:
        with st.container(border=True):
            get_data.display_pokemon_data(st.session_state.opponent_pokemon, f"Wild {st.session_state.opponent_pokemon['name'].capitalize()} appeared!", "front", fight = True)

    # Display radar chart for stats comparison
    if st.session_state.opponent_pokemon:
        fig = plot_charts.plot_stats_comparison(user_pokemon, st.session_state.opponent_pokemon)
        st.plotly_chart(fig)

    # Display user Pokémon moves and allow move selection
    with st.container(border=True):
        st.subheader(f"{user_pokemon['name'].capitalize()} Moves")
        user_attack_name = st.selectbox("**Select a Move:**", [attack['name'] for attack in pokemon_attacks])

        # Plot details of selected attack using Altair
        if user_attack_name:
            selected_attack = next((attack for attack in pokemon_attacks if attack['name'] == user_attack_name), None)
            st.session_state.user_attack_selected = selected_attack
            if selected_attack:
                bar_chart = plot_charts.create_attack_chart(selected_attack)
                st.altair_chart(bar_chart)

    # Button to use the selected attack
    if st.button("Use Move", key="use_move"):
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                damage_to_opponent = get_data.calculate_damage(50, user_pokemon['stats'][1]['base_stat'], st.session_state.opponent_pokemon['stats'][2]['base_stat'], st.session_state.user_attack_selected['power'], st.session_state.user_attack_selected['accuracy'], 1)
                st.session_state.opponent_pokemon_health -= damage_to_opponent
                if st.session_state.opponent_pokemon_health < 0:
                    st.session_state.opponent_pokemon_health = 0
                st.write(f"{user_pokemon['name'].capitalize()} used {user_attack_name.capitalize()}!")
                if damage_to_opponent == 0:
                    st.write("But, it failed!")
                else:
                    st.write(f"It dealt {damage_to_opponent} damage!")
                st.write(f"Wild {st.session_state.opponent_pokemon['name'].capitalize()}'s remaining health: {st.session_state.opponent_pokemon_health}")

                if st.session_state.opponent_pokemon_health == 0:
                    st.write(f"Wild {st.session_state.opponent_pokemon['name'].capitalize()} fainted!")
                    st.session_state.battle_in_progress = False
        
        with col2:
            with st.container(border=True):
                if st.session_state.opponent_pokemon_health > 0:
                    opponent_attacks = get_data.attacks(st.session_state.opponent_pokemon)
                    if opponent_attacks:
                        opponent_attack = random.choice(opponent_attacks)
                        damage_to_user = get_data.calculate_damage(50, st.session_state.opponent_pokemon['stats'][1]['base_stat'], user_pokemon['stats'][2]['base_stat'], opponent_attack['power'], opponent_attack['accuracy'], 1)
                        st.session_state.user_pokemon_health -= damage_to_user
                        if st.session_state.user_pokemon_health < 0:
                            st.session_state.user_pokemon_health = 0
                        st.write(f"Wild {st.session_state.opponent_pokemon['name'].capitalize()} used {opponent_attack['name'].capitalize()}!")
                        if damage_to_user == 0:
                            st.write("But, it failed!")
                        else:
                            st.write(f"It dealt {damage_to_user} damage!")
                        st.write(f"{user_pokemon['name'].capitalize()}'s remaining health: {st.session_state.user_pokemon_health}")

                        if st.session_state.user_pokemon_health == 0:
                            st.write(f"{user_pokemon['name'].capitalize()} fainted!")
                            st.session_state.battle_in_progress = False

        # Plot health bar chart after each round of attacks
        fig = plot_charts.plot_health_barchart(user_pokemon, st.session_state.opponent_pokemon)
        st.plotly_chart(fig)

# Button to reset user Pokémon's health after battle
if st.session_state.user_pokemon_health == 0:

    if st.button("Use Max Potion"):
        st.session_state.user_pokemon_health = user_pokemon['stats'][0]['base_stat']
        st.write(f"{user_pokemon['name'].capitalize()}'s health has been reset to {st.session_state.user_pokemon_health}.")
        st.session_state.battle_in_progress = True