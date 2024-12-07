import pandas as pd

# Path to the Parquet file
parquet_file_path = "/Users/nithinkeshav/Downloads/PRA/utility_patents.parquet"

# Load the Parquet file into a Pandas DataFrame
try:
    df = pd.read_parquet(parquet_file_path)

    # Display basic information about the DataFrame
    print("Parquet File Loaded Successfully!")
    print("Number of Records:", len(df))
    print("Columns:", df.columns.tolist())

    # Display a sample of the data
    print("\nSample Data:")
    print(df.head())

    # Optional: Display specific columns if needed
    print("\nSample Titles and Patent Numbers:")
    print(df[["title", "patent_number"]].head())

<<<<<<< HEAD
# import xml.etree.ElementTree as ET

# # Load and parse the XML file
# tree = ET.parse('/Users/nithinkeshav/Downloads/utility_patents/document_737.xml')
# root = tree.getroot()

# # Namespace handling if needed
# namespace = {'ns': 'http://www.wipo.int/xml/ns/ipcr'}

# # Extract citations
# citations = root.findall('.//us-citation')
# print(f"Found {len(citations)} citations.")

# # Process each citation
# for idx, citation in enumerate(citations, start=1):
#     doc_number = citation.find('./patcit/document-id/doc-number')
#     kind = citation.find('./patcit/document-id/kind')
#     name = citation.find('./patcit/document-id/name')
#     date = citation.find('./patcit/document-id/date')

#     print(f"Citation {idx}:")
#     print(f"  Doc Number: {doc_number.text if doc_number is not None else 'N/A'}")
#     print(f"  Kind: {kind.text if kind is not None else 'N/A'}")
#     print(f"  Name: {name.text if name is not None else 'N/A'}")
#     print(f"  Date: {date.text if date is not None else 'N/A'}")
#     print("-" * 30)


import os
import xml.etree.ElementTree as ET

def extract_relevant_fields(file_path):
    """
    Extract relevant fields for RAG from a single patent XML, including comprehensive citation details.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Extract fields with updated paths
        data = {
            "file_name": os.path.basename(file_path),
            "file_size": os.path.getsize(file_path),
            "title": root.findtext(".//invention-title", default="N/A"),
            "abstract": " ".join([p.text for p in root.findall(".//abstract/p") if p.text]),
            "claims": " ".join([claim.text for claim in root.findall(".//claims/claim/claim-text") if claim.text]),
            "description": " ".join([p.text for p in root.findall(".//description/p") if p.text]),
            "inventors": [
                f"{inventor.findtext('./addressbook/first-name', 'N/A')} {inventor.findtext('./addressbook/last-name', 'N/A')}"
                for inventor in root.findall(".//us-parties/inventor")
            ],
            "assignee": root.findtext(".//assignee/addressbook/orgname", default="N/A"),
            "application_type": root.find(".//application-reference").attrib.get("appl-type", "N/A") if root.find(".//application-reference") else "N/A",
            "patent_number": root.findtext(".//publication-reference/document-id/doc-number", default="N/A"),
            "publication_date": root.findtext(".//publication-reference/document-id/date", default="N/A"),
            "classification": root.findtext(".//classification-national/main-classification", default="N/A"),
            "citations": [],
            "priority_claims": [
                {
                    "doc_number": claim.findtext("./doc-number", "N/A"),
                    "date": claim.findtext("./date", "N/A"),
                }
                for claim in root.findall(".//priority-claims/priority-claim")
            ],
        }

        # Extract patent citations
        patent_citations = [
            {
                "type": "patent",
                "doc_number": patcit.findtext("./document-id/doc-number", "N/A").strip(),
                "kind": patcit.findtext("./document-id/kind", "N/A").strip(),
                "name": patcit.findtext("./document-id/name", "N/A").strip(),
                "date": patcit.findtext("./document-id/date", "N/A").strip(),
                "category": citation.attrib.get("category", "N/A")  # Optional field for categories
            }
            for citation in root.findall(".//us-references-cited/us-citation")
            if (patcit := citation.find("patcit")) is not None  # Ensure patcit exists
        ]

        # Extract non-patent citations
        non_patent_citations = [
            {
                "type": "non-patent",
                "text": nplcit.findtext("./othercit", "N/A").strip(),
                "category": nplcit.attrib.get("category", "N/A")  # Optional field for categories
            }
            for citation in root.findall(".//us-references-cited/us-citation")
            if (nplcit := citation.find("nplcit")) is not None  # Ensure nplcit exists
        ]

        # Combine citations
        data["citations"].extend(patent_citations)
        data["citations"].extend(non_patent_citations)

        # Debugging: Print extracted citations
        print(f"Patent Citations: {len(patent_citations)}")
        print(f"Non-Patent Citations: {len(non_patent_citations)}")

        # Validate critical fields
        if data["title"] == "N/A" or data["patent_number"] == "N/A":
            print(f"Warning: Missing critical data in {file_path}")
        return data

    except ET.ParseError as e:
        print(f"Error parsing {file_path}: {e}")
        return {"file_name": os.path.basename(file_path), "error": str(e)}

# Test with a single file
test_file = "C:/Users/SUJATA/Downloads/utility_patents/document_986.xml"  # Update with your file path

# Extract data from the test file
extracted_data = extract_relevant_fields(test_file)

# Print the extracted data
print("Extracted Data:")
for key, value in extracted_data.items():
    if isinstance(value, list):  # For lists, print items
        print(f"{key}:")
        for item in value:
            print(f"  {item}")
    else:
        print(f"{key}: {value}")
except Exception as e:
print(f"Error reading the Parquet file: {e}")
print("Please ensure the file format is correct.")
>>>>>>> 67a772d7ab8639869b23d9e275f4eaf335995171issue here
