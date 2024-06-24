import streamlit as st
import requests
import random
import pandas as pd
import altair as alt

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
def display_pokemon_data(pokemon, title, apperance):
    if pokemon:
        st.subheader(title)
        col1, col2 = st.columns(2)
        with col1:
            st.image(pokemon["sprites"][f"{apperance}_default"], width=150)
            audio_url = f"https://veekun.com/dex/media/pokemon/cries/{pokemon['id']}.ogg"
            st.audio(audio_url, format='audio/ogg')
            st.write(f"**Number:** {pokemon['id']}")
            st.write(f"**Name:** {pokemon['name'].capitalize()}")
            st.write(f"**Height:** {pokemon['height']/10} metres")
            st.write(f"**Weight:** {pokemon['weight']/10} kg")
        with col2:
            st.write("**Stats:**")
            for stat in pokemon["stats"]:
                st.write(f"- {stat['stat']['name'].capitalize()}: {stat['base_stat']}")
    return 0, []

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
    if base == 'N/A' or base is None:
        base = 0  # Set a default value if base power is not available
    if defense == 0:
        defense = 1  # Avoid division by zero
    damage = (((2 * level + 10) / 250) * (attack / defense) * base + 2) * modifier
    return int(damage)

# Initialize session state variables
if 'user_pokemon_number' not in st.session_state:
    st.session_state.user_pokemon_number = 1
if 'user_pokemon_health' not in st.session_state:
    st.session_state.user_pokemon_health = None

if 'opponent_pokemon' not in st.session_state:
    st.session_state.opponent_pokemon = None
if 'opponent_pokemon_health' not in st.session_state:
    st.session_state.opponent_pokemon_health = None

if 'user_attack_selected' not in st.session_state:
    st.session_state.user_attack_selected = None
if 'battle_in_progress' not in st.session_state:
    st.session_state.battle_in_progress = False

# Streamlit app
st.title("Pokémon Battle Simulator")

# Input field for user-selected Pokémon
st.session_state.user_pokemon_number = st.slider("Select your favourite Pokémon number", 1, 151, step=1)
user_pokemon = get_pokemon_data(st.session_state.user_pokemon_number)
if 'user_pokemon_health' not in st.session_state or st.session_state.user_pokemon_health is None:
    st.session_state.user_pokemon_health = user_pokemon['stats'][0]['base_stat']

pokemon_attacks = attacks(user_pokemon)
df_attacks = pd.DataFrame(pokemon_attacks)
col1, col2 = st.columns(2)
with col1:
    display_pokemon_data(user_pokemon, f"{user_pokemon['name'].capitalize()}", "front")
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
        display_pokemon_data(user_pokemon, f"{user_pokemon['name'].capitalize()} I choose you!", "back")
    with col2:
        display_pokemon_data(st.session_state.opponent_pokemon, f"Wild {st.session_state.opponent_pokemon['name'].capitalize()} appeared!", "front")

    st.subheader(f"{user_pokemon['name'].capitalize()} Moves")
   
    user_attack_name = st.selectbox("**Select a Move:**", [attack['name'] for attack in pokemon_attacks])
    if user_attack_name:
        st.session_state.user_attack_selected = next((attack for attack in pokemon_attacks if attack['name'] == user_attack_name), None)

    # Plotting attack moves
    if user_attack_name:
        selected_attack = next((attack for attack in pokemon_attacks if attack['name'] == user_attack_name), None)
        if selected_attack:
            df_selected_attack = pd.DataFrame([selected_attack])
            bar_chart = alt.Chart(df_selected_attack).mark_bar().encode(
                x=alt.X('value:Q', axis=alt.Axis(title='Value')),
                y=alt.Y('attribute:N', sort='-x')
            ).transform_fold(
                ['power', 'accuracy', 'pp']
            ).transform_calculate(
                attribute="datum.key",
                value="datum.value"
            ).properties(
                title=f"Details of {selected_attack['name'].capitalize()}",
                width=400
            )
            st.altair_chart(bar_chart)

        # Button to use the selected attack
    if st.button("Use Move", key="use_move"):
        col1, col2 = st.columns(2)
        with col1:
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
            if st.session_state.opponent_pokemon_health > 0:
                opponent_attacks = attacks(st.session_state.opponent_pokemon)
                if opponent_attacks:
                    opponent_attack = random.choice(opponent_attacks)
                    damage_to_user = calculate_damage(50, user_pokemon['stats'][1]['base_stat'], user_pokemon['stats'][2]['base_stat'], opponent_attack['power'], 1)
                    st.session_state.user_pokemon_health -= damage_to_user
                    if st.session_state.user_pokemon_health < 0:
                        st.session_state.user_pokemon_health = 0
                    st.write("\n \n \n")
                    st.write(f"Wild {st.session_state.opponent_pokemon['name'].capitalize()} used {opponent_attack['name'].capitalize()}!")
                    st.write(f"It dealt {damage_to_user} damage!")
                    st.write(f"{user_pokemon['name'].capitalize()}'s remaining health: {st.session_state.user_pokemon_health}")

                    if st.session_state.user_pokemon_health == 0:
                        st.write(f"{user_pokemon['name'].capitalize()} fainted!")
                        st.session_state.battle_in_progress = False

# Button to reset user Pokémon's health
if st.session_state.battle_in_progress == False:
    if st.button("Use Max Potion"):
        st.session_state.user_pokemon_health = user_pokemon['stats'][0]['base_stat']
        st.write(f"{user_pokemon['name'].capitalize()}'s health has been reset to {st.session_state.user_pokemon_health}.")
        st.session_state.battle_in_progress = True