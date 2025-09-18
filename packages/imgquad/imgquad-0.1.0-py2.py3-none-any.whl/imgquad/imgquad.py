#! /usr/bin/env python3

"""Image Quality Assessment for Digitisation batches

Johan van der Knijff

Copyright 2025, KB/National Library of the Netherlands

"""

import sys
import os
import shutil
import time
import argparse
import csv
import logging
from lxml import etree
from . import properties
from . import schematron
from . import shared

__version__ = "0.1.0"

# Create parser
parser = argparse.ArgumentParser(description="IMaGe QUality Assessment for Digitisation batches")


def parseCommandLine():
    """Parse command line"""

    # Sub-parsers for process and list commands

    subparsers = parser.add_subparsers(help='sub-command help',
                                       dest='subcommand')
    parser_process = subparsers.add_parser('process',
                                          help='process a batch')
    parser_process.add_argument('profile',
                                action="store",
                                help='validation profile name (use "imgquad list" to list available profiles)')
    parser_process.add_argument('batchDir',
                                action="store",
                                help="batch directory")
    parser_process.add_argument('--prefixout', '-p',
                                action="store",
                                default='iq',
                                help="prefix of output files")
    parser_process.add_argument('--outdir', '-o',
                                action="store",
                                default=os.getcwd(),
                                help="output directory")
    parser_process.add_argument('--delimiter', '-d',
                            action="store",
                            default=';',
                            help="output delimiter")
    parser_process.add_argument('--verbose', '-b',
                                action="store_true",
                                default=False,
                                help="report Schematron report in verbose format")
    parser_list = subparsers.add_parser('list',
                                        help='list available profiles and schemas')
    parser_copyps = subparsers.add_parser('copyps',
                                        help='copy default profiles and schemas to \
                                            user directory, note that this will overwrite \
                                            any user-modified versions of these files!')
    parser.add_argument('--version', '-v',
                        action="version",
                        version=__version__)

    # Parse arguments
    args = parser.parse_args()

    return args


def getFilesFromTree(rootDir, extensions):
    """Walk down whole directory tree (including all subdirectories) and
    return list of those files whose extensions match extensions list
    NOTE: directory names are disabled here!!
    implementation is case insensitive (all search items converted to
    upper case internally!
    """

    # Convert extensions to uppercase
    extensions = [extension.upper() for extension in extensions]
    filesList = []

    for dirname, dirnames, filenames in os.walk(rootDir):
        # Suppress directory names
        for subdirname in dirnames:
            thisDirectory = os.path.join(dirname, subdirname)

        for filename in filenames:
            thisFile = os.path.join(dirname, filename)
            thisExtension = os.path.splitext(thisFile)[1]
            thisExtension = thisExtension.upper().strip('.')
            if extensions[0].strip() == '*' or thisExtension in extensions:
                filesList.append(thisFile)
    return filesList


def writeXMLHeader(fileOut):
    """Write XML header"""
    xmlHead = "<?xml version='1.0' encoding='UTF-8'?>\n"
    xmlHead += "<imgquad>\n"
    with open(fileOut,"wb") as f:
        f.write(xmlHead.encode('utf-8'))


def writeXMLFooter(fileOut):
    """Write XML footer"""
    xmlFoot = "</imgquad>\n"
    with open(fileOut,"ab") as f:
        f.write(xmlFoot.encode('utf-8'))


