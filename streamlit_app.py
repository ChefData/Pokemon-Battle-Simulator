import streamlit as st
import requests
import re
import random
import pandas as pd
import altair as alt
import plotly.graph_objects as go

# Function to fetch Pokémon data from the API
def get_pokemon_data(number):
    url = f"https://pokeapi.co/api/v2/pokemon/{number}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error(f"Pokémon '{number}' not found.")
        return None

# Function to fetch a random Pokémon name from the API
def get_random_pokemon_name():
    url = "https://pokeapi.co/api/v2/pokemon?limit=151"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        pokemon_list = data['results']
        random_pokemon = random.choice(pokemon_list)
        return random_pokemon['name']
    else:
        st.error("Failed to fetch Pokémon list.")
        return None

# Function to display Pokémon data
def display_pokemon_data(pokemon, title, apperance, fight):
    if pokemon:
        st.subheader(title)
        audio_url = f"https://veekun.com/dex/media/pokemon/cries/{pokemon['id']}.ogg"
        if fight == False:
            col1, col2 = st.columns(2)
            with col1:
                st.image(pokemon["sprites"][f"{apperance}_default"], width=150)
                st.write(f"**Number:** {pokemon['id']}")
                st.write(f"**Name:** {pokemon['name'].capitalize()}")
                st.write(f"**Height:** {pokemon['height']/10} metres")
                st.write(f"**Weight:** {pokemon['weight']/10} kg")
            with col2:
                st.write("**Stats:**")
                for stat in pokemon["stats"]:
                    st.write(f"- {stat['stat']['name'].capitalize()}: {stat['base_stat']}")
            st.audio(audio_url, format='audio/ogg')
        else:
            st.image(pokemon["sprites"][f"{apperance}_default"], width=150)
            st.audio(audio_url, format='audio/ogg')
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Number:** {pokemon['id']}")
                st.write(f"**Name:** {pokemon['name'].capitalize()}")
            with col2:
                st.write(f"**Height:** {pokemon['height']/10} metres")
                st.write(f"**Weight:** {pokemon['weight']/10} kg")
    return 0, []

# Function to fetch all Pokémon names from the API
@st.cache_data
def get_all_pokemon_names():
    url = "https://pokeapi.co/api/v2/pokemon?limit=151"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        pokemon_list = data['results']
        return [pokemon['name'] for pokemon in pokemon_list]
    else:
        st.error("Failed to fetch Pokémon list.")
        return []

# Fetch all Pokémon names
all_pokemon_names = get_all_pokemon_names()

# Function to fetch move details from the move URL
def get_move_details(move_url):
    response = requests.get(move_url)
    if response.status_code == 200:
        move_data = response.json()
        power = move_data.get('power', 'N/A')
        accuracy = move_data.get('accuracy', 'N/A')
        pp = move_data.get('pp', 'N/A')
        return power, accuracy, pp
    else:
        return 'N/A', 'N/A', 'N/A'

# Function to fetch attacks details based on version group "red-blue"
def attacks(pokemon):
    attacks = []
    for move in pokemon['moves']:
        version_group_details = next((vg for vg in move['version_group_details'] if vg['version_group']['name'] == 'red-blue'), None)
        if version_group_details:
            move_name = move['move']['name']
            move_url = move['move']['url']
            power, accuracy, pp = get_move_details(move_url)
            attacks.append({'name': move_name, 'power': power, 'accuracy': accuracy, 'pp': pp})
    return attacks

# Function to calculate damage based on attack power and defense
def calculate_damage(level, attack, defense, base, modifier):
    if base is None:
        base = 0  # Set a default value if base power is not available
    if defense == 0:
        defense = 1  # Avoid division by zero
    damage = (((2 * level + 10) / 250) * (attack / defense) * base + 2) * modifier
    return int(damage)

# Function to create a radar chart comparing the stats of two Pokémon
def plot_stats_comparison(user_pokemon, opponent_pokemon):
    user_stats = [stat['base_stat'] for stat in user_pokemon['stats']]
    opponent_stats = [stat['base_stat'] for stat in opponent_pokemon['stats']]
    labels = [stat['stat']['name'].capitalize() for stat in user_pokemon['stats']]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=user_stats,
        theta=labels,
        line_color = "magenta",
        name=user_pokemon['name'].capitalize()
    ))

    fig.add_trace(go.Scatterpolar(
        r=opponent_stats,
        theta=labels,
        line_color = "orange",
        name=opponent_pokemon['name'].capitalize()
    ))
    
    fig.update_traces(fill='toself')
    fig.update_layout(
        polar=dict(
            bgcolor = "rgb(14, 17, 23)",
            radialaxis=dict(
                visible=True,
                range=[0, max(max(user_stats), max(opponent_stats)) + 10]
            )
        ),
        showlegend=True,
        title=f"Stats Comparison: {user_pokemon['name'].capitalize()} vs {opponent_pokemon['name'].capitalize()}"
    )
    return fig

