import os, re, sys
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from zipfile import ZipFile


#USAGE :
#   python3 getNewSite.py {path-to-working directory}

whoisPage = requests.get("https://www.whoisds.com/newly-registered-domains")
whoisSoup = BeautifulSoup(whoisPage.content, "lxml")
dateRegex = re.compile(r'\d{4}-\d{2}-\d{2}.txt')

def isInCurrentFileList(path, element):
    dirList = os.listdir(path)
    for dir in dirList :
        if (dateRegex.search(dir)):
            dateItem = datetime.strptime(dir[:max([idx for idx, x in enumerate(dir) if x == '.'])], '%Y-%m-%d').date()
            if (element == dateItem):
                return True
    return False

def downloadFile(soupObject, fileDate, path):
    i = 0
    zipFilename = path + "domain-names.txt"
    for td in soupObject.findAll("td"):
        i += 1
        if (i == 4):
            url = td.a["href"]
            with requests.get(url, stream=True) as fileContent:
                fileContent.raise_for_status()
                fileName = path + fileDate.strftime('%Y-%m-%d') + ".zip"
                with open(fileName, "wb") as file:
                    print("Downloading " + url + " at " + fileName)
                    for chunk in fileContent.iter_content(chunk_size=8192):
                        file.write(chunk)
                    print("Finished downloading.")
                with ZipFile(fileName, 'r') as zip:
                    print("Extracting " + fileName)
                    zip.extractall(path)
                    print("Finished extraction.")
                os.remove(fileName)
                os.rename(zipFilename, fileName.replace(".zip", ".txt"))



if (len(sys.argv) < 2):
    print("Wrong arguments: need to add path to work folder")
    exit()

table = whoisSoup.find(lambda tag: tag.name=='table')

for row in table.findAll("tr"):
    i = 0
    for td in row.findAll("td"):
        i += 1
        if (i == 3):
            dateobject = datetime.strptime(td.text, '%Y-%m-%d').date()
            if isInCurrentFileList(sys.argv[1], dateobject) == False:
                downloadFile(row, dateobject, sys.argv[1])
print("Last data aquired.")