def processFile(file, verboseFlag, schemas):
    """Process one file"""

    # Create output element for this file
    fileElt = etree.Element("file")

    # Initial value of flag that indicates whether image passes or fails quality checks
    validationOutcome = "Pass"
    # Initial value of flag that indicates whether validation was successful
    validationSuccess = False

    # Select schema based on directory or file name pattern defined in profile
    schemaMatchFlag, mySchema = schematron.findSchema(file, schemas)
    
    # Extract properties
    propertiesElt = properties.getProperties(file)

    # Validate extracted properties against schema
    if schemaMatchFlag:
        validationSuccess, validationOutcome, reportElt = schematron.validate(mySchema,
                                                                              propertiesElt,
                                                                              verboseFlag)
    else:
        # No schema match
        validationOutcome = "Fail"
        logging.warning("no schema match")

    if not validationSuccess:
        logging.warning("Schematron validation was not successful")

    # Create schema and status elements
    schemaElt = etree.Element("schema")
    schemaElt.text = mySchema
    validationSuccessElt = etree.Element("validationSuccess")
    validationSuccessElt.text = str(validationSuccess)
    validationOutcomeElt = etree.Element("validationOutcome")
    validationOutcomeElt.text = validationOutcome
    # Add all child elements to file element
    fileElt.append(propertiesElt)
    fileElt.append(schemaElt)
    fileElt.append(validationSuccessElt)
    fileElt.append(validationOutcomeElt)
    if schemaMatchFlag:
        fileElt.append(reportElt)

    return fileElt


def findEltValue(element, path, ns):
    """ Return text of path in element, or "n/a" if it doesn't exist """
    try:
        elOut = element.xpath(path, namespaces=ns)
        
        if len(elOut) > 0:
            if type(elOut[0]) == etree._Element:
                result = elOut[0].text
            elif type(elOut[0]) == etree._ElementUnicodeResult:
                result = elOut[0]
        else:
            result = "n/a"

    except Exception:
        raise
        result = "n/a"
    
    return result


