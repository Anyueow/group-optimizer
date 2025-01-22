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
from src.objects.person import Person  # If you store Person here, adjust accordingly


# --------------------------------------------------------------------------
# STEP 1: CanvasScraperManager
# --------------------------------------------------------------------------
def fetch_persons_from_canvas():
    """
    Uses CanvasScraperManager to fetch a list of Person objects.
    Returns:
        list of Person
    """
    print("\n=== STEP 1: Fetching Person objects from Canvas ===")

    canvas_manager = CanvasScraperManager()
    persons = canvas_manager.run()

    if not persons:
        print("No persons found from Canvas.")
        return None

    print(f"Fetched {len(persons)} Person objects from Canvas.")
    canvas_manager.close()
    return persons


# --------------------------------------------------------------------------
# STEP 2: URLFinder
# --------------------------------------------------------------------------
def find_linkedin_urls(persons):
    """
    Uses URLFinder to find LinkedIn URLs for each Person in the list.
    Returns:
        The updated list of Person objects (some may have new LinkedIn URLs).
    """
    print("\n=== STEP 2: Finding LinkedIn URLs for each Person ===")
    url_finder = URLFinder(debug=True)  # debug=False to reduce console logs if you prefer
    updated_persons = url_finder.update_person_list(persons)

    # Filter only those persons who have a LinkedIn URL
    persons_with_links = [p for p in updated_persons if p.linkedin]
    print(f"Out of {len(updated_persons)} total, "
          f"{len(persons_with_links)} now have LinkedIn URLs.")

    return updated_persons


# --------------------------------------------------------------------------
# STEP 3: LinkedInBatchAnalyzer
# --------------------------------------------------------------------------
def analyze_linkedin_profiles(persons):
    """
    Uses LinkedInBatchAnalyzer to analyze each Person's LinkedIn profile.
    Returns:
        The same list of Person objects, but with .details filled in.
    """
    print("\n=== STEP 3: Analyzing LinkedIn Profiles for Personality ===")

    # Provide your LinkedIn credentials from a secrets file or env variables
    EMAIL = "anyushah@gmail.com"
    PASSWORD = secrets.Link_ps  # e.g., from secrets.py

    batch_analyzer = LinkedInBatchAnalyzer(email=EMAIL, password=PASSWORD, headless=True)

    # Only pass LinkedIn URLs
    persons_with_links = [p for p in persons if p.linkedin]
    profile_urls = [person.linkedin for person in persons_with_links]

    # This returns a list of Person objects that presumably have 'details' set
    analyzed_persons = batch_analyzer.run_analysis(profile_urls)
    print(analyzed_persons)

    return persons


# --------------------------------------------------------------------------
# STEP 4: Sort & Print
# --------------------------------------------------------------------------
def sort_and_print_results(persons):
    """
    Sorts the person list by 'group_project_fit_score' in descending order
    and prints them.
    """
    print("\n=== STEP 4: Sort & Print Results (by group_project_fit_score) ===")

    # Sort in place by 'group_project_fit_score' (default 0 if missing)
    persons.sort(
        key=lambda p: p.details.get('group_project_fit_score', 0) if p.details else 0,
        reverse=True  # Highest score first
    )

    for person in persons:
        score = person.details.get('group_project_fit_score', 0) if person.details else 0
        print(
            f"Name: {person.name}, "
            f"LinkedIn: {person.linkedin}, "
            f"Score: {score}, "
            f"Details: {person.details if person.details else 'N/A'}"
        )


# --------------------------------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------------------------------
def main():
    # Step 1
    persons = fetch_persons_from_canvas()
    if not persons:
        print("Exiting pipeline after Step 1 due to no data.")
        return  # End pipeline early if no data

    # Step 2
    persons = find_linkedin_urls(persons)
    # You could do additional checks here if needed

    # Step 3
    persons = analyze_linkedin_profiles(persons)
    # Additional checks (e.g., do we have any relevant results?)

    # Step 4
    sort_and_print_results(persons)
    # Pipeline ends

if __name__ == "__main__":
    main()