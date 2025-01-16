import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import re
from typing import Optional, List, Dict
import logging
import secrets

class LinkedInScraper:
    def __init__(self, email: str, password: str, headless: bool = True):
        """
        Initialize the LinkedIn scraper with login credentials.
        
        Args:
            email (str): LinkedIn login email
            password (str): LinkedIn login password
            headless (bool): Whether to run browser in headless mode
        """
        self.email = email
        self.password = password

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Setup Selenium options
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def login(self) -> bool:
        """
        Log into LinkedIn using provided credentials.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            self.driver.get('https://www.linkedin.com/login')

            # Wait for and fill in email
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(self.email)

            # Fill in password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)

            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()

            # Wait for login to complete
            time.sleep(3)

            # Check if login was successful
            if "feed" in self.driver.current_url:
                self.logger.info("Successfully logged in to LinkedIn")
                return True
            else:
                self.logger.error("Failed to log in to LinkedIn")
                return False

        except Exception as e:
            self.logger.error(f"Login failed with error: {str(e)}")
            return False

    def scrape_profile(self, profile_url: str, keywords: Optional[List[str]] = None) -> Dict:
        """
        Scrape a LinkedIn profile page.
        
        Args:
            profile_url (str): URL of the LinkedIn profile to scrape
            keywords (list): Optional list of keywords to search for
            
        Returns:
            dict: Profile data including followers, experiences, etc.
        """
        if keywords is None:
            keywords = []

        try:
            self.driver.get(profile_url)
            time.sleep(3)  # Wait for dynamic content to load

            # Scroll to load all content
            self.scroll_page()

            # Get page source and create soup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            print(soup.prettify())

            # Extract followers
            followers = self._extract_followers(soup)

            # Extract experiences
            experiences = self._extract_experiences(soup)

            # Count keywords
            keyword_counts = self._count_keywords(soup, keywords)

            # Determine categories
            categories = self._determine_categories(soup)

            return {
                "followers": followers,
                "experiences": experiences,
                "keyword_counts": keyword_counts,
                "categories": categories
            }

        except Exception as e:
            self.logger.error(f"Profile scraping failed with error: {str(e)}")
            return {
                "followers": 0,
                "experiences": 0,
                "keyword_counts": {},
                "categories": ["Error"]
            }

    def scroll_page(self):
        """Scroll the page to load all dynamic content."""
        SCROLL_PAUSE_TIME = 1
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                break
            last_height = new_height

    def _extract_followers(self, soup: BeautifulSoup) -> int:
        """Extract number of followers from profile."""
        try:
            followers_text = soup.find('span', {'class': 'followers-count'})
            print(followers_text)
            if followers_text:
                return int(re.sub(r'[^\d]', '', followers_text.text))
            return 0
        except Exception:
            return 0

    def _extract_experiences(self, soup: BeautifulSoup) -> int:
        """Extract number of experiences from profile."""
        try:
            experience_section = soup.find('section', {'id': 'experience-section'})
            if experience_section:
                experiences = experience_section.find_all('li', {'class': 'experience-item'})
                return len(experiences)
            return 0
        except Exception:
            return 0

    def _count_keywords(self, soup: BeautifulSoup, keywords: List[str]) -> Dict[str, int]:
        """Count occurrences of keywords in profile text."""
        profile_text = soup.get_text(separator=" ").lower()
        return {
            keyword: profile_text.count(keyword.lower())
            for keyword in keywords
        }

    def _determine_categories(self, soup: BeautifulSoup) -> List[str]:
        """Determine profile categories based on content."""
        profile_text = soup.get_text(separator=" ").lower()

        categories = []
        tech_keywords = {"software", "developer", "engineer", "python", "java", "programming", "AWS", "Cloud", "Databases"}
        finance_keywords = {"finance", "banking", "investment", "trading"}
        marketing_keywords = {"marketing", "brand", "social media", "digital marketing"}

        if any(keyword in profile_text for keyword in tech_keywords):
            categories.append("Software/Tech")
        if any(keyword in profile_text for keyword in finance_keywords):
            categories.append("Finance")
        if any(keyword in profile_text for keyword in marketing_keywords):
            categories.append("Marketing")

        return categories if categories else ["Other"]

    def close(self):
        """Close the browser and clean up."""
        if self.driver:
            self.driver.quit()

# Example usage
if __name__ == "__main__":
    # Initialize scraper
    scraper = LinkedInScraper(
        email="anyushah@gmail.com",
        password= secrets.Link_ps,
        headless=True
    )

    try:
        # Login
        if scraper.login():
            # Scrape profile
            profile_data = scraper.scrape_profile(
                profile_url="https://www.linkedin.com/in/manvi-kottakota/",
                keywords=["Machine Learning", "Finance", "AI"]
            )

            # Print results
            print("\n--- LinkedIn Profile Results ---")
            print("Followers:", profile_data['followers'])
            print("Experiences:", profile_data['experiences'])
            print("Keyword Counts:", profile_data['keyword_counts'])
            print("Categories:", profile_data['categories'])
    finally:
        # Clean up
        scraper.close()