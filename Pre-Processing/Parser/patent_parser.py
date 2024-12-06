import boto3
import xml.etree.ElementTree as ET
from io import BytesIO
import re

def is_utility_patent(root: ET.Element) -> bool:
    """Check if the patent is a utility patent based on kind code and application type"""
    try:
        kind = root.find('.//kind').text
        appl_type = root.find('.//application-reference').get('appl-type')
        
        # Utility patents typically have kind codes B1, B2 and application type 'utility'
        is_utility = (kind.startswith('B') and appl_type == 'utility')
        return is_utility
    except AttributeError:
        return False

def parse_patents(bucket: str, key: str, max_patents: int = 5):
    """Parse utility patents from XML file"""
    try:
        print(f"Accessing file from s3://{bucket}/{key}")
        
        # Get file from S3
        s3_client = boto3.client('s3')
        response = s3_client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        
        # Split content into individual patent documents
        patent_pattern = r'(<\?xml[^>]+\?>.*?</us-patent-grant>)'
        patents = re.findall(patent_pattern, content, re.DOTALL)
        
        total_patents = len(patents)
        utility_patents = 0
        processed = 0
        
        print(f"\nFound {total_patents} total patents")
        print("Filtering for utility patents...\n")
        
        # Process each patent
        for patent_xml in patents:
            if utility_patents >= max_patents:
                break
                
            try:
                # Parse individual patent
                root = ET.fromstring(patent_xml)
                
                # Check if it's a utility patent
                if not is_utility_patent(root):
                    continue
                
                utility_patents += 1
                
                print(f"\n=== Utility Patent {utility_patents} ===")
                
                # Extract basic patent information
                doc_number = root.find('.//doc-number').text
                date = root.find('.//date').text
                kind = root.find('.//kind').text
                
                print(f"Document Number: {doc_number}")
                print(f"Publication Date: {date}")
                print(f"Kind: {kind}")
                
                # Application Information
                app_ref = root.find('.//application-reference')
                if app_ref is not None:
                    app_num = app_ref.find('.//doc-number').text
                    app_date = app_ref.find('.//date').text
                    print(f"Application Number: {app_num}")
                    print(f"Filing Date: {app_date}")
                
                # Extract title
                title = root.find('.//invention-title')
                if title is not None:
                    print(f"Title: {title.text}")
                
                # Technical Field
                tech_field = root.find('.//technical-field')
                if tech_field is not None:
                    tech_text = ' '.join(tech_field.itertext()).strip()
                    print(f"\nTechnical Field: {tech_text[:200]}...")
                
                # Extract inventors
                inventors = root.findall('.//inventor')
                if inventors:
                    print("\nInventors:")
                    for inventor in inventors:
                        first_name = inventor.find('.//first-name')
                        last_name = inventor.find('.//last-name')
                        if first_name is not None and last_name is not None:
                            print(f"- {first_name.text} {last_name.text}")
                
                # Extract assignee
                assignee = root.find('.//assignee//orgname')
                if assignee is not None:
                    print(f"\nAssignee: {assignee.text}")
                
                # Extract abstract
                abstract = root.find('.//abstract')
                if abstract is not None:
                    abstract_text = ' '.join(abstract.itertext()).strip()
                    print(f"\nAbstract: {abstract_text[:300]}...")
                
                # Extract classifications
                print("\nClassifications:")
                
                # IPC Classification
                ipc = root.find('.//classification-ipc//main-classification')
                if ipc is not None:
                    print(f"IPC: {ipc.text}")
                
                # CPC Classification
                cpc = root.find('.//classifications-cpc//classification-cpc')
                if cpc is not None:
                    main_cpc = cpc.find('.//classification-symbol')
                    if main_cpc is not None:
                        print(f"CPC: {main_cpc.text}")
                
                # Claims
                claims = root.findall('.//claim')
                if claims:
                    independent_claims = [c for c in claims if not c.findall('.//claim-ref')]
                    print(f"\nNumber of Claims: {len(claims)}")
                    print(f"Number of Independent Claims: {len(independent_claims)}")
                    if independent_claims:
                        claim_text = ' '.join(independent_claims[0].itertext()).strip()
                        print(f"\nFirst Independent Claim: {claim_text[:200]}...")
                
                print("-"*50)
                
            except ET.ParseError as e:
                print(f"Error parsing patent: {str(e)}")
                continue
        
        print(f"\nProcessed {utility_patents} utility patents out of {total_patents} total patents")
                
    except Exception as e:
        print(f"Error: {str(e)}")

# Usage
bucket = "patent-research-assistant-mv"
key = "uspto/fulltext-unzipped/2023/ipg230103/ipg230103.xml"
parse_patents(bucket, key)