def main():
    """Main function"""

    # Path to configuration dir (from https://stackoverflow.com/a/53222876/1209004
    # and https://stackoverflow.com/a/13184486/1209004).
    # TODO on Windows this should return the AppData/Local folder, does this work??
    configpath = os.path.join(
    os.environ.get('LOCALAPPDATA') or
    os.environ.get('XDG_CONFIG_HOME') or
    os.path.join(os.environ['HOME'], '.config'),
    "imgquad")

     # Create config directory if it doesn't exist already
    if not os.path.isdir(configpath):
        os.mkdir(configpath)
   
    # Locate package directory
    packageDir = os.path.dirname(os.path.abspath(__file__))

    # Profile and schema locations in installed package and config folder
    profilesDirPackage = os.path.join(packageDir, "profiles")
    schemasDirPackage = os.path.join(packageDir, "schemas")
    profilesDir = os.path.join(configpath, "profiles")
    schemasDir = os.path.join(configpath, "schemas")

    # Check if package profiles and schemas dirs exist
    shared.checkDirExists(profilesDirPackage)
    shared.checkDirExists(schemasDirPackage)

    # Copy profiles and schemas to respective dirs in config dir
    if not os.path.isdir(profilesDir):
        shutil.copytree(profilesDirPackage, profilesDir)
    if not os.path.isdir(schemasDir):
        shutil.copytree(schemasDirPackage, schemasDir)

    # Get input from command line
    args = parseCommandLine()
    action = args.subcommand

    if action == "process":
        # Check if all profiles and schemas can be parsed
        schematron.checkProfilesSchemas(profilesDir, schemasDir)
        profile = os.path.basename(args.profile)
        batchDir = os.path.normpath(args.batchDir)
        prefixOut = args.prefixout
        outDir = os.path.normpath(args.outdir)
        delimiter = args.delimiter
        verboseFlag = args.verbose
    elif action == "list":
        schematron.listProfilesSchemas(profilesDir, schemasDir)
    elif action == "copyps":
        shutil.copytree(profilesDirPackage, profilesDir, dirs_exist_ok=True)
        msg = ("copied profiles from {} to {}").format(profilesDirPackage, profilesDir)
        print(msg)
        shutil.copytree(schemasDirPackage, schemasDir, dirs_exist_ok=True)
        msg = ("copied schemas from {} to {}").format(schemasDirPackage, schemasDir)
        print(msg)
        sys.exit()
    elif action is None:
        print('')
        parser.print_help()
        sys.exit()
    
    # Add profilesDir to profile definition
    profile = os.path.join(profilesDir, profile)

    # Check if files / directories exist
    shared.checkFileExists(profile)
    shared.checkDirExists(batchDir)
    shared.checkDirExists(outDir)

    # Check if outDir is writable
    if not os.access(outDir, os.W_OK):
        msg = ("directory {} is not writable".format(outDir))
        shared.errorExit(msg)

    # Batch dir name
    batchDirName = os.path.basename(batchDir)
    # Construct output prefix for this batch
    prefixBatch = ("{}_{}").format(prefixOut, batchDirName)
    
    # Set up logging
    logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout)],
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    # Get file extensions, summary properties schema patterns and locations from profile
    extensions, namespaces, summaryProperties, schemas = schematron.readProfile(profile, schemasDir)

    # Add Schematron namespace definition
    namespaces["svrl"] = "http://purl.oclc.org/dsdl/svrl"

    if len(extensions) == 0:
        msg = ("no file extensions defined in profile")
        shared.errorExit(msg)

    # Summary file with quality check status (pass/fail) and properties that are selected in profile
    summaryFile = os.path.normpath(("{}_summary.csv").format(prefixBatch))
    summaryFile = os.path.join(outDir, summaryFile)

    # List with names of output properties
    propertyNames = []
    for property in summaryProperties:
        propertyName = property.split('/')[-1]
        propertyNames.append(propertyName)

    summaryHeadings = ["file", "validationSuccess", "validationOutcome", "validationErrors"] + propertyNames

    with open(summaryFile, 'w', newline='', encoding='utf-8') as fSum:
        writer = csv.writer(fSum, delimiter=delimiter)
        writer.writerow(summaryHeadings)

    listFiles = getFilesFromTree(batchDir, extensions)
    # TODO: perhaps define extensions in profile?

    # start clock for statistics
    start = time.time()
    print("imgquad started: " + time.asctime())

    # Iterate over all files
    fileOut = ("{}.xml").format(prefixBatch)
    fileOut = os.path.join(outDir, fileOut)
    writeXMLHeader(fileOut)

    for myFile in listFiles:
        logging.info(("file: {}").format(myFile))
        myFile = os.path.abspath(myFile)
        fileResult = processFile(myFile, verboseFlag, schemas)
        if len(fileResult) != 0:
            validationSuccess = findEltValue(fileResult, 'validationSuccess', namespaces)
            validationOutcome = findEltValue(fileResult, 'validationOutcome', namespaces)
            with open(summaryFile, 'a', newline='', encoding='utf-8') as fSum:
                propValues = []
                for property in summaryProperties:
                    propertyValue = findEltValue(fileResult, property, namespaces)
                    propValues.append(propertyValue)

                validationErrors = []
                
                failedAsserts = fileResult.xpath("schematronReport/svrl:schematron-output/svrl:failed-assert/svrl:text", namespaces=namespaces)
                for failedAssert in failedAsserts:
                    validationErrors.append(failedAssert.text)
                validationErrorsString = '|'.join(validationErrors)
                
                writer = csv.writer(fSum, delimiter=delimiter)
                myRow = [myFile, validationSuccess, validationOutcome, validationErrorsString] + propValues
                writer.writerow(myRow)
            # Convert output to XML and add to output file
            outXML = etree.tostring(fileResult,
                                    method='xml',
                                    encoding='utf-8',
                                    xml_declaration=False,
                                    pretty_print=True)

            with open(fileOut,"ab") as f:
                f.write(outXML)

    writeXMLFooter(fileOut)

    # Timing output
    end = time.time()

    print("imgquad ended: " + time.asctime())

    # Elapsed time (seconds)
    timeElapsed = end - start
    timeInMinutes = round((timeElapsed / 60), 2)

    print("Elapsed time: {} minutes".format(timeInMinutes))


if __name__ == "__main__":
    main()
