import os
import shutil
import tempfile
import subprocess
from subprocess import PIPE
from bs4 import BeautifulSoup
import copy
from grobid_client.grobid_client import GrobidClient
from pydantic import FilePath

def duplicate_for_translate(soup, element):
    container = soup.new_tag("div", attrs={"class": "float-container"})
    left = soup.new_tag("div", attrs={"class": "float-child", "translate": "no"})
    left.append(element)
    right = soup.new_tag("div", attrs={"class": "float-child"})
    right.append(copy.copy(element))
    container.append(left)
    container.append(right)
    return(container)

def pdf2html2col(file):
    tmpdir = tempfile.TemporaryDirectory()
    tmpfilename = "file"
    file_path = f'{tmpdir.name}/{tmpfilename}.pdf'

    with open(file_path, 'w+b') as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    client = GrobidClient(config_path=os.path.join(os.path.abspath(os.path.join(__file__, os.pardir)), "grobid_config.json"))
    client.process("processFulltextDocument", tmpdir.name, tmpdir.name)

    tei_path = os.path.join(tmpdir.name, tmpfilename + ".tei.xml")
    html_path = os.path.join(tmpdir.name, tmpfilename + '.html')
    proc = subprocess.run(f'teitohtml5 "{tei_path}" "{html_path}"', shell=True, stdout=PIPE, stderr=PIPE)

    with open(html_path) as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    title = soup.find(class_="maintitle")
    toc = soup.find(class_="toc toc_body")
    body = soup.find_all(class_="teidiv0")
    figure = soup.find_all(class_="figure")
    etc = soup.find_all(class_="teidiv1")

    targets = [title] + [toc] + sum([b.contents for b in body], []) + list(figure) + sum([e.contents for e in etc], [])

    for target in targets:
        if target is None:
            continue
        translate_target = copy.copy(target)
        target.replace_with(duplicate_for_translate(soup, translate_target))

    soup.find(class_="references")["translate"] = "no"

    soup.head.append(soup.new_tag('style'))
    soup.head.style.append('''
        .float-container {
            display: flex;
        }
        
        .float-child {
            display: inline-block;
            width: 50%;
            margin-left: 2%;
            margin-right: 2%;
        }
    ''')

    return soup.prettify()
