#!/usr/bin/perl
#
# tspec_text.pl
# Take a triplespec spectra in FITS format and output it to a text file
#
# Last updated: 05 November 2008 by George Privon
#
# CHANGELOG:
# 05 Nov 2008 - Initial Version

use strict;
use warnings;
use Astro::FITS::CFITSIO;
use PDL;

my $infile=$ARGV[0].".fits";
my $outfile=$ARGV[0].".txt";

my $status = 0;
my $ptr=Astro::FITS::CFITSIO::open_file($infile,Astro::FITS::CFITSIO::READONLY(),$status);

print "Status is: $status\n";

my $naxes=zeroes(2);

$ptr->get_img_parm(undef,undef,$naxes,$status);
my ($naxis1,$naxis2)=@$naxes;

# assuming we have a 2D image...
#my $image=zeroes $naxis2,$naxis1;
#my $image = zeroes 5,5;
print "$naxis1,$naxis2\n";

my ($image, $nullarray, $anynull);
#$ptr->read_pix(Astro::FITS::CFITSIO::TDOUBLE(),[1,1],$naxis1*$naxis2,0,$main::image,undef,$status);
$ptr->read_pixnull(Astro::FITS::CFITSIO::TDOUBLE(),[1,1], $naxis1*$naxis2,$image,$nullarray,$anynull,$status);
if ($anynull) {
  print "Null values in FITS file were replaced with NaN\n";
}
print "Status is: $status\n";

# now that we're done, close the file
$ptr->close_file($status);

# now write the image out to a file
open OUT, "> $outfile" or die "Can't open $outfile for writing.";
#for (my $i=0;$i<$naxis1;$i++) {
for (my $i=0;$i<2;$i=$i+1) {
  print $i;
  print OUT $main::image[$i][0];
  print OUT $main::image[$i][1];
  print OUT $main::image[$i][2];
}
close OUT;

exit;
