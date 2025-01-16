# scraper.py
"""
Non-class script that orchestrates the scraping.
"""
import os
import sys


from src.objects.CanvasScraper import CanvasScraper
from src.objects.person import Person


def main():
    # Initialize with Northeastern Canvas URL
    canvas_url = "https://northeastern.instructure.com"
    scraper = CanvasScraper(canvas_url)

    print("\nAttempting to load cookies from Edge browser...")
    if not scraper.load_cookies_from_browser('edge'):
        print("Failed to load cookies! Make sure you're logged into Canvas in Edge browser.")
        return

    print("Successfully loaded cookies!")

    # Fetch courses
    print("\nFetching courses...")
    courses = scraper.get_courses()

    if not courses:
        print("No courses found! Check if you're properly logged in.")
        return

    # Display courses
    print("\nAvailable Courses:")
    for i, (course_id, course_name) in enumerate(courses, 1):
        print(f"{i}. {course_name} (ID: {course_id})")

    # Get course selection
    while True:
        try:
            selection = int(input("\nEnter the number of the course to analyze: ")) - 1
            if 0 <= selection < len(courses):
                selected_course_id = courses[selection][0]
                break
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

    # Create output directory
    output_dir = "canvas_data"
    os.makedirs(output_dir, exist_ok=True)

    # Fetch roster and user data
    print(f"\nFetching roster for course ID: {selected_course_id}")
    roster = scraper.get_course_roster(selected_course_id)

    roster_data = []
    total_users = len(roster)
    print(f"\nFound {total_users} users. Processing user data...")

    # 6. Convert each dict in roster to a Person object
    persons = []
    for user_dict in roster:
        name = user_dict.get('name', 'Unknown Name')
        email = user_dict.get('email', 'No Email')
        person = Person(name, email)
        persons.append(person)

    print(f"Retrieved {len(persons)} persons from the roster.")



    # 8. Pass the persons to LinkedInScraper to enrich them
    #linkedin_scraper = LinkedInScraper()
    #linkedin_scraper.scrape_linkedin_info(persons)

    # 9. Print final results (or do something else with them)
    for p in persons:
        print(f"{p}")

if __name__ == "__main__":
    main()
