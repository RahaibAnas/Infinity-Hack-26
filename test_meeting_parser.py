from ai.meeting_parser import generate_draft

transcript = """
Project manager Sarah says the team will build a website
for UrbanCart.

The website should have a product catalog and checkout.

Ali will handle the frontend development.

The project deadline is October 20, 2026.

Ali estimates the frontend work at 12 hours.
"""


draft = generate_draft(transcript)

print("\nAI DRAFT\n")
print(draft.model_dump_json(indent=2))
