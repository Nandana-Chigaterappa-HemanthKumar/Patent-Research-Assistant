import boto3
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
import re
import textwrap

class UtilityPatentParser:
    def __init__(self, bucket: str, key: str):
        self.bucket = bucket
        self.key = key
        self.s3_client = boto3.client('s3')

    def get_patents_by_criteria(self, 
                              doc_number: str = None,
                              inventor_name: str = None,
                              title_keywords: List[str] = None,
                              max_results: int = 5):
        try:
            print(f"Accessing file from s3://{self.bucket}/{self.key}")
            
            try:
                response = self.s3_client.get_object(Bucket=self.bucket, Key=self.key)
                content = response['Body'].read().decode('utf-8')
            except self.s3_client.exceptions.NoSuchKey:
                print(f"Error: The key {self.key} does not exist in bucket {self.bucket}.")
                return []
            except Exception as e:
                print(f"Error: {str(e)}")
                return []

            patent_pattern = r'(<\?xml[^>]+\?>.*?</us-patent-grant>)'
            patents = re.findall(patent_pattern, content, re.DOTALL)
            
            print(f"\nSearching through {len(patents)} patents...")
            
            results = []
            for patent_xml in patents:
                try:
                    root = ET.fromstring(patent_xml)
                    
                    # Check if it's a utility patent
                    kind_code = root.find('.//kind').text
                    if not kind_code.startswith(('B', 'E')):  # Utility patents typically have B1, B2, E1, E2 kind codes
                        continue
                        
                    patent_data = self.extract_utility_patent_data(root)
                    
                    if self.matches_criteria(patent_data, doc_number, inventor_name, title_keywords):
                        results.append(patent_data)
                        if len(results) >= max_results:
                            break

                except ET.ParseError as e:
                    continue

            return results
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return []

    def extract_utility_patent_data(self, root: ET.Element) -> Dict:
        """Extract technical data specific to utility patents"""
        data = {
            'basic_info': {
                'doc_number': self.get_text(root, './/doc-number'),
                'date': self.get_text(root, './/date'),
                'kind': self.get_text(root, './/kind'),
                'title': self.get_text(root, './/invention-title'),
            },
            'inventors': self.extract_inventors(root),
            'assignee': self.extract_assignee(root),
            'classifications': self.extract_classifications(root),
            'technical_info': {
                'abstract': self.get_text(root, './/abstract'),
                'background': self.get_text(root, './/background-art'),
                'summary': self.get_text(root, './/summary-of-invention'),
                'detailed_description': self.get_text(root, './/description'),
                'claims': self.extract_claims(root),
            },
            'application_info': {
                'app_number': self.get_text(root, './/application-reference//doc-number'),
                'app_date': self.get_text(root, './/application-reference//date'),
                'app_type': root.find('.//application-reference').get('appl-type') if root.find('.//application-reference') is not None else None,
            },
            'priority_info': self.extract_priority_claims(root),
            'citations': self.extract_citations(root)
        }
        return data

    def extract_inventors(self, root: ET.Element) -> List[Dict]:
        inventors = []
        for inventor in root.findall('.//inventor'):
            inv_data = {
                'name': f"{self.get_text(inventor, './/first-name')} {self.get_text(inventor, './/last-name')}",
                'city': self.get_text(inventor, './/city'),
                'state': self.get_text(inventor, './/state'),
                'country': self.get_text(inventor, './/country')
            }
            inventors.append(inv_data)
        return inventors

    def extract_assignee(self, root: ET.Element) -> Dict:
        assignee = root.find('.//assignee')
        if assignee is not None:
            return {
                'name': self.get_text(assignee, './/orgname') or 
                       f"{self.get_text(assignee, './/first-name')} {self.get_text(assignee, './/last-name')}",
                'city': self.get_text(assignee, './/city'),
                'state': self.get_text(assignee, './/state'),
                'country': self.get_text(assignee, './/country')
            }
        return {}

    def extract_classifications(self, root: ET.Element) -> Dict:
        return {
            'ipc': [self.get_text(ipc, './/main-classification') 
                   for ipc in root.findall('.//classification-ipc')],
            'cpc': [self.get_text(cpc, './/main-classification') 
                   for cpc in root.findall('.//classification-cpc')],
            'national': [self.get_text(nat, './/main-classification') 
                        for nat in root.findall('.//classification-national')]
        }

    def extract_claims(self, root: ET.Element) -> List[Dict]:
        claims = []
        for claim in root.findall('.//claim'):
            claims.append({
                'number': claim.get('num', ''),
                'text': ' '.join(claim.itertext()).strip(),
                'type': 'independent' if not claim.findall('.//claim-ref') else 'dependent'
            })
        return claims

    def extract_priority_claims(self, root: ET.Element) -> List[Dict]:
        priority_claims = []
        for claim in root.findall('.//priority-claim'):
            priority_claims.append({
                'country': self.get_text(claim, './/country'),
                'date': self.get_text(claim, './/date'),
                'number': self.get_text(claim, './/doc-number')
            })
        return priority_claims

    def extract_citations(self, root: ET.Element) -> List[Dict]:
        citations = []
        for citation in root.findall('.//us-citation'):
            patcit = citation.find('.//patcit')
            if patcit is not None:
                citations.append({
                    'type': 'patent',
                    'doc_number': self.get_text(patcit, './/doc-number'),
                    'country': self.get_text(patcit, './/country'),
                    'date': self.get_text(patcit, './/date')
                })
        return citations

    def get_text(self, elem: ET.Element, xpath: str) -> str:
        """Safely extract text from XML element"""
        node = elem.find(xpath) if elem is not None else None
        return ' '.join(node.itertext()).strip() if node is not None else ""

    def matches_criteria(self, patent: Dict, doc_number: str = None,
                        inventor_name: str = None, title_keywords: List[str] = None) -> bool:
        if doc_number and doc_number != patent['basic_info']['doc_number']:
            return False

        if inventor_name:
            inventor_found = any(inventor_name.lower() in inv['name'].lower() 
                               for inv in patent['inventors'])
            if not inventor_found:
                return False

        if title_keywords and patent['basic_info']['title']:
            title_lower = patent['basic_info']['title'].lower()
            if not all(kw.lower() in title_lower for kw in title_keywords):
                return False

        return True

