import re
import os

def remove_duplicates_and_filter(file_path, dest_file_path):
    """Removes duplicates, filters unwanted URLs, and excludes URLs with dates between 1990 and 2020, as well as fiscal years FY11 to FY20."""
    try:
        with open(file_path, "r") as file:
            urls = file.readlines()

        # Remove duplicates while preserving order
        unique_urls = list(dict.fromkeys(url.strip() for url in urls))

        # Define unwanted patterns (case-insensitive)
        unwanted_extensions = {".xlsx", ".mp3", ".mp4", ".doc", ".csv", ".docx", ".pptx"}
        unwanted_substrings = {
            "/es", "https://www.uscis.gov/archive", "pashto", "dari", "korean",
            "chinese", "spanish", "tagalog", "vietnamese", "amharic", "arabic",
            "hindi", "creole", "farsi", "french", "polish", "punjabi", "russian",
            "somali", "urdu", "portugese", "portuguese", "kor", "viet", "arab", 
            "nepali", "/contracts", "foia", "posters/", "outreach-engagements/", 
            "website-metrics/", "outreach/", "save/", "lesson-plans/", "memos/", 
            "presentations/", "notices/", "brochures/", "flash-cards/",
            "injunctions/", "flyers/", "legal-docs/", "checklists/", "charts/",
            "aao-decisions/", "outstanding-americans-by-choice/", "reports/", "tip-sheets",
            "uscis-facilities-dedicated-to-the-memory-of-immigrant-medal-of-honor-recipients/"
        }

        # Define the date range filter for URLs with dates from 1990 to 2020
        date_pattern = r"(\d{4})"  # Looks for a 4-digit year pattern
        
        # Define fiscal year filter (FY11 to FY20)
        fiscal_year_pattern = r"FY(0[1-9]|20)"  # Matches FY01 to FY20

        # Filter URLs efficiently (case-insensitive)
        filtered_urls = [
            url for url in unique_urls
            if not (url.lower().endswith(tuple(unwanted_extensions)) 
                    or any(sub in url.lower() for sub in unwanted_substrings)
                    or any(1990 <= int(year) <= 2020 for year in re.findall(date_pattern, url))
                    or re.search(fiscal_year_pattern, url))  # Exclude URLs with FY11 to FY20
        ]

        # Write back only valid URLs while keeping the original case
        with open(dest_file_path, "w") as file:
            file.write("\n".join(filtered_urls) + "\n")

        print(f"Processed {file_path}: Removed duplicates, filtered URLs, and excluded URLs with dates from 1990 to 2020 and fiscal years FY11 to FY20")

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")

def main():
    """Main function to process the file."""
    root_dir = os.path.dirname(os.path.dirname(__file__))
    src_file_path = os.path.join(root_dir, "resources/uscis.txt")
    dest_file_path = os.path.join(root_dir, "resources/uscis_filtered.txt")
    remove_duplicates_and_filter(src_file_path, dest_file_path)

if __name__ == "__main__":
    main()
