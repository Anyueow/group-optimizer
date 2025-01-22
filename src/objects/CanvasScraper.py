import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import browser_cookie3

class CanvasScraper:
    """
    A class that handles Canvas-related scraping via HTTP requests
    (using cookies from an already logged-in browser session).
    """

    def __init__(self, canvas_url):
        """
        Initialize the scraper with your Canvas URL
        """
        self.base_url = canvas_url.rstrip('/')  # Ensure no trailing slash
        self.domain = urlparse(self.base_url).netloc
        self.session = requests.Session()

    def load_cookies_from_browser(self, browser_name='edge'):
        """
        Load cookies from an already logged-in browser session
        so the requests session is authenticated with Canvas.

        Returns:
            bool: True if cookies were loaded & Canvas returned a 200 OK,
                  False otherwise.
        """
        try:
            # Grab cookies from the specified browser
            if browser_name == 'chrome':
                cookie_jar = browser_cookie3.chrome(domain_name=self.domain)
            elif browser_name == 'firefox':
                cookie_jar = browser_cookie3.firefox(domain_name=self.domain)
            elif browser_name == 'safari':
                cookie_jar = browser_cookie3.safari(domain_name=self.domain)
            elif browser_name == 'edge':
                cookie_jar = browser_cookie3.edge(domain_name=self.domain)
            else:
                print(f"Unsupported browser: {browser_name}")
                return False

            # Update our requests session
            self.session.cookies.update(cookie_jar)

            # Test cookies by hitting an authenticated endpoint
            test_url = f"{self.base_url}/api/v1/users/self"
            response = self.session.get(test_url)
            return response.ok

        except Exception as e:
            print(f"Error loading cookies: {str(e)}")
            return False

    def get_courses(self):
        """
        Get the list of courses by scraping the /courses page HTML.

        Returns:
            list of tuples: [(course_id, course_name), ...]
        """
        response = self.session.get(f"{self.base_url}/courses")
        if not response.ok:
            print(f"Failed to fetch courses: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        courses = []

        # Canvas can show courses in different layouts. Try them:
        rows = (
                soup.find_all('tr', class_='course-list-table-row') or  # Table layout
                soup.find_all('div', class_='ic-DashboardCard') or      # Card layout
                soup.find_all('li', class_='ic-DashboardCard')          # Alternative card layout
        )

        for item in rows:
            course_id = None
            course_name = None

            # 1) Table layout
            course_span = item.find('span', attrs={'data-course-id': True})
            if course_span:
                course_id = course_span.get('data-course-id')
                name_span = item.find('span', class_='name')
                if name_span:
                    course_name = name_span.get_text(strip=True)

            # 2) Card layout
            if not course_id:
                card_link = item.find('a', attrs={'href': lambda x: x and '/courses/' in x})
                if card_link:
                    href = card_link.get('href', '')
                    try:
                        # e.g. /courses/1234 => split out "1234"
                        course_id = href.split('/courses/')[1].split('/')[0]
                        course_name = card_link.get_text(strip=True)
                    except IndexError:
                        continue

            if course_id and course_name:
                courses.append((course_id, course_name))

        return courses

    def get_course_roster(self, course_id):
        """
        Get the roster (list of enrolled users) for a specific course via Canvas API.

        Returns:
            list of dict: each dict represents a user's data in Canvas
        """
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

            # Get next-page URL from the Link header
            url = response.links.get('next', {}).get('url')
            # We only pass params the first time;
            # subsequent requests rely on the next URL
            params = {} if url else params

        return all_users

    def close(self):
        """
        Close the underlying requests session (optional).
        """
        self.session.close()
        print("Session closed.")
