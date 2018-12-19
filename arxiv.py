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
    parser.add_option('-d', '--directory', dest='directory', 
        type=str, default=os.curdir, help='Output directory')            
    opts, args = parser.parse_args()
    
    for item in args:
        m_number = ptn_number.search(item)
        if m_number:
            url = 'https://arxiv.org/e-print/' + m_number.group(1)
            
            with tempfile.TemporaryDirectory() as tmpdir:
                file_tgz = os.path.join(tmpdir, m_number.group(1) + '.tgz')
            
                print('Retrieving %s ...' % url)
                urllib.request.urlretrieve(url, file_tgz)
            
                print('Extracting %s ...' % file_tgz)
                subprocess.call(['tar', '-zxf', file_tgz], cwd=tmpdir)
                
                for title in os.listdir(tmpdir):
                    if os.path.splitext(title)[-1] == '.tex':
                        file_tex = os.path.join(tmpdir, title)
                        
                        file_tex2 = os.path.join(
                            opts.directory, m_number.group(1) + '.tex'
                        )   
                        
                        file_csv = os.path.join(
                            opts.directory, m_number.group(1) + '.csv.gz'
                        )    
                        
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
            
        
    
        
