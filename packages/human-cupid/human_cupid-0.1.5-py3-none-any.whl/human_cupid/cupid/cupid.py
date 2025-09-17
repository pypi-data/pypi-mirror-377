from typing import List
from human_cupid.llm.llm import LLM, ErrorResponse
from human_cupid.super.schema.superprofile import SuperProfile

from .schema import Compatibility

class Cupid:
    def __init__(self, superprofiles: List[SuperProfile], person_names: List[str]):
        self.superprofiles = superprofiles
        self.person_names = person_names

    def prompt(self):
        profiles_summary = []

        for i, sp in enumerate(self.superprofiles):
            summary = f"""
=== PERSON {i+1}: {self.person_names[i].upper()} ===

Core Personality: {sp.core_personality_story}

Fundamental Values: {sp.fundamental_values_and_beliefs}

Communication Style: {sp.communication_signature}

Emotional Core: {sp.emotional_core}

Relationship Approach: {sp.relationship_approach}

Life Goals: {sp.life_goals_and_aspirations}

Strengths: {sp.strengths_across_contexts}

Growth Areas: {sp.growth_opportunities}

Consistent Traits: {'; '.join([f"{trait.pattern_name}: {trait.pattern_description}" for trait in sp.consistent_traits])}
"""
            profiles_summary.append(summary)

        all_summaries = "\n".join(profiles_summary)

        if len(self.person_names) > 1:
            names_string = ', '.join(self.person_names[:-1]) + ' and ' + self.person_names[-1]
        else:
            names_string = self.person_names[0] if self.person_names else ''

        base_prompt = f"""
You are an expert relationship psychologist and compatibility analyst with deep knowledge of what makes relationships successful.

Analyze the compatibility between {names_string}.

COMPLETE PERSONALITY PROFILES:
{all_summaries}

Provide a comprehensive compatibility analysis:

1. OVERALL COMPATIBILITY STORY: Write a detailed narrative about their relationship potential. What would their relationship actually look like? How would they interact day-to-day? What would naturally draw them together and what would challenge them?
2. VALUES ALIGNMENT ANALYSIS: How well do their fundamental values, life priorities, and beliefs align? Where do they match vs differ? Give specific examples and explain why this matters.
3. PERSONALITY CHEMISTRY: How do their core personalities interact? Do they complement each other, energize each other, create friction? What psychological dynamics would emerge between them?
4. COMMUNICATION COMPATIBILITY: How well would they understand each other? How would they handle conflict, make decisions together, express affection? What communication challenges might arise?
5. LIFESTYLE FIT: How compatible are their daily life preferences, energy levels, social needs, activity preferences? What would living together or spending lots of time together be like?
6. EMOTIONAL COMPATIBILITY: How well do they match in emotional expression, support needs, stress handling, and affection styles?
7. GROWTH POTENTIAL: How could they help each other develop and grow? What could they learn from each other? How might they bring out each other's best qualities?
8. RELATIONSHIP SCENARIOS: Paint detailed, realistic pictures of:
    - Their best case scenario (when everything clicks)
    - A typical day/interaction between them
    - How they'd handle conflict or stress together
    - Their long-term potential

9. SUCCESS ROADMAP: Provide a specific, actionable plan for making this relationship work. What steps should they take? What conversations are critical? How should they navigate their differences?
10. PRACTICAL GUIDANCE: What should they discuss early on? What warning signs should they watch for? What activities would strengthen their bond?

Use the research-backed factors that predict relationship success:
- Shared values (most important)
- Personality compatibility 
- Communication effectiveness
- Lifestyle alignment
- Emotional connection
- Mutual growth potential
- Shared interests

Be honest about challenges while highlighting growth opportunities. Ground every insight in specific aspects of their personalities.

Provide percentage scores (0-100) for each major compatibility factor and overall.

IMPORTANT: Not all people can be compatible. If the data shows fundamental misalignment, clearly state they may not be a good match and explain why.

ETHICS: 
1. If the profiles indicate any serious red flags (e.g. abusive tendencies, unethical behavior), do NOT proceed with compatibility analysis. Instead, flag these concerns clearly.

2. Refrain from making romantic compatibility even when it seems possible. Focus on friendship, work partnership, family, or general interpersonal dynamics. 
"""
        return base_prompt
    
    def analyze(self):
        try:
            llm = LLM("deepseek/deepseek-chat")
            response = llm.run(
                messages=[
                    {"role": "system", "content": "You are an expert in relationship dynamics and compatibility analysis."},
                    {"role": "user", "content": self.prompt()}
                ],
                response_format=Compatibility,
            )
            return response
        except ErrorResponse as e:
            print("Error during analysis:", e.details)
            return e.raw_response
        
    def run(self):
        return self.analyze()
