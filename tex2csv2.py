#!/usr/bin/env python3
import optparse
import string
import re
import sys
import os
import chardet
import csv

ptn_input = re.compile(r'\\input\{\s*(\S+)\s*\}')


def extract_texdir(texdir):
    cache = {}
    for dirname, dirlist, filelist in os.walk(texdir):
        for title in filelist:
            if os.path.splitext(title)[1] == '.tex':
                file_tex = os.path.abspath(os.path.join(dirname, title))
                with open(file_tex, 'rb') as fh_tex:
                    buff = fh_tex.read()
                charset = chardet.detect(buff)
                cache[file_tex] = buff.decode(charset['encoding'])

    def _expand_inp(m, file_tex):
        title = '%s.tex' % os.path.splitext(m.group(1))[0]
        dirname = os.path.dirname(file_tex)
        file_tex_child = os.path.abspath(os.path.join(dirname, title))
        return _read_tex(file_tex_child)

    def _read_tex(file_tex):
        stderr.write('# Merging %s ...' % file_tex)
        tmp = cache[file_tex]
        tmp = ptn_input.sub(lambda m: _expand_inp(m, file_tex), tmp)
        return tmp

    count = [(v.count(r"\input"), k) for k, v in cache.items()]
    count.sort(reverse=True)

    _, file_main_tex = count[0]

    tmp = _read_tex(file_main_tex)

    return tmp


def run(inputfile, outputfile):

    if os.path.isfile(inputfile):
        with open(inputfile) as fh:
            text = fh.read()
    elif os.path.isdir(inputfile):
        text = extract_texdir(text)
    else:
        sys.stderr.write("ERROR! '%s' is not found!\n" % inputfile)
        sys.exit(-1)

    with tempfile.NamedTemporaryFile(suffix='.tex') as fh_tmp:
        fh_tmp.write(text.encode('utf-8'))
        fh_tmp.flush()

        result = subprocess.check_output(
            ['pandoc', '-i', fh_tmp.name, '--to=plain'
        ])
        
        text = result.decode('utf-8')

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

        if outputfile.endswith('.gz'):
            fh = gzip.open(outputfile, "wt")
        else:
            fh = open(outputfile, "wt")

        writer = csv.writer(fh)
        pos = 0
        while pos < len(buff):
            writer.writerow(buff[pos:pos+ncolumn])
            pos += ncolumn
        fh.close()


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-i", "--inputfile", dest="inputfile",
                      type=str, default='', help="inputfile")
    parser.add_option("-o", "--outputfile", dest="outputfile",
                      type=str, default='', help="outputfile")
    opts, args = parser.parse_args()

    main(opts.inputfile, opts.outputfile)
