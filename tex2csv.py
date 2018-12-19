import subprocess
import nltk
import gzip
import sys
import csv
import tempfile

def clean_tex(text):
    # Removing outside of document section:
    tag_doc1 = r"\begin{document}"
    tag_doc2 = r"\end{document}"
    pos_doc1 = text.find(tag_doc1)
    if 0 <= pos_doc1:
        pos_doc2 = text.find(tag_doc2) + len(tag_doc2)
        text = text[pos_doc1:pos_doc2]
        print("Cut doc")
    
    # Removing thebibliography section
    tag_bib1 = r"\begin{thebibliography}"
    tag_bib2 = r"\end{thebibliography}"
    pos_bib1 = text.find(tag_bib1)
    if 0 <= pos_bib1:
        pos_bib2 = text.find(tag_bib2) + len(tag_bib2)
        text = text[:pos_bib1] + text[pos_bib2:]
        print("Cut bib")
    return text

def tex2csv(file_tex, file_csv, ncolumn=24):

    with tempfile.NamedTemporaryFile(suffix='.tex') as fh_tmp:
        with open(file_tex) as fh_tex:
            fh_tmp.write(clean_tex(fh_tex.read()).encode('utf-8'))
        fh_tmp.flush()
        code = subprocess.check_output(["pandoc", "-i", fh_tmp.name, "--to", "plain"])
    text = code.decode('utf-8')

    buff = []
    for i, tmp1 in enumerate(text.split("$$")):
        if i % 2 == 0:
            for j, tmp2 in enumerate(tmp1.split("$")):
                if j % 2 == 0:
                    buff += nltk.tokenize.word_tokenize(tmp2)
                else:
                    buff += ['[Math]']
        else:
            buff += ['[Math]']

    if file_csv.endswith('.gz'):
        fh = gzip.open(file_csv, "wt")
    else:
        fh = open(file_csv, "wt")

    writer = csv.writer(fh)
    pos = 0
    while pos < len(buff):
        writer.writerow(buff[pos:pos+ncolumn])
        pos += ncolumn
    fh.close()

if __name__ == '__main__':
    tex2csv(sys.argv[1], sys.argv[2])
