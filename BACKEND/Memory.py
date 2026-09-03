import json
import os

PERSON_DETAILS_FILE = "Data/person_details.json"
RELATIONSHIP_MEMORY_FILE = "Data/relationship_memory.json"

def get_person_details() -> dict:
    """Load stored person details from Data/person_details.json."""
    if not os.path.exists(PERSON_DETAILS_FILE):
        default_data = {
            "people": {}
        }
        os.makedirs("Data", exist_ok=True)
        with open(PERSON_DETAILS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=4)
        return default_data
    try:
        with open(PERSON_DETAILS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[MITO Memory Error] Error reading person details: {e}")
        return {"people": {}}

def add_or_update_person(name: str, relationship: str = "", details: str = ""):
    """Add or update details about a person in memory."""
    data = get_person_details()
    data["people"][name.strip().capitalize()] = {
        "relationship": relationship.strip(),
        "details": details.strip()
    }
    with open(PERSON_DETAILS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"[MITO Memory] Saved details for person: {name}")

def format_person_details_for_prompt() -> str:
    """Format stored person details for injection into the Chatbot system prompt."""
    data = get_person_details()
    people = data.get("people", {})
    if not people:
        return ""
    
    formatted = "\n--- KNOWN PEOPLE & PERSON DETAILS ---\n"
    for name, info in people.items():
        rel = info.get("relationship", "Acquaintance/Contact")
        det = info.get("details", "")
        formatted += f"- Name: {name}\n  Relationship: {rel}\n  Details: {det}\n"
    formatted += "--------------------------------------\n"
    return formatted
