import pytest
from fastapi.testclient import TestClient
from haute_couture_api import app, HauteCoutureProfile, MaterialDetail, FabricCombination, ColorSpec, TextureSpec, PhysicalProperties, SustainabilityInfo, CareInstructions, DigitalProperties
from material_specs import HAUTE_COUTURE_MATERIALS
import requests
import json
from datetime import datetime

client = TestClient(app)

def test_material_detail_creation():
    """Test creation of MaterialDetail with all properties."""
    color = ColorSpec(
        primary="#FFFFFF",
        secondary="#F0F0F0",
        accent="#E0E0E0",
        metallic=True,
        iridescent=True,
        opacity=0.9,
        light_reflection="subtle sheen"
    )
    
    texture = TextureSpec(
        type="smooth",
        pattern="floral",
        pattern_scale="small",
        embossed=True,
        quilted=False,
        surface_finish="lustrous"
    )
    
    physical = PhysicalProperties(
        weight=45.0,
        thickness=0.1,
        stretch=2.0,
        drape="fluid",
        breathability=8,
        thermal_properties="temperature regulating",
        sound="soft rustle"
    )
    
    sustainability = SustainabilityInfo(
        origin="France",
        certifications=["OEKO-TEX", "GOTS"],
        recycled_content=0.0,
        organic=True,
        vegan=True,
        cruelty_free=True,
        supplier="Luxury Fabrics Co."
    )
    
    care = CareInstructions(
        washing="Dry clean only",
        drying="Lay flat",
        ironing="Low heat, steam",
        dry_cleaning="Recommended",
        special_instructions=["Avoid direct sunlight", "Store in breathable container"],
        aging_characteristics="Develops patina over time"
    )
    
    digital = DigitalProperties(
        pbr_params={
            "roughness": 0.2,
            "metallic": 0.0,
            "specular": 0.5
        },
        texture_maps={
            "albedo": "silk_albedo.png",
            "normal": "silk_normal.png",
            "roughness": "silk_roughness.png"
        },
        swatch_url="https://example.com/silk_swatch",
        preview_url="https://example.com/silk_preview"
    )
    
    material = MaterialDetail(
        type="silk",
        specific_type="charmeuse",
        properties=["natural fiber", "breathable", "elegant drape"],
        usage="dresses",
        color=color,
        texture=texture,
        physical=physical,
        sustainability=sustainability,
        care=care,
        digital=digital,
        finish="natural",
        construction_notes="Requires French seams",
        quality_grade="A+",
        seasonal_suitability=["spring", "summer"],
        durability=8
    )
    
    assert material.type == "silk"
    assert material.specific_type == "charmeuse"
    assert material.color.primary == "#FFFFFF"
    assert material.texture.type == "smooth"
    assert material.physical.weight == 45.0
    assert material.sustainability.origin == "France"
    assert material.care.washing == "Dry clean only"
    assert material.digital.pbr_params["roughness"] == 0.2

def test_material_detail_from_fabric_details():
    """Test creation of MaterialDetail from fabric details."""
    fabric_details = HAUTE_COUTURE_MATERIALS['luxury_fabrics']['silk']
    material = MaterialDetail.from_fabric_details(
        fabric_type="silk",
        fabric_details=fabric_details,
        specific_type="charmeuse",
        usage="dresses"
    )
    
    assert material.type == "silk"
    assert material.specific_type == "charmeuse"
    assert material.color.primary == "#FFFFFF"
    assert material.texture.type == "smooth"
    assert material.physical.weight == 45.0
    assert material.sustainability.origin == "China"
    assert material.care.washing == "Dry clean only"
    assert material.digital.pbr_params["roughness"] == 0.2

def test_material_detail_minimal():
    """Test creation of MaterialDetail with minimal properties."""
    material = MaterialDetail(
        type="silk",
        specific_type="charmeuse",
        properties=["natural fiber"],
        usage="dresses"
    )
    
    assert material.type == "silk"
    assert material.specific_type == "charmeuse"
    assert material.color is None
    assert material.texture is None
    assert material.physical is None
    assert material.sustainability is None
    assert material.care is None
    assert material.digital is None

