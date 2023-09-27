import argparse
import logging
import time
import sys
import json
import subprocess
import os
import signal

from solcx import install_solc_pragma, set_solc_version_pragma, compile_files, get_compilable_solc_versions, get_installable_solc_versions
from solcx.exceptions import SolcNotInstalled
from solcx.install import get_executable
from solidity_parser.parser import parse
from print_pragma_version import get_solc

import finder.vulnerability_finder
from rattle import Recover,Recover1
from solidity.source_map import SourceMap
from executor import symbolic_executor
from executor.symbolic_executor import SymExec
from finder import available_modules
from finder.vulnerability_finder import VulnerabilityFinder
from helper import static_parser

logging.basicConfig(level=logging.INFO, filename="log.txt")
logger = logging.getLogger()
sys.setrecursionlimit(100000)

logging.basicConfig(level=logging.INFO, filename="log.txt")
logger = logging.getLogger()
sys.setrecursionlimit(100000)

def timeout_handler(signum, frame):
    raise TimeoutError("Function execution timed out")


def get_solc_version_string(file):
    parsed = parse(file.read().decode('utf-8'))
    for children in parsed['children']:
        if children['type'] == 'PragmaDirective':
            return children['value']
    # return get_available_solc_versions()[0]
    return get_compilable_solc_versions()[0]


def get_constructor_traces(constructor_bytecode):
    ssa = Recover(constructor_bytecode, edges=[], optimize=True)

    sym_exec = SymExec(ssa)
    return sym_exec.execute()


