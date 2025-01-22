# run_batch_analysis.py
"""
Class-based script that handles LinkedIn profile scraping
and personality analysis in a batch.
"""
from typing import List
import secrets  # optional if you store credentials in a separate secrets file

from src.scraper.linkedin.profile_analyzer import LinkedInPersonalityAnalyzer
from src.objects.person import Person
from src.scraper.linkedin.linkedinscraper_cust import LinkedInScraper_Anyu
from src.scraper.linkedin.models import LinkedInProfile


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

    def run_analysis(self, persons: List[Person]) -> List[Person]:
        """
        Accepts a list of Person objects. For each person who has a
        LinkedIn URL, scrape + analyze that profile, storing results
        back into that same Person. Returns the same list.
        """
        if not self.login():
            print("Login failed; cannot proceed with scraping.")
            return persons  # return them unmodified if login fails


        for person in persons:
            print(f"Analyzing {person.name}")
            linkedin_profile = self.scraper.scrape_profile(person.linkedin)

            if not linkedin_profile:
                print(f"Failed to retrieve LinkedIn profile for {person.name}.")


            # Convert to dict, then analyze
            profile_dict = self._profile_to_dict(linkedin_profile)
            analysis_result = self.analyzer.analyze_profile(profile_dict)

            # Suppose the analyzer returns a dict like:
            # {
            #   "name": "Fu Chai",
            #   "personality_score": 0.85,
            #   "extroversion": 0.7,
            #   ...
            # }
            #
            # Store the entire analysis in person.details
            person.details = analysis_result

            # Optionally also call a setter if your Person class has it
            personality_score = analysis_result.get('personality_score')
            person.set_personality_score(personality_score)

            # Close the scraper once finished
        self.scraper.close()
        return persons


if __name__ == "__main__":
    # Example usage:
    # Use your real credentials here (or from a separate secrets file).
    EMAIL = "anyushah@gmail.com"
    PASSWORD = secrets.Link_ps  # e.g., stored in secrets.py

    # A list of Person objects with name + linkedin
    kaamil = Person(name= "Kaamil Thobani")
    kaamil.linkedin ="https://www.linkedin.com/in/kaamil-thobani-9a7237210/"
    persons = [
        kaamil
        # Add more Person objects if you like
    ]
    # Instantiate and run the batch analysis
    batch_analyzer = LinkedInBatchAnalyzer(email=EMAIL, password=PASSWORD, headless=True)
    analysis_results = batch_analyzer.run_analysis(persons)

    print("\n=== Final Batch Analysis Results ===")
    for person in analysis_results:
        print(person)
        # Example output:
        # Person(name='Alice Smith', personality_score=70.5, ...)
        # Person(name='Bob Johnson', personality_score=58.0, ...)
