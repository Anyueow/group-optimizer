import re  # Add missing import
import browser_cookie3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json
import os

class CanvasCookieScraper:
    def __init__(self, canvas_url):
        """
        Initialize scraper with your Canvas URL
        """
        self.base_url = canvas_url.rstrip('/')  # Ensure no trailing slash
        self.domain = urlparse(canvas_url).netloc
        self.session = requests.Session()

    def load_cookies_from_browser(self, browser_name='chrome'):
        """
        Load cookies from your already logged-in browser session
        """
        try:
            if browser_name == 'chrome':
                cookie_jar = browser_cookie3.chrome(domain_name=self.domain)
            elif browser_name == 'firefox':
                cookie_jar = browser_cookie3.firefox(domain_name=self.domain)
            elif browser_name == 'safari':
                cookie_jar = browser_cookie3.safari(domain_name=self.domain)
            elif browser_name == 'edge':
                cookie_jar = browser_cookie3.edge(domain_name=self.domain)

            self.session.cookies.update(cookie_jar)
            response = self.session.get(f"{self.base_url}/api/v1/users/self")
            return response.ok

        except Exception as e:
            print(f"Error loading cookies: {str(e)}")
            return False

    def get_courses(self):
        """Get courses using direct HTML parsing"""
        response = self.session.get(f"{self.base_url}/courses")
        if not response.ok:
            print(f"Failed to fetch courses: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        courses = []

        # Try multiple selectors as Canvas might have different layouts
        rows = (
                soup.find_all('tr', class_='course-list-table-row') or  # Table layout
                soup.find_all('div', class_='ic-DashboardCard') or      # Card layout
                soup.find_all('li', class_='ic-DashboardCard')          # Alternative card layout
        )

        for item in rows:
            course_id = None
            course_name = None

            # Try table layout first
            course_span = item.find('span', attrs={'data-course-id': True})
            if course_span:
                course_id = course_span.get('data-course-id')
                name_span = item.find('span', class_='name')
                if name_span:
                    course_name = name_span.get_text(strip=True)

            # Try card layout
            if not course_id:
                card_link = item.find('a', attrs={'href': lambda x: x and '/courses/' in x})
                if card_link:
                    href = card_link.get('href', '')
                    try:
                        course_id = href.split('/courses/')[1].split('/')[0]
                        course_name = card_link.get_text(strip=True)
                    except IndexError:
                        continue

            if course_id and course_name:
                courses.append((course_id, course_name))

        return courses

    def get_course_roster(self, course_id):
        """Get roster for a specific course"""
        url = f"{self.base_url}/api/v1/courses/{course_id}/users"
        params = {
            'include[]': ['enrollments', 'email'],
            'per_page': 100
        }

        all_users = []
        while url:
            response = self.session.get(url, params=params)
            if not response.ok:
                print(f"Error fetching roster: {response.status_code}")
                break

            users = response.json()
            all_users.extend(users)

            # Get next page URL
            url = response.links.get('next', {}).get('url')
            params = {} if url else params

        return all_users

    def get_user_courses(self, user_id):
        """Get all courses for a specific user"""
        url = f"{self.base_url}/api/v1/users/{user_id}/courses"
        params = {
            'include[]': ['total_students'],
            'per_page': 100
        }

        all_courses = []
        while url:
            response = self.session.get(url, params=params)
            if not response.ok:
                break

            courses = response.json()
            all_courses.extend(courses)

            url = response.links.get('next', {}).get('url')
            params = {} if url else params

        return all_courses

def main():
    # Initialize with Northeastern Canvas URL
    canvas_url = "https://northeastern.instructure.com"
    scraper = CanvasCookieScraper(canvas_url)

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

    for index, user in enumerate(roster, 1):
        print(f"Processing user {index}/{total_users}: {user['name']}")
        user_courses = scraper.get_user_courses(user['id'])

        user_data = {
            'id': user['id'],
            'name': user['name'],
            'email': user.get('email', 'Not available'),
            'enrollments': [
                {
                    'type': enrollment['type'],
                    'role': enrollment['role'],
                    'section': enrollment.get('course_section_id')
                }
                for enrollment in user.get('enrollments', [])
            ],

        }
        roster_data.append(user_data)

    # Save to file
    output_file = os.path.join(output_dir, f'course_{selected_course_id}_roster_data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(roster_data, f, indent=2)

    print(f"\nData has been saved to {output_file}")

if __name__ == "__main__":
    main()