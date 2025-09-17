from typing import Dict, List
from pydantic import Field
from human_cupid.utils.model import Model
from human_cupid.utils.schemas import ConfidenceLevel

class CrossContextPattern(Model):
    pattern_name: str = Field(description="Brief name for this pattern")
    pattern_description: str = Field(description="Detailed explanation of this consistent personality trait")
    evidence_across_contexts: Dict[str, List[str]] = Field(description="Evidence from different contexts")
    consistency_rating: ConfidenceLevel = Field(description="How consistently this pattern appears across contexts")

class SuperProfile(Model):
    id: str = Field("ID_PLACEHOLDER")    
    contexts_analyzed: List[str] = Field(description="Which contexts contributed to this profile")
    core_personality_story: str = Field(description="The authentic self that emerges across all contexts - who they really are underneath adaptations")
    fundamental_values_and_beliefs: str = Field(description="Deep values that drive behavior across all relationships, with evidence from multiple contexts")
    communication_signature: str = Field(description="Their unique communication style that persists across contexts, plus how they adapt for different audiences")
    emotional_core: str = Field(description="How they process emotions, handle stress, express care, and cope with challenges across all relationships")
    relationship_approach: str = Field(description="Their overall approach to relationships - how they connect, trust, maintain boundaries, show loyalty")
    life_goals_and_aspirations: str = Field(description="What they're working toward in life based on patterns across all contexts")
    consistent_traits: List[CrossContextPattern] = Field(description="Personality traits that appear consistently across contexts")
    contextual_adaptations: str = Field(description="How they modify their behavior for different relationships while maintaining core self")
    authenticity_analysis: str = Field(description="When and where they're most genuine vs when they adapt, and what drives these adaptations")
    strengths_across_contexts: str = Field(description="What they do exceptionally well in relationships and life")
    growth_opportunities: str = Field(description="Areas where they could develop or patterns that might limit them")
    potential_blind_spots: str = Field(description="Things they might not realize about themselves or how others perceive them")
    profile_confidence: ConfidenceLevel = Field(description="Overall confidence in this personality assessment")
    data_completeness: str = Field(description="What contexts or time periods are well-covered vs missing")
    recommendations_for_improvement: List[str] = Field(description="What additional data would make this profile more accurate",)
    interests_and_activities: str = Field(description="Hobbies, entertainment preferences, activities")