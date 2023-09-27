from solcx import install_solc_pragma, set_solc_version_pragma, compile_files, get_compilable_solc_versions, get_installable_solc_versions
from solcx.exceptions import SolcNotInstalled
from solcx.install import get_executable
from solidity_parser.parser import parse
from print_pragma_version import get_solc
import os
import glob
import re
from solidity.source_map import SourceMap



def switch_global_version(file_name):
    
    PATTERN = re.compile(r"pragma solidity\s*(?:\^|>=|<=)?\s*(\d+\.\d+\.\d+)")
    
    with open(file_name, encoding="utf8") as file_desc:
        try:
            buf = file_desc.read()
            solc_v = PATTERN.findall(buf)[0]
            print(solc_v)
        except:
            print(f'{file_name}')
            solc_v = '0.5.0'
    
    with open(f"xxx/.virtualenvs/py38/.solc-select/global-version", "w") as f:
        f.write(solc_v)
    print("Switched global version to", solc_v)
    
    return solc_v

def save_sol_file_names(folder_path):
        for root, dirs, files in os.walk(folder_path):
            sol_files = glob.glob(os.path.join(root, '*.sol'))
            for file_path in sol_files:
                file_name_rt_hex = os.path.splitext(file_path)[0]
                directory_path = os.path.dirname(file_path)
                solc_version = switch_global_version(file_path)
                
                abi_tmp_dir = "%s/abi" % (directory_path)
                cmd = "solc --abi --overwrite -o %s %s" % (abi_tmp_dir, file_path)
                os.system(cmd)
                
                bin_tmp_dir = "%s/runtime" % (directory_path)
                cmd1 = "solc --bin-runtime --overwrite -o %s %s" % (bin_tmp_dir, file_path)
                os.system(cmd1)
                        
                


if __name__ == "__main__":
    
    folder_path = './input/Smartbugs_dataset/'
    save_sol_file_names(folder_path)