# 🏀 NBA Draft Bidding Game

An interactive web application for running NBA player draft bidding games using real player statistics from Excel files.

## 🎮 Features

- **Excel Data Integration**: Pulls NBA player stats directly from your Excel files
- **Interactive Bidding**: Real-time bidding system with budget management
- **Live Draft Board**: Track all players and budgets in real-time
- **Customizable Setup**: Adjust number of players, rounds, and player names
- **Accurate Stats**: Uses your own NBA player data (PPG, APG, RPG)
- **Responsive Design**: Works on desktop and mobile devices

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/itemp22/nba-draft-app.git
   cd nba-draft-app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your Excel file**
   - Place your NBA player stats Excel file in the project folder
   - File should have columns for: Player Name, PPG, APG, RPG
   - Supported formats: `.xlsx`, `.xls`

4. **Run the app**
   ```bash
   streamlit run nbadraft_app.py
   ```

### Streamlit Cloud Deployment

1. **Fork this repository** to your GitHub account
2. **Go to [share.streamlit.io](https://share.streamlit.io)**
3. **Sign in with GitHub**
4. **Click "New app"**
5. **Select your repository**: `your-username/nba-draft-app`
6. **Set main file path**: `nbadraft_app.py`
7. **Click "Deploy"**
8. **Upload your Excel file** to the deployed app

## 🎯 How to Play

1. **Setup Game**
   - Set number of rounds (default: 6)
   - Set number of participants (default: 4)
   - Enter player names

2. **Start Draft**
   - Click "Start Draft" to begin
   - Each player gets $1000 budget

3. **Bidding Process**
   - NBA players are randomly selected each round
   - View player stats (PPG, APG, RPG)
   - Set bid amount and select winning bidder
   - Budget is deducted from winning bidder
   - Players can be skipped if no one wants to bid

4. **Track Progress**
   - Live draft board shows all teams
   - Monitor remaining budgets
   - View drafted players and their stats

## 📊 Excel File Format

Your Excel file should contain these columns:

| Column | Description | Example |
|--------|-------------|---------|
| Player Name | Full player name | "LeBron James" |
| PPG | Points per game | "25.4" |
| APG | Assists per game | "7.2" |
| RPG | Rebounds per game | "7.8" |

**Supported column names:**
- Player Name: "Player", "Name", "Player Name"
- PPG: "PPG", "Points", "PTS", "Points Per Game"
- APG: "APG", "Assists", "AST", "Assists Per Game"
- RPG: "RPG", "Rebounds", "REB", "Rebounds Per Game"

## 🛠️ Technical Details

- **Framework**: Streamlit
- **Data Source**: Excel files (.xlsx, .xls)
- **Dependencies**: pandas, openpyxl
- **Session Management**: Persistent game state across interactions
- **Error Handling**: Graceful handling of missing or invalid data

## 📁 Project Structure

```
nba-draft-app/
├── nbadraft_app.py      # Main application file
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .gitignore          # Git ignore rules
└── your-excel-file.xlsx # Your NBA player data
```

## 🔧 Dependencies

- `streamlit>=1.28.0` - Web application framework
- `pandas>=2.0.0` - Data manipulation
- `openpyxl>=3.1.0` - Excel file reading

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🏀 Enjoy Your Draft!

Create exciting NBA draft experiences with real player statistics and competitive bidding!
