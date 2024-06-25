import streamlit as st
import altair as alt
import pandas as pd
import plotly.graph_objects as go


class PlotCharts:
    @staticmethod
    def plot_stats_comparison(user_pokemon: dict, opponent_pokemon: dict) -> go.Figure:
        """
        Creates a radar chart comparing the stats of two Pokémon.

        Args:
        - user_pokemon (dict): The data of the user's Pokémon.
        - opponent_pokemon (dict): The data of the opponent's Pokémon.

        Returns:
        - go.Figure: The Plotly Figure object containing the radar chart.
        """
        try:
            user_stats = [stat['base_stat'] for stat in user_pokemon['stats']]
            opponent_stats = [stat['base_stat'] for stat in opponent_pokemon['stats']]
            labels = [stat['stat']['name'].capitalize() for stat in user_pokemon['stats']]

            fig = go.Figure()

            # Add user's Pokémon stats to the radar chart
            fig.add_trace(go.Scatterpolar(
                r=user_stats,
                theta=labels,
                line_color="magenta",
                name=user_pokemon['name'].capitalize(),
                fill='toself'
            ))

            # Add opponent's Pokémon stats to the radar chart
            fig.add_trace(go.Scatterpolar(
                r=opponent_stats,
                theta=labels,
                line_color="orange",
                name=opponent_pokemon['name'].capitalize(),
                fill='toself'
            ))

            # Update layout of the radar chart
            fig.update_layout(
                polar=dict(
                    bgcolor="rgb(14, 17, 23)",
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(max(user_stats), max(opponent_stats)) + 10]
                    )
                ),
                showlegend=True,
                title=f"Stats Comparison: {user_pokemon['name'].capitalize()} vs {opponent_pokemon['name'].capitalize()}"
            )

            return fig

        except Exception as e:
            st.error(f"An error occurred while plotting stats comparison: {str(e)}")
            return go.Figure()

    @staticmethod
    def plot_health_barchart(user_pokemon: dict, opponent_pokemon: dict) -> go.Figure:
        """
        Creates a bar chart showing health reduction of two Pokémon.

        Args:
        - user_pokemon (dict): The data of the user's Pokémon.
        - opponent_pokemon (dict): The data of the opponent's Pokémon.

        Returns:
        - go.Figure: The Plotly Figure object containing the bar chart.
        """
        try:
            fig = go.Figure()

            # Add bar chart for health comparison
            fig.add_trace(go.Bar(
                y=[opponent_pokemon['name'].capitalize(), user_pokemon['name'].capitalize()],
                x=[st.session_state['opponent_pokemon_health'], st.session_state['user_pokemon_health']],
                marker_color=['orange', 'magenta'],
                orientation='h'
            ))

            # Update layout of the bar chart
            fig.update_layout(
                xaxis_title="Remaining health",
                margin=dict(l=40, r=40, t=0, b=40)  # Adjust margins to reduce head space
            )

            return fig

        except Exception as e:
            st.error(f"An error occurred while plotting health bar chart: {str(e)}")
            return go.Figure()

    @staticmethod
    def create_attack_chart(selected_attack: dict) -> alt.Chart:
        """Create Altair chart for displaying attack details."""
        """
        Create Altair chart for displaying attack details.

        Args:
        - selected_attack (dict): The data of the attack details.

        Returns:
        - alt.Chart: The altair Figure object containing the bar chart.
        """
        df_selected_attack = pd.DataFrame([selected_attack])
        bar_chart = alt.Chart(df_selected_attack).mark_bar().encode(
            x=alt.X('value:Q', axis=alt.Axis(title='Value')),
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
        return bar_chart
