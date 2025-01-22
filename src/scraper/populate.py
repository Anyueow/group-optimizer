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
    Returns the same list of Person objects, but with .details filled in.
    """
    print("\n=== STEP 3: Analyzing LinkedIn Profiles for Personality ===")

    EMAIL = "anyushah@gmail.com"
    PASSWORD = secrets.Link_ps

    batch_analyzer = LinkedInBatchAnalyzer(email=EMAIL, password=PASSWORD, headless=True)

    # Just pass the entire list of persons into run_analysis
    enriched_persons = batch_analyzer.run_analysis(persons)

    # Now 'enriched_persons' is the same list object as 'persons',
    # but with details appended. (In Python, lists are mutable.)
    return enriched_persons


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
        key=lambda p: p.details.get('personality_score', 0) if p.details else 0,
        reverse=True  # Highest score first
    )

    for person in persons:
        print(
            f"Name: {person.name}, "
            f"LinkedIn: {person.linkedin}, "
            f"Score: {person.personality_score}, "
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
    updated_persons = find_linkedin_urls(persons)
    # You could do additional checks here if needed

    # Step 3
    enriched_persons = analyze_linkedin_profiles(updated_persons)
    # Additional checks (e.g., do we have any relevant results?)

    # Step 4
    sort_and_print_results(enriched_persons)
    # Pipeline ends

if __name__ == "__main__":
    main()