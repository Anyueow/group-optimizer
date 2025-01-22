import time
import traceback
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class URLFinder:
    def __init__(
            self,
            college="Northeastern University",
            debug=False,
            rate_limit_per_second=1,
            headless=False
    ):
        """
        Initialize the URLFinder with necessary configurations.
        """
        self.college = college
        self.debug = debug
        self.rate_limit_per_second = rate_limit_per_second
        self.last_request_time = 0  # For rate limiting

        # Basic settings for retries
        self.base_delay = 1
        self.max_retries = 3

        # --(1) Initialize Selenium Driver (Safari example)--
        # Safari does not currently support a "headless" mode.
        # Make sure "Allow Remote Automation" is enabled in Safari Develop menu.
        self.driver = webdriver.Safari()  # or webdriver.Chrome(), webdriver.Edge(), etc.

        # If you wanted to do something like "headless" with Chrome, do:
        # from selenium.webdriver.chrome.options import Options
        # options = Options()
        # options.headless = True
        # self.driver = webdriver.Chrome(options=options)

    def _debug_print(self, message, level=1):
        if self.debug:
            prefix = "  " * (level - 1)
            print(f"[DEBUG-{level}] {prefix}{message}")

    def fetch_linkedin_url(self, name):
        """
        Perform a Bing web search with Selenium for:
            "name" "self.college" site:linkedin.com/in/
        Return the *first* matching LinkedIn URL found.
        """
        retries = 0
        delay = self.base_delay
        found_url = None

        while retries < self.max_retries:
            try:
                # Simple rate-limiting to avoid slamming Bing too quickly
                current_time = time.time()
                elapsed = current_time - self.last_request_time
                if elapsed < (1 / self.rate_limit_per_second):
                    time.sleep((1 / self.rate_limit_per_second) - elapsed)
                self.last_request_time = time.time()

                # Build the query
                search_query = f'"{name}" "{self.college}" site:linkedin.com/in/'
                encoded_query = quote_plus(search_query)
                search_url = f"https://www.bing.com/search?q={encoded_query}&setmkt=en-US"

                self._debug_print(f"Navigating to: {search_url}", level=1)

                # --(2) Navigate the real browser to Bing--
                self.driver.get(search_url)

                # --(3) Wait a bit for page to load--
                time.sleep(2)

                # --(4) Now get the raw HTML from Selenium's current page--
                page_source = self.driver.page_source

                # --(5) Parse with BeautifulSoup--
                soup = BeautifulSoup(page_source, "html.parser")

                # 6) Search the DOM for first li.b_algo
                ol_results = soup.find("ol", id="b_results")
                if not ol_results:
                    self._debug_print("No b_results found. Retrying...", level=1)
                    raise Exception("No b_results found")

                li_b_algo = ol_results.find("li", class_="b_algo")
                if not li_b_algo:
                    self._debug_print("No li.b_algo found. Retrying...", level=1)
                    raise Exception("No li.b_algo found")

                # 7) Grab the first <a> that has "linkedin.com/in" in it
                a_tag = li_b_algo.find("a", href=True)
                if not a_tag:
                    self._debug_print("No <a> found in the first b_algo. Retrying...", level=1)
                    raise Exception("No anchor found")

                href = a_tag["href"]
                if "linkedin.com/in" in href.lower():
                    found_url = href
                    self._debug_print(f"Found LinkedIn URL: {href}", level=1)
                    break  # exit loop if found
                else:
                    self._debug_print("No valid LinkedIn URL in the first b_algo. Retrying...", level=1)
                    raise Exception("No LinkedIn URL found in anchor")

            except Exception as e:
                self._debug_print(f"Exception: {e}", level=2)
                self._debug_print(f"Traceback: {traceback.format_exc()}", level=3)
                self._debug_print(f"Retrying after {delay} second(s)...", level=2)
                time.sleep(delay)
                retries += 1
                delay *= 2  # Exponential backoff

        return found_url

    def update_person_list(self, person_list):
        """
        Given a list of Person objects,
        update their .linkedin with the discovered LinkedIn URL.
        """
        updated_count = 0
        for person in person_list:
            self._debug_print(f"\nProcessing person: {person.name}", level=1)
            if not person.linkedin:
                linkedin_url = self.fetch_linkedin_url(person.name)
                if linkedin_url:
                    person.linkedin = linkedin_url
                    updated_count += 1
                    self._debug_print(
                        f"Successfully updated {person.name} with URL: {linkedin_url}",
                        level=1
                    )
                else:
                    self._debug_print(f"No LinkedIn URL found for {person.name}", level=1)

                # Optional: Add a small delay between scrapes
                time.sleep(1)

        self._debug_print(f"\nUpdated {updated_count} out of {len(person_list)} profiles", level=1)
        return person_list

    def close(self):
        """
        Close the Selenium browser session.
        """
        self.driver.quit()
def main():
    class Person:
        def __init__(self, name, linkedin=None):
            self.name = name
            self.linkedin = linkedin

        def __repr__(self):
            return f"Person(name='{self.name}', linkedin='{self.linkedin}')"

    persons = [
        Person(name="Fu Chai"),
        Person(name="Siya Patel"),
        Person(name="Random Nonexistent Person"),
    ]

    finder = URLFinder(debug=True)
    try:
        updated_persons = finder.update_person_list(persons)
        print("\nFinal Results:")
        for p in updated_persons:
            print(p)
    finally:
        # Always close the driver
        finder.close()

if __name__ == "__main__":
    main()
