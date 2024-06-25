import streamlit as st
import requests
import random
from typing import Optional, List, Tuple, Union

class GetData:

    @staticmethod
    def fetch_data(url: str) -> Optional[dict]:
        """
        Fetches data from a given URL and returns it as JSON.

        Args:
        - url (str): The URL to fetch data from.

        Returns:
        - dict or None: The JSON data if successful, None if the request fails.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
            return None

    @staticmethod
    def get_pokemon_data(number: int) -> Optional[dict]:
        """
        Fetches Pokémon data from the PokeAPI based on the Pokémon number.

        Args:
        - number (int): The Pokémon number.

        Returns:
        - dict or None: The Pokémon data if found, None if not found or request fails.
        """
        url = f"https://pokeapi.co/api/v2/pokemon/{number}"
        return GetData.fetch_data(url)

    @staticmethod
    def get_random_pokemon_name() -> Optional[str]:
        """
        Fetches a random Pokémon name from the PokeAPI.

        Returns:
        - str or None: The name of a random Pokémon if successful, None if request fails.
        """
        url = "https://pokeapi.co/api/v2/pokemon?limit=151"
        data = GetData.fetch_data(url)
        if data:
            pokemon_list = data['results']
            random_pokemon = random.choice(pokemon_list)
            return random_pokemon['name']
        return None

    @staticmethod
    def display_pokemon_data(pokemon: Optional[dict], title: str, appearance: str, fight: bool) -> Tuple[int, List]:
        """
        Displays Pokémon data in a Streamlit app.

        Args:
        - pokemon (dict or None): The Pokémon data to display.
        - title (str): The title for the Pokémon display section.
        - appearance (str): The appearance of the Pokémon (e.g., "front", "back").
        - fight (bool): Whether to display fight-related details or general details.

        Returns:
        - Tuple[int, List]: A tuple containing an integer and an empty list (for compatibility reasons).
        """
        if pokemon:
            st.subheader(title)
            audio_url = f"https://veekun.com/dex/media/pokemon/cries/{pokemon['id']}.ogg"
            if fight == False:
                col1, col2 = st.columns(2)
                with col1:
                    st.image(pokemon["sprites"][f"{appearance}_default"], width=150)
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
                st.image(pokemon["sprites"][f"{appearance}_default"], width=150)
                st.audio(audio_url, format='audio/ogg')
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Number:** {pokemon['id']}")
                    st.write(f"**Name:** {pokemon['name'].capitalize()}")
                with col2:
                    st.write(f"**Height:** {pokemon['height']/10} metres")
                    st.write(f"**Weight:** {pokemon['weight']/10} kg")
        return 0, []

    @staticmethod
    @st.cache_data
    def get_all_pokemon_names() -> List[str]:
        """
        Fetches all Pokémon names from the PokeAPI.

        Returns:
        - List[str]: A list of Pokémon names if successful, an empty list if request fails.
        """
        url = "https://pokeapi.co/api/v2/pokemon?limit=151"
        data = GetData.fetch_data(url)
        if data:
            return [pokemon['name'] for pokemon in data['results']]
        return []

    @staticmethod
    def get_move_details(move_url: str) -> Tuple[Union[int, str], Union[int, str], Union[int, str]]:
        """
        Fetches move details from a given move URL.

        Args:
        - move_url (str): The URL of the move.

        Returns:
        - Tuple[int or str, int or str, int or str]: The power, accuracy, and PP of the move.
          Returns 'N/A' for each value if request fails or data is not available.
        """
        data = GetData.fetch_data(move_url)
        if data:
            power = data.get('power', 'N/A')
            accuracy = data.get('accuracy', 'N/A')
            pp = data.get('pp', 'N/A')
            return power, accuracy, pp
        return 'N/A', 'N/A', 'N/A'

    def attacks(self, pokemon: dict) -> List[dict]:
        """
        Retrieves attack details for a given Pokémon based on the "red-blue" version group.

        Args:
        - pokemon (dict): The Pokémon data.

        Returns:
        - List[dict]: A list of dictionaries containing attack details (name, power, accuracy, pp).
        """
        attacks = []
        for move in pokemon['moves']:
            version_group_details = next((vg for vg in move['version_group_details'] if vg['version_group']['name'] == 'red-blue'), None)
            if version_group_details:
                move_name = move['move']['name']
                move_url = move['move']['url']
                power, accuracy, pp = self.get_move_details(move_url)
                attacks.append({'name': move_name, 'power': power, 'accuracy': accuracy, 'pp': pp})
        return attacks

    @staticmethod
    def calculate_damage(level: int, attack: int, defense: int, base: Optional[int], accuracy: int, modifier: int) -> int:
        """
        Calculates damage based on attack and defense stats.

        Args:
        - level (int): Level of the attacking Pokémon
        - attack (int): Attack stat of the attacking Pokémon
        - defense (int): Defense stat of the defending Pokémon
        - base (int or None): The base power of the attack.
        - accuracy (int): Accuracy of the move
        - modifier (int): Additional modifier for damage calculation.

        Returns:
        - int: The calculated damage value.
        """
        if base is None:
            base = 0  # Set a default value if base power is not available
        if accuracy is None:
            accuracy = 100  # Set a default value if base power is not available
        if defense == 0:
            defense = 1  # Avoid division by zero
        if random.randint(1, 100) <= accuracy:
            # If the move hits
            return int((((2 * level + 10) / 250) * (attack / defense) * base + 2) * modifier)
        else:
            # If the move misses
            return 0