def display_utility_patent(patent: Dict):
    """Display utility patent information in a detailed format"""
    print("\n" + "="*80)
    print("UTILITY PATENT DETAILS")
    print("="*80)

    # Basic Information
    basic = patent['basic_info']
    print(f"\nPATENT NUMBER: {basic['doc_number']} ({basic['kind']})")
    print(f"TITLE: {basic['title']}")
    print(f"DATE: {basic['date']}")

    # Application Information
    app = patent['application_info']
    print(f"\nAPPLICATION INFORMATION:")
    print(f"Application Number: {app['app_number']}")
    print(f"Filing Date: {app['app_date']}")
    print(f"Application Type: {app['app_type']}")

    # Inventors
    print("\nINVENTORS:")
    for inv in patent['inventors']:
        location = f"{inv['city']}, {inv['state']}, {inv['country']}"
        print(f"- {inv['name']} ({location})")

    # Assignee
    if patent['assignee']:
        print("\nASSIGNEE:")
        ass = patent['assignee']
        print(f"- {ass['name']}")
        print(f"  Location: {ass['city']}, {ass['state']}, {ass['country']}")

    # Classifications
    print("\nCLASSIFICATIONS:")
    if patent['classifications']['ipc']:
        print("IPC:", ', '.join(patent['classifications']['ipc']))
    if patent['classifications']['cpc']:
        print("CPC:", ', '.join(patent['classifications']['cpc']))
    if patent['classifications']['national']:
        print("National:", ', '.join(patent['classifications']['national']))

    # Technical Information
    tech = patent['technical_info']
    
    if tech['abstract']:
        print("\nABSTRACT:")
        print(textwrap.fill(tech['abstract'], width=80))

    if tech['background']:
        print("\nBACKGROUND:")
        print(textwrap.fill(tech['background'][:500] + "...", width=80))

    if tech['summary']:
        print("\nSUMMARY OF INVENTION:")
        print(textwrap.fill(tech['summary'][:500] + "...", width=80))

    # Claims
    print(f"\nCLAIMS ({len(tech['claims'])}):")
    independent_claims = [c for c in tech['claims'] if c['type'] == 'independent']
    print(f"Number of Independent Claims: {len(independent_claims)}")
    print("\nFirst Independent Claim:")
    for claim in tech['claims']:
        if claim['type'] == 'independent':
            print(textwrap.fill(claim['text'], width=80))
            break

    # Citations
    if patent['citations']:
        print(f"\nCITATIONS ({len(patent['citations'])}):")
        for i, cite in enumerate(patent['citations'][:5], 1):
            print(f"{i}. {cite['country']} {cite['doc_number']} ({cite['date']})")
        if len(patent['citations']) > 5:
            print(f"... and {len(patent['citations'])-5} more citations")

    print("\n" + "="*80)

def main():
    parser = UtilityPatentParser(
        bucket="patent-research-assistant-mv",
        key="uspto/fulltext-unzipped/2023/ipg230103/ipg230103.xml"
    )

    while True:
        print("\nUtility Patent Search Options:")
        print("1. Search by Patent Number")
        print("2. Search by Inventor Name")
        print("3. Search by Title Keywords")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == '1':
            doc_number = input("Enter patent number: ").strip()
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

        if results:
            print(f"\nFound {len(results)} matching utility patents:")
            for patent in results:
                display_utility_patent(patent)
        else:
            print("\nNo matching utility patents found.")

if __name__ == "__main__":
    main()