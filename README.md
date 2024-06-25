# Pokémon Battle Simulator

Welcome to the Pokémon Battle Simulator! This Streamlit application allows you to simulate Pokémon battles between your favourite Pokémon and wild Pokémon. You can choose your Pokémon, select attacks, and battle against a randomly selected opponent. The application displays real-time health bars, attack details, and battle outcomes using Streamlit, Altair and Plotly for visualisations.

You can choose from the original 151 Pokémon from the 1996 RPGs Pokémon Red Version and Pokémon Blue Version.

![Blue](<https://imgs.search.brave.com/3LkWG5fIbgfiLb4pr0pU7nNt1A1_3UHw3Hta6rR1quQ/rs:fit:860:0:0/g:ce/aHR0cHM6Ly9pbWcu/cG9rZW1vbmRiLm5l/dC9ib3hlcy9ibHVl/LmpwZw>) ![Red](<https://imgs.search.brave.com/a3Zf3BcR4OAJ0oISRKUAJNA-ru5EsbQTD87lOUagDuw/rs:fit:860:0:0/g:ce/aHR0cHM6Ly9pbWcu/cG9rZW1vbmRiLm5l/dC9ib3hlcy9yZWQu/anBn>)

## Features

- Select your favourite Pokémon by name or number.
- View Pokémon stats and attack moves.
- Initiate battles with a wild Pokémon.
- Choose attacks and see real-time damage calculations.
- Reset Pokémon health after battles with a Max Potion.

## Technologies Used

- **Streamlit**: For building and deploying the web application.
- **Python**: Backend logic and calculations.
- **Pandas**: Data manipulation and handling.
- **Altair**: Visualising attack details using interactive charts.
- **Random**: Generating random opponents for battles.

## Installation

To run the Pokémon Battle Simulator locally, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/ChefData/pokemon-battle-simulator.git
   cd pokemon-battle-simulator
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit application:

   ```bash
   streamlit run streamlit_app.py
   ```

4. Open your web browser and go to `http://localhost:8501` to view the application.

## Usage

   ![Choose](<images/Choose.png>)

1. **Select Your Pokémon:**
   - Use the slider to choose your Pokémon by number (1-151).
   - Alternatively, select your Pokémon by name from the dropdown list.

2. **View Pokémon Stats and Moves:**
   - Once a Pokémon is selected, its stats and available attack moves are displayed.

   ![Choose](<images/Move.png>)

3. **Battle Start:**
   - Click on "Wild Pokémon appeared!" to start a battle with a randomly chosen wild Pokémon.

4. **Battle Interface:**
   - During battles, see your Pokémon facing off against the opponent.
   - Use the dropdown to select an attack move for your Pokémon.

   ![Choose](<images/Fight.png>)

5. **Attack and Damage:**
   - Click "Use Move" to execute the selected attack.
   - Damage dealt and remaining health are displayed for both Pokémon.

6. **Battle Outcome:**
   - Continue battling until one Pokémon's health drops to zero.
   - Once a battle ends, reset your Pokémon's health using "Use Max Potion" and call another opponent by clicking "Wild Pokémon appeared!" again.

## Contributing

Contributions are welcome! If you have any suggestions, improvements, or bug fixes, please submit a pull request or raise an issue.

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

## License

This project is licensed under the Apache License - see the [LICENSE](LICENSE) file for details.
