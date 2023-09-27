import os
import concurrent.futures

def split_file(input_file, chunk_size):
    with open(input_file, 'r') as f:
        content = f.readlines()

    file_list = []
    for i in range(0, len(content), chunk_size):
        chunk = content[i:i + chunk_size]
        chunk_file = f'chunk_{i}.txt'
        with open(chunk_file, 'w') as chunk_f:
            chunk_f.writelines(chunk)
        file_list.append(chunk_file)

    return file_list


def process_content(file_path):

    script = "execute.sh"  
    log_file = f'log_{os.path.basename(file_path)}.log'

    command = f'bash {script} {file_path} >> {log_file} 2>&1'
    os.system(command)


if __name__ == '__main__':
    input_file = 'id.txt' 
    chunk_size = 2000

    file_list = split_file(input_file, chunk_size)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_content, file_list)
