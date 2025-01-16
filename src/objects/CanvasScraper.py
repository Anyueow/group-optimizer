# canvas_scraper.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import browser_cookie3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json
import os
# ... add any additional Selenium imports

class CanvasScraper:
    """
    A class that handles all Canvas-related scraping via Selenium.
    """

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


    def close(self):
        """
        Close the Selenium browser.
        """
        self.driver.quit()
