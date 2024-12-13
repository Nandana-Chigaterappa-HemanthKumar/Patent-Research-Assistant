import os
import pandas as pd
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

def process_all_files_in_folder(input_dir, output_file):
    """
    Process all XML files in a folder and save the extracted data to a Parquet file.
    """
    extracted_data = []
    total_files = 0
    skipped_files = 0

    # Iterate through all XML files in the directory
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".xml"):
            total_files += 1
            file_path = os.path.join(input_dir, file_name)
            print(f"Processing: {file_name}")
            data = extract_relevant_fields(file_path)
            if "error" in data:
                skipped_files += 1
            else:
                extracted_data.append(data)

    # Convert the data to a DataFrame
    df = pd.DataFrame(extracted_data)

    # Save to Parquet
    df.to_parquet(output_file, index=False)
    print(f"Data saved to Parquet file: {output_file}")
    print(f"Processed {total_files} files, skipped {skipped_files} due to errors.")

# Define paths
input_directory = "/Users/nithinkeshav/Downloads/utility_patents"  # Path to your folder with XML files
output_parquet_file = "/Users/nithinkeshav/Downloads/PRA/utility_patents_new.parquet"  # Output file path

# Process all files in the folder
process_all_files_in_folder(input_directory, output_parquet_file)
