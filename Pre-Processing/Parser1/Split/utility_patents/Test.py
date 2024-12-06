import xml.etree.ElementTree as ET
import os

def extract_relevant_fields_with_logging(file_path):
    """
    Extract relevant fields for RAG with improved XPath and detailed error logging.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Detailed logging
        print(f"Processing File: {file_path}")
        print(f"Root Tag: {root.tag}")

        data = {
            "file_name": os.path.basename(file_path),
            "title": root.findtext(".//invention-title", default="N/A"),
            "abstract": " ".join([p.text for p in root.findall(".//abstract/p") if p.text]),
            "claims": " ".join([claim.text for claim in root.findall(".//claims/claim/claim-text") if claim.text]),
            "description": " ".join([p.text for p in root.findall(".//description/p") if p.text]),
            "inventors": [
                f"{inventor.findtext('./addressbook/first-name', 'N/A')} {inventor.findtext('./addressbook/last-name', 'N/A')}"
                for inventor in root.findall(".//us-parties/inventors/inventor")
            ],
            "assignee": root.findtext(".//assignees/assignee/addressbook/orgname", default="N/A"),
            "application_type": root.find(".//application-reference").attrib.get("appl-type", "N/A") if root.find(".//application-reference") else "N/A",
            "patent_number": root.findtext(".//publication-reference/document-id/doc-number", default="N/A"),
            "publication_date": root.findtext(".//publication-reference/document-id/date", default="N/A"),
            "classification": root.findtext(".//classifications-ipcr/classification-ipcr/main-group", default="N/A"),
            "citations": [citation.findtext("./document-id/doc-number", "N/A") for citation in root.findall(".//us-references-cited/us-citation")],
            "priority_claims": [
                {
                    "doc_number": claim.findtext("./doc-number", "N/A"),
                    "date": claim.findtext("./date", "N/A"),
                }
                for claim in root.findall(".//priority-claims/priority-claim")
            ],
        }

        # Validation and logging for critical fields
        if data["title"] == "N/A":
            print("Warning: Title is missing or failed to parse.")
        if data["patent_number"] == "N/A":
            print("Warning: Patent number is missing or failed to parse.")
        if data["publication_date"] == "N/A":
            print("Warning: Publication date is missing or failed to parse.")
        if data["classification"] == "N/A":
            print("Warning: Classification is missing or failed to parse.")

        return data

    except ET.ParseError as e:
        print(f"XML Parse Error in file {file_path}: {e}")
        return {"file_name": os.path.basename(file_path), "error": str(e)}

# Path to the test XML file
file_path = "/Users/nithinkeshav/Downloads/utility_patents/document_737.xml"  # Replace with actual path

# Extract data from the test file
extracted_data = extract_relevant_fields_with_logging(file_path)

# Display the extracted data
print("\nExtracted Data:")
print(extracted_data)
