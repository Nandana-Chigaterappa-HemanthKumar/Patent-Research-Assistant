import os
import pandas as pd
import xml.etree.ElementTree as ET

def extract_relevant_fields(file_path, namespaces=None):
    """
    Extract relevant fields for RAG from a single patent XML.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        data = {
            "file_name": os.path.basename(file_path),
            "file_size": os.path.getsize(file_path),  # Add file size for metadata
            "title": root.findtext("./invention-title", default="N/A"),
            "abstract": " ".join([p.text for p in root.findall("./abstract/p", namespaces) if p.text]),
            "claims": " ".join([claim.text for claim in root.findall("./claims/claim/claim-text", namespaces) if claim.text]),
            "description": " ".join([p.text for p in root.findall("./description/p", namespaces) if p.text]),
            "inventors": [
                f"{inventor.findtext('./addressbook/first-name', 'N/A', namespaces)} {inventor.findtext('./addressbook/last-name', 'N/A', namespaces)}"
                for inventor in root.findall("./us-parties/inventor", namespaces)
            ],
            "assignee": root.findtext("./assignee/addressbook/orgname", default="N/A", namespaces=namespaces),
            "application_type": root.find("./application-reference", namespaces).attrib.get("appl-type", "N/A") if root.find("./application-reference", namespaces) else "N/A",
            "patent_number": root.findtext("./publication-reference/document-id/doc-number", default="N/A", namespaces=namespaces),
            "publication_date": root.findtext("./publication-reference/document-id/date", default="N/A", namespaces=namespaces),
            "classification": root.findtext("./classification-national/main-classification", default="N/A", namespaces=namespaces),
            "citations": [citation.findtext("./document-id/doc-number", "N/A", namespaces) for citation in root.findall("./us-references-cited/us-citation", namespaces)],
            "priority_claims": [
                {
                    "doc_number": claim.findtext("./doc-number", "N/A", namespaces),
                    "date": claim.findtext("./date", "N/A", namespaces),
                }
                for claim in root.findall("./priority-claims/priority-claim", namespaces)
            ],
        }

        # Validate critical fields
        if data["title"] == "N/A" or data["patent_number"] == "N/A":
            print(f"Warning: Missing critical data in {file_path}")
        return data

    except ET.ParseError as e:
        print(f"Error parsing {file_path}: {e}")
        return {"file_name": os.path.basename(file_path), "error": str(e)}

def process_all_files_to_parquet(input_dir, output_file):
    """
    Process all XML files in the directory and save extracted data to Parquet.
    """
    extracted_data = []
    namespaces = {"ns": "http://example.com"}  # Adjust namespace if required

    total_files = 0
    skipped_files = 0

    # Loop through all XML files in the directory
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".xml"):
            total_files += 1
            file_path = os.path.join(input_dir, file_name)
            print(f"Processing: {file_name}")
            data = extract_relevant_fields(file_path, namespaces)
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

# Paths
input_dir = "/Users/nithinkeshav/Downloads/utility_patents"  # Directory with XML files
output_file = "/Users/nithinkeshav/Downloads/PRA/utility_patents.parquet"  # Output Parquet file

# Process and save
process_all_files_to_parquet(input_dir, output_file)
