#!/usr/bin/perl -w

# Script to read in an ASCII catalog of astronomical data and write it out as a
# Google Sky KML file with proper positional information.
#
# Version 0.0.2  (27 October 2009)
#
# CHANGELOG
#
# v0.0.3 (29Oct2009): Bugfixes, functionality increase
# 	- Fixed error with RA calculation
# 	- Added comment tag with version information to output
# 	- Better HTML formatting for <description> output
# v0.0.2 (27Oct2009): Functionality Increases
#	- added support for tab separated ASCII files
#	- RA and Dec can now be separated by blank spaces, 'h(d)ms' or ':'
#	- rudimentary icon ability (user specifies URL of icon)
# v0.0.1 (27Oct2009): Initial Version

# TODO/Wishlist:
# - allow user specified icons
# - permit multiple "Folders" in a single file (run an 'interactive' mode if no input file is given?)
# - add fleibility for using different colums as source name, RA&Dec, etc
# - add ability to add images. Perhaps ask user if they want to add images? Then allow them to give the path to 1-3 FITS images for a particular source.
# - probably should separate the various tasks into functions for ease of maintainence (e.g., header creation, icon creation, etc)

# usage:
# catalog.pl cat_file [icon]

# output file is cat_file with the .kml suffix instead of whatever suffix was there

# program flow:
# 1. open catalog file
# 2. open kml file for writing
# 3. write header and icon information to the kml file
# 4. write KML "Folder Information"
# 5. loop through catalog, write individual source information

$version='0.0.3';
$verdate='29 October 2009';

print "\nGoogle Sky catalog converter v$version ($verdate)\n";
print "Written by George Privon\n\n";

# look at the number of command line arguments
$nargs=$#ARGV+1;
if ($nargs == 1) {
  # no icon specified
  $icons=0;
  $catalog=$ARGV[0];
} elsif ($nargs == 2) {
  # icon specified
  $icons=1;
  $catalog=$ARGV[0];
  $icon=$ARGV[1];
} else {
  # oops! someone missed the memo
  print "Error, incorrect number of arguments. Usage:\n\n";
  print "$0 catalog [icon]\n";
  die();
}

# now that we have the arguments, load the catalog
open(CATALOG,$catalog) || die "Can't open catalog: $catalog for reading.\n\n";

print "Please type the name of your catalog as you wish it to appear in google: ";
$catname=<STDIN>;
chop($catname);

print "\nCreating a catalog named: $catname\n\n";

# load kml output file
$kmlcat=$catalog;
$kmlcat=~s/\.dat/.kml/;
open(KMLCAT,">$kmlcat") || die "Can't create KML file ($kmlcat) for writing.\n\n";
$i=0;

# write header
printf KMLCAT "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
printf KMLCAT "<kml xmlns=\"http://www.opengis.net/kml/2.2\" xmlns:gx=\"http://www.google.com/kml/ext/2.2\" xmlns:kml=\"http://www.opengis.net/kml/2.2\" xmlns:atom=\"http://www.w3.org/2005/Atom\" hint=\"target=sky\">\n";
printf KMLCAT "<!-- Generated by Google Sky catalog convertor $version ($verdate). Written by George Privon <gcp8y\@virginia.edu> -->\n";
printf KMLCAT "<Document>\n";

# put in catalog name
printf KMLCAT "\t<name>$catname</name>\n";

if ($icons) {
  # write information using a specific icon
  printf KMLCAT "\t<StyleMap id=\"icon1\">\n\t\t<Pair>\n\t\t\t<key>normal</key>\n";
  printf KMLCAT "\t\t\t<styleUrl>\#icon1-i</styleUrl>\n\t\t</Pair>\n\t\t<Pair>\n";
  printf KMLCAT "\t\t\t<key>highlight</key>\n\t\t\t<styleUrl>\#icon1-i</styleUrl>\n";
  printf KMLCAT "\t\t</Pair>\n\t</StyleMap>\n";

  # icon style
  printf KMLCAT "\t<Style id=\"icon1-i\">\n\t\t<IconStyle>\n\t\t\t<scale>1.3</scale>\n";
  printf KMLCAT "\t\t\t<Icon>\n\t\t\t\t<href>$icon</href>\n";
  printf KMLCAT "\t\t\t</Icon>\n\t\t\t<hotSpot x=\"0\" y=\"0\" xunits=\"pixels\" yunits=\"pixels\"/>\n";
  printf KMLCAT "\t\t</IconStyle>\n\t</Style>\n";
} else {
  # write a standard icon (pushpin)
  # style map first
  printf KMLCAT "\t<StyleMap id=\"icon1\">\n\t\t<Pair>\n\t\t\t<key>normal</key>\n";
  printf KMLCAT "\t\t\t<styleUrl>\#icon1-i</styleUrl>\n\t\t</Pair>\n\t\t<Pair>\n";
  printf KMLCAT "\t\t\t<key>highlight</key>\n\t\t\t<styleUrl>\#icon1-i</styleUrl>\n";
  printf KMLCAT "\t\t</Pair>\n\t</StyleMap>\n";

  # icon style
  printf KMLCAT "\t<Style id=\"icon1-i\">\n\t\t<IconStyle>\n\t\t\t<scale>1.3</scale>\n";
  printf KMLCAT "\t\t\t<Icon>\n\t\t\t\t<href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>\n";
  printf KMLCAT "\t\t\t</Icon>\n\t\t\t<hotSpot x=\"0\" y=\"0\" xunits=\"pixels\" yunits=\"pixels\"/>\n";
  printf KMLCAT "\t\t</IconStyle>\n\t</Style>\n";
}

# write the "folder" (catalog) header
printf KMLCAT "\t<Folder>\n\t\t<name>$catname</name>\n\t\t<open>1</open>\n";

