import time
import re
import logging
from typing import Optional, List, Dict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup

from src.scraper.linkedin.models import LinkedInProfile

class LinkedInScraper_Anyu:
    """
    OOP scraper class that logs into LinkedIn and scrapes a profile snippet
    to extract fields like name, followers, title, verified badge, experiences (with descriptions), and skills.
    """

    def __init__(self, email: str, password: str, headless: bool = True):
        """
        Initialize the LinkedInScraper with login credentials and Selenium options.

        Args:
            email (str): LinkedIn login email
            password (str): LinkedIn login password
            headless (bool): Whether to run browser in headless mode
        """
        self.email = email
        self.password = password

        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

        # Selenium driver options
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')

        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')

        self.logger.debug("Initializing WebDriver with options: %s", options.arguments)
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def login(self) -> bool:
        """
        Log into LinkedIn using provided credentials.

        Returns:
            bool: True if login was successful, False otherwise.
        """
        try:
            self.logger.info("Navigating to LinkedIn login page...")
            self.driver.get('https://www.linkedin.com/login')

            # Wait for and fill in the email/username field
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            email_field.send_keys(self.email)
            self.logger.debug("Entered email: %s", self.email)

            # Fill in password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)
            self.logger.debug("Entered password: [PROTECTED]")

            # Click the login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()

            # Wait a bit for the page to load
            time.sleep(3)
            self.logger.debug("Current URL after login attempt: %s", self.driver.current_url)

            if "feed" in self.driver.current_url or "checkpoint" in self.driver.current_url:
                self.logger.info("Successfully logged in to LinkedIn.")
                return True
            else:
                self.logger.error("Failed to log in to LinkedIn.")
                return False

        except Exception as e:
            self.logger.error("Login failed with error: %s", str(e))
            return False

    def scrape_profile(self, profile_url: str) -> LinkedInProfile:
        """
        Scrape the LinkedIn profile page at the given URL, extracting:
          - name
          - followers
          - title (headline)
          - verified (boolean)
          - experiences (with descriptions)
          - skills

        Returns:
            LinkedInProfile: an object containing the parsed data.
        """
        try:
            self.logger.info("Navigating to %s...", profile_url)
            self.driver.get(profile_url)
            time.sleep(3)  # Wait for initial load

            # Scroll to load all dynamic content (experience, skills, etc.)
            self._scroll_page()

            # Create a BeautifulSoup object
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            self.logger.debug("Page source length: %d", len(self.driver.page_source))

            # Parse fields from the snippet
            profile_data = self._parse_profile_soup(soup)
            self.logger.debug("Parsed profile data: %s", profile_data)

            return profile_data

        except Exception as e:
            self.logger.error("Profile scraping failed with error: %s", str(e))
            return LinkedInProfile()

    def _scroll_page(self):
        """
        Scroll down to load dynamic sections on the LinkedIn profile page.
        """
        SCROLL_PAUSE_TIME = 1
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        #self.logger.debug("Initial page height: %d", last_height)

        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            #self.logger.debug("New page height after scroll: %d", new_height)
            if new_height == last_height:
                break
            last_height = new_height

    def _parse_profile_soup(self, soup: BeautifulSoup) -> LinkedInProfile:
        """
        Given a BeautifulSoup object from a LinkedIn profile page,
        extract relevant fields:
          - name, followers, title, verified, experiences (with descriptions), skills
        Returns a LinkedInProfile object.
        """
        profile = LinkedInProfile()

        # -- Name --
        name_tag = soup.find("h1", class_=re.compile(r"inline\s+t-24\s+v-align-middle\s+break-words"))
        if name_tag:
            profile.name = name_tag.get_text(strip=True)
            self.logger.debug("Extracted name: %s", profile.name)

        # -- Followers --
        activity_header = soup.find("p", class_=re.compile(r"pvs-header__optional-link"))
        if activity_header:
            text = activity_header.get_text(strip=True)
            match = re.search(r"([\d,]+)\s+followers", text)
            if match:
                profile.followers = int(match.group(1).replace(",", ""))
                self.logger.debug("Extracted followers: %d", profile.followers)

        # -- Title (Headline) --
        title_tag = soup.find("div", class_=re.compile(r"text-body-medium\s+break-words"))
        if title_tag:
            profile.title = title_tag.get_text(strip=True)
            self.logger.debug("Extracted title: %s", profile.title)

        # -- Verified Badge --
        verified_badge = soup.find("svg", class_=re.compile("pv-text-details__verified-badge-icon"))
        if verified_badge:
            profile.verified = True
            self.logger.debug("Verified badge found.")

        # -- Experiences (with descriptions) --
        profile.experiences = self._extract_experiences(soup)
        self.logger.debug("Extracted experiences: %s", profile.experiences)

        # -- Skills --
        profile.skills = self._extract_skills(soup)
        self.logger.debug("Extracted skills: %s", profile.skills)

        return profile

    def _extract_experiences(self, soup: BeautifulSoup) -> List[Dict[str, Optional[str]]]:
        """
        Extract each experience (role, company, dates, description) from the "experience" section.

        Returns a list of dictionaries, e.g.:
        [
          {
            "role": "Co-President",
            "company": "NU Entrepreneurs Club",
            "date_range": "Apr 2024 - Present · 10 mos",
            "description": "Overseeing 1500+ students ..."
          },
          ...
        ]
        """
        experiences = []

        exp_section = soup.find("div", id="experience")
        if not exp_section:
            self.logger.debug("No experience section found.")
            return experiences

        exp_items = exp_section.find_next("ul").find_all("li", class_=re.compile(r"artdeco-list__item"))
        for exp_item in exp_items:
            exp_data = {
                "role": None,
                "company": None,
                "date_range": None,
                "description": None
            }

            role_tag = exp_item.find("div", class_=re.compile(r"t-bold"))
            if role_tag:
                role = role_tag.find("span", attrs={"aria-hidden": "true"})
                if role:
                    exp_data["role"] = role.get_text(strip=True)

            company_tag = exp_item.find("span", class_=re.compile(r"t-14 t-normal"))
            if company_tag:
                exp_data["company"] = company_tag.get_text(strip=True)

            date_range_tag = exp_item.find("span", class_=re.compile(r"pvs-entity__caption-wrapper"))
            if date_range_tag:
                exp_data["date_range"] = date_range_tag.get_text(strip=True)

            desc_tag = exp_item.find("div", class_=re.compile(r"inline-show-more-text"))
            if desc_tag:
                exp_data["description"] = desc_tag.get_text(strip=True)

            experiences.append(exp_data)

        return experiences

    def _extract_skills(self, soup: BeautifulSoup) -> List[str]:
        """
        Extract skill names from the "skills" section.

        Returns a list of skill strings, e.g. ["Digital Marketing", "Copywriting", ...]
        """
        skills_list = []

        skills_anchor = soup.find("div", class_=re.compile(r"QvYTNNlszJhnEXEKkmnBOtkhIHmILXpwOMOo"))
        if not skills_anchor:
            self.logger.debug("No skills anchor found.")
            return skills_list

        ul_tag = skills_anchor.find("ul", class_=re.compile(r"lOyOOfntTFbfWOJazSiFUKGPknYpbFyQbenfto"))
        if not ul_tag:
            self.logger.debug("No skills list found.")
            return skills_list

        skill_items = ul_tag.find_all("li", class_=re.compile(r"artdeco-list__item"))
        for item in skill_items:
            skill_span = item.find("span", attrs={"aria-hidden": "true"})
            if skill_span:
                skill_text = skill_span.get_text(strip=True)
                if skill_text:
                    skills_list.append(skill_text)
                    self.logger.debug("Extracted skill: %s", skill_text)

        return skills_list

    def close(self):
        """
        Close the Selenium browser session.
        """
        if self.driver:
            self.driver.quit()
            self.logger.info("Browser closed.")
