import boto3
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
import re

class PatentParser:
    def __init__(self, bucket: str, key: str):
        self.bucket = bucket
        self.key = key
        self.s3_client = boto3.client('s3')

    def get_patents_by_criteria(self, 
                              doc_number: str = None,
                              inventor_name: str = None,
                              title_keywords: List[str] = None,
                              max_results: int = 5):
        """Search patents based on various criteria"""
        try:
            print(f"Accessing file from s3://{self.bucket}/{self.key}")
            
            # Get file from S3
            try:
                response = self.s3_client.get_object(Bucket=self.bucket, Key=self.key)
                content = response['Body'].read().decode('utf-8')
            except self.s3_client.exceptions.NoSuchKey:
                print(f"Error: The key {self.key} does not exist in bucket {self.bucket}.")
                return []
            except Exception as e:
                print(f"Error: {str(e)}")
                return []

            # Split content into individual patent documents
            patent_pattern = r'(<\?xml[^>]+\?>.*?</us-patent-grant>)'
            patents = re.findall(patent_pattern, content, re.DOTALL)
            
            print(f"\nSearching through {len(patents)} patents...")
            
            results = []
            for patent_xml in patents:
                try:
                    root = ET.fromstring(patent_xml)
                    
                    # Extract patent data
                    patent_data = self.extract_patent_data(root)
                    
                    # Apply filters
                    if self.matches_criteria(patent_data, doc_number, inventor_name, title_keywords):
                        results.append(patent_data)
                        if len(results) >= max_results:
                            break

                except ET.ParseError:
                    continue  # Skip the malformed XML document

            return results
        except Exception as e:
            print(f"An error occurred during the search: {str(e)}")
            return []

    def extract_patent_data(self, root: ET.Element) -> Dict:
        """Extract relevant data from patent XML"""
        data = {
            'doc_number': self.get_text(root, './/doc-number'),
            'date': self.get_text(root, './/date'),
            'kind': self.get_text(root, './/kind'),
            'title': self.get_text(root, './/invention-title'),
            'inventors': [],
            'abstract': self.get_text(root, './/abstract'),
            'claims': self.extract_claims(root),
            'description': self.get_text(root, './/description')
        }
        
        # Extract inventors
        for inventor in root.findall('.//inventor'):
            first_name = self.get_text(inventor, './/first-name')
            last_name = self.get_text(inventor, './/last-name')
            if first_name and last_name:
                data['inventors'].append(f"{first_name} {last_name}")
                
        return data

    def get_text(self, elem: ET.Element, xpath: str) -> Optional[str]:
        """Safely extract text from XML element"""
        node = elem.find(xpath)
        return ' '.join(node.itertext()).strip() if node is not None else ""

    def extract_claims(self, root: ET.Element) -> List[str]:
        """Extract patent claims"""
        claims = []
        for claim in root.findall('.//claim'):
            claim_text = ' '.join(claim.itertext()).strip()
            claims.append(claim_text)
        return claims

    def matches_criteria(self, 
                      patent: Dict, 
                      doc_number: str = None,
                      inventor_name: str = None,
                      title_keywords: List[str] = None) -> bool:
        """Check if patent matches search criteria"""
        # Check document number
        if doc_number and doc_number != patent['doc_number']:
            return False

        # Check inventor name
        if inventor_name:
            inventor_found = any(inventor_name.lower() in inv.lower() for inv in patent['inventors'])
            if not inventor_found:
                return False

        # Check title keywords
        if title_keywords and patent['title']:
            title_lower = patent['title'].lower()
            if not all(kw.lower() in title_lower for kw in title_keywords):
                return False

        return True

def display_patent(patent: Dict):
    """Display patent information in a formatted way"""
    print("\n" + "="*50)
    print(f"Patent: {patent['doc_number']}")
    print(f"Date: {patent['date']}")
    print(f"Kind: {patent['kind']}")

    if patent['title']:
        print(f"\nTitle: {patent['title']}")

    if patent['inventors']:
        print("\nInventors:")
        for inventor in patent['inventors']:
            print(f"- {inventor}")

    if patent['abstract']:
        print(f"\nAbstract: {patent['abstract'][:300]}...")

    if patent['claims']:
        print(f"\nNumber of Claims: {len(patent['claims'])}")
        print("First Claim:", patent['claims'][0][:200], "...")
        
    print("="*50)

def main():
    # Initialize parser
    parser = PatentParser(
        bucket="patent-research-assistant-mv",
        key="uspto/fulltext-unzipped/2023/ipg230103/ipg230103.xml"
    )

    while True:
        print("\nPatent Search Options:")
        print("1. Search by Patent Number")
        print("2. Search by Inventor Name")
        print("3. Search by Title Keywords")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == '1':
            doc_number = input("Enter patent number (e.g., D1008603): ").strip()
            results = parser.get_patents_by_criteria(doc_number=doc_number)

        elif choice == '2':
            inventor = input("Enter inventor name: ").strip()
            results = parser.get_patents_by_criteria(inventor_name=inventor)

        elif choice == '3':
            keywords = input("Enter title keywords (space-separated): ").strip().split()
            results = parser.get_patents_by_criteria(title_keywords=keywords)

        elif choice == '4':
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")
            continue

        # Display results
        if results:
            print(f"\nFound {len(results)} matching patents:")
            for patent in results:
                display_patent(patent)
        else:
            print("\nNo matching patents found.")

if __name__ == "__main__":
    main()