def test_haute_couture_design_creation():
    """Test creation of haute couture design with enhanced material properties."""
    response = client.post(
        "/api/haute-couture/design",
        json={
            "client_name": "Test Client",
            "measurements": {
                "height": 170,
                "bust": 90,
                "waist": 70,
                "hips": 95
            },
            "style_preferences": ["elegant", "modern"],
            "color_preferences": ["black", "white"],
            "fabric_preferences": ["silk", "lace"],
            "special_requirements": "Evening wear",
            "event_details": {
                "type": "gala",
                "season": "winter",
                "formality": "black tie"
            },
            "budget_range": "high",
            "timeline": "3 months"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify design structure
    assert "design_name" in data
    assert "silhouette" in data
    assert "fabric_combinations" in data
    assert "construction_techniques" in data
    
    # Verify material properties
    for fabric in data["fabric_combinations"]:
        assert "type" in fabric
        assert "specific_type" in fabric
        assert "usage" in fabric
        assert "properties" in fabric
        if fabric.get("color") is not None:
            assert "primary" in fabric["color"]
            assert "opacity" in fabric["color"]
        if fabric.get("texture") is not None:
            assert "type" in fabric["texture"]
        if fabric.get("physical") is not None:
            assert "weight" in fabric["physical"]
            assert "drape" in fabric["physical"]
        if fabric.get("sustainability") is not None:
            assert "origin" in fabric["sustainability"]
        if fabric.get("care") is not None:
            assert "washing" in fabric["care"]
        if fabric.get("digital") is not None:
            assert "pbr_params" in fabric["digital"]

def test_haute_couture_outfit_generation():
    """Test generation of haute couture outfit with enhanced material properties."""
    response = client.post(
        "/api/haute-couture/outfit",
        json={
            "client_name": "Test Client",
            "measurements": {
                "height": 170,
                "bust": 90,
                "waist": 70,
                "hips": 95
            },
            "style_preferences": ["elegant", "modern"],
            "color_preferences": ["black", "white"],
            "fabric_preferences": ["silk", "lace"],
            "special_requirements": "Evening wear",
            "event_details": {
                "type": "gala",
                "season": "winter",
                "formality": "black tie"
            },
            "budget_range": "high",
            "timeline": "3 months"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify outfit structure
    assert "design_concept" in data
    assert "materials" in data
    assert "material_costs" in data
    assert "construction_techniques" in data
    assert "quality_control" in data
    
    # Verify material properties
    for material in data["materials"]:
        assert "type" in material
        assert "specific_type" in material
        assert "usage" in material
        assert "properties" in material
        if material.get("color") is not None:
            assert "primary" in material["color"]
            assert "opacity" in material["color"]
        if material.get("texture") is not None:
            assert "type" in material["texture"]
        if material.get("physical") is not None:
            assert "weight" in material["physical"]
            assert "drape" in material["physical"]
        if material.get("sustainability") is not None:
            assert "origin" in material["sustainability"]
        if material.get("care") is not None:
            assert "washing" in material["care"]
        if material.get("digital") is not None:
            assert "pbr_params" in material["digital"]
    
    # Verify material costs
    for cost in data["material_costs"]:
        assert "fabric_type" in cost
        assert "base_cost" in cost
        assert "quality_multiplier" in cost
        assert "complexity_multiplier" in cost
        assert "total_cost" in cost

def test_material_properties_consistency():
    """Test consistency of material properties across the API."""
    # Test silk properties
    silk_details = HAUTE_COUTURE_MATERIALS['luxury_fabrics']['silk']
    silk_material = MaterialDetail.from_fabric_details(
        fabric_type="silk",
        fabric_details=silk_details,
        specific_type="charmeuse",
        usage="dresses"
    )
    
    assert silk_material.color.primary == "#FFFFFF"
    assert silk_material.color.opacity == 0.9
    assert silk_material.texture.type == "smooth"
    assert silk_material.physical.weight == 45.0
    assert silk_material.physical.drape == "fluid"
    assert silk_material.sustainability.origin == "China"
    assert silk_material.care.washing == "Dry clean only"
    assert silk_material.digital.pbr_params["roughness"] == 0.2
    
    # Test lace properties
    lace_details = HAUTE_COUTURE_MATERIALS['luxury_fabrics']['lace']
    lace_material = MaterialDetail.from_fabric_details(
        fabric_type="lace",
        fabric_details=lace_details,
        specific_type="chantilly",
        usage="overlays"
    )
    
    assert lace_material.color.primary == "#FFFFFF"
    assert lace_material.color.opacity == 0.7
    assert lace_material.texture.type == "patterned"
    assert lace_material.physical.weight == 35.0
    assert lace_material.physical.drape == "structured"
    assert lace_material.sustainability.origin == "France"
    assert lace_material.care.washing == "Hand wash"
    assert lace_material.digital.pbr_params["roughness"] == 0.4
    
    # Test velvet properties
    velvet_details = HAUTE_COUTURE_MATERIALS['luxury_fabrics']['velvet']
    velvet_material = MaterialDetail.from_fabric_details(
        fabric_type="velvet",
        fabric_details=velvet_details,
        specific_type="silk",
        usage="evening wear"
    )
    
    assert velvet_material.color.primary == "#000000"
    assert velvet_material.color.opacity == 1.0
    assert velvet_material.texture.type == "plush"
    assert velvet_material.physical.weight == 280.0
    assert velvet_material.physical.drape == "structured"
    assert velvet_material.sustainability.origin == "Italy"
    assert velvet_material.care.washing == "Dry clean only"
    assert velvet_material.digital.pbr_params["roughness"] == 0.8

def test_haute_couture_api():
    """Test the Haute Couture API endpoints."""
    base_url = "http://127.0.0.1:5002"
    
    # Test profile
    test_profile = {
        "client_name": "Test Client",
        "measurements": {
            "height": 170,
            "bust": 85,
            "waist": 65,
            "hips": 90,
            "shoulder_width": 38
        },
        "style_preferences": ["elegant", "modern"],
        "color_preferences": ["navy", "silver"],
        "fabric_preferences": ["silk", "lace"],
        "special_requirements": ["hand-sewn", "custom fit"],
        "event_details": {
            "type": "gala",
            "time": "evening",
            "venue": "grand ballroom",
            "season": "winter"
        },
        "budget_range": "luxury",
        "timeline": "3 months"
    }
    
    try:
        # Test 1: Get available materials
        print("\nTesting GET /api/haute-couture/materials")
        response = requests.get(f"{base_url}/api/haute-couture/materials")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)[:200]}...")
        else:
            print(f"Error: {response.text}")
        
        # Test 2: Get available silhouettes
        print("\nTesting GET /api/haute-couture/silhouettes")
        response = requests.get(f"{base_url}/api/haute-couture/silhouettes")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)[:200]}...")
        else:
            print(f"Error: {response.text}")
        
        # Test 3: Create a design
        print("\nTesting POST /api/haute-couture/design")
        response = requests.post(f"{base_url}/api/haute-couture/design", json=test_profile)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)[:200]}...")
        else:
            print(f"Error: {response.text}")
        
        # Test 4: Generate an outfit
        print("\nTesting POST /api/haute-couture/outfit")
        response = requests.post(f"{base_url}/api/haute-couture/outfit", json=test_profile)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)[:200]}...")
        else:
            print(f"Error: {response.text}")
        
        # Save the test results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"test_results_{timestamp}.json", "w") as f:
            json.dump({
                "test_profile": test_profile,
                "materials": requests.get(f"{base_url}/api/haute-couture/materials").json(),
                "silhouettes": requests.get(f"{base_url}/api/haute-couture/silhouettes").json(),
                "design": requests.post(f"{base_url}/api/haute-couture/design", json=test_profile).json(),
                "outfit": requests.post(f"{base_url}/api/haute-couture/outfit", json=test_profile).json()
            }, f, indent=2)
            
        print(f"\nTest results saved to test_results_{timestamp}.json")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server. Make sure it's running on http://127.0.0.1:5002")
    except Exception as e:
        print(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    test_haute_couture_api() 
