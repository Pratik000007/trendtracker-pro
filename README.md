# TrendTracker - Social Media Intelligence Platform

A social listening platform that monitors Twitter/X, Reddit, and YouTube to identify trending topics for business intelligence.

## Features

- **Multi-platform monitoring**: Twitter/X, Reddit, YouTube
- **AI-powered analysis**: Sentiment analysis, keyword extraction, topic clustering
- **Trending velocity detection**: Identifies rising, steady, and falling topics
- **Automated scheduling**: Runs every 6 hours via GitHub Actions
- **Interactive dashboard**: Streamlit-based visualization

## Quick Start

### Local Development

```bash
# 1. Clone and navigate
cd trendtracker

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"

# 5. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 6. Run collector
python main.py

# 7. Launch dashboard
streamlit run dashboard.py