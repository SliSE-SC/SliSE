from slither.slither import Slither  
from slither.utils.code_complexity import compute_cyclomatic_complexity
from slither.utils.loc import compute_loc_metrics
from slither.analyses.evm.convert import get_evm_instructions
import subprocess
import json
import os
import re
from print_pragma_version import get_solc
import solcx
import csv

def switch_global_version(file_name):
    
    PATTERN = re.compile(r"pragma solidity\s*(?:\^|>=|<=)?\s*(\d+\.\d+\.\d+)")
    
    with open(file_name, encoding="utf8") as file_desc:
        buf = file_desc.read()
        solc_v = PATTERN.findall(buf)[0]
        print(solc_v)
    
    with open(f"xxx/.virtualenvs/py38/.solc-select/global-version", "w") as f:
        f.write(solc_v)
    print("Switched global version to", solc_v)
    
    return solc_v

def compute_metrics(filename):
    slither = Slither(filename) 
    Total_Contract = len(slither.contracts)
    Total_Function = 0
    Total_Variable = 0
    Total_Internal_Call = 0
    Max_Cyclomatic_Complexity = 0
    
    loc = compute_loc_metrics(slither)
    File_loc = loc.src.loc
    Sloc = loc.src.sloc
    Cloc = loc.src.cloc
    

    for contract in slither.contracts:
        # contract = slither.get_contract_from_name(contract_name=contract.name)
        # contract_ins = get_evm_instructions(contract)
        # print(contract.name)
        Total_Function += len(contract.functions)
        for function in contract.functions:
            cyclomatic_complexity = compute_cyclomatic_complexity(function)
            if cyclomatic_complexity > Max_Cyclomatic_Complexity:
                Max_Cyclomatic_Complexity = cyclomatic_complexity
            Total_Variable += len(function.state_variables_read + function.solidity_variables_read)
            Total_Internal_Call += len(function.internal_calls)

    return Total_Contract, Total_Function, Total_Variable, Total_Internal_Call, Max_Cyclomatic_Complexity, File_loc, Sloc, Cloc

def write_metrics_to_csv(metrics, output_file):
    header = ['Total_Contract', 'Total_Function', 'Total_Variable', 'Total_Internal_Call', 'Max_Cyclomatic_Complexity', 'Loc', 'sLoc', 'cLoc']
    
    with open(output_file, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(metrics)


file_path = 'xxx.txt'
output_file = 'metrics.csv'
with open(file_path, 'r') as file:
    filenames = file.read().splitlines()
    
    for filename in filenames:
        try:
            switch_global_version(filename)
            metrics = compute_metrics(filename)
            write_metrics_to_csv([filename] + list(metrics), output_file)
        except Exception as e:
            print(f"{str(e)}")
            continue

print("Done")