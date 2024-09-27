# Daily News Collector

## Overview
The **Daily News Collector** is an automated system that collects, analyzes, and visualizes daily domestic broadcast news. It provides insights into news trends and automatically sends reports via email, making it a valuable tool for researchers and analysts.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Data Structure](#data-structure)
- [Workflow](#workflow)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Features
- **Automated Data Collection**: Gathers news data daily.
- **Data Visualization**: Generates visual representations of trends and keywords.
- **Email Reporting**: Sends daily email reports with visualizations attached.
- **Customizable Configurations**: Easily adjust settings for email and data paths.

## Installation
To set up the Daily News Collector, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/daily-news-collector.git
   cd daily-news-collector
   ```

2. **Install Required Dependencies**:
   Ensure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
To execute the news collection process manually, run:
```bash
python src/main.py
```
This command triggers the collection of news data, visualization generation, and email dispatch.

## Data Structure
The project follows a specific directory structure for organization:
```
├── config
│   ├── SimHei.ttf                # Font file for visualizations
│   ├── blackwords-en.txt         # English stop words
│   ├── blackwords-zh.txt         # Chinese stop words
│   └── config.py                 # Configuration settings
├── data
│   ├── [Various CSV/JSON files]  # Collected news data
│   └── original_data             # Original raw data files
├── figures
│   ├── [Visualizations]           # Generated visual outputs
├── logs                           # Log files for tracking
├── src
│   ├── main.py                    # Main execution script
│   └── news_collect_for_today.py  # Data collection script
└── util
    ├── [Utility scripts]          # Various utility functions
```

## Workflow
The main workflow consists of several key steps:

1. **Data Collection**: The script `news_collect_for_today.py` fetches the latest news and formats it for analysis.
2. **Data Visualization**: The `run_visualizations` function creates visualizations for the collected data, including keyword analysis and trends.
3. **Email Notification**: An email with the visualizations is sent to the configured recipients using the `EmailSender` class.

## Configuration
Before running the project, ensure to update the `config/config.py` file with your email settings and file paths. You can set the following variables:
- `EMAIL_ADDRESS`
- `EMAIL_PASSWORD`
- `TO_EMAILS`
- Paths for data and images

## Contributing
We welcome contributions to enhance the Daily News Collector! If you'd like to contribute:
1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request or open an issue for discussion.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.