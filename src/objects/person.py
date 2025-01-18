# person.py

class Person:
    """
    Represents a single person (or user) in the roster.
    """

    def __init__(self, name):
        self.name = name
        self.email = None
        self.linkedin = None
        self.personality_score = None
        self.details = None

    def set_linkedin_profile(self, profile_url):
        """
        Optionally store a LinkedIn profile URL.
        """
        self.linkedin = profile_url

    def set_personality_score(self, score):
        """
        Optionally store a personality score.
        """
        self.personality_score = score

    def set_details(self, details):
        """
         store a personality details - archetype, extraversion & etc

        """
        self.details = details

    def return_archetype(self, details):
        print(f"Person {self.name} is {details['archetype']}")
        return details['archetype']


    def __repr__(self):
        return (f"<Person name={self.name}, email={self.email}, linkedin={self.linkedin}>, personality_score={self.personality_score}>,"
                f"details={self.details})")
