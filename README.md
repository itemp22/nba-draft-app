# 🏀 NBA Draft Bidding Game

A fun interactive web app for running NBA player draft auctions with friends! Built with Streamlit and powered by real NBA statistics.

## 🎮 Features

- **Real NBA Data**: Fetches current player statistics from the balldontlie API
- **Auction Bidding**: Players bid on NBA stars with virtual currency
- **Budget Management**: Each player starts with $1000 and must manage their budget
- **Live Draft Board**: Real-time tracking of all players and their drafted teams
- **Customizable**: Set number of rounds and players
- **Fallback Data**: Uses sample data if API is unavailable

## 🚀 Quick Start

### Option 1: Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/nba-draft-app.git
   cd nba-draft-app
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```bash
   streamlit run nbadraft_app.py
   ```

4. **Open your browser** and go to `http://localhost:8501`

### Option 2: Deploy to Streamlit Cloud

1. Fork this repository to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repository
5. Deploy! Your app will be live at a public URL

## 🎯 How to Play

1. **Setup**: Configure number of rounds and players in the sidebar
2. **Start**: Click "🚀 Start Draft" to begin the auction
3. **Bid**: For each NBA player:
   - Review their stats (PPG, APG, RPG)
   - Enter your bid amount
   - Choose the winning bidder
   - Submit the bid
4. **Track**: Monitor the live draft board to see everyone's teams
5. **Win**: Build the best team within your budget!

## 🛠️ Technical Details

- **Frontend**: Streamlit
- **Data Source**: balldontlie API (free, no authentication required)
- **Backend**: Python
- **Deployment**: Streamlit Cloud

## 📊 API Information

This app uses the [balldontlie API](https://www.balldontlie.io/) to fetch real NBA player statistics. The API is free to use and doesn't require authentication.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

---

**Enjoy your NBA Draft! 🏀**
