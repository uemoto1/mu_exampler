import urllib.request
import optparse
import re
import os
import subprocess
import tempfile
import shutil
import chardet

from tex2csv import tex2csv

ptn_number = re.compile(r'(\d+\.\d+)')


    


if __name__ == '__main__':
    
    parser = optparse.OptionParser()
    parser.add_option('-r', '--reload', dest='reload', 
        action='store_true', default=False, help='Force reloading')            
    opts, args = parser.parse_args()
    
    for item in args:
        m_number = ptn_number.search(item)
        if m_number:
            url = 'https://arxiv.org/e-print/' + m_number.group(1)
            file_tar_gz = os.path.abspath("%s.tar.gz" % m_number.group(1))
            
            if opts.reload or not os.path.file(file_tar_gz):
                print('Retrieving %s ...' % url)
                urllib.request.urlretrieve(url, file_tar_gz)
            else:
                print('%s already exists...' % file_tar_gz)
            
            with tempfile.TemporaryDirectory() as tmpdir:
                print('Extracting %s ...' % file_tar_gz)
                subprocess.call(['tar', '-zxf', file_tar_gz], cwd=tmpdir)
            
                for basedir, _, filelist in os.walk(tmpdir):
                    for title in filelist:
                        if os.path.splitext(title)[-1] == '.tex':
                            file_tex = os.path.join(basedir, title)
                            
                        
                        file_tex2 = os.path.join(
                            opts.directory, m_number.group(1) + '.tex'
                        )   
                        
                        file_csv = os.path.join(
                            opts.directory, m_number.group(1) + '.csv.gz'
                        )    
                        
                        print("Reading ")
                        with open(file_tex, 'rb') as fh:
                            buff = fh.read()
                        
                        cd = chardet.detect(buff)
                        print('Detecting charset: %s' % cd['encoding'])
                        buff2 = buff.decode(cd['encoding'])
                        
                        print('Converting %s ...' % file_tex2)
                    with open(file_tex2, 'w') as fh:
                        fh.write(buff2)
                    
                    tex2csv(file_tex, file_csv)
                    break
                        
                
                
            dir_src = os.path.join(opts.directory, m_number.group(1))
            
        
    
        
