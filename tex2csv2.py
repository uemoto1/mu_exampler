#!/usr/bin/env python3
import optparse
import string
import re
import sys
import os
import chardet

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
        tmp = cache[file_tex]
        tmp = ptn_input.sub(lambda m: _expand_inp(m, file_tex), tmp)
        return tmp
    
    count = [(v.count(r"\input"), k) for k, v in cache.items()]
    count.sort(reverse=True)
    
    _, file_main_tex = count[0]
    
    tmp = _read_tex(file_main_tex)
    
    return tmp
    


def main():
    parser = optparse.OptionParser()
    parser.add_option("-d", "--directory", dest="directory", 
        type=str, default=mydir, help="csv directory")            
    parser.add_option("-r", "--rebuild", dest="rebuild", 
        action="store_true", default=False,  help="rebuild database")            
    opts, args = parser.parse_args()


dat = extract_texdir("test")

with open("out.tex", 'wt') as fh:
    fh.write(dat)
