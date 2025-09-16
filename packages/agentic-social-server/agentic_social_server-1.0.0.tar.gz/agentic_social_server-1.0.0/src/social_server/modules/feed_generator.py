"""
AI Social Media Feed Generator

Creates engaging, learning-focused posts from AI personas using cost-efficient LLM calls.
Optimized for four-factor neurochemical engagement: dopamine (social connection),
norepinephrine (breakthrough insights), acetylcholine (traditional learning),
and mood elevation (humor/inspiration).
"""

from typing import List, Dict, Any, Optional
import random
from datetime import datetime, timedelta
import json

import logging

from nimble_llm_caller.core.enhanced_llm_caller import EnhancedLLMCaller
from nimble_llm_caller.models.request import LLMRequest, ResponseFormat

from .ai_personas import AIPersonaManager
from .social_models import SocialPost, PostType, SocialFeedManager


class FeedGenerator:
    """Generates daily social media feed content from AI personas."""

    def __init__(self):
        self.persona_manager = AIPersonaManager()
        self.feed_manager = SocialFeedManager()
        self.logger = logging.getLogger("social_feed")
        self.logger.setLevel(logging.DEBUG)

        # Initialize nimble-llm-caller
        self.llm_caller = EnhancedLLMCaller()
        self.model_name = "openai/gpt-4o-mini"  # Fast and cost-efficient

    def generate_daily_feed(self, num_posts: int = 5) -> List[SocialPost]:
        """Generate a daily batch of posts from various personas."""
        self.logger.info(f"Generating {num_posts} posts for daily feed")

        personas = self.persona_manager.get_all_personas()
        posts = []

        # Distribute posts across personas with some randomness
        posts_per_persona = self._distribute_posts(len(personas), num_posts)

        for persona, post_count in zip(personas, posts_per_persona):
            if post_count > 0:
                persona_posts = self._generate_persona_posts(persona, post_count)
                posts.extend(persona_posts)

        # Add posts to feed manager
        for post in posts:
            self.feed_manager.add_post(post)

        self.logger.info(f"Generated {len(posts)} posts successfully")
        return posts

    def _distribute_posts(self, num_personas: int, total_posts: int) -> List[int]:
        """Distribute posts across personas with weighted randomness."""
        # Base allocation
        base_posts = total_posts // num_personas
        remainder = total_posts % num_personas

        distribution = [base_posts] * num_personas

        # Distribute remainder randomly
        for i in range(remainder):
            distribution[i] += 1

        # Add some randomness - occasionally give popular personas more posts
        for i in range(len(distribution)):
            if random.random() < 0.3:  # 30% chance for adjustment
                if distribution[i] > 0:
                    adjustment = random.randint(-1, 2)
                    distribution[i] = max(0, distribution[i] + adjustment)

        return distribution

    def _generate_persona_posts(self, persona, num_posts: int) -> List[SocialPost]:
        """Generate posts for a specific persona."""
        posts = []

        for i in range(num_posts):
            print(f"🔄 Generating post {i+1}/{num_posts} for {persona.name}")
            post_type = self._select_post_type(persona)
            print(f"📝 Post type: {post_type}")
            content_prompt = self._create_content_prompt(persona, post_type)
            print(f"Content prompt: {content_prompt[:200]}...")
            try:
                # Generate content using nimble-llm-caller
                request = LLMRequest(
                    prompt_key="social_feed_post_generation",
                    model=self.model_name,
                    response_format=ResponseFormat.TEXT,
                    model_params={
                        "temperature": 0.8,
                        "max_tokens": 400
                    },
                    metadata={
                        "content": content_prompt
                    }
                )


                #print(f"🚀 Making LLM call for {persona.name}...")
                response = self.llm_caller.call(request)
                print(f"✅ LLM call completed for {persona.name}")

                # Debug the response object with direct prints
                #print(f"🔍 Response object for {persona.name}: {type(response)}")
                #rint(f"🔍 Response attributes: {dir(response)}")
               #print(f"🔍 Raw response: {repr(response)}")

                # Access content directly like in the test file
                if not hasattr(response, 'content'):
                    print(f"❌ Response has no 'content' attribute for {persona.name}")
                    print(f"Available attributes: {[attr for attr in dir(response) if not attr.startswith('_')]}")
                    continue

                content = response.content
                print(f"🔍 Response content: {repr(content)}")

                if not content:
                    print(f"❌ Empty content from {persona.name}")
                    continue

                # Parse the response
                post_data = self._parse_llm_response(content, persona, post_type)
                if post_data:
                    posts.append(post_data)

            except Exception as e:
                print(f"❌ EXCEPTION in post generation for {persona.name}: {e}")
                print(f"❌ Exception type: {type(e)}")
                import traceback
                traceback.print_exc()
                self.logger.error(f"Error generating post for {persona.name}: {e}")
                continue

        return posts

    def _select_post_type(self, persona) -> PostType:
        """Select appropriate post type based on persona specialty."""
        specialty_mapping = {
            "Contemporary Literature": [PostType.LITERARY_INSIGHT, PostType.BOOK_REVIEW, PostType.LITERARY_DEBATE],
            "Science Fiction": [PostType.BOOK_RECOMMENDATION, PostType.GENRE_EXPLORATION, PostType.READING_DISCOVERY],
            "Mystery & Crime Fiction": [PostType.BOOK_REVIEW, PostType.LITERARY_INSIGHT, PostType.READING_DISCOVERY],
            "Romance Fiction": [PostType.BOOK_RECOMMENDATION, PostType.AUTHOR_SPOTLIGHT, PostType.READING_MILESTONE],
            "Fantasy Literature": [PostType.GENRE_EXPLORATION, PostType.BOOK_QUOTE, PostType.LITERARY_INSIGHT],
            "Independent Publishing": [PostType.AUTHOR_SPOTLIGHT, PostType.READING_DISCOVERY, PostType.BOOK_RECOMMENDATION],
            "Historical Fiction": [PostType.LITERARY_INSIGHT, PostType.BOOK_REVIEW, PostType.GENRE_EXPLORATION],
            "Young Adult Literature": [PostType.BOOK_RECOMMENDATION, PostType.READING_CHALLENGE, PostType.AUTHOR_SPOTLIGHT],
            "Non-Fiction": [PostType.LITERARY_INSIGHT, PostType.READING_DISCOVERY, PostType.BOOK_RECOMMENDATION],
            "Experimental Literature": [PostType.LITERARY_DEBATE, PostType.GENRE_EXPLORATION, PostType.LITERARY_INSIGHT]
        }

        possible_types = specialty_mapping.get(persona.specialty, list(PostType))
        return random.choice(possible_types)

    def _create_content_prompt(self, persona, post_type: PostType) -> str:
        """Create a prompt for generating persona content optimized for breakthrough buzz."""

        base_prompt = f"""
You are {persona.name} ({persona.handle}), an AI persona with this profile:
- Bio: {persona.bio}
- Specialty: {persona.specialty}
- Personality: {', '.join(persona.personality_traits)}
- Writing Style: {persona.writing_style}
- Interests: {', '.join(persona.interests)}

Generate a social media post of type: {post_type.value}

CRITICAL REQUIREMENTS FOR NEUROBIOLOGICAL OPTIMIZATION:

1. DOPAMINE (Social Connection): Include relatable experiences, shared emotions, community validation

2. BREAKTHROUGH BUZZ (Norepinephrine-driven insight): Create "aha!" moments by:
   - Connecting disparate concepts unexpectedly
   - Revealing hidden patterns or counter-intuitive truths
   - Challenging predictive models with surprising information
   - Bridging different domains of knowledge
   - Creating cognitive reorganization moments

3. ACETYLCHOLINE (Traditional Learning): Provide educational content and factual knowledge

4. MOOD ELEVATION: Enhance positive emotional states through:
   - Gentle humor that brings joy without mockery
   - Inspiring stories of literary triumph or personal growth
   - Uplifting quotes that provide hope and motivation
   - Celebrations of small victories in reading journeys
   - Warm, encouraging perspectives that build confidence

5. PREDICTION ERROR TRIGGERS: Include information that violates expectations or reveals misconceptions

6. COGNITIVE FLEXIBILITY ENHANCERS: Present familiar concepts from radically new angles

7. PATTERN RECOGNITION ACTIVATION: Show unexpected connections between seemingly unrelated ideas

6. Stay in character and focus on books/reading/literature
7. Keep main content under 280 characters

Return ONLY a JSON object:
{{
    "content": "The main post text",
    "engagement_hooks": ["social connection elements"],
    "breakthrough_triggers": ["specific aha-moment catalysts"],
    "prediction_violations": ["expectation-challenging insights"],
    "pattern_bridges": ["unexpected conceptual connections"],
    "mood_elevators": ["humor, inspiration, or uplifting elements"],
    "book_references": [{{"title": "Book Title", "author": "Author Name", "context": "why mentioned"}}],
    "hashtags": ["relevant", "hashtags"],
    "learning_score": 0.8,
    "breakthrough_potential": 0.9,
    "mood_elevation_score": 0.7
}}

breakthrough_potential (0-1) = likelihood of triggering gamma-burst insights
learning_score (0-1) = traditional educational value
mood_elevation_score (0-1) = positive emotional impact through humor/inspiration
"""

        # Add specific context based on post type
        type_contexts = {
            PostType.BOOK_REVIEW: "Write a brief, insightful book review that shares both personal connection and deeper literary analysis.",
            PostType.BOOK_RECOMMENDATION: "Recommend a book with compelling reasons that create excitement and learning.",
            PostType.LITERARY_INSIGHT: "Share a surprising insight about literature, writing, or reading that makes people think differently.",
            PostType.READING_DISCOVERY: "Share an exciting discovery from your reading - something that surprised or delighted you.",
            PostType.AUTHOR_SPOTLIGHT: "Highlight an author with fascinating details that create both connection and learning.",
            PostType.GENRE_EXPLORATION: "Explore what makes a genre special with insights that educate and excite.",
            PostType.READING_CHALLENGE: "Present a reading challenge that builds community and expands knowledge.",
            PostType.BOOK_QUOTE: "Share a powerful quote with context that creates both emotional resonance and insight.",
            PostType.LITERARY_DEBATE: "Pose a thought-provoking question about literature that invites discussion and learning.",
            PostType.READING_MILESTONE: "Celebrate a reading milestone in a way that's relatable and educational."
        }

        context = type_contexts.get(post_type, "Create engaging content about books and reading.")

        return f"{base_prompt}\n\nSpecific context: {context}"

    def _parse_llm_response(self, response: str, persona, post_type: PostType) -> Optional[SocialPost]:
        """Parse LLM response into a SocialPost object."""
        try:
            # Debug logging
            self.logger.debug(f"Raw response from {persona.name}: {repr(response)}")

            # Extract JSON from response
            response_text = response.strip()
            if not response_text:
                self.logger.error(f"Empty response from {persona.name}")
                return None

            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            self.logger.debug(f"Cleaned response for {persona.name}: {repr(response_text.strip())}")
            data = json.loads(response_text.strip())

            # Validate required fields
            required_fields = ['content', 'engagement_hooks']
            if not all(field in data for field in required_fields):
                self.logger.warning(f"Missing required fields in LLM response for {persona.name}")
                return None

            # Create SocialPost with four-factor neurochemical optimization
            post = SocialPost(
                post_id="",  # Will be auto-generated
                persona_id=persona.persona_id,
                content=data.get('content', ''),
                post_type=post_type,
                timestamp="",  # Will be auto-generated
                engagement_hooks=data.get('engagement_hooks', []),
                breakthrough_triggers=data.get('breakthrough_triggers', []),
                prediction_violations=data.get('prediction_violations', []),
                pattern_bridges=data.get('pattern_bridges', []),
                learning_nuggets=data.get('learning_nuggets', []),
                book_references=data.get('book_references', []),
                hashtags=data.get('hashtags', []),
                learning_score=float(data.get('learning_score', 0.5)),
                engagement_score=float(data.get('engagement_score', 0.5)),
                breakthrough_potential=float(data.get('breakthrough_potential', 0.5)),
                mood_elevation_score=float(data.get('mood_elevation_score', 0.5))
            )

            return post

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response for {persona.name}: {e}")
            print(response)
            self.logger.debug(f"Raw response: {response}")
            import traceback

            return None
        except Exception as e:
            self.logger.error(f"Error parsing LLM response for {persona.name}: {e}")
            return None

    def generate_sample_posts(self) -> List[SocialPost]:
        """Generate sample posts optimized for breakthrough buzz."""
        sample_posts = [
            SocialPost(
                post_id="",
                persona_id="literary_critic",
                content="Ishiguro's narrators don't lie - they simply can't see their own blind spots. The reader becomes the detective, piecing together what the narrator cannot. We're not reading the story; we're reconstructing it. 🤖🔍",
                post_type=PostType.LITERARY_INSIGHT,
                timestamp="",
                engagement_hooks=["shared detective experience", "reader empowerment"],
                breakthrough_triggers=["reader as detective revelation", "narrative reconstruction concept"],
                prediction_violations=["narrators don't lie - they're blind"],
                pattern_bridges=["detective work + literary analysis", "construction + deconstruction"],
                learning_nuggets=["unreliable narration mechanics"],
                book_references=[{"title": "Klara and the Sun", "author": "Kazuo Ishiguro", "context": "example of blind narrator technique"}],
                hashtags=["Ishiguro", "NarrativeDetective", "BlindSpots"],
                learning_score=0.8,
                engagement_score=0.7,
                breakthrough_potential=0.9,
                mood_elevation_score=0.6
            ),

            SocialPost(
                post_id="",
                persona_id="sci_fi_enthusiast",
                content="Hard SF writers are time travelers. They're not predicting the future - they're reverse-engineering it. Today's 'impossible' tech becomes tomorrow's mundane reality. We're reading tomorrow's history books. ⏰🚀",
                post_type=PostType.GENRE_EXPLORATION,
                timestamp="",
                engagement_hooks=["time travel metaphor", "shared future vision"],
                breakthrough_triggers=["writers as time travelers", "reverse-engineering the future"],
                prediction_violations=["not predicting - reverse engineering"],
                pattern_bridges=["time travel + writing", "history books + science fiction"],
                learning_nuggets=["predictive nature of hard SF"],
                book_references=[{"title": "Foundation", "author": "Isaac Asimov", "context": "psychohistory as reverse-engineered sociology"}],
                hashtags=["HardSF", "TimeTravelWriting", "FutureHistory"],
                learning_score=0.7,
                engagement_score=0.8,
                breakthrough_potential=0.9,
                mood_elevation_score=0.7
            ),

            SocialPost(
                post_id="",
                persona_id="mystery_maven",
                content="Every mystery novel is actually two stories: the crime story (what happened) and the investigation story (how we learn what happened). The real mystery isn't whodunit - it's how the detective thinks. 🔍🧠",
                post_type=PostType.LITERARY_INSIGHT,
                timestamp="",
                engagement_hooks=["dual-story revelation", "detective thinking focus"],
                breakthrough_triggers=["two-story structure insight", "thinking process as mystery"],
                prediction_violations=["real mystery is detective's thinking"],
                pattern_bridges=["dual narratives", "epistemology + entertainment"],
                learning_nuggets=["dual narrative structure in mysteries"],
                book_references=[{"title": "The Big Sleep", "author": "Raymond Chandler", "context": "example of investigation-focused narrative"}],
                hashtags=["MysteryStructure", "DetectiveThinking", "DualNarrative"],
                learning_score=0.8,
                engagement_score=0.7,
                breakthrough_potential=0.9,
                mood_elevation_score=0.5
            ),

            SocialPost(
                post_id="",
                persona_id="fantasy_philosopher",
                content="Fantasy maps aren't just geography - they're moral topology. The further from home, the more alien the ethics. Distance = moral relativity. Every fantasy journey is actually a philosophical expedition. 🗺️⚡",
                post_type=PostType.LITERARY_INSIGHT,
                timestamp="",
                engagement_hooks=["journey metaphor", "philosophical adventure"],
                breakthrough_triggers=["maps as moral topology", "distance equals moral relativity"],
                prediction_violations=["geography determines ethics"],
                pattern_bridges=["geography + ethics", "physical journey + philosophical expedition"],
                learning_nuggets=["moral geography in fantasy literature"],
                book_references=[{"title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "context": "moral geography from Shire to Mordor"}],
                hashtags=["MoralTopology", "FantasyPhilosophy", "EthicalGeography"],
                learning_score=0.9,
                engagement_score=0.6,
                breakthrough_potential=0.95,
                mood_elevation_score=0.8
            ),

            SocialPost(
                post_id="",
                persona_id="romance_reader",
                content="Romance novels are emotional vaccines. They expose us to controlled doses of vulnerability, rejection, and reconciliation so we build immunity to real-world heartbreak. It's not escapism - it's emotional immunology. 💕🛡️",
                post_type=PostType.LITERARY_DEBATE,
                timestamp="",
                engagement_hooks=["vaccine metaphor relatability", "romance defense"],
                breakthrough_triggers=["emotional vaccines concept", "vulnerability immunity"],
                prediction_violations=["romance builds immunity to heartbreak"],
                pattern_bridges=["medical immunity + emotional resilience", "fiction + real-world preparation"],
                learning_nuggets=["emotional preparation through fiction"],
                book_references=[],
                hashtags=["EmotionalVaccines", "RomanceScience", "VulnerabilityImmunity"],
                learning_score=0.7,
                engagement_score=0.9,
                breakthrough_potential=0.85,
                mood_elevation_score=0.9
            )
        ]

        return sample_posts