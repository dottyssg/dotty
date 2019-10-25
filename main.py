from datetime import date, datetime, timedelta
import json, time, requests, os, sys, shutil
from markdown2 import markdown
from jinja2 import Environment, FileSystemLoader
import sass

# Start the timer...
startTime = time.time()

def altConfig(configFile):
    defaultConfig = {
        "outputFolder": "site",
        "templateFolder": "layouts",
        "assets": {
            "assetSource": "assets",
            "assetTarget": "assets"
        },
        "sass": {
            "sassSource": "sass",
            "sassTarget": "assets/css"
        },
        "dataFolder": "data"
    }
    # Check if there is a config file, otherwise set to default
    if os.path.exists(configFile):
        # Open the config file and get the content and output folders
        fname = f"./{configFile}"
        with open(fname, 'r') as f:
            data = json.load(f)
        
        defaultConfig.update(data)

    # print(defaultConfig)        
    return defaultConfig

def findAllFiles():
    # Find all files in a directory and subdirectories

    # Get a List of Pages and Tags - pageList and tagList
    pageList = []
    tagList = []
    exclude = getIgnoreList()
    for root, dirs, files in os.walk('./'):
        for file in files:
            if file.endswith(('.html','.md')):
                excludedInRoot = [x for x in exclude if x in os.path.join(root, file)]
                if len(excludedInRoot) == 0:
                    # Set the default metadata values
                    pageMetaData = {
                        "type": "page",
                        "template": "page.html",
                        "tags": "page"
                    }

                    # Resolve metadata - get any folder specific metadata...
                    pageParentDir= root.split('/')[-1]
                    if os.path.exists(f"{root}/{pageParentDir}.json"):
                        with open(f"{root}/{pageParentDir}.json", 'r') as f:
                            pageParentMetaData = json.load(f)

                        pageMetaData.update(pageParentMetaData)
                    
                    # ... parse the page metadata
                    page = os.path.join(root, file)
                    with open(page, 'r') as f:
                        parsedPage = markdown(f.read(), extras=['metadata'])
                    
                    # and update the parent with the page metadata
                    pageMetaData.update(parsedPage.metadata)
                    
                    # Figure out permalink
                    if 'permalink' not in pageMetaData:
                        # If the page type is 'post' then make a post specific permalink
                        if pageMetaData['type'] == 'post':
                            pagePermalink = f"/{file.split('.')[0].replace('-','/')}"
                        elif file in ['index.html','index.md']:
                            # If the filename is index then do not make an index folder
                            pagePermalink = '/'.join(root.split('/')[1:])
                        else:
                            pagePermalinkPath = '/'.join(root.split('/')[1:])
                            pagePermalink = f"{pagePermalinkPath}/{file.split('.')[0]}"
                        
                        pageMetaData['permalink'] = pagePermalink
                    
                    # Correct the root path
                    if root == './':
                        pagePath = '.'
                    else:
                        pagePath = root

                    # Define the page metadata and push it to the master list
                    pageDetails = {
                        "pagePath": pagePath,
                        "pageFileName": file,
                        "pageMetaData": pageMetaData,
                        "pageHTML": parsedPage
                    }

                    pageList.append(pageDetails)

                    tagList += pageMetaData['tags'].split(',')

    # Remove duplicates and spaces from tagList
    tagList = [x.strip() for x in list(dict.fromkeys(tagList))]

    return pageList, tagList

def copyAssets(siteConfig):
    
    outputFolder = siteConfig['outputFolder']
    assetSource = siteConfig['assets']['assetSource']
    assetTarget = siteConfig['assets']['assetTarget']

    assetSourcePath = f"./{assetSource}"
    assetTargetPath = f"./{outputFolder}/{assetTarget}"

    if os.path.isdir(assetSource):
        # os.makedirs(assetTargetPath, exist_ok=True)  # Force the creation of the target folder
        shutil.copytree(assetSourcePath, assetTargetPath)
        print(f"Assets copied to the {assetTargetPath} folder")
    else:
        print(f"Assets source folder does not exist: {assetSource}")

