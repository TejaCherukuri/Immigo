import re
from html import unescape
import os

EXCLUDED_EXTENSIONS = {".mp3", ".csv", ".doc"}

def is_valid_url(url: str) -> bool:
    """Checks if a URL should be processed."""
    return not any(url.endswith(ext) for ext in EXCLUDED_EXTENSIONS) and '/es' not in url

def load_urls(filename: str = "sitemap_urls.txt") -> list:
    """Loads URLs from a file, filtering out unwanted extensions."""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"{filename} not found.")

    with open(filename, "r") as file:
        urls = [line.strip() for line in file.readlines()]
    return [url for url in urls if is_valid_url(url)]

def clean_text(text: str) -> str:

    # Remove HTML entities (e.g., &amp;, &lt;, etc.)
    text = unescape(text)
    
    # Replace multiple whitespaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Ensure there's a space between paragraphs or sections
    text = re.sub(r'\n+', ' ', text)
    
    # Convert to lowercase
    text = text.lower()

    # Strip leading/trailing spaces
    text = text.strip()

    text = remove_header_and_footer(text)
    
    return text

def remove_header_and_footer(text):
    text = text.replace("uscis skip to main content an official website of the united states government here's how you know español multilingual resources official websites use .gov a .gov website belongs to an official government organization in the united states. secure .gov websites use https a lock ( a locked padlock ) or https:// means you've safely connected to the .gov website. share sensitive information only on official, secure websites. sign in access uscis online services. sign in create account menu sign in create account topics topics family family of green card holders (permanent residents) family of refugees and asylees family of u.s. citizens adoption before you start immigration through adoption military citizenship for military family members naturalization through military service humanitarian humanitarian parole refugees and asylum temporary protected status visit the u.s. change my nonimmigrant status extend your stay working in the united states permanent workers temporary (nonimmigrant) workers e-verify i-9 central avoid scams common scams find legal services report immigration scams careers at uscis career opportunities special hiring programs forms forms most accessed forms i-9, employment eligibility verification i-485, application to register permanent residence or adjust status i-765, application for employment authorization i-90, application to replace permanent resident card (green card) n-400, application for naturalization family based forms i-129f, petition for alien fiancé(e) i-130, petition for alien relative i-360, petition for amerasian, widow(er), or special immigrant i-600, petition to classify orphan as an immediate relative i-751, petition to remove conditions on residence all forms file online employment based forms i-129, petition for a nonimmigrant worker i-140, immigrant petition for alien workers i-526, immigrant petition by standalone investor i-539, application to extend/change nonimmigrant status humanitarian based forms i-589, application for asylum and for withholding of removal i-730, refugee/asylee relative petition i-821, application for temporary protected status newsroom newsroom all news alerts fact sheets news releases stakeholder messages media contacts multimedia gallery social media directory speeches, statements, testimony citizenship citizenship learners apply for citizenship learn about citizenship naturalization test and study resources educators educational products for educators resources for educational programs teacher training sessions organizations outreach tools civic integration naturalization-related data and statistics grants success stories from grant recipients green card green card green card processes and procedures adjustment of status after we grant your green card employment authorization document visa availability and priority dates green card eligibility categories how to apply for a green card replace your green card while your green card application is pending with uscis laws laws legislation immigration and nationality act class action, settlement notices and agreements unlawful presence and inadmissibility policy manual regulations administrative appeals tools tools self-help tools check case processing times case status online change of address e-request password resets and technical support website resources archive a-z index website policies additional resources explore my options immigration and citizenship data multilingual resource center uscis tools and resources", "")
    text = text.replace("previouspreviousnextnext return to top topics forms newsroom citizenship green card laws tools contact uscis agency description uscis.gov an official website of the u.s. department of homeland security important links about uscis accessibility budget and performance dhs components freedom of information act no fear act data privacy and legal disclaimers site map office of the inspector general the white house usa.gov looking for u.s. government information and services? visit usa.gov", "")
    return text