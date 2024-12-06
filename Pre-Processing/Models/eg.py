import pandas as pd
import logging

# Configure logging
logging.basicConfig(filename='patent_data_extraction.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load a sample Parquet file containing one patent document
parquet_file_path = '/Users/nithinkeshav/Downloads/xml_parquet_output/document_.parquet'
patent_df = pd.read_parquet(parquet_file_path)

# Function to display available fields in the patent document
def show_available_fields(patent_df):
    logging.info("Displaying available fields in the patent document")
    print("Available fields in the patent document:")
    for column in patent_df.columns:
        print(column)

# Display the available fields
show_available_fields(patent_df)

# Extract and display relevant information
try:
    # Extracting text data
    invention_title = patent_df.get('us-patent-grant.us-bibliographic-data-grant.invention-title.#text', pd.Series(['Not available'])).iloc[0]
    description_of_drawings = patent_df.get('us-patent-grant.description.description-of-drawings.p', pd.Series(['Not available'])).iloc[0]
    claim_statement = patent_df.get('us-patent-grant.us-claim-statement', pd.Series(['Not available'])).iloc[0]
    claims = patent_df.get('us-patent-grant.claims.claim.claim-text', pd.Series(['Not available'])).tolist()

    print("\nText Data:")
    print(f"Invention Title: {invention_title}")
    print(f"Description of Drawings: {description_of_drawings}")
    print(f"Claim Statement: {claim_statement}")
    print(f"Claims: {claims}")

    # Extracting metadata
    patent_id = patent_df.get('us-patent-grant.@id', pd.Series(['Not available'])).iloc[0]
    country = patent_df.get('us-patent-grant.@country', pd.Series(['Not available'])).iloc[0]
    filing_date = patent_df.get('us-patent-grant.us-bibliographic-data-grant.application-reference.document-id.date', pd.Series(['Not available'])).iloc[0]
    publication_date = patent_df.get('us-patent-grant.@date-publ', pd.Series(['Not available'])).iloc[0]
    application_type = patent_df.get('us-patent-grant.us-bibliographic-data-grant.application-reference.@appl-type', pd.Series(['Not available'])).iloc[0]
    applicants = [{
        "orgname": patent_df.get('us-patent-grant.us-bibliographic-data-grant.us-parties.us-applicants.us-applicant.addressbook.orgname', pd.Series(['Not available'])).iloc[0],
        "city": patent_df.get('us-patent-grant.us-bibliographic-data-grant.us-parties.us-applicants.us-applicant.addressbook.address.city', pd.Series(['Not available'])).iloc[0],
        "state": patent_df.get('us-patent-grant.us-bibliographic-data-grant.us-parties.us-applicants.us-applicant.addressbook.address.state', pd.Series(['Not available'])).iloc[0],
        "country": patent_df.get('us-patent-grant.us-bibliographic-data-grant.us-parties.us-applicants.us-applicant.addressbook.address.country', pd.Series(['Not available'])).iloc[0],
    }]
    inventors = [{
        "first_name": patent_df.get('us-patent-grant.us-bibliographic-data-grant.us-parties.inventors.inventor.addressbook.first-name', pd.Series(['Not available'])).iloc[0],
        "last_name": patent_df.get('us-patent-grant.us-bibliographic-data-grant.us-parties.inventors.inventor.addressbook.last-name', pd.Series(['Not available'])).iloc[0],
        "city": patent_df.get('us-patent-grant.us-bibliographic-data-grant.us-parties.inventors.inventor.addressbook.address.city', pd.Series(['Not available'])).iloc[0],
        "state": patent_df.get('us-patent-grant.us-bibliographic-data-grant.us-parties.inventors.inventor.addressbook.address.state', pd.Series(['Not available'])).iloc[0],
        "country": patent_df.get('us-patent-grant.us-bibliographic-data-grant.us-parties.inventors.inventor.addressbook.address.country', pd.Series(['Not available'])).iloc[0],
    }]
    classifications = {
        "IPC": patent_df.get('us-patent-grant.us-bibliographic-data-grant.classification-locarno.main-classification', pd.Series(['Not available'])).iloc[0],
        "CPC": patent_df.get('us-patent-grant.us-bibliographic-data-grant.us-field-of-classification-search.classification-cpc-text', pd.Series(['Not available'])).iloc[0],
        "National": patent_df.get('us-patent-grant.us-bibliographic-data-grant.classification-national.main-classification', pd.Series(['Not available'])).iloc[0],
    }
    citations = patent_df.get('us-patent-grant.us-bibliographic-data-grant.us-references-cited.us-citation', pd.Series(['Not available'])).tolist()

    print("\nMetadata:")
    print(f"Patent ID: {patent_id}")
    print(f"Country: {country}")
    print(f"Filing Date: {filing_date}")
    print(f"Publication Date: {publication_date}")
    print(f"Application Type: {application_type}")
    print(f"Applicants: {applicants}")
    print(f"Inventors: {inventors}")
    print(f"Classifications: {classifications}")
    print(f"Citations: {citations}")

    # Extracting image data
    drawing_ids = patent_df.get('us-patent-grant.drawings.@id', pd.Series(['Not available'])).tolist()
    figures = [{
        "figure_id": figure_id,
        "description": "Description for figure " + figure_id
    } for figure_id in drawing_ids]

    print("\nImage Data:")
    print(f"Drawing IDs: {drawing_ids}")
    print(f"Figures: {figures}")

except Exception as e:
    logging.error(f"Error extracting data: {e}")
