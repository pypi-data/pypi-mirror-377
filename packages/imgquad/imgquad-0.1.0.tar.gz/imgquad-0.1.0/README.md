# IMaGe QUality Assessment for Digitisation batches

## What is imgquad?

Imgquad is a simple tool for automated quality assessment of images in digitisation batches against a user-defined technical profile. It uses [Pillow](https://pillow.readthedocs.io/) to extract the relevant technical properties.

These properties are serialized to a simple XML structure, which is then evaluated against [Schematron rules](http://en.wikipedia.org/wiki/Schematron) that define the expected/required technical characteristics.


## Installation

Install the software with the [pip package manager](https://en.wikipedia.org/wiki/Pip_(package_manager)):

```
pip install imgquad
```

Then run imgquad once:

```
imgquad
```

Depending on your system, imgquad will create a folder named *imgquad* in one of the following locations: 

- For Linux, it will use the location defined by environment variable *$XDG_CONFIG_HOME*. If this variable is not set, it will use the *.config* directory in the user's home folder (e.g. `/home/johan/.config/imgquad`). Note that the *.config* directory is hidden by default.
- For Windows, it will use the *AppData\Local* folder (e.g. `C:\Users\johan\AppData\Local\imgquad`).

The folder contains two subdirectories named *profiles* and *schemas*, which are explained in the "Profiles" and "Schemas" sections below.

## Command-line syntax

The general syntax of imgquad is:

```
usage: imgquad [-h] [--version] {process,list,copyps} ...
```

Imgquad has three sub-commands:

|Command|Description|
|:-----|:--|
|process|Process a batch.|
|list|List available profiles and schemas.|
|copyps|Copy default profiles and schemas to user directory.|

### process command

Run imgquad with the *process* command to process a batch. The syntax is:

```
usage: imgquad process [-h] [--prefixout PREFIXOUT] [--outdir OUTDIR]
                       [--delimiter DELIMITER] [--verbose]
                       profile batchDir
```

The *process* command expects the following positional arguments: 

|Argument|Description|
|:-----|:--|
|profile|This defines the validation profile. Note that any file paths entered here will be ignored, as Imgquad only accepts  profiles from the profiles directory. You can just enter the file name without the path. Use the *list* command to list all available profiles.|
|batchDir|This defines the batch directory that will be analyzed.|

In addition, the following optional arguments are available:

|Argument|Description|
|:-----|:--|
|--prefixout, -p|This defines a text prefix on which the names of the output files are based (default: "pq").|
|--outdir, -o|This defines the directory where output is written (default: current working directory from which imgquad is launched).|
|--delimiter, -d|This defines the delimiter that is used in the output summary file (default: ';')|
|--verbose, -b|This tells imgquad to report Schematron output in verbose format.|

In the simplest case, we can call imgquad with the profile and the batch directory as the only arguments:

```
imgquad process beeldstudio-retro.xml ./mybatch
```

Imgquad will now recursively traverse all directories and files inside the "mybatch" directory, and analyse all image files (based on a file extension match).

### list command

Run imgquad with the *list* command to get a list of the available profiles and schemas, as well as their locations. For example:

```
imgquad list
```

Results in:

```
Available profiles (directory /home/johan/.config/imgquad/profiles):
  - mh-2025-tiff.xml
Available schemas (directory /home/johan/.config/imgquad/schemas):
  - mh-2025-tiff-600.sch
```

### copyps command

If you run imgquad with the *copyps* command, it will copy the default profiles and schemas that are included in the installation over to your user directory.

**Warning:** any changes you made to the default profiles or schemas will be lost after this operation, so proceed with caution! If you want to keep any of these files, just make a copy and save them under a different name before running the *copyps* command.

## Profiles

A profile is an XML file that defines how a digitisation batch is evaluated. Here's an example:

```xml
<?xml version="1.0"?>

<profile>

<!-- Middeleeuwse Handschriften, 2025 specs (TIFF)-->

<!-- File extensions that will be processed (case insensitive) -->
<extension>tif</extension>
<extension>tiff</extension>

<!-- Namespace definitions (used in summaryProperty paths)-->
<ns uri="adobe:ns:meta/" prefix="x"/>
<ns uri="http://www.w3.org/1999/02/22-rdf-syntax-ns#" prefix="rdf"/>
<ns uri="http://ns.adobe.com/photoshop/1.0/" prefix="photoshop"/>

<!-- Properties that are written to summary file -->
<summaryProperty>properties/image/format</summaryProperty>
<summaryProperty>properties/image/icc_profile_name</summaryProperty>
<summaryProperty>properties/image/tiff/XResolution</summaryProperty>
<summaryProperty>properties/image/tiff/YResolution</summaryProperty>
<summaryProperty>properties/image/tiff/ResolutionUnit</summaryProperty>
<summaryProperty>properties/image/tiff/ImageWidth</summaryProperty>
<summaryProperty>properties/image/tiff/ImageLength</summaryProperty>
<summaryProperty>properties/image/tiff/BitsPerSample</summaryProperty>
<summaryProperty>properties/image/tiff/Copyright</summaryProperty>
<summaryProperty>properties/image/exif/ColorSpace</summaryProperty>
<summaryProperty>properties/image/exif/Compression</summaryProperty>
<summaryProperty>properties/image/exif/Software</summaryProperty>
<summaryProperty>properties/image/exif/DateTimeOriginal</summaryProperty>
<summaryProperty>properties/image/exif/Model</summaryProperty>
<summaryProperty>properties/image/exif/Make</summaryProperty>
<summaryProperty>properties/image/exif/ShutterSpeedValue</summaryProperty>
<summaryProperty>properties/image/exif/ApertureValue</summaryProperty>
<summaryProperty>properties/image/exif/ISOSpeedRatings</summaryProperty>
<!-- Below properties can be encoded as either sub-elements or attibutes of
an rdf:Description element, so they are duplicated here to cover both cases -->
<summaryProperty>properties/image/x:xmpmeta/rdf:RDF/rdf:Description/photoshop:Headline</summaryProperty>
<summaryProperty>properties/image/x:xmpmeta/rdf:RDF/rdf:Description/photoshop:Credit</summaryProperty>
<summaryProperty>properties/image/x:xmpmeta/rdf:RDF/rdf:Description/@photoshop:Headline</summaryProperty>
<summaryProperty>properties/image/x:xmpmeta/rdf:RDF/rdf:Description/@photoshop:Credit</summaryProperty>

<!-- Schematron schema definitions -->

<schema>mh-2025-tiff-600.sch</schema>

</profile>
```

The profile is made up of the following components:

1. One or more *extension* elements, which tell imgquad what file extensions to look for. Imgquad handles file extensions in a case-insensitive way, so *tif* covers both "rubbish.tif" and "rubbish.TIF".
2. Zero or more *ns* elements, each of which maps a namespace prefix to its corresponding uri.
3. One or more *summaryProperty* elements, which define the properties that are written to the summary file. Each summary property is expressed as an xpath expression. 
4. One or more *schema* elements, that each link a file or directory naming pattern to a Schematron file (explained in the next section).

In the example, there's only one  *schema* element, which is used for all processed images. Optionally, each *schema* element may contain *type*, *match* and *pattern* attributes, which define how a schema is linked to file or directory names inside the batch:

- If **type** is "fileName", the matching is based on the naming of an image. In case of "parentDirName" the matching uses the naming of the direct parent directory of an image.
- The **match** attribute defines whether the matching pattern with the file or directory name is exact ("is") or partial ("startswith", "endswith", "contains".)
- The **pattern** attribute defines a text string that is used for the match.

See the [pdfquad documentation](https://github.com/KBNLresearch/pdfquad#profiles) for an example of how these attributes are used.

### Available profiles

Currently the following profiles are included:

|Profile|Description|
|:--|:--|
|mh-2025-tiff.xml|Profile for digitised medieval manuscripts.|

## Schemas

Schemas contain the Schematron rules on which the quality assessment is based. Some background information about this type of rule-based validation can be found in [this blog post](https://www.bitsgalore.org/2012/09/04/automated-assessment-jp2-against-technical-profile). Currently the following schemas are included:

### mh-2025-tiff-600.sch

This is a schema for digitised medieval manuscripts. It includes the following checks:

|Check|Value|
|:---|:---|
|Image format|TIFF|
|ICC profile name|eciRGB v2|
|XResolution TIFF tag|tag exists|
|YResolution TIFF tag|tag exists|
|XResolution|600 (+/- 1) |
|YResolution|600 (+/- 1) |
|ResolutionUnit TIFF tag|tag exists|
|ResolutionUnit|2 (inches)|
|ImageWidth TIFF tag|tag exists|
|ImageLength TIFF tag|tag exists|
|BitsPerSample TIFF tag|tag exists|
|BitsPerSample|'8 8 8'|
|ICCProfile TIFF tag|tag exists|
|Copyright TIFF tag|tag exists|
|ColorSpace EXIF tag|tag exists|
|ColorSpace|65535 (Uncalibrated)|
|Compression EXIF tag|tag exists|
|Compression|1 (Uncompressed)|
|Software EXIF tag|tag exists|
|DateTimeOriginal EXIF tag|tag exists|
|Model EXIF tag|tag exists|
|Make EXIF tag|tag exists|
|ShutterSpeedValue EXIF tag|tag exists|
|ApertureValue EXIF tag|tag exists|
|ISOSpeedRatings EXIF tag|tag exists|
|photoshop:Headline|defined in XMP metadata as either element `rdf:RDF/rdf:Description/photoshop:Headline`, or attribute `rdf:RDF/rdf:Description/@photoshop:Headline`|
|photoshop:Credit|defined in XMP metadata as either element `rdf:RDF/rdf:Description/photoshop:Credit`, or attribute `rdf:RDF/rdf:Description/@photoshop:Credit`|

The schema also includes an additional check on any exceptions that occurred while parsing the image, as this may indicate a corrupted file.

## Output

Imgquad reports the following output:

### Comprehensive output file (XML)

For each batch, Imgquad generates one comprehensive output file in XML format. This file contains, for each image, all extracted properties, as well as the Schematron report and the assessment status. <!-- TODO add example file [Here's an example file](./examples/pq_batchtest_001.xml).-->

### Summary file (CSV)

This is a comma-delimited text file that summarises the analysis. At the minimum, Imgquad reports the following columns for each image:

|Column|Description|
|:-----|:--|
|file|Full path to the image file.|
|validationSuccess|Flag with value *True* if Schematron validation was succesful, and *False* if not. A value *False* indicates that the file could not be validated (e.g. because no matching schema was found, or the validation resulted in an unexpected exception)|
|validationOutcome|The outcome of the Schematron validation/assessment. Value is *Pass* if file passed all tests, and *Fail* otherwise. Note that it is automatically set to *Fail* if the Schematron validation was unsuccessful (i.e. "validationSuccess" is *False*)|
|validationErrors|List of validation errors (separated by "\|" characters).|

In addition, the summary file contains additional columns with the properties that are defined by the *summaryProperty* elements in the profile.

<!-- TODO add example

Here's an example:

``` csv
```

-->

## Licensing

Imgquad is released under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).

## Useful links

- [Schematron](http://en.wikipedia.org/wiki/Schematron)


