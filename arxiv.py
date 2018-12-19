import urllib.request
import optparse
import re
import os
import subprocess
import tempfile
import string

from tex2csv import tex2csv

ptn_number = re.compile(r'(\w+/)?([\d\.v]+)')

def read_tex(filelist_tex):
    # Generate ascii text
    fulltext = ""
    for file_tex in filelist_tex:
        with open(file_tex, 'rb') as fh:
            buff = [chr(x) for x in fh.read() if chr(x) in string.printable]
        text = ''.join(buff)
        
        text=text.replace(r"\beq", r"\begin{equation}")
        #text.replace(r"\end\n", r"\begin{equation}")

        tag1 = r"\begin{document}"
        tag2 = r"\end{document}"
        pos1 = text.find(tag1) + len(tag1)
        if 0 <= pos1:
            text = text[pos1:]
        pos2 = text.find(tag2)
        if 0 <= pos2:
            text = text[:pos2]
        
        tag1 = r'\begin{thebibliography}'
        tag2 = r'\end{thebibliography}'
        pos1 = text.find(tag1)
        if 0 <= pos1:
            pos2 = text.find(tag2) + len(tag2)
            text = text[:pos1] + text[pos2:]
        fulltext += text
#    print(fulltext)
    return fulltext
    


if __name__ == '__main__':

    parser = optparse.OptionParser()
    parser.add_option('-r', '--reload', dest='reload',
                      action='store_true', default=False, help='Force reloading')
    opts, args = parser.parse_args()

    # https://arxiv.org/e-print/
    for item in args:
        url = 'https://arxiv.org/e-print/%s' % item
        out_title = item.replace('/', '_')
        file_tar_gz = os.path.abspath("%s.tar.gz" % out_title)

        if opts.reload or not os.path.isfile(file_tar_gz):
            print('Retrieving %s ...' % url)
            urllib.request.urlretrieve(url, file_tar_gz)
        else:
            print('%s already exists...' % file_tar_gz)

        with tempfile.TemporaryDirectory() as tmpdir:
            print('Extracting %s ...' % file_tar_gz)
            subprocess.call(['tar', '-zxf', file_tar_gz], cwd=tmpdir)

            filelist_tex = []
            for basedir, _, filelist in os.walk(tmpdir):
                for title in filelist:
                    if os.path.splitext(title)[-1] == '.tex':
                        filelist_tex += [os.path.join(basedir, title)]
            filelist_tex.sort()
            
            tex = read_tex(filelist_tex)
            
        with open("log.tex", "w") as fh:
            fh.write(tex)

        with tempfile.NamedTemporaryFile(suffix='.tex') as fh_tmp:
            fh_tmp.write(tex.encode('utf-8'))
            fh_tmp.flush()
            
            file_csv = out_title + '.csv.gz'
            
            print("Converting %s ..." % fh_tmp.name)
            tex2csv(fh_tmp.name, file_csv)
