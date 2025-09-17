from enum import Enum
from typing import List
from pydantic import Field
from human_cupid.utils.model import Model
from human_cupid.utils.schemas import ConfidenceLevel

class Subprofile(Model):
    id: str = Field("ID_PLACEHOLDER")
    context_type: str = Field(description="family, friends, work, social_media, etc.")
    personality_narrative: str = Field(description="Comprehensive description of how they behave and communicate in this context, with specific examples")
    communication_style_analysis: str = Field(description="Detailed analysis of their communication patterns: formality, directness, humor, emotional expression, response patterns")
    values_expressed: str = Field(description="What values and priorities show up in this context, with specific quotes and examples")
    emotional_patterns: str = Field(description="How they handle emotions, stress, conflict, and joy in this context")
    relationship_dynamics: str = Field(description="What role they play, how they give/receive support, handle boundaries, show care")
    interests_and_activities: str = Field(description="Hobbies, entertainment preferences, activities mentioned in this context")
    authentic_moments: str = Field(description="When they seem most genuine vs when they seem to be performing or adapting")
    unique_to_this_context: str = Field(description="Behaviors or traits that only appear in this relationship type")
    adaptation_patterns: str = Field(description="How they adapt their behavior for this specific relationship context")
    key_supporting_quotes: List[str] = Field(description="Specific quotes that reveal character in this context",)
    behavioral_examples: List[str] = Field(description="Specific behaviors or incidents that show personality patterns")
    confidence_assessment: ConfidenceLevel = Field(description="How confident this analysis is based on available data")
    data_quality_notes: str = Field(description="Assessment of data richness, time span, conversation depth, any limitations")
