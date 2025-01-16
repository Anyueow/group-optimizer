import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import unquote
import gzip
import io
import json
import random
class URLFinder:
    def __init__(self, college="Northeastern University", debug=False):
        self.college = college
        self.debug = debug
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",  # Explicitly handle gzip
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _debug_print(self, message, level=1):
        if self.debug:
            prefix = "  " * (level - 1)
            print(f"[DEBUG-{level}] {prefix}{message}")

    def _decode_response(self, response):
        """Properly decode the response content"""
        try:
            # Check if content is gzipped
            if response.headers.get('content-encoding') == 'gzip':
                buf = io.BytesIO(response.content)
                with gzip.GzipFile(fileobj=buf) as f:
                    content = f.read().decode('utf-8')
            else:
                content = response.content.decode('utf-8')
            return content
        except Exception as e:
            self._debug_print(f"Error decoding response: {str(e)}", 2)
            # Fallback to raw text
            return response.text

    def fetch_linkedin_url(self, name):
        try:
            search_query = f'"{name}" "{self.college}" site:linkedin.com/in/'
            search_url = f"https://www.google.com/search?q={requests.utils.quote(search_query)}&hl=en"
            self._debug_print(f"Search URL: {search_url}")

            # Add random delay
            rand = random.random()
            time.sleep(2 + rand)

            # Make the request
            response = self.session.get(
                search_url,
                timeout=10,
                allow_redirects=True,
                headers=self.headers
            )
            response.raise_for_status()

            # Decode the response
            content = self._decode_response(response)

            # Save raw HTML for debugging
            with open('debug_output.html', 'w', encoding='utf-8') as f:
                f.write(content)
            self._debug_print("Saved decoded HTML to debug_output.html")

            # Parse with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')

            # Debug response info
            self._debug_print(f"Response status code: {response.status_code}")
            self._debug_print(f"Response headers: {json.dumps(dict(response.headers), indent=2)}", 2)

            # Look for any divs with class 'g' (Google search results)
            results = soup.find_all('div', class_='g')
            self._debug_print(f"Found {len(results)} search result containers")

            for result in results:
                self._debug_print("\nAnalyzing search result:", 2)
                # Look for the title element
                title = result.find('h3', class_=['LC20lb', 'DKV0Md'])
                if title:
                    self._debug_print(f"Found title: {title.text}", 2)

                # Find all links in this result
                links = result.find_all('a')
                for link in links:
                    href = link.get('href', '')
                    self._debug_print(f"Found link: {href}", 3)

                    if 'linkedin.com/in/' in href:
                        # Clean up the URL
                        if "/url?q=" in href:
                            href = href.split("/url?q=")[1].split("&")[0]
                        href = unquote(href)

                        if not href.endswith('/'):
                            href += '/'

                        self._debug_print(f"Found LinkedIn URL: {href}")
                        return href

            # If no results found in main container, try alternative selectors
            self._debug_print("\nTrying alternative selectors...")

            # Try finding any link containing linkedin.com/in
            all_links = soup.find_all('a', href=lambda x: x and 'linkedin.com/in/' in x)
            self._debug_print(f"Found {len(all_links)} direct LinkedIn links")

            for link in all_links:
                href = link.get('href', '')
                self._debug_print(f"Processing direct link: {href}", 2)

                if 'linkedin.com/in/' in href:
                    if "/url?q=" in href:
                        href = href.split("/url?q=")[1].split("&")[0]
                    href = unquote(href)

                    if not href.endswith('/'):
                        href += '/'

                    return href

            self._debug_print("No LinkedIn URL found")
            return None

        except Exception as e:
            self._debug_print(f"Error in fetch_linkedin_url: {str(e)}")
            import traceback
            self._debug_print(f"Traceback: {traceback.format_exc()}", 2)
            return None

    def update_person_list(self, person_list):
        updated_count = 0
        for person in person_list:
            self._debug_print(f"\nProcessing person: {person.name}")
            if not person.linkedin:
                linkedin_url = self.fetch_linkedin_url(person.name)
                if linkedin_url:
                    person.linkedin = linkedin_url
                    updated_count += 1
                    self._debug_print(f"Successfully updated {person.name} with URL: {linkedin_url}")
                else:
                    self._debug_print(f"No LinkedIn URL found for {person.name}")

            time.sleep(3)

        self._debug_print(f"\nUpdated {updated_count} out of {len(person_list)} profiles")
        return person_list

def main():
    from src.objects.person import Person

    persons = [
        Person(name="Ananya Shah", email="No Email"),
        Person(name="Fu Chai", email="No Email")
    ]

    scraper = URLFinder(debug=True)
    updated_persons = scraper.update_person_list(persons)

    print("\nFinal Results:")
    for person in updated_persons:
        print(person)

if __name__ == "__main__":
    main()