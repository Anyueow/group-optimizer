from linkedin_scraper import LinkedInScraper
import secrets

def main():
    EMAIL = 'anyushah@gmail.com'
    PASSWORD = secrets.Link_ps
    scraper = LinkedInScraper(EMAIL, PASSWORD, headless=True)

    if scraper.login():
        profile_url = "https://www.linkedin.com/in/armaanajoomal"
        profile = scraper.scrape_profile(profile_url)

        print("\n=== Profile Results ===")
        print("Name:", profile.name)
        print("Followers:", profile.followers)
        print("Title:", profile.title)
        print("Verified:", profile.verified)

        print("\nExperiences:")
        for exp in profile.experiences:
            print("  -", exp)

        print("\nSkills:")
        for skill in profile.skills:
            print("  -", skill)

    scraper.close()

if __name__ == "__main__":
    main()