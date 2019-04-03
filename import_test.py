import socket
import os
import time
import sys
from pdf2ps_convert import pdf_to_ps

filename = sys.argv[1]
print("the filename is %s:" %filename)
pdf_to_ps(filename)