# Function to create a bar chart showing health reduction
def plot_health_barchart(user_pokemon, opponent_pokemon):
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=[opponent_pokemon['name'].capitalize(), user_pokemon['name'].capitalize()],
        x=[st.session_state['opponent_pokemon_health'], st.session_state['user_pokemon_health']],
        marker_color=['orange', 'magenta'],
        orientation='h'
    ))

    fig.update_layout(
        xaxis_title="Remaining health",
        margin=dict(l=40, r=40, t=0, b=40)  # Adjust margins to reduce head space
    )

    return fig

# Initialise session state variables
if 'user_pokemon_name' not in st.session_state:
    st.session_state.user_pokemon_name = None

if 'user_pokemon_number' not in st.session_state:
    st.session_state.user_pokemon_number = 1

if 'opponent_pokemon' not in st.session_state:
    st.session_state.opponent_pokemon = None
    
if 'user_pokemon_health' not in st.session_state:
    st.session_state.user_pokemon_health = None

if 'opponent_pokemon_health' not in st.session_state:
    st.session_state.opponent_pokemon_health = None

if 'user_attack_selected' not in st.session_state:
    st.session_state.user_attack_selected = None

if 'battle_in_progress' not in st.session_state:
    st.session_state.battle_in_progress = False

# Streamlit app
st.title("Pokémon Battle Simulator")

# Simple persistent state: The dictionary returned by `get_state()` will be
# persistent across browser sessions.
@st.cache_resource()
def get_state():
    return {}

# The actual creation of the widgets is done in this function.
# Whenever the selection changes, this function is also used to refresh the input
# widgets so that they reflect their new state in the browser when the script is re-run
# to get visual updates.
def display_widgets():
    options = [f"{name.capitalize()} ({i+1})" for i, name in enumerate(all_pokemon_names)]
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
    state["selection_name"] = all_pokemon_names[0]
if "selection_index" not in state:
    state["selection_index"] = 0

# Initial layout
number_placeholder = st.empty()
option_placeholder = st.empty()

# Grab input and detect changes
selected_number, selected_option = display_widgets()

input_changed = False

# Handle changes in slider
if selected_number != state["selection_number"] and not input_changed:
    state["selection_number"] = selected_number
    state["selection_name"] = all_pokemon_names[selected_number - 1]
    state["selection_index"] = selected_number - 1
    input_changed = True
    selected_number, selected_option = display_widgets()

# Handle changes in select box
selected_option_id = int(re.match(r".* \((\d+)\)", selected_option).group(1))
if selected_option_id != state["selection_number"] and not input_changed:
    state["selection_number"] = selected_option_id
    state["selection_name"] = all_pokemon_names[selected_option_id - 1]
    state["selection_index"] = selected_option_id - 1
    input_changed = True
    selected_number, selected_option = display_widgets()

# Get user Pokémon data
user_pokemon = get_pokemon_data(state["selection_name"])
if 'user_pokemon_health' not in state or state['user_pokemon_health'] is None:
    state['user_pokemon_health'] = user_pokemon['stats'][0]['base_stat']
if 'user_pokemon_health' not in st.session_state or st.session_state.user_pokemon_health is None:
    st.session_state.user_pokemon_health = user_pokemon['stats'][0]['base_stat']

pokemon_attacks = attacks(user_pokemon)
df_attacks = pd.DataFrame(pokemon_attacks)
with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        display_pokemon_data(user_pokemon, f"{user_pokemon['name'].capitalize()}", "front", fight = False)
    with col2:
        st.subheader(f"{user_pokemon['name'].capitalize()} Moves")
        st.dataframe(df_attacks)

if st.button("Wild Pokémon appeared!") or (st.session_state.battle_in_progress and not st.session_state.opponent_pokemon):
    opponent_pokemon_name = get_random_pokemon_name()
    st.session_state.opponent_pokemon = get_pokemon_data(opponent_pokemon_name)
    st.session_state.opponent_pokemon_health = st.session_state.opponent_pokemon['stats'][0]['base_stat']
    st.session_state.battle_in_progress = True

