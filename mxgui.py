#!/bin/python
# -*-coding:utf8-*-

import tkinter as tk
import tkinter.scrolledtext as tkst
import optparse

import os
import sys
from lib import corpus

mydir = os.path.dirname(__file__)


class App:
    


    def __init__(self, default_keyword=''):

        self.corpus = corpus.Corpus(".cache")

        self.root = tk.Tk()
        self.root.title('mu-exampler')

        self.top = tk.Frame(self.root)
        self.lab_status = tk.Label(self.root, foreground="darkgray")
        self.pw = tk.PanedWindow(self.root, sashwidth=5, orient=tk.VERTICAL)
        
        self.top.pack(fill=tk.X)
        self.lab_status.pack(anchor=tk.W)
        self.pw.pack(expand=True, fill=tk.BOTH)

        self.txt_keyword = tk.Entry(self.top)
        self.txt_keyword.insert(0, default_keyword)
        self.chk_stemming = tk.Checkbutton(self.top, text='Stemming')
        self.btn_search = tk.Button(self.top, text="Search")

        self.lb_pattern = tk.Listbox(self.pw)
        self.txt_result = tkst.ScrolledText(self.pw, background='cornsilk')
        self.txt_result.tag_config('li', foreground='white', background='blue')
        self.txt_result.tag_config('em', foreground="blue", underline=1)

        self.btn_search.bind("<Button-1>", self.search)
        self.lb_pattern.bind('<<ListboxSelect>>', self.select)

        self.txt_keyword.bind("<Return>", self.search)
        self.txt_keyword.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.btn_search.pack(side=tk.LEFT)
        self.chk_stemming.pack(side=tk.LEFT)

        self.pw.add(self.lb_pattern)
        self.pw.add(self.txt_result)

        self.root.mainloop()

    def search(self, e=None):
        self.keyword = self.txt_keyword.get().strip()
        if self.keyword:
            
            if "*" not in self.keyword:
                self.keyword += " *"
            
            self.lab_status.config(text='Searching...')
            self.txt_result.delete('1.0', tk.END)
            self.lb_pattern.delete(0, tk.END)
            self.result = self.corpus.find(self.keyword)
            self.number = sum([len(x) for x in self.result])
            for item in self.result:
                self.lb_pattern.insert(tk.END, 
                    "%s [%d found]" % (" ".join(item[0][0]), len(item))
                )
                print(" ".join(item[0][0]))
            
            self.lab_status.config(
                text='%d patterns (total %d snippets) are found' % (len(self.result), self.number)
            )

    def select(self, e):
        self.txt_result.delete('1.0', tk.END)
        for i in self.lb_pattern.curselection():
            for j, (main, head, tail) in enumerate(self.result[i], start=1):
                self.txt_result.insert(tk.END, '%d.' % j, 'li')
                self.txt_result.insert(tk.END, ' ' + ' '.join(head) + ' ')
                self.txt_result.insert(tk.END, ' '.join(main), 'em')
                self.txt_result.insert(tk.END,  ' ' + ' '.join(tail) + '\n')



def rebuild_database(directory):
    print("Rebuilding cache...")
    c = corpus.Corpus()
    for item in os.listdir(directory):
        if item.endswith('.csv') or item.endswith('.csv.gz'):
            print("Loading %s" % item)
            c.migrate(os.path.join(directory, item))
    c.dump_cache(".cache")
    

if __name__ == '__main__':
        parser = optparse.OptionParser()
        parser.add_option("-d", "--directory", dest="directory", 
            type=str, default=mydir, help="csv directory")            
        parser.add_option("-r", "--rebuild", dest="rebuild", 
            action="store_true", default=False,  help="rebuild database")            
        opts, args = parser.parse_args()
        
        if opts.rebuild:
            rebuild_database(opts.directory)
            sys.exit(0)

        
        app = App('* discuss * * section')