def compileSass(siteConfig):
    
    outputFolder = siteConfig['outputFolder']
    sassSource = siteConfig['sass']['sassSource']
    sassTarget = siteConfig['sass']['sassTarget']

    if os.path.isdir(sassSource):
        sass.compile(dirname=(sassSource, f"{outputFolder}/{sassTarget}"))
        print('Sass file compiled and created')
    else:
        print(f"Sass source folder does not exist: {sassSource}")

def renderFile(siteConfig, pageData, tagList, siteData):
    # Initialise some site variables
    templateFolder = siteConfig['templateFolder']
    outputFolder = siteConfig['outputFolder']
    templateFile = pageData['pageMetaData']['template']
    pageMetaData = pageData['pageMetaData']
    permalink = pageData['pageMetaData']['permalink']
    pageMetaData['content'] = pageData['pageHTML']
    sourceFile = f"{pageData['pagePath']}/{pageData['pageFileName']}"

    # If templateFolder and templateFile exists, then render using Jinja2
    if os.path.exists(templateFolder) and os.path.exists(f"{templateFolder}/{templateFile}"):
        # Initialise Jinja2
        file_loader = FileSystemLoader(templateFolder)
        env = Environment(loader=file_loader)

        # Render with Jinja2
        targetTemplate = env.get_template(templateFile)
        targetHTML = targetTemplate.render(post=pageMetaData, site=siteConfig, data=siteData, tags=tagList)
    else:
        # otherwise just send the parsed content to the file
        targetHTML = pageMetaData['content']

    targetPath = f"./{outputFolder}{permalink}"

    # Write the file to the output folder
    targetFile = f"{targetPath}/index.html"
    os.makedirs(targetPath, exist_ok=True)  # Force the creation of the target folder
    with open(targetFile, 'w') as file:
        file.write(targetHTML)
    
    print(f"Writing file {targetFile} from {sourceFile}")

def removeSite(siteConfig):
    outputFolder = siteConfig['outputFolder']
    if os.path.exists(outputFolder):
        shutil.rmtree(outputFolder)

def generatePages(siteConfig, pageList, tagList, siteData):
    # Initialise variables. 
    tagList = []

    for p in pageList:
        pageData = p
        renderFile(siteConfig, pageData, tagList, siteData)
    
def getIgnoreList():
    # Creates a list of files and folders to ignore when building a site with Dotty
    # Set default ignore list
    defaultIgnoreList = ['layouts', 'node_modules','site','includes','README.md']

    # If there is a .dottyignore, add this to the list
    # Only look in the root of the repo
    ignoreFile = f"./.dottyignore"
    if os.path.exists(ignoreFile):
        ignoreList = open(ignoreFile).read().splitlines()
    else:
        ignoreList = []
    
    ignoreList += defaultIgnoreList
    ignoreList = list(dict.fromkeys(ignoreList)) # Removes duplicates

    return ignoreList

def getData(siteConfig):
    # Initialise some variables from siteConfig
    dataFolder = siteConfig['dataFolder']

    dataForSite = {}
    if os.path.exists(dataFolder):
        # For each file in data, grab it, add to a list
        dataFiles = [x for x in os.listdir(f"./{dataFolder}") if x.endswith(".json")]
        for d in dataFiles:
            dataFName = os.path.splitext(d)[0]
            dataFNameExt = os.path.splitext(d)[1]
            fname = f"./{dataFolder}/{d}"
            with open(fname, 'r') as f:
                dataFetched = json.load(f)
            dataForSiteIndiv = { dataFName: dataFetched }
            dataForSite.update(dataForSiteIndiv)
    
    return dataForSite

# Get the site config and assign some variables
siteConfig = altConfig('dottyconfig.json')

# If previously built site exists, remove it, vopy over assets and compile sass
removeSite(siteConfig)
copyAssets(siteConfig)
compileSass(siteConfig)

# From the data folder, import all data
siteData = getData(siteConfig)

# Compile a list of pages and tags
pageList, tagList = findAllFiles()
# with open('pages.json', 'w') as f:
#     json.dump(pageList, f)
numPages = len(pageList)

# Generate all the pages for the site
generatePages(siteConfig, pageList, tagList, siteData)


# ... and stop the timer!
endTime = time.time()
duration = endTime - startTime
if numPages == 1:
    print(f"Dotty generated {numPages} file in {str(round(duration, 3))} seconds.")
else:
    print(f"Dotty generated {numPages} files in {str(round(duration, 3))} seconds.")
    