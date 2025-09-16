#IMPPAT downloader: fetches *all* available structure formats (MOL, SDF, PDB, etc.)
#For each IMPHY ID, creates a folder and saves all available files there.
#Also creates a manifest.csv summarizing results.

#requests lets python to fetch raw HTML of any webpage
import requests

import datetime

#it allows us to parse that HTML and search for <a href="..."> links to see to whcih format it points to 
from bs4 import BeautifulSoup

#library to handle command line arguments
import argparse

import time

import os

import csv

from urllib.parse import urljoin

# Base URLs
#went to IMPPAT website and searched few IDs, and this was the common part of the URL
BASE_DETAILED = "https://cb.imsc.res.in/imppat/phytochemical-detailedpage/" #continued with the IMPHYnumber
BASE_HOST = "https://cb.imsc.res.in"

# Output settings
#main folder for all downloaded compounds
DOWNLOAD_ROOT = "imppat_structures"


#filename for the log file-csv file, with IMPHY ID, page url, file url, status
MANIFEST_CSV = "download_manifest.csv"


# Networking
HEADERS = {
    #polite way of saying who you are to the server
    #general format -> <ProductName/Version ExtraInfo (+ContactInfo))
    #Mozilla5.0 (many servers accept this), IMPPATscraper/2.0 (own program name, version), (+your.email@example)- optional contact info, good practice
    "User-Agent": "Mozilla/5.0 IMPPAT-scraper/2.0 (+your.email@example)",
}

#wait for 20 seconds to get a reply from the server
REQUEST_TIMEOUT = 30

#create main folder: imppat_structures, exist_ok = True will allow the program to reuse the folder if it already exists, instead of crashing
os.makedirs(DOWNLOAD_ROOT, exist_ok=True)

#define a helper function to safely fetch a webpage/file
#We are using the requests library, specifically its .get() method, to fetch the web page for a given IMPPAT phytochemical ID.
#While making the request, we attach custom headers (the User-Agent) so the server knows who we are, and we also set a timeout of 20 seconds so the script won’t hang forever if the site is slow.
#url -> web address you want to fetch, session (optional), NONE if nothing is passed
def safe_get(url, session=None):
    session = session or requests #if caller gave a session use it, or else fall back to plain requests library 
    try:
        #make HTTP request to the website, send out user agent (HEADERS), wait for 20 seconds.
        r = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        return r #now r contains, r.status_code, r.text, r.content
    #If something goes wrong while making the request, raise an Exception
    except Exception as e:
        print(f"  ✖ Network error for {url}: {e}")
        return None


#This function looks through all the links on a compound’s page. If the link points to a structure file (.mol, .sdf, .pdb, .mol2), it builds the full download link, figures out a good filename, and saves both into a list.
#Function to collect all links that look like downloadable structure files for a compound
def find_structure_links(soup, id_str):
    #Returns list of (absolute_url, filename_guess).
    formats = []
    
    #loop over all links on the page
    #soup.findall("a", href=True) will find every <a> anchor tags in the HTML that have href attribute
    #eg: <a href="/imppat/images/3D/MOL/IMPHY000001.mol">MOL file</a>
    for a in soup.find_all("a", href=True):
        
        #extract the URL from the tag and pulls out the actual link (/imppat/images/...mol).
        href = a["href"].strip()
        
        #check if the link is a structure file
        #only given links are kept and rest are ignored
        if any(href.lower().endswith(ext) for ext in [".mol", ".sdf", ".pdb", ".mol2",".sif"]):
            #build a complete URL 
            #urljoin combines the href with the BASE_HOST
            abs_url = urljoin(BASE_HOST, href)
            
            #make a file name guess
            #href.split("?")[0] will remove stuff like ?downlaod =true
            #os.path.basename(....) gets only the last part, eg: "IMPHY000001.mol"
            #if nothing wors, fallback to "IMPHY000001.dat"
            fname = os.path.basename(href.split("?")[0]) or f"{id_str}.dat"
            
            #save the results (URL and File name) as a tuple to the list initialised in the beginning 
            
            #                BASE_HOST         href                               file_name
            #eg: "https://cb.imsc.res.in/imppat/images/3D/MOL/IMPHY000001.mol", "IMPHY000001.mol"
            formats.append((abs_url, fname))
    
    return formats



