import os
import time



def pdf_to_ps(file_pdf):
    file_dir = "/home/dell/Documents/pdffiles/single_test/"
    pdf_filename = file_dir + file_pdf

    def pdf2ps_convert(filename) :

        os.system("pdftops -level3 " + pdf_filename)

    start_time = time.time()
    pdf2ps_convert(pdf_filename)
    end_time = time.time()

    last_time = end_time - start_time
    print("Convertion cost %s time:" %last_time)
    print("Convertion finisheld! Starting printing...")