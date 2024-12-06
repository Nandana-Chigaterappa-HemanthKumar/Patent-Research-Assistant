import boto3
import re
from lxml import etree
from io import BytesIO
import logging
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(
    filename='xml_validation_parallel.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Assuming boto3 is already initialized
s3 = boto3.client('s3')

# Replace with your bucket and prefix (path)
BUCKET_NAME = "patent-research-assistant-mv"
#FILE_KEY = "uspto/fulltext-unzipped/2023/ipg230103/ipg230103.xml"\
FILE_KEY = "C:/Users/SUJATA/Downloads/utility-patents/document_986.xml"

DTD_FILE_PATH = "us-patent-grant-v45-2014-04-03.dtd"

def split_xml_content(xml_content, root_tag="us-patent-grant"):
    """Splits a concatenated XML file into individual documents based on a specific root tag."""
    pattern = f"(</{root_tag}>)"
    parts = re.split(pattern, xml_content)
    
    documents = []
    for i in range(0, len(parts) - 1, 2):
        document = parts[i] + parts[i + 1]
        documents.append(document)
    
    return documents

def process_xml_segment(xml_segment, dtd):
    """Processes an individual XML segment by parsing and validating it against the DTD."""
    try:
        xml_segment = xml_segment.strip()
        if not xml_segment.startswith('<?xml'):
            xml_segment = '<?xml version="1.0" encoding="utf-8"?>\n' + xml_segment

        # Parse the XML
        xml_tree = etree.parse(BytesIO(xml_segment.encode('utf-8')))

        # Validate the XML against the DTD
        if dtd.validate(xml_tree):
            logging.info("Segment is valid according to the DTD")
            return "Valid"
        else:
            error_messages = dtd.error_log.filter_from_errors()
            logging.error(f"Segment is invalid. Errors: {error_messages}")
            return "Invalid"
    
    except Exception as e:
        logging.error(f"Error processing segment: {e}", exc_info=True)
        return "Error"

try:
    # Step 1: Load the XML file from S3
    logging.info(f"Attempting to load XML file from S3: Bucket={BUCKET_NAME}, Key={FILE_KEY}")
    xml_file_obj = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
    xml_content = xml_file_obj['Body'].read().decode('utf-8')
    logging.info(f"Successfully loaded XML file from S3: {FILE_KEY}")

    # Step 2: Split the XML content into smaller parts
    logging.info("Splitting the XML content into individual documents")
    xml_segments = split_xml_content(xml_content)
    logging.info(f"Split XML into {len(xml_segments)} segments")

    # Step 3: Load the DTD for validation
    logging.info(f"Loading DTD from file: {DTD_FILE_PATH}")
    with open(DTD_FILE_PATH, "r") as dtd_file:
        dtd = etree.DTD(dtd_file)
    logging.info("Successfully loaded DTD")

    # Step 4: Process each XML segment in parallel
    logging.info("Processing XML segments in parallel")
    with ThreadPoolExecutor(max_workers=4) as executor:  # Adjust the number of workers as needed
        results = list(executor.map(lambda segment: process_xml_segment(segment, dtd), xml_segments))

    # Step 5: Log summary results
    valid_count = results.count("Valid")
    invalid_count = results.count("Invalid")
    error_count = results.count("Error")
    logging.info(f"Processing completed: {valid_count} valid, {invalid_count} invalid, {error_count} errors")
    print(f"Processing completed: {valid_count} valid, {invalid_count} invalid, {error_count} errors")

except Exception as e:
    logging.error(f"Error during processing: {e}", exc_info=True)
    print(f"Error: {e}")