#function to download one file and saving it 
# url-> download link, filepath-> where to save the file locally, session-> optional, lets us use a requests.session for efficiency 
def download_file(url, filepath, session=None):
    #if session is passed use it or else fallback to normal requests library 
    session = session or requests
    try:
        #sessions.get -> asks the server 
        #we send a fake user agent (HEADERS) to look like a normal browser
        #stream=True -> tells requests to not download everything at once but piece by piece
        #timeout-> equal to the seconds we initialised at the beginning 
        with session.get(url, headers=HEADERS, stream=True, timeout=REQUEST_TIMEOUT) as r:
            
            #if HTTP code = 200 means success, if the server replies with something like 404(not found), 500(server error) we stop and return failure
            if r.status_code != 200:
                return False, f"HTTP {r.status_code}"
            
            #open a new file on disk in wb mode, write binary mode (because structure files are not plain text)
            with open(filepath, "wb") as f:
                #read response in small pieces (8kb at a time/ 1kb = 1024 bytes, because computers work in the power of 2)
                for chunk in r.iter_content(8192):
                    if chunk:
                        f.write(chunk)
                        
        #report success if everything worked
        return True, "OK"
    
    #if something like, no internet, timeout, permission error happens raise error with message 
    except Exception as e:
        return False, str(e)


#main function - main driver of the whole script
#script actually starts downloading all the IMPPAT compounds.
#here, we call all the functions defined earlier.

#Create a session and a manifest.
#Loop over a range of compound IDs.
#Fetch the detailed page for each compound.
#Parse the page to find downloadable structure files.
#Make a folder for this compound.
#Download each structure file and save it locally.
#Record success/failure in the manifest.
#Pause between requests to be polite.
#At the end, save the manifest to a CSV and print a summary.

def main():
    
    parser = argparse.ArgumentParser(description="IMPPAT Downloader Tool")
    parser.add_argument("--start", type=int, required=True, help="Start ID (integer)")
    parser.add_argument("--end", type = int, required = True, help="End ID (integer, exclusive)")
    parser.add_argument("--delay", type = float, default=2.0, help= "Delay between downloads (seconds)")
    parser.add_argument("--skip-existing", action="store_true", help="Skip Files that are already downloaded")
    
    args = parser.parse_args()
    
    start, end, delay, skip_existing = args.start, args.end, args.delay, args.skip_existing
    
    #keep the TCP connection alive so that multiple requests are fasters
    session = requests.Session()
    
    #an empty list to record everything we do, ID, URL, file URL, status
    manifest = []
    
    #go through the range of IDs, 
    for idx in range(start, end):
        #format the id as IMPHY000001
        #06d means, format decimal integer with 6 characters long and pad with leading zeros if the number has fewer than 6 digits.
        id_str = f"IMPHY{idx:06d}"
        
        #build the full URL of the detailed page of the compound
        page_url = urljoin(BASE_DETAILED, id_str)
        
        #show progress
        print(f"\n[{idx}] {id_str} -> {page_url}")

        #fetch the compound page
        #use safe_get function to download the page
        # if it fails, r is NONE or the server returns a bad HTTP status , record failure in the manifest and skip to next ID
        r = safe_get(page_url, session=session)
        if r is None or r.status_code != 200:
            status = f"PAGE_FAIL_{r.status_code if r else 'NO_RESP'}"
            manifest.append((id_str, page_url, "", status))
            continue

        #parse the HTML of the page so we can extract the links
        soup = BeautifulSoup(r.text, "lxml")
        
        #returns a list of structure file links, by passing the HTML page (soup) and the IMPPAT id (id_str) to the function
        links = find_structure_links(soup, id_str)
        
        
        if not links:
            print("  ⚠ No structure links found.")
            manifest.append((id_str, page_url, "", "NO_FILES"))
            
            #pause politely before the next request
            time.sleep(delay)
            continue



        # make per-ID folder (subfolder inside the main folder: imppat_structures/IMPHY000001/)
        id_folder = os.path.join(DOWNLOAD_ROOT, id_str)
        os.makedirs(id_folder, exist_ok=True)
        
        
        #download all structure files
        #loop through each file found
        for file_url, fname in links:
            
            #build a full local file path 
            filepath = os.path.join(id_folder, fname)
            
            #skip if the file already exists
            if skip_existing and os.path.exists(filepath):
                print(f"⏩ Skipping {fname}, already exists.")
                manifest.append((id_str, page_url, file_url,"SKIPPED"))
                continue
            
            #progress
            print(f"  → Downloading {fname} from {file_url}")
            
            #downlod_file function returns True (into ok) and "OK" (into msg)
            ok, msg = download_file(file_url, filepath, session=session)
            
            if ok:
                print(f"    ✅ Saved {fname}")
                manifest.append((id_str, page_url, file_url, "OK"))
            
            else:
                print(f"    ✖ Failed {fname}: {msg}")
                manifest.append((id_str, page_url, file_url, f"FAIL_{msg}"))

        #wait 2 seconds before requesting the next compound
        time.sleep(delay)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    manifest_name = f"download_manifest_{timestamp}.csv"

    # Save manifest (log file) with ID, URL, file_URL, status 
    with open(manifest_name, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["IMPHY_ID", "PAGE_URL", "FILE_URL", "STATUS"])
        writer.writerows(manifest)

    print("\nDone. Manifest written to:", manifest_name)
    print("All compound folders inside:", DOWNLOAD_ROOT)



def run():
    main()
