#!/usr/bin/env python2

from PyPDF2 import PdfFileReader, PdfFileWriter
import argparse

parser=argparse.ArgumentParser(description='Combine a bunch of pdf files into a single pdf file.')
parser.add_argument('pdfs',type=str,nargs='+',help='PDFs to combine (in the order of combination).')
parser.add_argument('-outfile',action='store',default='output.pdf',help='Name of output file.')
args=parser.parse_args()

output = PdfFileWriter()

for pdf in args.pdfs:
  inpdf=PdfFileReader(file(pdf,'rb'))
  for i in range(inpdf.getNumPages()):
    output.addPage(inpdf.getPage(i))

output.write(file(args.outfile,"wb"))
