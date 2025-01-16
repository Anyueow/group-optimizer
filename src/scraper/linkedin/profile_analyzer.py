import torch
import numpy as np
from transformers import pipeline, DistilBertTokenizer, DistilBertForSequenceClassification
from typing import Dict, List, Optional

class LinkedInPersonalityAnalyzer:
    def __init__(self):
        """
        Initialize the analyzer with DistilBERT model for sentiment analysis
        and various classification capabilities.
        """
        print("\n[INFO] Initializing LinkedIn Personality Analyzer...")
        try:

            self.tokenizer = DistilBertTokenizer.from_pretrained(
                "distilbert-base-uncased-finetuned-sst-2-english"
            )


            self.model = DistilBertForSequenceClassification.from_pretrained(
                "distilbert-base-uncased-finetuned-sst-2-english"
            )


            self.model.eval()

            print("[STATUS] Initializing sentiment analysis pipeline...")
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                return_all_scores=True
            )

            print("[STATUS] Loading archetype keywords...")
            self.archetype_keywords = {
                'Tech_Bro': ['software', 'engineering', 'development', 'tech', 'coding', 'programming', 'web', 'app'],
                'ML_AI_Cracked': ['machine learning', 'artificial intelligence', 'ML', 'AI', 'deep learning', 'neural', 'data science'],
                'Finance_Bro': ['finance', 'investment', 'banking', 'trading', 'portfolio', 'analyst', 'hedge fund'],
                'Business_Dud': ['marketing', 'communications', 'sales', 'business development', 'strategy', 'consulting']
            }
            print("[SUCCESS] Initialization complete!\n")

        except Exception as e:
            print(f"[ERROR] Initialization failed: {str(e)}")
            raise RuntimeError(f"Failed to initialize models: {str(e)}")

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze the sentiment of input text using the DistilBERT model."""
        if not text or text.strip() == "":
            print("[INFO] Empty text provided, skipping sentiment analysis")
            return {'NEUTRAL': 1.0}

        print(f"[STATUS] Analyzing sentiment for text: '{text[:50]}...'")
        try:
            results = self.sentiment_analyzer(text)[0]
            print("[SUCCESS] Sentiment analysis complete")
            return {score['label']: score['score'] for score in results}
        except Exception as e:
            print(f"[ERROR] Sentiment analysis failed: {str(e)}")
            raise RuntimeError(f"Sentiment analysis failed: {str(e)}")

    def calculate_extraversion_score(self, profile: Dict) -> float:
        """Calculate extraversion score based on various factors"""
        print("\n[STATUS] Calculating extraversion score...")
        score = 0.0

        # Followers contribution
        followers = profile.get('Followers', 0)
        follower_score = min(40, (followers / 1000) * 20)
        score += follower_score
        print(f"[INFO] Follower score: {follower_score:.2f}/40")

        # Leadership roles contribution
        leadership_keywords = ['president', 'director', 'lead', 'founder', 'chair']
        leadership_score = 0
        valid_experiences = 0

        for exp in profile.get('Experiences', []):
            role = exp.get('role', '')
            if not role or role.strip() == "":
                continue

            valid_experiences += 1
            if any(keyword in role.lower() for keyword in leadership_keywords):
                leadership_score += 10

        if valid_experiences > 0:
            leadership_score = min(30, leadership_score)
            score += leadership_score
            print(f"[INFO] Leadership score: {leadership_score}/30")
        else:
            print("[INFO] No valid experiences found for leadership scoring")

        # Community involvement
        community_score = 0
        valid_descriptions = 0

        for exp in profile.get('Experiences', []):
            desc = exp.get('description', '')
            if not desc or desc.strip() == "":
                continue

            valid_descriptions += 1
            if any(term in desc.lower() for term in ['community', 'team', 'group', 'club', 'organization']):
                community_score += 10

        if valid_descriptions > 0:
            community_score = min(30, community_score)
            score += community_score
            print(f"[INFO] Community involvement score: {community_score}/30")
        else:
            print("[INFO] No valid descriptions found for community scoring")

        final_score = min(100, score)
        print(f"[SUCCESS] Final extraversion score: {final_score:.2f}/100\n")
        return final_score

    def calculate_conscientiousness_score(self, profile: Dict) -> float:
        """Calculate conscientiousness score based on various factors"""
        print("\n[STATUS] Calculating conscientiousness score...")
        score = 0.0

        # Verification status
        if profile.get('Verified', False):
            score += 20
            print("[INFO] Verification score: 20/20")
        else:
            print("[INFO] Verification score: 0/20")

        # Experience completeness
        experiences = profile.get('Experiences', [])
        exp_score = 0
        valid_experiences = 0

        for exp in experiences:
            # Skip completely empty experiences
            if not any([exp.get('role'), exp.get('company'),
                        exp.get('date_range'), exp.get('description')]):
                print("[INFO] Skipping empty experience entry")
                continue

            current_exp_score = 0
            if exp.get('role') and exp.get('role').strip():
                current_exp_score += 3
            if exp.get('date_range') and exp.get('date_range').strip():
                current_exp_score += 3
            if exp.get('description') and exp.get('description').strip():
                current_exp_score += 4

            if current_exp_score > 0:
                valid_experiences += 1
                exp_score += min(10, current_exp_score)

        # Only calculate score if we have valid experiences
        if valid_experiences > 0:
            normalized_exp_score = min(40, (exp_score / valid_experiences) * 4)
            score += normalized_exp_score
            print(f"[INFO] Experience completeness score: {normalized_exp_score:.2f}/40")
        else:
            print("[INFO] No valid experiences found for scoring")

        # Duration and consistency
        duration_score = 0
        if valid_experiences >= 4:
            duration_score = 20
        elif valid_experiences >= 2:
            duration_score = 10
        score += duration_score
        print(f"[INFO] Duration and consistency score: {duration_score}/20")

        # Detailed descriptions
        desc_score = 0
        for exp in experiences:
            desc = exp.get('description', '')
            if desc and desc.strip() and len(desc.split()) >= 20:
                desc_score += 5
        score += desc_score
        print(f"[INFO] Description detail score: {desc_score}/20")

        final_score = min(100, score)
        print(f"[SUCCESS] Final conscientiousness score: {final_score:.2f}/100\n")
        return final_score

    def determine_archetype(self, profile: Dict) -> str:
        """Determine the archetype based on experiences and keywords"""
        print("\n[STATUS] Determining archetype...")
        experiences = profile.get('Experiences', [])

        # Check for "Dud energy"
        if len(experiences) < 3:
            print("[INFO] Checking for Dud energy criteria...")
            if (self.calculate_extraversion_score(profile) < 21 and
                    self.calculate_conscientiousness_score(profile) < 31):
                print("[INFO] Profile matches Dud energy criteria")
                return "Dud energy"

        # Count keyword matches
        print("[STATUS] Analyzing keyword matches for archetypes...")
        archetype_scores = {archetype: 0 for archetype in self.archetype_keywords.keys()}
        valid_experiences = 0

        for exp in experiences:
            role = exp.get('role', '')
            description = exp.get('description', '')

            # Skip if both role and description are empty
            if not role and not description:
                print("[INFO] Skipping experience with no role and description")
                continue

            # Combine available text fields
            text_parts = []
            if role and role.strip():
                text_parts.append(role)
            if description and description.strip():
                text_parts.append(description)

            if not text_parts:
                continue

            text = " ".join(text_parts).lower()
            print(f"\n[INFO] Analyzing experience: {text[:50]}...")

            sentiment = self.analyze_sentiment(text)
            sentiment_boost = 0.5 if sentiment.get('POSITIVE', 0) > 0.6 else 0
            print(f"[INFO] Sentiment boost: {sentiment_boost}")

            for archetype, keywords in self.archetype_keywords.items():
                matches = sum(1 for keyword in keywords if keyword.lower() in text)
                if matches:
                    archetype_scores[archetype] += matches * (1 + sentiment_boost)
                    print(f"[INFO] {archetype}: {matches} keyword matches")

            valid_experiences += 1

        if valid_experiences > 0:
            print("\n[INFO] Final archetype scores:")
            for archetype, score in archetype_scores.items():
                normalized_score = score / valid_experiences
                archetype_scores[archetype] = normalized_score
                print(f"- {archetype}: {normalized_score:.2f}")

            max_score = max(archetype_scores.values())
            if max_score == 0:
                print("[INFO] No strong archetype matches found, defaulting to Business_Dud")
                return "Business_Dud"

            dominant_archetype = max(archetype_scores.items(), key=lambda x: x[1])[0]
            print(f"[SUCCESS] Determined archetype: {dominant_archetype}\n")
            return dominant_archetype.replace('_', ' ')
        else:
            print("[INFO] No valid experiences found for analysis, defaulting to Business_Dud")
            return "Business_Dud"

    def analyze_profile(self, profile: Dict) -> Dict:
        """Analyze a profile and return comprehensive results"""
        print("\n[STATUS] Starting comprehensive profile analysis...")
        try:
            print("\n[STATUS] Calculating base scores...")
            extraversion = self.calculate_extraversion_score(profile)
            conscientiousness = self.calculate_conscientiousness_score(profile)
            archetype = self.determine_archetype(profile)

            print("\n[STATUS] Analyzing about section sentiment...")
            about_sentiment = {}
            if 'About' in profile and profile['About'] and profile['About'].strip():
                about_sentiment = self.analyze_sentiment(profile['About'])

            print("\n[STATUS] Compiling final analysis...")
            analysis = {
                'name': profile.get('Name', 'Unknown'),
                'extraversion_score': round(extraversion, 2),
                'conscientiousness_score': round(conscientiousness, 2),
                'archetype': archetype,
                'group_project_fit_score': round((extraversion * 0.4 + conscientiousness * 0.6), 2)
            }

            if about_sentiment:
                analysis['about_sentiment'] = about_sentiment

            print("[SUCCESS] Profile analysis complete!")
            return analysis

        except Exception as e:
            print(f"[ERROR] Profile analysis failed: {str(e)}")
            raise RuntimeError(f"Profile analysis failed: {str(e)}")

if __name__ == "__main__":
    print("\n=== LinkedIn Personality Analyzer Demo ===")
    analyzer = LinkedInPersonalityAnalyzer()

    # Test profile with edge cases
    test_profile = {
        "Name": "John Doe",
        "Followers": 500,
        "Verified": True,
        "About": "",  # Empty about section
        "Experiences": [
            {
                "role": "Senior Software Engineer",
                "company": "Tech Corp",
                "date_range": "2020-Present",
                "description": None  # Missing description
            },
            {
                "role": "Co-founder",  # Empty role
                "company": "FindHer",  # Empty company
                "date_range": "2022-2023",  # Empty date
                "description": "Built an application to help increase diversity in the workforce"
            },
            {
                "role": "Team Lead",
                "company": "Dev Inc",
                "date_range": "2018-2020",
                "description": "Leading AI projects"
            },
            {
                "role": "Teaching Assistant",
                "company": "Northeastern University",
                "date_range": "2020-2022",
                "description": "Helping teach python concepts, grade papers and guide students"
            }
        ]
    }

    print("\n[STATUS] Starting analysis of test profile...")
    results = analyzer.analyze_profile(test_profile)
    print("\n=== Analysis Results ===")
    for key, value in results.items():
        print(f"{key}: {value}")