import requests
import json
from datetime import datetime
from haute_couture_api import HauteCoutureProfile

def generate_outfit(profile):
    """Generate a haute couture outfit using the API."""
    response = requests.post("http://127.0.0.1:5003/api/haute-couture/outfit", json=profile)
    return response.json()

# 1. Evening Gala Gown
gala_profile = HauteCoutureProfile(
    client_name="Sophia",
    measurements={
        "height": 175,
        "bust": 88,
        "waist": 65,
        "hips": 92,
        "shoulder_width": 39
    },
    style_preferences=["dramatic", "elegant"],
    color_preferences=["emerald", "black"],
    fabric_preferences=["silk", "lace"],
    special_requirements=["hand-sewn", "custom fit", "dramatic train"],
    event_details={
        "type": "gala",
        "time": "evening",
        "venue": "grand ballroom",
        "season": "fall"
    },
    budget_range="luxury",
    timeline="3 months"
)

# 2. Bridal Couture
bridal_profile = HauteCoutureProfile(
    client_name="Isabella",
    measurements={
        "height": 168,
        "bust": 85,
        "waist": 62,
        "hips": 90,
        "shoulder_width": 38
    },
    style_preferences=["romantic", "ethereal"],
    color_preferences=["ivory", "pearl"],
    fabric_preferences=["silk", "lace"],
    special_requirements=["hand-sewn", "custom fit", "intricate beading"],
    event_details={
        "type": "bridal",
        "time": "morning",
        "venue": "cathedral",
        "season": "spring"
    },
    budget_range="luxury",
    timeline="6 months"
)

# 3. Winter Ball Gown
winter_profile = HauteCoutureProfile(
    client_name="Victoria",
    measurements={
        "height": 172,
        "bust": 86,
        "waist": 64,
        "hips": 91,
        "shoulder_width": 39
    },
    style_preferences=["opulent", "regal"],
    color_preferences=["burgundy", "gold"],
    fabric_preferences=["velvet", "silk"],
    special_requirements=["hand-sewn", "custom fit", "rich embellishments"],
    event_details={
        "type": "winter ball",
        "time": "evening",
        "venue": "palace ballroom",
        "season": "winter"
    },
    budget_range="luxury",
    timeline="4 months"
)

# 4. Spring Garden Party
spring_garden_profile = HauteCoutureProfile(
    client_name="Lady Victoria",
    measurements={
        "height": 170,
        "bust": 86,
        "waist": 64,
        "hips": 90,
        "shoulder_width": 38
    },
    style_preferences=["feminine", "delicate", "garden-inspired"],
    color_preferences=["pastel pink", "mint green", "lavender"],
    fabric_preferences=["silk", "lace", "cotton"],
    special_requirements=["light and breathable", "weather appropriate", "garden walking"],
    event_details={
        "type": "garden party",
        "time": "afternoon",
        "venue": "botanical gardens",
        "season": "spring"
    },
    budget_range="luxury",
    timeline="2 months"
)

# 5. Opera Night
opera_profile = HauteCoutureProfile(
    client_name="Eleanor",
    measurements={
        "height": 173,
        "bust": 87,
        "waist": 64,
        "hips": 93,
        "shoulder_width": 39
    },
    style_preferences=["sophisticated", "timeless"],
    color_preferences=["navy", "silver"],
    fabric_preferences=["silk", "velvet"],
    special_requirements=["hand-sewn", "custom fit", "elegant details"],
    event_details={
        "type": "opera",
        "time": "evening",
        "venue": "opera house",
        "season": "winter"
    },
    budget_range="luxury",
    timeline="3 months"
)

# Avant-Garde Couture
avant_garde_profile = HauteCoutureProfile(
    client_name="Lady Isadora",
    measurements={
        "height": 175,
        "bust": 88,
        "waist": 66,
        "hips": 92,
        "shoulder_width": 40
    },
    style_preferences=["architectural", "sculptural", "avant-garde"],
    color_preferences=["metallic silver", "gunmetal", "iridescent"],
    fabric_preferences=["neoprene", "metallic mesh", "acrylic"],
    special_requirements=["experimental", "avant-garde", "conceptual"],
    event_details={
        "type": "fashion show",
        "time": "evening",
        "venue": "contemporary art museum",
        "season": "fall"
    },
    budget_range="luxury",
    timeline="3 months"
)

# Generate all outfits
outfits = []
profiles = [
    ("Gala Gown", gala_profile),
    ("Bridal Couture", bridal_profile),
    ("Winter Ball Gown", winter_profile),
    ("Spring Garden Party", spring_garden_profile),
    ("Opera Night", opera_profile),
    ("Avant-Garde Couture", avant_garde_profile)
]

for name, profile in profiles:
    print(f"\nGenerating {name}...")
    try:
        outfit = generate_outfit(profile.model_dump())
        outfits.append((name, outfit))
        print(f"Successfully generated {name}")
    except Exception as e:
        print(f"Error generating {name}: {str(e)}")

# Save outfits to file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"haute_couture_outfits_{timestamp}.json"
with open(filename, 'w') as f:
    json.dump({name: outfit for name, outfit in outfits}, f, indent=2)
print(f"\nOutfits saved to {filename}") 