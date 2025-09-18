<?xml version="1.0"?>
<!-- Schematron rules for  Beeldstudio Retro files-->

<s:schema xmlns:s="http://purl.oclc.org/dsdl/schematron">

<s:pattern>
    <s:title>Beeldstudio Retro checks</s:title>

    <!-- Checks at image level -->
    <s:rule context="//properties/image">
        <!-- Checks on expected image format -->
        <s:assert test="(count(format) > 0)">Missing format tag</s:assert>
        <s:assert test="(format = 'JPEG') or (format = 'TIFF')">Unexpected image format (expected: JPEG or TIFF)</s:assert>
        <!-- Check on icc profile -->
        <s:assert test="(count(icc_profile) > 0)">Missing ICC profile</s:assert>
        <!-- Check on absence of any exceptions while parsing the image -->
        <s:assert test="(count(exceptions/exception) = 0)">Properties extraction at image level resulted in one or more exceptions</s:assert>
    </s:rule>

    <!-- Checks at Exif tag level -->
        <s:rule context="//properties/image/exif">
        <!-- Checks for X- and Y resolution tags -->
        <s:assert test="(count(XResolution) > 0)">Missing XResolution tag</s:assert>
        <s:assert test="(count(YResolution) > 0)">Missing YResolution tag</s:assert>
        <!-- Checks for camera related tags -->
        <s:assert test="(count(Make) > 0)">Missing Make tag</s:assert>
        <s:assert test="(count(Model) > 0)">Missing Model tag</s:assert>
        <s:assert test="(count(LensMake) > 0)">Missing LensMake tag</s:assert>
        <s:assert test="(count(LensSpecification) > 0)">Missing LensSpecification tag</s:assert>
        <s:assert test="(count(LensModel) > 0)">Missing LensModel tag</s:assert>
        <s:assert test="(count(LensSerialNumber) > 0)">Missing LensSerialNumber tag</s:assert>
        <!-- Checks for camera settings tags -->
        <s:assert test="(count(ExposureTime) > 0)">Missing ExposureTime tag</s:assert>
        <s:assert test="(count(FNumber) > 0)">Missing FNumber tag</s:assert>
        <s:assert test="(count(ISOSpeedRatings) > 0)">Missing ISOSpeedRatings tag</s:assert>
        <s:assert test="(count(WhiteBalance) > 0)">Missing WhiteBalance tag</s:assert>
        <!-- Check for Software tags -->
        <s:assert test="(count(Software) > 0)">Missing Software tag</s:assert>
    </s:rule>

</s:pattern>
</s:schema>
