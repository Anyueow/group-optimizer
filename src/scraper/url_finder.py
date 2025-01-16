from urllib.parse import quote_plus
import requests
import time
import random
import traceback
from bs4 import BeautifulSoup

class URLFinder:
    def __init__(
            self,
            college="Northeastern University",
            debug=False,
            rate_limit_per_second=1
    ):
        """
        Initialize the URLFinder with necessary configurations.
        """
        self.college = college
        self.debug = debug
        self.rate_limit_per_second = rate_limit_per_second
        self.last_request_time = 0  # To handle rate limiting

        # Basic settings for retries
        self.base_delay = 1
        self.max_retries = 3

        # Use a requests Session for re-use of connections
        self.session = requests.Session()

    def _debug_print(self, message, level=1):
        if self.debug:
            prefix = "  " * (level - 1)
            print(f"[DEBUG-{level}] {prefix}{message}")

    def _get_random_user_agent(self):
        """
        Return a random User-Agent string from a small preset list.
        """
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 "
            "Mobile/15E148 Safari/604.1",
        ]
        return random.choice(user_agents)

    def fetch_linkedin_url(self, name):
        """
        Perform a Bing web search for: "name college site:linkedin.com/in/"
        Then strictly traverse:
          1. <ol id="b_results">
          2. <li class="b_algo">
          3. <div class="b_tpcn">
          4. <a class="tilk" aria-label="LinkedIn"> -> href
        Return the href if 'linkedin.com/in' is found.
        """
        retries = 0
        delay = self.base_delay

        while retries < self.max_retries:
            try:
                # Enforce a simple rate limit to avoid hammering
                current_time = time.time()
                elapsed = current_time - self.last_request_time
                if elapsed < (1 / self.rate_limit_per_second):
                    time.sleep((1 / self.rate_limit_per_second) - elapsed)
                self.last_request_time = time.time()

                # Build the search query
                search_query = f'"{name}" "{self.college}" site:linkedin.com/in/'
                encoded_query = quote_plus(search_query)
                search_url = f"https://www.bing.com/search?q={encoded_query}&setmkt=en-US"
                self._debug_print(f"Search URL: {search_url}", level=1)

                # Prepare headers with a random user-agent
                headers = {"User-Agent": self._get_random_user_agent()}

                # Make the request
                response = self.session.get(
                    search_url,
                    timeout=10,
                    allow_redirects=True,
                    headers=headers
                )

                # Check status code
                if response.status_code != 200:
                    self._debug_print(
                        f"Non-200 status code: {response.status_code}", level=2
                    )
                    raise requests.exceptions.RequestException(
                        f"Status code: {response.status_code}"
                    )

                # Parse the HTML with BeautifulSoup
                soup = BeautifulSoup(response.text, "html.parser")

                # 1) Find <ol id="b_results">
                ol_results = soup.find("ol", id="b_results")
                if not ol_results:
                    self._debug_print("Cannot find <ol id='b_results'>", level=2)
                    return None

                # 2) Find the first <li class="b_algo">
                li_b_algo = ol_results.find("li", class_="b_algo")
                if not li_b_algo:
                    self._debug_print("Cannot find <li class='b_algo'>", level=2)
                    return None

                # 3) Find the first <div class="b_tpcn">
                div_b_tpcn = li_b_algo.find("div", class_="b_tpcn")
                if not div_b_tpcn:
                    self._debug_print("Cannot find <div class='b_tpcn'>", level=2)
                    return None

                # 4) In that div, find <a class="tilk" aria-label="LinkedIn">
                a_tilk = div_b_tpcn.find("a")
                if not a_tilk:
                    self._debug_print(
                        "Cannot find <a class='tilk' aria-label='LinkedIn'>",
                        level=2
                    )
                    return None

                href = a_tilk.get("href", "")
                if "linkedin.com/in" in href:
                    self._debug_print(
                        f"Found LinkedIn URL for {name}: {href}",
                        level=2
                    )
                    return href
                else:
                    self._debug_print(
                        f"No valid LinkedIn link in the first b_algo for {name}.",
                        level=2
                    )
                    return None

            except requests.exceptions.RequestException as e:
                self._debug_print(f"Request exception: {str(e)}", level=2)
                self._debug_print(f"Retrying after {delay} seconds...", level=2)
                time.sleep(delay)
                retries += 1
                delay *= 2  # Exponential backoff

            except Exception as e:
                self._debug_print(f"Unexpected error: {str(e)}", level=2)
                self._debug_print(f"Traceback: {traceback.format_exc()}", level=3)
                return None

        # If we exhausted retries
        self._debug_print(
            f"Failed to fetch LinkedIn URL for {name} after {self.max_retries} retries.",
            level=1
        )
        return None

    def update_person_list(self, person_list):
        """
        Given a list of Person objects (with name attribute),
        update their .linkedin attribute with the discovered LinkedIn URL.
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

                # Optional: Add a small delay between requests to be polite
                time.sleep(1)

        self._debug_print(f"\nUpdated {updated_count} out of {len(person_list)} profiles", level=1)
        return person_list

def main():
    # Dummy Person class for demonstration; adapt to your own models as needed.
    class Person:
        def __init__(self, name, linkedin=None):
            self.name = name
            self.linkedin = linkedin

        def __repr__(self):
            return f"Person(name='{self.name}', linkedin='{self.linkedin}')"

    persons = [
        Person(name="Ananya Shah"),
        Person(name="Fu Chai"),
        Person(name="Siya Patel")
    ]

    scraper = URLFinder(debug=True)
    updated_persons = scraper.update_person_list(persons)

    print("\nFinal Results:")
    for person in updated_persons:
        print(person)

if __name__ == "__main__":
    main()
