# scraper.py
"""
Class-based script that orchestrates the scraping.
"""
import os
import sys

from src.objects.CanvasScraper import CanvasScraper
from src.objects.person import Person


class CanvasScraperManager:
    """
    Orchestrates loading cookies from Edge, fetching course details,
    and processing the roster for a given course on Northeastern's Canvas.
    """

    def __init__(self, canvas_url: str = "https://northeastern.instructure.com"):
        """
        Initializes the CanvasScraper with the given Canvas URL.
        """
        self.canvas_url = canvas_url
        self.scraper = CanvasScraper(self.canvas_url)
        self.output_dir = "canvas_data"

    def run(self):
        """
        Orchestrates the scraping logic: loads cookies, lists courses,
        prompts user for course selection, fetches the roster, and processes it.
        """
        # 1. Load cookies
        print("\nAttempting to load cookies from Chrome browser...")
        if not self.scraper.load_cookies_from_browser('edge'):
            print("Failed to load cookies! Make sure you're logged into Canvas in Edge browser.")
            return
        print("Successfully loaded cookies!")

        # 2. Fetch courses
        print("\nFetching courses...")
        courses = self.scraper.get_courses()
        if not courses:
            print("No courses found! Check if you're properly logged in.")
            return

        # 3. Display courses
        print("\nAvailable Courses:")
        for i, (course_id, course_name) in enumerate(courses, 1):
            print(f"{i}. {course_name} (ID: {course_id})")

        # 4. Get course selection from user input
        selected_course_id = self._select_course(courses)
        if not selected_course_id:
            return  # Invalid or no selection made, just return

        # 5. Create output directory if it does not exist
        os.makedirs(self.output_dir, exist_ok=True)

        # 6. Fetch roster and create Person objects
        print(f"\nFetching roster for course ID: {selected_course_id}")
        roster = self.scraper.get_course_roster(selected_course_id)
        total_users = len(roster)
        print(f"\nFound {total_users} users. Processing user data...")

        # Convert each dict in roster to a Person object
        persons = [Person(user_dict.get('name', 'Unknown Name')) for user_dict in roster]
        print(f"Retrieved {len(persons)} persons from the roster.")

        # 7. (Optional) Enrich the data (e.g., LinkedInScraper)
        # linkedin_scraper = LinkedInScraper()
        # linkedin_scraper.scrape_linkedin_info(persons)

        # 8. Print final results (or do something else with them)
        for p in persons:
            print(f"{p}")
            # At the very end, if we want to exit after finishing:
        print("Scraping complete. Exiting now.")

        self.close()

        return persons


    def _select_course(self, courses):
        """
        Helper method to prompt user for course selection from a list of courses.
        Returns the selected course ID or None if selection is invalid.
        """
        while True:
            try:
                selection = int(input("\nEnter the number of the course to analyze: ")) - 1
                if 0 <= selection < len(courses):
                    return courses[selection][0]
                print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

    def close(self):
        self.scraper.close()

if __name__ == "__main__":
    manager = CanvasScraperManager()
    manager.run()