def main():
    is_solidity_file_default = False
    log_output_default = 'Error'
    all_vuln_types = list(available_modules.keys())
    max_depth_default = 25
    find_all_vulnerabilities_default = False
    default_timeout = 100
    is_reentrant = False
    
    text_art = '''                                                                    
   SSSSSSSSSSSSSSS lllllll   iiii     SSSSSSSSSSSSSSS EEEEEEEEEEEEEEEEEEEEEE
 SS:::::::::::::::Sl:::::l  i::::i  SS:::::::::::::::SE::::::::::::::::::::E
S:::::SSSSSS::::::Sl:::::l   iiii  S:::::SSSSSS::::::SE::::::::::::::::::::E
S:::::S     SSSSSSSl:::::l         S:::::S     SSSSSSSEE::::::EEEEEEEEE::::E
S:::::S             l::::l iiiiiii S:::::S              E:::::E       EEEEEE
S:::::S             l::::l i:::::i S:::::S              E:::::E             
 S::::SSSS          l::::l  i::::i  S::::SSSS           E::::::EEEEEEEEEE   
  SS::::::SSSSS     l::::l  i::::i   SS::::::SSSSS      E:::::::::::::::E   
    SSS::::::::SS   l::::l  i::::i     SSS::::::::SS    E:::::::::::::::E   
       SSSSSS::::S  l::::l  i::::i        SSSSSS::::S   E::::::EEEEEEEEEE   
            S:::::S l::::l  i::::i             S:::::S  E:::::E             
            S:::::S l::::l  i::::i             S:::::S  E:::::E       EEEEEE
SSSSSSS     S:::::Sl::::::li::::::iSSSSSSS     S:::::SEE::::::EEEEEEEE:::::E
S::::::SSSSSS:::::Sl::::::li::::::iS::::::SSSSSS:::::SE::::::::::::::::::::E
S:::::::::::::::SS l::::::li::::::iS:::::::::::::::SS E::::::::::::::::::::E
 SSSSSSSSSSSSSSS   lllllllliiiiiiii SSSSSSSSSSSSSSS   EEEEEEEEEEEEEEEEEEEEEE
                                                                            
'''
    print(text_art)

    parser = argparse.ArgumentParser(description='Vulnerability detection tool for EVM')
    parser.add_argument('file', type=argparse.FileType('rb'), help='File to analyse')
    parser.add_argument('--solidity-file', '-s', action='store_true', default=is_solidity_file_default,
                        help=f'Use this option when file is a solidity file instead of EVM bytecode hex string. By default it is {"unset" if not is_solidity_file_default else "set"}')
    parser.add_argument('--vuln-type', '-vt', action='append', default=[],
                        help=f'Default = {"reentrancy"}')
    parser.add_argument('--timeout', '-t', type=int, default=default_timeout,
                        help=f'Timeout to Z3 Solver. Default = {default_timeout}')
    parser.add_argument('--target_function', '-tf', type=str, help='The target function to analyze')
    parser.add_argument('--target_contract', '-tc', type=str, help='The target contract to analyze')
    args = parser.parse_args()
    if not args.vuln_type:
        args.vuln_type = all_vuln_types

    symbolic_executor.MAX_DEPTH = args.max_depth
    finder.vulnerability_finder.Z3_TIMEOUT = args.timeout

    try:
        log_level = getattr(logging, args.verbosity.upper())
    except AttributeError:
        log_level = None

    logger.setLevel(level=log_level)
    file = args.file
    filename = file.name
    static_detection = None
    len_d = 0

    bytecodes = {}
    srcmap = None
    if args.solidity_file:
        static_detection, len_d = static_parser(filename)
        solc_version = get_solc(filename)
        start_time_stage2 = time.perf_counter()
        try:
            set_solc_version_pragma(solc_version)
        except SolcNotInstalled:
            logger.info(f'Installing solc version {solc_version}...')
            install_solc_pragma(solc_version)
            set_solc_version_pragma(solc_version)
            logger.info('Installed')
            
        logger.info(f'Compiling {filename}...')
        try:
            contracts = compile_files([filename])
            logger.info('Compiled successfully')
            srcmap = SourceMap(filename, get_executable())
            for name, contract in contracts.items():
                runtime_bytecode = contract['bin-runtime']
                bytecodes[name] = runtime_bytecode.encode('utf-8')
        except:
            print(f'{filename}存在编译错误')
            return  False,filename
    else:
        start_time_stage2 = time.perf_counter()
        bytecodes[filename] = args.file.read()
        
    data = {
            'filename': filename,
            'vulnerabilities': []
            }

    for name, bytecode in bytecodes.items():
        if len(bytecode) == 0:
            logger.info('Nothing to analyse')
            continue
        vulnerabilities_found = []
        target_block_list = []
        logger.info(f'Analysing {name}...')
        try:
            function_name = args.target_function
            try:
                timeout = 60
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout)  
                try:
                    ssa = Recover(bytecode, edges=[], optimize=True)
                except TimeoutError:
                    ssa = Recover1(bytecode, edges=[], optimize=True)
                finally:
                    signal.alarm(0)
            except Exception as e:
                print(f"SSA recovery exception occurred: {e}")
                ssa = Recover1(bytecode, edges=[], optimize=True)
                
            with open('out.txt', "w") as file:
                file.write(str(ssa))  
             
            sym_exec = SymExec(ssa)
            traces = sym_exec.execute()
            checker = VulnerabilityFinder(traces, ssa.functions, name, srcmap, args.find_all_vulnerabilities)
            vulnerabilities_found.extend(checker.analyse_only(args.vuln_type))
            
            if len(vulnerabilities_found) == 0 :
                for call in ssa.calls():
                    if call.insn.name == 'DELEGATECALL':
                        gas, to, in_offset, in_size, out_offset, out_size = call.arguments
                        value = None
                    else:
                        gas, to, value, in_offset, in_size, out_offset, out_size = call.arguments
                        

                    if to.writer:
                        target_block_list.append(call.parent_block.offset)
                    else:
                        pass
                
                if len(target_block_list) != 0:
                    for block_id in target_block_list:
                        timeout = 120
                        signal.signal(signal.SIGALRM, timeout_handler)
                        signal.alarm(timeout) 
                        try:
                            sym_exec = SymExec(ssa,target_block_id= block_id)
                            traces = sym_exec.execute()
                            checker = VulnerabilityFinder(traces, ssa.functions, name, srcmap, args.find_all_vulnerabilities)
                            vulnerabilities_found.extend(checker.analyse_only(args.vuln_type))
                            if len(vulnerabilities_found) != 0:
                                break
                        except TimeoutError:
                            print("target block execution timed out")
                        finally:
                            signal.alarm(0)  
        except Exception as e:
            logger.exception(e)
            continue

        if len(vulnerabilities_found) == 0:
            continue
        for vuln in vulnerabilities_found:
            line_number = vuln.line_number
            vuln_str = f'Vulnerability: {vuln.type}. ' \
                    f'Maybe in function: {vuln.function_name}. ' \
                    f'function_hash: {vuln.function_hash}. ' \
                    f'PC: {hex(vuln.pc)}. ' \
                    f'Line number: {line_number if line_number else ""}.'
            logger.info(vuln_str)
            print(vuln_str)
            for i, (var_name, value) in enumerate(vuln.model.items()):
                if i == 0:
                    logger.info(f'If {var_name} = {value}')
                else:
                    logger.info(f'and {var_name} = {value}')
            
            vulnerability_data = {
                'contract_name':name,
                'type': vuln.type,
                'function_name': vuln.function_name,
                'function_hash': vuln.function_hash,
                'pc': hex(vuln.pc),
                'Line number': line_number if line_number else ""
            }
            
            data['vulnerabilities'].append(vulnerability_data)
            
    end_time_stage2 = time.perf_counter()
    duration_stage2 = end_time_stage2 - start_time_stage2
    with open('detectiion_output/stage2_detection.txt','a') as f:
        if len(data['vulnerabilities']) != 0:
            f.write(data['filename']+',stage2_reentrancy!,'+str(duration_stage2))
            f.write('\n')
        else :
            f.write(data['filename']+',stage2_No_reentrancy!,'+str(duration_stage2))
            f.write('\n')
            
        
        
    with open('detectiion_output/vulnerabilities.json', 'r') as f:
        ori_data = json.load(f)
        if (static_detection and len(data['vulnerabilities']) != 0) or (static_detection is None and len(data['vulnerabilities']) != 0) or (len_d == 0 and len(data['vulnerabilities']) != 0):
            ori_data.append(data)
            is_reentrant = True

    with open('detectiion_output/vulnerabilities.json', 'w') as f:
        json.dump(ori_data, f)
        
    return is_reentrant,filename
        

if __name__ == '__main__':
    start_time = time.perf_counter()
    is_reentrant,filename = main()
    end_time = time.perf_counter()
    duration = end_time - start_time
    with open('detectiion_output/stage1&2_detection.txt','a') as f:
        f.write(f"{filename},{is_reentrant},{duration}")
        f.write('\n')
    
    
