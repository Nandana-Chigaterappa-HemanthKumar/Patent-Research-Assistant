import os
import xml.etree.ElementTree as ET

def extract_utility_patents(input_dir, output_dir):
    """
    Extract Utility Patents (appl-type = 'utility') from split XML files.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)

        try:
            # Parse the XML file
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Find <application-reference> and check appl-type
            app_ref = root.find(".//application-reference")
            appl_type = app_ref.attrib.get("appl-type") if app_ref is not None else None

            if appl_type == "utility":  # Only process Utility Patents
                output_file = os.path.join(output_dir, file_name)
                tree.write(output_file, encoding="utf-8", xml_declaration=True)
                print(f"Utility Patent Saved: {output_file}")
            else:
                print(f"Skipped (Not Utility Patent): {file_name}")

        except ET.ParseError as e:
            print(f"Error parsing {file_name}: {e}")
        except Exception as e:
            print(f"Error processing {file_name}: {e}")

# Paths
input_dir = "C:/Users/SUJATA/Downloads/xml_split_output"  # Directory with split XML files
output_dir = "C:/Users/SUJATA/Downloads/utility_patents"  # Directory to save Utility Patents

# Extract Utility Patents
extract_utility_patents(input_dir, output_dir)
print("Extraction of Utility Patents completed.")
