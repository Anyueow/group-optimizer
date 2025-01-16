# run_batch_analysis.py

from typing import List
import secrets  # optional if you store credentials in a separate secrets file

from linkedin_scraper import LinkedInScraper
from models import LinkedInProfile
from profile_analyzer import LinkedInPersonalityAnalyzer


def profile_to_dict(lp: LinkedInProfile) -> dict:
    """
    Convert LinkedInProfile dataclass to a dictionary
    that matches the expected input for LinkedInPersonalityAnalyzer.
    """
    return {
        "Name": lp.name or "",
        "Followers": lp.followers or 0,
        "Verified": lp.verified or False,
        "Experiences": [
            {
                "role": exp.get("role", ""),
                "company": exp.get("company", ""),
                "date_range": exp.get("date_range", ""),
                "description": exp.get("description", "")
            }
            for exp in lp.experiences
        ]
    }


def run_batch_analysis(profile_urls: List[str]) -> List[dict]:
    """
    Given a list of LinkedIn profile URLs, scrape & analyze each,
    returning a list of dictionaries: [{name, personality_score}, ...]
    """
    # 1) Setup your LinkedIn credentials
    EMAIL = "anyushah@gmail.com"
    PASSWORD = secrets.Link_ps

    # 2) Create the scraper
    scraper = LinkedInScraper(email=EMAIL, password=PASSWORD, headless=True)

    # 3) Log in once
    if not scraper.login():
        print("Login failed; cannot proceed with scraping.")
        return []

    # 4) Prepare the personality analyzer
    analyzer = LinkedInPersonalityAnalyzer()

    results = []

    # 5) Loop over each profile URL
    for url in profile_urls:
        print(f"\nScraping profile: {url}")
        linkedin_profile = scraper.scrape_profile(url)

        if not linkedin_profile:
            print("Failed to retrieve profile data.")
            continue

        # Convert to dict for analyzer
        profile_dict = profile_to_dict(linkedin_profile)

        # Run the analyzer
        analysis_result = analyzer.analyze_profile(profile_dict)

        # The user wants a dict { name: "xx", personality_score: 0.0 }
        # The `analysis_result` might look like:
        #   {
        #     'name': 'John Doe',
        #     'extraversion_score': 65.0,
        #     'conscientiousness_score': 72.0,
        #     'archetype': 'Tech Bro',
        #     'group_project_fit_score': 69.8
        #   }
        # We can define "personality_score" however we like (maybe group_project_fit_score?).
        # Or we can create a custom measure. For now, let's reuse group_project_fit_score:

        name = analysis_result['name']
        personality_score = analysis_result['group_project_fit_score']  # or define your own logic

        # Append final output
        results.append({
            'name': name,
            'personality_score': personality_score
        })

    # 6) Close the scraper
    scraper.close()

    return results


if __name__ == "__main__":
    # Example usage
    # A list of LinkedIn profile URLs to scrape
    profiles = [
        "https://www.linkedin.com/in/manvi-kottakota",
        "https://www.linkedin.com/in/anyushah",
        "https://www.linkedin.com/in/armaanajoomal",
        # ...
    ]

    # Run batch analysis
    analysis_results = run_batch_analysis(profiles)

    print("\n=== Final Batch Analysis Results ===")
    for result in analysis_results:
        print(result)
    # e.g.:
    # {'name': 'Alice Smith', 'personality_score': 70.5}
    # {'name': 'Bob Johnson', 'personality_score': 58.0}
