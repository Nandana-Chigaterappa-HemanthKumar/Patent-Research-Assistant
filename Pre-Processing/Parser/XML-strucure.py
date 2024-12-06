import boto3
import xml.etree.ElementTree as ET
from io import BytesIO
import re

def analyze_patent_xml(bucket: str, key: str, patent_number: str):
    """Analyze the structure of a specific patent XML"""
    try:
        print(f"Accessing file from s3://{bucket}/{key}")
        s3_client = boto3.client('s3')
        response = s3_client.get_object(Bucket=bucket, Key=key)
        xml_content = response['Body'].read().decode('utf-8')

        # Split the file into individual patent documents
        patents = re.split(r'(<?xml.*?>)', xml_content)
        target_patent = None
        
        print("Searching for patent...")
        
        # Find the specific patent
        for patent in patents:
            if f"<doc-number>{patent_number}</doc-number>" in patent:
                target_patent = patent
                break
        
        if not target_patent:
            print(f"Patent {patent_number} not found")
            return

        print(f"\nAnalyzing structure for patent {patent_number}")
        print("="*80)

        # Clean and parse the XML
        clean_xml = re.sub(r'\s+', ' ', target_patent).strip()
        try:
            root = ET.fromstring(clean_xml)
            analyze_element(root)
        except ET.ParseError as e:
            print(f"Error parsing XML: {str(e)}")
            analyze_raw_xml(clean_xml)

    except Exception as e:
        print(f"Error: {str(e)}")

def analyze_element(element, depth=0, path=""):
    """Recursively analyze XML element structure"""
    indent = "  " * depth
    current_path = f"{path}/{element.tag}" if path else element.tag

    # Print element information
    print(f"\n{indent}Element: {element.tag}")
    print(f"{indent}Path: {current_path}")

    # Print attributes
    if element.attrib:
        print(f"{indent}Attributes:")
        for key, value in element.attrib.items():
            print(f"{indent}  {key}: {value}")

    # Print text content
    if element.text and element.text.strip():
        text = element.text.strip()
        if len(text) > 100:
            text = f"{text[:100]}..."
        print(f"{indent}Text: {text}")

    # Process children
    children = list(element)
    if children:
        # Group similar children
        child_tags = {}
        for child in children:
            child_tags[child.tag] = child_tags.get(child.tag, 0) + 1

        print(f"{indent}Child Elements ({len(children)} total):")
        for tag, count in child_tags.items():
            print(f"{indent}  {tag}: {count} occurrence(s)")

        # Analyze each child
        for child in children:
            analyze_element(child, depth + 1, current_path)

def analyze_raw_xml(xml_content):
    """Analyze XML structure without parsing"""
    print("\nRaw XML Analysis:")
    print("="*80)
    
    # Find all XML tags
    tags = re.findall(r'</?([^> ]+)[^>]*>', xml_content)
    tag_counts = {}
    
    for tag in tags:
        if tag.startswith('/'):
            continue
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    print("\nFound XML Elements:")
    for tag, count in sorted(tag_counts.items()):
        print(f"- {tag}: {count} occurrence(s)")
    
    # Find main sections
    sections = [
        "us-bibliographic-data-grant",
        "abstract",
        "description",
        "claims",
        "drawings"
    ]
    
    print("\nMain Sections Found:")
    for section in sections:
        if f"<{section}" in xml_content:
            start = xml_content.find(f"<{section}")
            end = xml_content.find(f"</{section}>")
            if start != -1 and end != -1:
                section_content = xml_content[start:end+len(section)+3]
                print(f"\n{section.upper()}:")
                print("-"*80)
                # Show first few lines of the section
                lines = section_content.split('\n')[:5]
                for line in lines:
                    print(line.strip())
                if len(lines) < len(section_content.split('\n')):
                    print("...")

def main():
    bucket = "patent-research-assistant-mv"
    key = "uspto/fulltext-unzipped/2023/ipg230103/ipg230103.xml"
    patent_number = input("Enter patent number to view structure: ").strip()
    analyze_patent_xml(bucket, key, patent_number)

if __name__ == "__main__":
    main()