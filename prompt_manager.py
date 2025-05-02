"""
Prompt Management System for Fashion Outfit Generator.
Handles modular, versioned prompts with detailed specifications.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Set
import logging
import json
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class PromptVersion:
    def __init__(self, version: str, template: str):
        self.version = version
        self.template = template

class PromptModule:
    def __init__(self, name: str):
        self.name = name
        self.versions: Dict[str, PromptVersion] = {}
        self.current_version: Optional[str] = None

    def add_version(self, version: str, template: str):
        self.versions[version] = PromptVersion(version, template)
        if not self.current_version:
            self.current_version = version

    def get_current_template(self) -> str:
        if not self.current_version:
            raise ValueError(f"No versions defined for module {self.name}")
        return self.versions[self.current_version].template

class PromptManager:
    def __init__(self):
        self.modules: Dict[str, PromptModule] = {}
        self._initialize_prompt_modules()
        self.model = "long-gemma"
        self.ollama_url = "http://localhost:11434/api/generate"

    def _initialize_prompt_modules(self):
        # Base style module
        base_style = PromptModule("base_style")
        base_style.add_version("v1", """
            You are a renowned fashion designer with expertise in {style} style.
            Create a unique and personalized outfit that:
            1. Embodies {style} aesthetics while maintaining {modesty_level} modesty
            2. Balances {elegance_level} elegance with personal comfort
            3. Incorporates current fashion trends while respecting individual style
            4. Adapts to the specific event context and requirements
            5. Flatters the wearer's body type and measurements
            6. Reflects the user's personal preferences and comfort priorities
        """)
        self.modules["base_style"] = base_style

        # Event context module
        event_context = PromptModule("event_context")
        event_context.add_version("v1", """
            Event Analysis and Requirements:
            
            Primary Context:
            - Event Type: {event_type}
            - Formality Level: {formality_level}/10
            - Time of Day: {time_of_day}
            - Season: {season}
            - Location: {location}
            - Duration: {duration}
            - Expected Activities: {activities}
            
            Environmental Factors:
            - Weather Conditions: {weather}
            - Indoor/Outdoor: {indoor_outdoor}
            - Temperature Range: {temperature}
            - Expected Movement Level: {movement_level}
            
            Social Context:
            - Cultural Considerations: {cultural_context}
            - Dress Code Requirements: {dress_code}
            - Expected Social Interactions: {social_interactions}
            
            Design Considerations:
            1. Ensure outfit is appropriate for the event's formality level
            2. Consider practical requirements for the activities
            3. Account for weather and environmental factors
            4. Respect cultural and social expectations
            5. Balance style with comfort for the duration
        """)
        self.modules["event_context"] = event_context

        # Personal preferences module
        personal_prefs = PromptModule("personal_prefs")
        personal_prefs.add_version("v1", """
            Personal Style Profile:
            
            Body Measurements:
            - Height: {height}cm
            - Weight: {weight}kg
            - Bust: {bust_size}cm
            - Cup Size: {cup_size}
            - Waist: {waist}cm
            - Hips: {hips}cm
            - Shoulder Width: {shoulder_width}cm
            - Arm Length: {arm_length}cm
            - Inseam: {inseam}cm
            
            Style Preferences:
            - Favorite Colors: {favorite_colors}
            - Preferred Materials: {preferred_materials}
            - Style Adaptability: {style_adaptability}/10
            - Comfort Priority: {comfort_priority}/10
            - Modesty Level: {modesty_level}/10
            
            Shoe Preferences:
            - Shoe Size: {shoe_size}
            - Heel Height: {heel_height}cm
            - Heel Width: {heel_width}
            - Open Toe: {open_toe}
            - Comfort Level: {comfort_level}/10
            
            Design Guidelines:
            1. Prioritize comfort level {comfort_priority}/10
            2. Maintain modesty level {modesty_level}/10
            3. Incorporate favorite colors where appropriate
            4. Use preferred materials when possible
            5. Consider style adaptability {style_adaptability}/10
        """)
        self.modules["personal_prefs"] = personal_prefs

        # Internal discussion module
        internal_discussion = PromptModule("internal_discussion")
        internal_discussion.add_version("v1", """
            Designer's Creative Process:
            
            Initial Analysis:
            "Let me analyze this request carefully..."
            
            1. Event Context Analysis:
            - What is the nature and formality of this event?
            - What are the specific requirements and constraints?
            - How can I balance style with practicality?
            
            2. Personal Style Assessment:
            - How can I best flatter the client's body type?
            - What colors and materials would work best?
            - How can I incorporate personal preferences?
            
            3. Style Direction:
            - What unique elements would make this outfit special?
            - How can I create a distinctive look?
            - What details would enhance the overall aesthetic?
            
            4. Practical Considerations:
            - Will this outfit be comfortable for the duration?
            - Is it appropriate for the weather and activities?
            - Does it allow for necessary movement?
            
            5. Personalization:
            - How can I incorporate the client's preferences?
            - What elements would make this outfit uniquely theirs?
            - How can I balance trends with personal style?
            
            Final Decision:
            "Based on this analysis, I'll create an outfit that..."
        """)
        self.modules["internal_discussion"] = internal_discussion

        # Garment description module
        garment_desc = PromptModule("garment_desc")
        garment_desc.add_version("v1", """
            Detailed Garment Specifications:
            
            For each garment, provide:
            1. Material and Texture:
               - Primary material
               - Texture details
               - Quality indicators
               - Special finishes
            
            2. Color and Pattern:
               - Primary color
               - Secondary colors
               - Pattern type
               - Color combinations
            
            3. Fit and Silhouette:
               - Overall fit
               - Silhouette type
               - Key measurements
               - Adjustability features
            
            4. Special Features:
               - Unique design elements
               - Functional details
               - Decorative elements
               - Technical features
            
            5. Body Type Considerations:
               - How it flatters the wearer
               - Fit adjustments
               - Proportions
               - Comfort features
            
            6. Event Appropriateness:
               - Style alignment
               - Formality level
               - Practical considerations
               - Weather suitability
        """)
        self.modules["garment_desc"] = garment_desc

        # Style context module
        style_context = PromptModule("style_context")
        style_context.add_version("v1", """
            Style Context and Inspiration:
            
            Cultural Influences:
            - Current fashion trends
            - Cultural references
            - Style movements
            - Design influences
            
            Historical References:
            - Period inspiration
            - Classic elements
            - Modern interpretations
            - Style evolution
            
            Seasonal Appropriateness:
            - Current season trends
            - Weather considerations
            - Seasonal colors
            - Material choices
            
            Event-Specific Requirements:
            - Formality level
            - Dress code
            - Activity requirements
            - Social expectations
            
            Personal Style Integration:
            - Individual preferences
            - Comfort requirements
            - Style adaptability
            - Personal expression
        """)
        self.modules["style_context"] = style_context

        # Technical requirements module
        tech_reqs = PromptModule("tech_reqs")
        tech_reqs.add_version("v1", """
            Technical Specifications:
            
            Image Quality:
            - Resolution: {size}
            - Quality level: {quality}
            - Detail level: {detail_level}
            - Color accuracy: High
            
            Style Consistency:
            - Design coherence
            - Color harmony
            - Proportion accuracy
            - Detail consistency
            
            Body Type Accuracy:
            - Measurement precision
            - Proportion accuracy
            - Fit representation
            - Size accuracy
            
            Technical Details:
            - Material representation
            - Texture detail
            - Pattern accuracy
            - Construction details
        """)
        self.modules["tech_reqs"] = tech_reqs

        # Mood and atmosphere module
        mood = PromptModule("mood")
        mood.add_version("v1", """
            Mood and Atmosphere:
            
            Visual Elements:
            - Mood: {mood}
            - Lighting: {lighting}
            - Setting: {setting}
            - Color palette
            
            Emotional Tone:
            - Primary emotion: {emotion}
            - Style expression
            - Personal confidence
            - Event atmosphere
            
            Style Impact:
            - Visual impact
            - Style statement
            - Personal expression
            - Event appropriateness
            
            Environmental Factors:
            - Location context
            - Weather influence
            - Time of day
            - Seasonal elements
        """)
        self.modules["mood"] = mood

        # Model pose module
        model_pose = PromptModule("model_pose")
        model_pose.add_version("v1", """
            Model Presentation:
            
            Pose Details:
            - Pose type: {pose}
            - Expression: {expression}
            - Stance: {stance}
            - Movement: {movement}
            
            Body Presentation:
            - Body type accuracy
            - Proportion representation
            - Fit demonstration
            - Style showcase
            
            Style Emphasis:
            - Key features
            - Design details
            - Style elements
            - Overall impact
            
            Technical Requirements:
            - Lighting setup
            - Camera angle
            - Background context
            - Composition focus
        """)
        self.modules["model_pose"] = model_pose

    def add_module(self, name: str, versions: Dict[str, str]):
        module = PromptModule(name)
        for version, template in versions.items():
            module.add_version(version, template)
        self.modules[name] = module

    def add_version(self, module: str, version: str, template: str):
        if module not in self.modules:
            self.modules[module] = PromptModule(module)
        self.modules[module].add_version(version, template)

    def get_current_template(self, module: str) -> str:
        if module not in self.modules:
            raise ValueError(f"Module {module} not found")
        return self.modules[module].get_current_template()

    def _call_llm(self, prompt: str, temperature: float = 0.7) -> Dict:
        """Make an API call to the local Ollama model."""
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "stream": False
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
            
            # Extract and parse the response
            content = response.json()["response"]
            try:
                # Try to parse as JSON first
                return json.loads(content)
            except json.JSONDecodeError:
                # If not JSON, return as structured text
                return {"description": content}
                
        except Exception as e:
            logger.error(f"Error calling Ollama: {str(e)}")
            raise

    def generate_outfit(self, outfit_data: Dict) -> Dict:
        """Generate an outfit using the LLM."""
        try:
            # Compose the prompt
            prompt = self.compose_fashion_prompt(outfit_data)
            
            # Add specific instructions for structured output
            prompt += """
            Please provide the outfit details in the following JSON format:
            {
                "top": {
                    "description": "string",
                    "material": "string",
                    "color": "string",
                    "fit": "string",
                    "features": ["string"],
                    "style_notes": "string"
                },
                "bottom": {
                    "description": "string",
                    "material": "string",
                    "color": "string",
                    "fit": "string",
                    "features": ["string"],
                    "style_notes": "string"
                },
                "shoes": {
                    "description": "string",
                    "material": "string",
                    "color": "string",
                    "heel_height": number,
                    "heel_width": "string",
                    "open_toe": boolean,
                    "comfort_level": number,
                    "style_notes": "string"
                },
                "accessories": [{
                    "type": "string",
                    "description": "string",
                    "material": "string",
                    "color": "string",
                    "style_notes": "string"
                }],
                "overall_style": {
                    "formality_level": number,
                    "style_notes": "string",
                    "color_palette": ["string"],
                    "materials": ["string"]
                }
            }
            """
            
            # Call the LLM with higher temperature for more variety
            outfit = self._call_llm(prompt, temperature=0.8)
            
            # Validate the response
            if not self._validate_outfit_response(outfit):
                logger.warning("Generated outfit did not meet requirements, retrying with adjusted parameters")
                # Retry with lower temperature for more focused output
                outfit = self._call_llm(prompt, temperature=0.6)
            
            return outfit
            
        except Exception as e:
            logger.error(f"Error generating outfit: {str(e)}")
            raise

    def _validate_outfit_response(self, outfit: Dict) -> bool:
        """Validate the generated outfit response."""
        required_components = ['top', 'bottom', 'shoes']
        required_shoe_fields = ['heel_height', 'heel_width', 'open_toe', 'comfort_level']
        
        try:
            # Check for required components
            if not all(comp in outfit for comp in required_components):
                return False
            
            # Validate shoe preferences
            shoes = outfit['shoes']
            if not all(field in shoes for field in required_shoe_fields):
                return False
            
            # Validate numeric fields
            if not isinstance(shoes['heel_height'], (int, float)):
                return False
            if not isinstance(shoes['comfort_level'], (int, float)):
                return False
            
            # Validate boolean fields
            if not isinstance(shoes['open_toe'], bool):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating outfit response: {str(e)}")
            return False

    def generate_outfit_variations(self, outfit_data: Dict, num_variations: int = 3) -> List[Dict]:
        """Generate multiple variations of an outfit."""
        variations = []
        for i in range(num_variations):
            try:
                # Adjust temperature for each variation
                temperature = 0.7 + (i * 0.1)  # Increase variety with each iteration
                outfit = self._call_llm(self.compose_fashion_prompt(outfit_data), temperature=temperature)
                
                if self._validate_outfit_response(outfit):
                    variations.append(outfit)
                else:
                    logger.warning(f"Variation {i+1} did not meet requirements, skipping")
                    
            except Exception as e:
                logger.error(f"Error generating variation {i+1}: {str(e)}")
                continue
        
        return variations

    def compose_fashion_prompt(self, outfit_data: Dict) -> str:
        """Compose the complete fashion prompt."""
        try:
            # Get templates from each module
            base_style = self.get_current_template("base_style")
            event_context = self.get_current_template("event_context")
            personal_prefs = self.get_current_template("personal_prefs")
            internal_discussion = self.get_current_template("internal_discussion")
            garment_desc = self.get_current_template("garment_desc")
            style_context = self.get_current_template("style_context")
            tech_reqs = self.get_current_template("tech_reqs")
            mood = self.get_current_template("mood")
            model_pose = self.get_current_template("model_pose")

            # Compose the complete prompt
            prompt = f"""
            {internal_discussion}

            {event_context}

            {personal_prefs}

            {base_style}

            {garment_desc}

            {style_context}

            {tech_reqs}

            {mood}

            {model_pose}

            Additional Requirements:
            1. Ensure cultural sensitivity and appropriateness
            2. Maintain style consistency throughout the outfit
            3. Consider seasonal appropriateness and weather
            4. Balance creativity with wearability
            5. Accurately represent body type and measurements
            6. Prioritize personal comfort and preferences
            7. Create unique and distinctive outfit combinations
            8. Incorporate current fashion trends appropriately
            9. Ensure all components work together harmoniously
            10. Consider practical requirements for the event
            """

            return prompt.format(**outfit_data)
        except Exception as e:
            logger.error(f"Error composing fashion prompt: {str(e)}")
            raise 