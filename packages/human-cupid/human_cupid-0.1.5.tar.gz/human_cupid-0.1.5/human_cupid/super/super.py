from typing import List

from human_cupid.llm.llm import LLM, ErrorResponse
from .schema import SuperProfile
from human_cupid.sub.schema.subprofile import Subprofile

class SuperprofileAnalyzer:
    def __init__(self, target: str, subprofiles: List[Subprofile]):
        self.target = target
        self.subprofiles = subprofiles

    def prompt(self):
        subprofile_summaries = []

        for i, sp in enumerate(self.subprofiles):
            context_summary = f"""
=== SUBPROFILE {i + 1}: {sp.context_type.upper()} CONTEXT ===

Personality: {sp.personality_narrative}

Communication Style: {sp.communication_style_analysis}

Values Expressed: {sp.values_expressed}

Emotional Patterns: {sp.emotional_patterns}

Relationship Dynamics: {sp.relationship_dynamics}

Authentic Moments: {sp.authentic_moments}

Unique to Context: {sp.unique_to_this_context}

Adaptation Patterns: {sp.adaptation_patterns}

Key Quotes: {', '.join(sp.key_supporting_quotes[:5])}

Confidence: {sp.confidence_assessment.value}
Data Notes: {sp.data_quality_notes}
"""
            subprofile_summaries.append(context_summary)
        
        all_summaries = "\n".join(subprofile_summaries)

        base_prompt = f"""
You are an expert psychologist specializing in personality synthesis and human behavior analysis.

Analyze all the context-specific personality data for {self.target} and create a comprehensive personality profile that captures their authentic self across all relationships.

SUBPROFILE DATA FROM MULTIPLE CONTEXTS:
{all_summaries}

Create a holistic personality profile by:

1. CORE PERSONALITY SYNTHESIS: What is {self.target}'s authentic self that emerges across all contexts? What are their fundamental personality traits that remain consistent?
2. FUNDAMENTAL VALUES: What deeply held values and beliefs drive their behavior across ALL relationships? Look for patterns in what they consistently prioritize, defend, or seek.
3. COMMUNICATION SIGNATURE: What's their unique communication style that persists across contexts? How do they adapt their communication for different audiences while maintaining their core approach?
4. EMOTIONAL CORE: How do they fundamentally process emotions, handle stress, express care, and cope with challenges? What patterns are consistent vs context-dependent?
5. RELATIONSHIP APPROACH: What's their overall philosophy and style for relationships? How do they build trust, maintain boundaries, show loyalty, handle conflict across different relationship types?
6. CROSS-CONTEXT PATTERNS: Identify personality traits that appear consistently across multiple contexts. What behaviors, values, or communication patterns show up regardless of the relationship?
7. CONTEXTUAL ADAPTATIONS: How do they modify their behavior for different relationships while still being authentically themselves? What drives these adaptations?
8. AUTHENTICITY ANALYSIS: When and where are they most genuine? What situations bring out their truest self vs when do they feel they need to perform?
9. GROWTH OPPORTUNITIES: Based on patterns across all contexts, where could they develop or what might be limiting their relationships?
10. RELIABILITY ASSESSMENT: How confident can we be in this analysis? What contexts or information are we missing?

Synthesize insights across ALL contexts to reveal the complete person. Ground every conclusion in evidence from multiple subprofiles.

Focus on insights that would be valuable for compatibility analysis with others.
"""
        return base_prompt

    def analyze(self):
        try:
            llm = LLM("deepseek/deepseek-chat")
            response = llm.run(
                messages=[
                    {"role": "system", "content": "You are an expert in psychological profiling and communication analysis."},
                    {"role": "user", "content": self.prompt()}
                ],
                response_format=SuperProfile,
            )
            return response
        except ErrorResponse as e:
            print("Error during superprofile analysis:", e.details)
            return e.raw_response

    def run(self):
        return self.analyze()