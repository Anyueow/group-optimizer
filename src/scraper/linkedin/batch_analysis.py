# run_batch_analysis.py
"""
Class-based script that handles LinkedIn profile scraping
and personality analysis in a batch.
"""
from typing import List
import secrets  # optional if you store credentials in a separate secrets file

from linkedin_scraper import LinkedInScraper_Anyu
from models import LinkedInProfile
from profile_analyzer import LinkedInPersonalityAnalyzer
from src.objects.person import Person


class LinkedInBatchAnalyzer:
    """
    Orchestrates the scraping of multiple LinkedIn profiles
    and performs personality analysis for each.
    """

    def __init__(self, email: str, password: str, headless: bool = True):
        """
        Initializes LinkedIn credentials and headless mode setting for the scraper.
        """
        self.email = email
        self.password = password
        self.headless = headless
        self.scraper = None
        self.analyzer = LinkedInPersonalityAnalyzer()

    @staticmethod
    def _profile_to_dict(lp: LinkedInProfile) -> dict:
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

    def login(self) -> bool:
        """
        Creates and logs into the LinkedInScraper instance.
        Returns True if login is successful; False otherwise.
        """
        self.scraper = LinkedInScraper_Anyu(email=self.email, password=self.password, headless=self.headless)
        return self.scraper.login()

    def run_analysis(self, profile_urls: List[str]) -> List[Person]:
        """
        Given a list of LinkedIn profile URLs, scrape & analyze each,
        returning a list of Person objects with their personality scores.
        """
        # 1) Create & log in to the scraper
        if not self.login():
            print("Login failed; cannot proceed with scraping.")
            return []

        results = []

        # 2) Loop over each profile URL
        for url in profile_urls:
            print(f"\nScraping profile: {url}")
            linkedin_profile = self.scraper.scrape_profile(url)

            if not linkedin_profile:
                print("Failed to retrieve profile data.")
                continue

            # Convert to dict for analyzer
            profile_dict = self._profile_to_dict(linkedin_profile)

            # Run the analyzer
            analysis_result = self.analyzer.analyze_profile(profile_dict)

            # Extract a name and a chosen "personality_score" from the analysis result
            name = analysis_result.get('name', 'Unknown')
            personality_score = analysis_result.get('group_project_fit_score', 0.0)

            # Create a Person object & set the personality score
            person = Person(name=name)
            person.set_personality_score(personality_score)

            # Collect the result
            results.append(person)

        # 3) Close the scraper once finished
        self.scraper.close()
        return results


if __name__ == "__main__":
    # Example usage:
    # Use your real credentials here (or from a separate secrets file).
    EMAIL = "anyushah@gmail.com"
    PASSWORD = secrets.Link_ps  # e.g., stored in secrets.py

    # A list of LinkedIn profile URLs to scrape
    profiles = [
        "https://www.linkedin.com/in/manvi-kottakota",
        "https://www.linkedin.com/in/anyushah",
        "https://www.linkedin.com/in/armaanajoomal",
    ]

    # Instantiate and run the batch analysis
    batch_analyzer = LinkedInBatchAnalyzer(email=EMAIL, password=PASSWORD, headless=True)
    analysis_results = batch_analyzer.run_analysis(profiles)

    print("\n=== Final Batch Analysis Results ===")
    for person in analysis_results:
        print(person)
        # Example output:
        # Person(name='Alice Smith', personality_score=70.5, ...)
        # Person(name='Bob Johnson', personality_score=58.0, ...)
