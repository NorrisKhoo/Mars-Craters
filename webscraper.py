# webscraper.py
# Norris Khoo

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from tqdm import tqdm
import re
import csv
import requests
import math

driver = webdriver.Firefox()
driver.get("https://viewer.mars.asu.edu/viewer/ctx#T=1")

longitudeMinInput = "0"
longitudeMaxInput = "1"
latitudeMinInput = "0"
latitudeMaxInput = "1"

csvFilename = "longitude_" + longitudeMinInput + "_" + longitudeMaxInput + "_latitude_" + latitudeMinInput + "_" + latitudeMaxInput + "_crater.csv"
csvCrater = []
print csvFilename

# Minimum longitude
longitudeMin = driver.find_element_by_name("s2[longitude][start]")
longitudeMin.send_keys(longitudeMinInput)

# Maximum longitude
longitudeMax = driver.find_element_by_name("s2[longitude][end]")
longitudeMax.send_keys(longitudeMaxInput)

# Minimum latitude
latitudeMin = driver.find_element_by_name("s2[latitude][start]")
latitudeMin.send_keys(latitudeMinInput)

# Maximum latitude
latitudeMax = driver.find_element_by_name("s2[latitude][end]")
latitudeMax.send_keys(latitudeMaxInput)

# Press "Run Query"
runQuery = driver.find_element_by_xpath('//*[@id="edit-bottom-buttons-bottom-submit"]')
runQuery.click()

###

nextPage = True
i = 0

while nextPage:
    
    sleep(4)
    
    images = driver.find_elements_by_tag_name("tr")
    images = images[1:]
    
    sleep(4)

    for image in images:

        column = image.find_elements_by_tag_name("td")
        column[0].click()

        sleep(4)

        table = driver.find_elements_by_tag_name("table")[2].get_attribute('innerHTML')
        if i == 0:
            name = re.findall('(?<=data-role="tooltip">)(.*?)(?=<\/span>)', table)
            name.append('MinimumLatitude')
            name.append('MaximumLatitude')
            name.append('MinimumLongitude')
            name.append('MaximumLongitude')
            name.append('UpperLeftCornerX')
            name.append('UpperLeftCornerY')
            name.append('PixelResolution')
            name.append('Scale')
            csvCrater.append(name)
            
        attributeASCII = re.findall('(?<=<span\sclass="datatable-data">)(.*?)(?=<\/span>)', table)
        attributeUnicode = [ASCII.encode("utf-8") for ASCII in attributeASCII]

        sleep(2)

        tiff = driver.find_elements_by_tag_name("table")[4].get_attribute('innerHTML')
        url = re.findall('(?<=href=")(.*?)(?="\starget="_blank">Pyramidized\sTIFF)', tiff)[0]
        r = requests.get(url, stream=True)
        total_size = int(r.headers.get('content-length', 0)); 
        block_size = 1024
        wrote = 0 
        with open(attributeUnicode[0] + ".tiff", 'wb') as f:
            for data in tqdm(r.iter_content(block_size), total=math.ceil(total_size//block_size) , unit='KB', unit_scale=True):
                wrote = wrote  + len(data)
                f.write(data)
        if total_size != 0 and wrote != total_size:
            print("ERROR, something went wrong")
        
        sleep(2)
        
        url = re.findall('(?<=Pyramidized TIFF</a></td><td><a href=")(.*?)(?=" target="_blank">ISIS Header)', tiff)[0]
        r = requests.get(url, stream=True)
        total_size = int(r.headers.get('content-length', 0)); 
        block_size = 1024
        wrote = 0 
        with open(attributeUnicode[0] + ".isis.hdr", 'wb') as f:
            for data in tqdm(r.iter_content(block_size), total=math.ceil(total_size//block_size) , unit='KB', unit_scale=True):
                wrote = wrote  + len(data)
                f.write(data)
        if total_size != 0 and wrote != total_size:
            print("ERROR, something went wrong")  

        sleep(2)
        
        with open(attributeUnicode[0] + ".isis.hdr", "r") as f:
            for line in f:
                if 'MinimumLatitude' in line:
                    MinimumLatitude = float(re.findall('(?<=\s=\s)(.*)', line)[0])
                    attributeUnicode.append(MinimumLatitude)
                if 'MaximumLatitude' in line:
                    MaximumLatitude = float(re.findall('(?<=\s=\s)(.*)', line)[0])
                    attributeUnicode.append(MaximumLatitude)
                if 'MinimumLongitude' in line:
                    MinimumLongitude = float(re.findall('(?<=\s=\s)(.*)', line)[0])
                    attributeUnicode.append(MinimumLongitude)
                if 'MaximumLongitude' in line:
                    MaximumLongitude = float(re.findall('(?<=\s=\s)(.*)', line)[0])
                    attributeUnicode.append(MaximumLongitude)
                if 'UpperLeftCornerX' in line:
                    UpperLeftCornerX = re.findall('(?<=\s=\s)(.*)(?=\s<meters>)', line)[0]
                    attributeUnicode.append(UpperLeftCornerX)
                if 'UpperLeftCornerY' in line:
                    UpperLeftCornerY = re.findall('(?<=\s=\s)(.*)(?=\s<meters>)', line)[0]
                    attributeUnicode.append(UpperLeftCornerY)
                if 'PixelResolution' in line:
                    PixelResolution = float(re.findall('(?<=\s=\s)(.*)(?=\s<meters/pixel>)', line)[0])
                    attributeUnicode.append(PixelResolution)
                if 'Scale' in line:
                    Scale = float(re.findall('(?<=\s=\s)(.*)(?=\s<pixels/degree>)', line)[0])
                    attributeUnicode.append(Scale)
   
        sleep(2)
        
        csvCrater.append(attributeUnicode)
        
        close = driver.find_elements_by_class_name("close-icon")[0]
        close.click()

        i = i + 1
        # if i == 1:
        #     break
            
    # if i == 1:
    #     break
            
    forward = driver.find_element_by_xpath("/html/body/div[2]/div/div[2]/div/div[1]/div/div/div/div/div/div/div[1]/div/div/div/div[1]/div[2]/div/div/div/div/div/div/div/div/div/div[1]/div/div/span[2]/a[3]").get_attribute("outerHTML")
    if "k-state-disabled" in forward:
        nextPage = False
    else:
        driver.find_elements_by_css_selector('a.k-link:nth-child(4)')[0].click()
        
with open(csvFilename, "wb") as f:
    writer = csv.writer(f)
    writer.writerows(csvCrater)