# load catalog lines individually
while ($line=<CATALOG>) {
  if (substr($line,0,1) ne '#') {
    $i=$i+1;
    # this line is a valid data line
    # assume a CSV or tab-separated table
#    ($source,$source1,$ra,$dec,$junk)=split(/[,\t]/,$line);
    ($source,$ra,$dec,$Lir,$irac36,$irac45,$irac58,$irac80,$mips24,$mips70,$mips160,$irssh,$irslh,$irssl,$irsll,$acsf435,$acsf814,$galexnuv,$galexfuv,$chandraacis)=split(/[,\t]/,$line);
#    $source1=~s/\s+$//;

    printf KMLCAT "\t\t<Placemark>\n\t\t\t<name>$source</name>\n";

    # write a lengthy description
    printf KMLCAT "\t\t\t<description><![CDATA[<p>Log(L_IR/L_sun)=$Lir</p>";
    #IRAC
    printf KMLCAT "<h4>Available data</h4>\n<p>IRAC: ";
    if ($irac36 eq 'Y') {
      printf KMLCAT "3.6, ";
    }
    if ($irac45 eq 'Y') {
      printf KMLCAT "4.5, ";
    }
    if ($irac58 eq 'Y') {
      printf KMLCAT "5.8, ";
    }
    if ($irac80 eq 'Y') {
      printf KMLCAT "8.0<br />\n";
    }
    if ($irac36 eq 'X' && $irac45 eq 'X' && $irac58 eq 'X' && $irac80 eq 'X') {
      printf KMLCAT "none<br />\n";
    }
    # MIPS
    printf KMLCAT "MIPS: ";
    if ($mips24 eq 'Y') {
      printf KMLCAT "24, ";
    }
    if ($mips70 eq 'Y') {
      printf KMLCAT "70, ";
    }
    if ($mips160 eq 'Y') {
      printf KMLCAT "160<br />\n";
    }
    if ($mips24 eq 'X' && $mips70 eq 'X' && $mips160 eq 'X') {
      printf KMLCAT "none<br />\n";
    }
    # IRS
    printf KMLCAT "IRS: ";
    if ($irssh eq 'Y') {
      printf KMLCAT "SH, ";
    }
    if ($irslh eq 'Y') {
      printf KMLCAT "LH, ";
    }
    if ($irssl eq 'Y') {
      printf KMLCAT "SL, ";
    }
    if ($irsll eq 'Y') {
      printf KMLCAT "LL<br />\n";
    }
    if ($irssh eq 'X' && $irslh eq 'X' && $irssl eq 'X' && $irsll eq 'X') {
      printf KMLCAT "none<br />\n";
    }
    # ACS
    printf KMLCAT "HST ACS: ";
    if ($acsf435 eq 'Y') {
      printf KMLCAT "F435, ";
    }
    if ($acsf814 eq 'Y') {
      printf KMLCAT "F814<br />\n";
    }
    if ($acsf435 eq 'X' && $acsf814 eq 'X') {
      printf KMLCAT "none<br />\n";
    }
    # GALEX
    printf KMLCAT "Galex: ";
    if ($galexnuv eq 'Y') {
      printf KMLCAT "NUV, ";
    }
    if ($galexfuv eq 'Y') {
      printf KMLCAT "FUV<br />\n";
    }
    if ($galexnuv eq 'X' && $galexfuv eq 'X') {
      printf KMLCAT "none<br />\n";
    }
    # Chandra ACIS
    printf KMLCAT "Chandra: ";
    if ($chandraacis eq 'Y') {
      printf KMLCAT "ACIS<br />\n";
    } else {
      printf KMLCAT "none<br />\n";
    }
    printf KMLCAT "</p>]]></description>\n";

    printf KMLCAT "\t\t\t<LookAt>\n";

    # compute latitude and longitude (RA and Dec) in degrees
    ($hour,$min,$sec)=split(/[: hms]/,$ra);
    ($deg,$amin,$asec)=split(/[: dms]/,$dec);
    $long=15.*$hour+15.*$min/60.+15.*$sec/3600.;
    # in Googlesky, longitude of 0 is RA of 12. Compensate for this
    $long=$long-180.;
    # do this properly for positive/negative dec
    if ($deg > 0.) {
      $lat=$deg+$amin/60.+$asec/3600.;
    } else {
      $lat=$deg-$amin/60.-$asec/3600.;
    }

    printf KMLCAT "\t\t\t\t<longitude>$long</longitude>\n";
    printf KMLCAT "\t\t\t\t<latitude>$lat</latitude>\n";
    printf KMLCAT "\t\t\t\t<altitude>0</altitude>\n";
    printf KMLCAT "\t\t\t\t<range>3500</range>\n";
    printf KMLCAT "\t\t\t\t<tilt>0</tilt>\n";
    printf KMLCAT "\t\t\t\t<heading>0</heading>\n";
    printf KMLCAT "\t\t\t\t<altitudeMode>relativeToGround</altitudeMode>\n";

    # finish up this entry
    printf KMLCAT "\t\t\t</LookAt>\n\t\t\t<styleUrl>#icon1</styleUrl>\n";
    printf KMLCAT "\t\t\t<Point>\n\t\t\t\t<coordinates>$long,$lat</coordinates>\n";
    printf KMLCAT "\t\t\t</Point>\n\t\t</Placemark>\n";
  } # otherwise, move on to the next line
}


# write the closing "folder" (catalog) kml
printf KMLCAT "\t</Folder>\n</Document>\n</kml>";

# close files
close(CATALOG);
close(KMLCAT);

# concluding notes
print "Finishing converting $i records in $catalog to KML. Written to: $kmlcat\n";