from typing import Optional

from human_cupid.llm.llm import LLM, ErrorResponse

from .schema import Subprofile

class SubprofileAnalyzer:
    def __init__(
            self,
            target: str, 
            conversation: list[dict[str, str]] = [], 
            profile: Optional[str] = None
    ):
        self.target = target
        self.conversation = conversation

        self.profile = None

        if profile:
            self.profile = Subprofile.model_validate_json(profile)

    def prompt(self):
        conversation_text = "\n".join(
            [f"{msg['sender']}: {msg['content']}" for msg in self.conversation]
        )
                
        base_prompt = f"""
You are an expert psychologist specializing in communication analysis and personality assessment. 

Analyze {self.target}'s personality and behavioral patterns.

CONVERSATION DATA:
{conversation_text}

Provide a comprehensive analysis focusing on:

1. PERSONALITY IN THIS CONTEXT: How do they behave, communicate, and present themselves? What's their energy, mood, and approach? Give specific examples.
2. COMMUNICATION SIGNATURE: What's unique about how they communicate here? Formality level, directness, humor style, emotional expression, response patterns. Include specific language patterns or phrases they use.
3. VALUES EXPRESSED: What matters to them based on what they say, defend, get excited about, or criticize? What priorities show up in this context?
4. EMOTIONAL PATTERNS: How do they handle different emotions here? Stress, joy, frustration, excitement? How do they seek/offer support?
5. RELATIONSHIP DYNAMICS: What role do they play in this relationship type? How do they maintain boundaries, show care, handle conflict, express needs?
6. AUTHENTICITY ANALYSIS: When do they seem most genuine vs when are they adapting their behavior? What drives their adaptations?
7. CONTEXT-SPECIFIC TRAITS: What's unique to this relationship context vs likely universal traits?

Ground every insight in specific quotes and behavioral examples. Be detailed and nuanced - this will be used for compatibility analysis.

Focus on patterns that would affect their compatibility with others in similar relationship contexts.

"""
        if self.profile:
            base_prompt += f"""
EXISTING PROFILE:
{self.profile.model_dump_json(indent=2)}

PROFILE UPDATE INSTRUCTIONS:
- The existing profile is based on prior conversations and should be treated as your foundation
- Only update traits where new conversation data provides CLEAR, CONSISTENT contradictions
- For minor variations, describe them as contextual differences rather than changing the core assessment
- Extend and refine the existing analysis rather than replacing it
- If you see genuine contradictions, acknowledge them in data_quality_notes and explain your reasoning
- Maintain consistency in communication style, core values, and fundamental personality patterns unless overwhelming evidence suggests otherwise

Your goal is to EVOLVE the profile thoughtfully, not recreate it from scratch.
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
                response_format=Subprofile,
            )

            return response
        except ErrorResponse as e:
            print("Error during analysis:", e.details)
            return e.raw_response
    
    def run(self):
        return self.analyze()