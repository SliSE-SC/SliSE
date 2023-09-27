import sys, json
import os,re
from typing import Optional

VOID_START = re.compile('//|/\*|"|\'')
PRAGMA = re.compile('pragma solidity.*?;')
QUOTE_END = re.compile("(?<!\\\\)'")
DQUOTE_END = re.compile('(?<!\\\\)"')

def remove_void(line):
    while m := VOID_START.search(line):
        if m[0] == '//':
            return (line[:m.start()], False)
        if m[0] == '/*':
            end = line.find('*/', m.end())
            if end == -1:
                return (line[:m.start()], True)
            else:
                line = line[:m.start()] + line[end+2:]
                continue
        if m[0] == '"':
            m2 = DQUOTE_END.search(line[m.end():])
        else: # m[0] == "'":
            m2 = QUOTE_END.search(line[m.end():])
        if m2:
            line = line[:m.start()] + line[m.end()+m2.end():]
            continue
        return (line[:m.start()], False)
    return (line, False)



def get_pragma(file: str) -> Optional[str]:
    in_comment = False
    for line in file.splitlines():
        if in_comment:
            end = line.find('*/')
            if end == -1:
                continue
            else:
                line = line[end+2:]
        line, in_comment = remove_void(line)
        if m := PRAGMA.search(line):
            return m[0]
    return None





def get_solc(filename):
    with open(filename) as f:

        contract_source_code = f.read()
        solc_compiler = get_pragma(contract_source_code)
        if solc_compiler != None:
            pragma = re.sub(r'pragma solidity','',solc_compiler)
            pragma = re.sub(r">=0\.", r"^0.", pragma)
            pragma = re.sub(r"\ 0\.", r"^0.", pragma)
            pragma1 = re.findall(r'\^(.*);', pragma)
        else:
            pragma1 = ["0.4.25"]
    return(pragma1[0])


