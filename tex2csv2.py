#!/usr/bin/env python3
import optparse
import string
import re
import sys
import os
import chardet

ptn_input = re.compile(r'\\input\{\s*(\S+)\s*\}')

def read_tex(file_tex):
    
    basedir = os.path.dirname(file_tex)
    
    def _is_upper_level(file_item):
        rel = os.path.relpath(file_item, basedir)
        return rel.startswith(os.pardir)
        
    def _expand_input(m):
        title_tex = '%s.tex' % os.path.splitext(m.group(1))[0]
        file_tex_child = os.path.join(basedir, title_tex)
        if not _is_upper_level(file_tex_child):
            return read_tex(file_tex_child)
    
    sys.stderr.write('# Reading %s ...\n' % file_tex)
    
    with open(file_tex, 'rb') as fh_tex:
        buff = fh_tex.read()
    charset = chardet.detect(buff)['encoding']
    
    sys.stderr.write('# Decoding charset from %s ...\n' % charset)
    text = buff.decode(charset)
    text = ptn_input.sub(_expand_input, text)
    
    return text



def main():
    parser = optparse.OptionParser()
    parser.add_option("-d", "--directory", dest="directory", 
        type=str, default=mydir, help="csv directory")            
    parser.add_option("-r", "--rebuild", dest="rebuild", 
        action="store_true", default=False,  help="rebuild database")            
    opts, args = parser.parse_args()


dat = read_tex("test/wannier-2col.tex")

# rule_list = [
#     [r'\beq', r'\begin{equation}'],
#     [r'\eeq', r'\end{equation}'],
#     [r'\newcommand', r'%%']
#     [r'\def', r'%%']
# ]
rule_list = []

for x, y in rule_list:
    dat = dat.replace(x, y)

with open("out.tex", 'wt') as fh:
    fh.write(dat)