if st.session_state.opponent_pokemon:
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            display_pokemon_data(user_pokemon, f"{user_pokemon['name'].capitalize()} I choose you!", "back", fight = True)
    with col2:
        with st.container(border=True):
            display_pokemon_data(st.session_state.opponent_pokemon, f"Wild {st.session_state.opponent_pokemon['name'].capitalize()} appeared!", "front", fight = True)

    # Radar chart for stats comparison
    if st.session_state.opponent_pokemon:
        fig = plot_stats_comparison(user_pokemon, st.session_state.opponent_pokemon)
        st.plotly_chart(fig)

    st.subheader(f"{user_pokemon['name'].capitalize()} Moves")
   
    with st.container(border=True):
        user_attack_name = st.selectbox("**Select a Move:**", [attack['name'] for attack in pokemon_attacks])
        if user_attack_name:
            st.session_state.user_attack_selected = next((attack for attack in pokemon_attacks if attack['name'] == user_attack_name), None)

        # Plotting attack moves
        if user_attack_name:
            selected_attack = next((attack for attack in pokemon_attacks if attack['name'] == user_attack_name), None)
            if selected_attack:
                df_selected_attack = pd.DataFrame([selected_attack])
                bar_chart = alt.Chart(df_selected_attack).mark_bar().encode(
                    # quantitative :Q a continuous real-valued quantity
                    x=alt.X('value:Q', axis=alt.Axis(title='Value')),
                    # nominal :N a discrete unordered category
                    y=alt.Y('attribute:N')
                ).transform_fold(
                    ['power', 'accuracy', 'pp']
                ).transform_calculate(
                    attribute="datum.key",
                    value="datum.value"
                ).properties(
                    title=f"Details of {selected_attack['name'].capitalize()}",
                    width=600
                )
                st.altair_chart(bar_chart)
    
    # Button to use the selected attack
    if st.button("Use Move", key="use_move"):
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                damage_to_opponent = calculate_damage(50, user_pokemon['stats'][1]['base_stat'], st.session_state.opponent_pokemon['stats'][2]['base_stat'], st.session_state.user_attack_selected['power'], 1)
                st.session_state.opponent_pokemon_health -= damage_to_opponent
                if st.session_state.opponent_pokemon_health < 0:
                    st.session_state.opponent_pokemon_health = 0
                st.write(f"{user_pokemon['name'].capitalize()} used {user_attack_name.capitalize()}!")
                st.write(f"It dealt {damage_to_opponent} damage!")
                st.write(f"Wild {st.session_state.opponent_pokemon['name'].capitalize()}'s remaining health: {st.session_state.opponent_pokemon_health}")

                if st.session_state.opponent_pokemon_health == 0:
                    st.write(f"Wild {st.session_state.opponent_pokemon['name'].capitalize()} fainted!")
                    st.session_state.battle_in_progress = False
        
        with col2:
            with st.container(border=True):
                if st.session_state.opponent_pokemon_health > 0:
                    opponent_attacks = attacks(st.session_state.opponent_pokemon)
                    if opponent_attacks:
                        opponent_attack = random.choice(opponent_attacks)
                        damage_to_user = calculate_damage(50, st.session_state.opponent_pokemon['stats'][1]['base_stat'], user_pokemon['stats'][2]['base_stat'], opponent_attack['power'], 1)
                        st.session_state.user_pokemon_health -= damage_to_user
                        if st.session_state.user_pokemon_health < 0:
                            st.session_state.user_pokemon_health = 0
                        st.write(f"Wild {st.session_state.opponent_pokemon['name'].capitalize()} used {opponent_attack['name'].capitalize()}!")
                        st.write(f"It dealt {damage_to_user} damage!")
                        st.write(f"{user_pokemon['name'].capitalize()}'s remaining health: {st.session_state.user_pokemon_health}")

                        if st.session_state.user_pokemon_health == 0:
                            st.write(f"{user_pokemon['name'].capitalize()} fainted!")
                            st.session_state.battle_in_progress = False

        fig = plot_health_barchart(user_pokemon, st.session_state.opponent_pokemon)
        st.plotly_chart(fig)


# Button to reset user Pokémon's health
if st.session_state.battle_in_progress == False and (st.session_state.user_pokemon_health == 0 or st.session_state.opponent_pokemon_health == 0):
    if st.button("Use Max Potion"):
        st.session_state.user_pokemon_health = user_pokemon['stats'][0]['base_stat']
        st.write(f"{user_pokemon['name'].capitalize()}'s health has been reset to {st.session_state.user_pokemon_health}.")
        st.session_state.battle_in_progress = True