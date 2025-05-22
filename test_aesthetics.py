from fastapi.testclient import TestClient
from haute_couture_api import app
import json
from pprint import pprint

def print_section(title, content):
    print("\n" + "="*80)
    print(f"{title:^80}")
    print("="*80)
    if isinstance(content, dict) or isinstance(content, list):
        pprint(content, indent=2, width=80)
    else:
        print(content)

def test_aesthetic_quality():
    client = TestClient(app)
    
    # Create a sophisticated client profile
    profile = {
        "client_name": "Duchess of Elegance",
        "measurements": {
            "height": 175,
            "bust": 88,
            "waist": 65,
            "hips": 92,
            "shoulder_width": 38,
            "arm_length": 60
        },
        "style_preferences": [
            "avant-garde",
            "architectural",
            "ethereal",
            "sophisticated"
        ],
        "color_preferences": [
            "midnight blue",
            "champagne gold",
            "pearl white",
            "silver mist"
        ],
        "fabric_preferences": [
            "silk",
            "lace",
            "metallic mesh",
            "velvet"
        ],
        "special_requirements": [
            "hand-embroidered details",
            "sustainable materials",
            "hidden pockets",
            "transformable elements"
        ],
        "event_details": {
            "type": "royal gala",
            "occasion": "winter solstice celebration",
            "venue": "crystal palace ballroom",
            "time": "evening",
            "season": "winter",
            "dress_code": "haute couture"
        },
        "budget_range": "unlimited",
        "timeline": "2 months"
    }
    
    # Generate the outfit
    response = client.post("/api/haute-couture/outfit", json=profile)
    assert response.status_code == 200
    result = response.json()
    
    # Display the results in a beautiful format
    print_section("HAUTE COUTURE DESIGN PROPOSAL", "")
    
    print_section("CLIENT PROFILE", {
        "Name": profile["client_name"],
        "Event": profile["event_details"]["occasion"],
        "Venue": profile["event_details"]["venue"],
        "Style": ", ".join(profile["style_preferences"])
    })
    
    if result["design"]:
        print_section("DESIGN CONCEPT", {
            "Name": result["design"]["design_name"],
            "Silhouette": result["design"]["silhouette"],
            "Complexity Level": result["design"]["complexity_level"],
            "Estimated Hours": result["design"]["estimated_hours"]
        })
    
    if result["materials"]:
        print_section("MATERIALS", [
            {
                "Type": mat["type"],
                "Specific Type": mat["specific_type"],
                "Properties": mat["properties"],
                "Usage": mat["usage"],
                "Quality Grade": mat["quality_grade"] if "quality_grade" in mat else "standard"
            }
            for mat in result["materials"]
        ])
    
    if result["material_costs"]:
        print_section("MATERIAL COSTS", [
            {
                "Fabric": f"{cost['fabric_type']} ({cost['specific_type']})",
                "Base Cost": f"${cost['base_cost']:,.2f}",
                "Quality Multiplier": f"{cost['quality_multiplier']}x",
                "Complexity Multiplier": f"{cost['complexity_multiplier']}x",
                "Total Cost": f"${cost['total_cost']:,.2f}"
            }
            for cost in result["material_costs"]
        ])
    
    if result["construction_notes"]:
        print_section("CONSTRUCTION TECHNIQUES", result["construction_notes"])
    
    if result["quality_control_points"]:
        print_section("QUALITY CONTROL", result["quality_control_points"])
    
    if result.get("avant_garde_details"):
        print_section("AVANT-GARDE ELEMENTS", result["avant_garde_details"])

if __name__ == "__main__":
    test_aesthetic_quality() 