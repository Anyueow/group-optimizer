# Canvas-LinkedIn Profile Analyzer

## The Problem

We've all been there. That dreaded moment in class when the professor announces, "Pick your project teams!" As students, we often make quick decisions based on limited information - maybe choosing friends, or the people sitting nearby. But these snap judgments can lead to challenging group dynamics:

- The team where everyone's a leader, but no one wants to follow
- The quiet group where no one takes initiative
- The imbalanced team where one person carries the load
- The group that seems perfect... until deadlines approach and communication breaks down

These mismatched teams not only affect the project quality but can impact grades and create unnecessary stress. After experiencing this frustration firsthand, I decided to build a solution.

## The Solution

This tool automates the process of understanding potential teammates before group formation. It:

1. Pulls student information from Canvas
2. Finds their LinkedIn profiles
3. Analyzes their professional background and experiences
4. Generates compatibility scores for better team matching

Think of it as "Moneyball" for student project teams - using data to make more informed grouping decisions.
When forming teams, consider:

### Using the Scores
1. **Aim for 75+ Group Fit Scores**
   - Teams scoring above 75 show significantly better outcomes
   - Balance is more important than individual high scores

2. **Watch for Red Flags**
   - All members scoring < 30 on conscientiousness
   - No members scoring > 60 on extraversion
   - Technical skill gaps in critical areas

3. **Optimal Distribution**
   - 1-2 high extroversion (>70) members per team
   - At least 2 high conscientiousness (>80) members
   - Mixed technical strength distribution (archetypes for each role - select based on class & project)

### Research Backing

Our approach is grounded in organizational psychology research:
- Google's Project Aristotle findings on team effectiveness
- MIT's Human Dynamics Laboratory studies on team communication
- Harvard Business Review's research on high-performing teams

## How It Works

### Pipeline Overview

1. **Canvas Scraping**
   - Fetches class roster from your Canvas course
   - Extracts student names and available information

2. **LinkedIn Discovery**
   - Automatically finds corresponding LinkedIn profiles
   - Matches profiles based on name and university

3. **Profile Analysis**
   - Analyzes LinkedIn data for key indicators
   - Generates personality and compatibility metrics

4. **Team Optimization**
   - Sorts students by group project compatibility
   - Suggests balanced team compositions

## Getting Started

### Prerequisites

- Python 3.8+
- Microsoft Edge browser
- Active Canvas login session in Edge
- LinkedIn account credentials

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd canvas-linkedin-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Configuration

1. Create `secrets.py` with your LinkedIn credentials:
```python
Link_ps = "your_linkedin_password"
```

2. Ensure you're logged into Canvas in Microsoft Edge

## Limitations

### Educational Context
- Currently designed specifically for university students using Canvas LMS
- Optimized for Northeastern University's Canvas implementation
- Requires active student status and Canvas access

### Authentication Requirements
- Canvas login must be active in Microsoft Edge browser
- LinkedIn account with login credentials required
- Proper configuration of `secrets.py` needed

### Technical Considerations
- Rate limits apply to protect against API restrictions
- LinkedIn profile visibility affects analysis quality
- Results depend on profile completeness

## Project Structure

```
├── requirements.txt
├── src/
│   ├── scraper/
│   │   ├── populate.py        # Main pipeline orchestrator
│   │   ├── run_scraper.py     # Canvas scraping manager
│   │   └── url_finder.py      # LinkedIn URL finder
│   └── objects/
│       ├── CanvasScraper.py   # Canvas interaction logic
│       └── person.py          # Person data model
```

## Usage

1. Run the main pipeline:
```bash
python src/scraper/populate.py
```

2. Follow the interactive prompts to:
   - Select your Canvas course
   - Wait for LinkedIn profile discovery
   - Review compatibility analysis

## Technical Details

### Rate Limiting
- Implements respectful delays between requests
- Honors platform-specific rate limits
- Uses exponential backoff for failures

### Error Handling
- Robust exception management
- Debug logging options
- Graceful handling of missing data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your chosen license here]

## Disclaimer

This tool is for educational purposes only. Please ensure compliance with:
- Canvas Terms of Service
- LinkedIn's User Agreement
- Your institution's policies

## Support

For issues, questions, or contributions, please [open an issue](link-to-issues).
