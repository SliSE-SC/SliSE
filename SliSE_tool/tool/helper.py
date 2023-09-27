import subprocess
import json
import os
import re
import time

def parse_warnings_data(file_path):
    with open(file_path, 'r') as file:
        data_dict = json.load(file)
        
    markdown_dict = {}  

    if data_dict:
        try:
            success = data_dict['success']
            error = data_dict['error']
            results = data_dict['results']
            
            if success and error is None and len(results) != 0:
                detectors = results['detectors']
                for data in detectors:
                    check_item = data.get('check', '')
                    first_markdown_element = data.get('first_markdown_element', '')
                    markdown = data.get('markdown', '')
                    matche = re.findall(r'\[(.*?)\]', markdown)[0]
                    first_markdown_element = matche + '%%' + first_markdown_element.split("#")[1]
                    if check_item in markdown_dict:
                        markdown_dict[check_item].append(first_markdown_element)
                    else:
                        markdown_dict[check_item] = [first_markdown_element]
        except json.JSONDecodeError as e:
            print("JSON parser error:", str(e))
    else:
        print("ERROR!")
    

    if success and error is None:
        output = "True"
    else:
        output = "False"
        
        
    return output, markdown_dict

def switch_global_version(file_name):
    
    PATTERN = re.compile(r"pragma solidity\s*(?:\^|>=|<=)?\s*(\d+\.\d+\.\d+)")
    
    with open(file_name, encoding="utf8") as file_desc:
        buf = file_desc.read()
        match = PATTERN.search(buf)
        if match:
            solc_v = match.group(1)
            with open("xxx/.virtualenvs/py38/.solc-select/global-version", "w") as f:
                f.write(solc_v)
            print("Switched global version to", solc_v)
            return solc_v
        else:
            print("No pragma statement found in the file.")
            return None
    

def static_parser(file_path):
    start_time = time.time()
    arg1 = file_path
    static_detect = False
    file_name = os.path.splitext(os.path.basename(arg1))[0] + '.json'
    switch_global_version(arg1)
    cmd2 = f"slither {arg1} --detect reentrancy-eth,reentrancy-no-eth,arbitrary-send-erc20,controlled-delegatecall --solc-disable-warnings --json {file_name}"
    result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True)

    success, results = parse_warnings_data(file_name)
    allowed_keys = {"controlled-delegatecall", "reentrancy-no-eth"}
    if len(results.keys()) != 0:
        if "controlled-delegatecall" not in results:
            static_detect = True
        else:
            if set(results.keys()) == allowed_keys:
                static_detect = True
        


    json_file = os.path.splitext(os.path.basename(file_path))[0] + '.json'
    if os.path.exists(json_file):
        os.remove(json_file)

        
    end_time = time.time()
    run_time = end_time - start_time
    
    with open('detectiion_output/stage1_detection.txt','a') as f:
        if static_detect:
            f.write(arg1+',stage1_reentrancy!,'+str(run_time))
            f.write('\n')
        else :
            f.write(arg1+',stage1_No_reentrancy!,'+str(run_time))
            f.write('\n')
            
    
    return static_detect,len(results.keys())
    
    
    
def parser():
    

    with open("id.txt", 'r') as file:
        file_paths = file.readlines()

    for file_path in file_paths:
        file_path = file_path.strip()

        if not os.path.isfile(file_path):
            print(f"no file: {file_path}")
            continue
        
        arg1 = file_path
        file_name = os.path.splitext(os.path.basename(arg1))[0] + '.json'
        
        switch_global_version(arg1)

        cmd2 = f"slither {arg1} --detect reentrancy-eth,reentrancy-no-eth,arbitrary-send-erc20,controlled-delegatecall --solc-disable-warnings --json {file_name}"

        result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True)

        success, results = parse_warnings_data(file_name)
        output_file = "detect_results.txt"
        allowed_keys = {"controlled-delegatecall", "reentrancy-no-eth"}
        with open(output_file, 'a') as file:
            if len(results.keys()) != 0:
                if "controlled-delegatecall" not in results:
                    file.write(f"\n{file_path},")
                    file.write(','.join(results.keys()))
                else:
                    if set(results.keys()) == allowed_keys:
                        file.write(f"\n{file_path},")
                        file.write(','.join(results.keys())) 

        json_file = os.path.splitext(os.path.basename(file_path))[0] + '.json'
        if os.path.exists(json_file):
            os.remove(json_file)
            print(f"已删除文件: {json_file}")


# if __name__ == "__main__":
#     parser()