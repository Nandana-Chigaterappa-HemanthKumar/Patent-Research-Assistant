import os
from lxml import etree

def validate_all_with_dtd(xml_folder, dtd_file):
    """
    Validate all XML files in a folder against a DTD.
    """
    try:
        # Load the DTD
        with open(dtd_file, "r") as f:
            dtd = etree.DTD(f)

        # Iterate through all XML files in the folder
        for file_name in os.listdir(xml_folder):
            if file_name.endswith(".xml"):  # Only process XML files
                file_path = os.path.join(xml_folder, file_name)
                print(f"Validating: {file_name}")

                # Parse the XML file
                try:
                    with open(file_path, "r") as f:
                        doc = etree.parse(f)

                    # Validate the XML
                    is_valid = dtd.validate(doc)
                    if is_valid:
                        print(f"  -> {file_name} is VALID.")
                    else:
                        print(f"  -> {file_name} is NOT VALID.")
                        print(f"  Validation Errors:\n{dtd.error_log}")

                except Exception as e:
                    print(f"  -> Error processing {file_name}: {e}")

    except Exception as e:
        print(f"An error occurred during validation: {e}")

# Paths
xml_folder = "/Users/nithinkeshav/Downloads/utility_patents"  # Replace with your folder path
dtd_file = "/Users/nithinkeshav/Desktop/Patent-Research-Assistant/us-patent-grant-v45-2014-04-03 (1).dtd"  # Path to the uploaded DTD

# Validate all XML files
validate_all_with_dtd(xml_folder, dtd_file)
