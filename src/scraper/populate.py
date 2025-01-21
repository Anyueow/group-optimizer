# run_full_pipeline.py
"""
1) Run CanvasScraperManager to fetch Person objects from Canvas.
2) Run URLFinder to populate Person.linkedin attributes.
3) Run LinkedInBatchAnalyzer to generate personality scores
   and store them in Person.details.
4) Print all Person objects, sorted by group_project_fit_score.
"""

import secrets  # or wherever you store your credentials

# Adjust the import paths to match your project structure
from run_scraper import CanvasScraperManager
from url_finder import URLFinder
from linkedin.batch_analysis import LinkedInBatchAnalyzer
from linkedin.linkedin_scraper import LinkedInScraper
from src.objects.person import Person  # If you store Person here, adjust accordingly


def main():
    # --------------------------------------------------------------------------
    # 1) CanvasScraperManager: Fetch Person objects from Canvas
    # --------------------------------------------------------------------------
    print("\n=== STEP 1: Fetching Person objects from Canvas ===")
    canvas_manager = CanvasScraperManager()
    # Ensure your CanvasScraperManager has a method that returns a list of Person objects
    # (e.g., modify its `run()` method to return persons instead of only printing them)
    persons = canvas_manager.run()

    if not persons:
        print("No persons found from Canvas. Exiting pipeline.")
        return

    print(f"Fetched {len(persons)} Person objects from Canvas.")

# Test
    # --------------------------------------------------------------------------
    # 2) URLFinder: Populate Person.linkedin
    # --------------------------------------------------------------------------
    print("\n=== STEP 2: Finding LinkedIn URLs for each Person ===")
    url_finder = URLFinder(debug=True)  # Set `debug=False` to reduce console logs
    persons = url_finder.update_person_list(persons)

    # Filter only those persons who have a LinkedIn URL
    persons_with_links = [p for p in persons if p.linkedin]
    print(f"Out of {len(persons)} total, {len(persons_with_links)} now have LinkedIn URLs.")


    # --------------------------------------------------------------------------
    # 3) LinkedInBatchAnalyzer: Analyze each LinkedIn profile for personality
    # --------------------------------------------------------------------------
    print("\n=== STEP 3: Analyzing LinkedIn Profiles for Personality ===")

    # Provide your LinkedIn credentials from a secrets file or environment variables
    EMAIL = "anyushah@gmail.com"
    PASSWORD = secrets.Link_ps  # e.g., from secrets.py

    # Instantiate the batch analyzer
    batch_analyzer = LinkedInBatchAnalyzer(email=EMAIL, password=PASSWORD, headless=True)

    # We only need the list of LinkedIn URLs to pass to run_analysis()
    profile_urls = [person.linkedin for person in persons_with_links]

    # This returns a list of Person objects that have 'details' set
    # or however your `run_analysis` method is currently designed.
    analyzed_persons = batch_analyzer.run_analysis(profile_urls)

    # If `run_analysis` returns new Person objects with name + details,
    # we match them back to the original list by name (or another unique identifier).
    for analyzed_person in analyzed_persons:
        # Attempt to find the corresponding original Person by matching name
        for original_person in persons_with_links:
            if analyzed_person.name.strip().lower() == original_person.name.strip().lower():
                # Suppose 'details' is the dictionary that includes extraversion, conscientiousness, etc.
                original_person.details = getattr(analyzed_person, 'details', {})
                break


    # --------------------------------------------------------------------------
    # 4) Sort & Print: Sort persons by their "group_project_fit_score"
    # --------------------------------------------------------------------------
    # For anyone missing 'details', default the score to 0
    persons.sort(
        key=lambda p: (p.details.get('group_project_fit_score', 0)
                       if p.details else 0),
        reverse=True  # Highest score first
    )

    print("\n=== FINAL RESULTS (Sorted by group_project_fit_score) ===")
    for person in persons:
        score = person.details.get('group_project_fit_score', 0) if person.details else 0
        print(
            f"Name: {person.name}, "
            f"LinkedIn: {person.linkedin}, "
            f"Score: {score}, "
            f"Details: {person.details if person.details else 'N/A'}"
        )


if __name__ == "__main__":
    main()
