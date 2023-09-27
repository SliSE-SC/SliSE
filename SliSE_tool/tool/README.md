# SliSE

SliSE is a tool designed to efficiently detect reentrancy vulnerabilities in complex smart contracts.

## Dependencies Installation

### [virtualenv](https://virtualenvwrapper.readthedocs.io/en/latest/) for configuring the Python environment.

```bash
$ pip3 install virtualenvwrapper
$ source /usr/local/bin/virtualenvwrapper.sh
$ mkvirtualenv --python=`which python3.8` python38
```

### solc-select
```bash
$ pip3 install solc-select
```

### [z3](https://github.com/Z3Prover/z3/releases) Theorem Prover version 4.5.0.

Download the [source code of version z3-4.5.0](https://github.com/Z3Prover/z3/releases/tag/z3-4.5.0)

Install z3 using Python bindings

```bash
$ python3 scripts/mk_make.py --python
$ cd build
$ make
$ sudo make install
```

### Tool Installation
Run the following script to install the tools:
```bash
$ bash install.sh
```

## How to Run SliSE

Run ```python3 SliSE.py -h``` to view a list of options.

```plaintext
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
                                                                            

usage: smart_pdg.py [-h] [--solidity-file] [--vuln-type VULN_TYPE] [--timeout TIMEOUT] [--target_function TARGET_FUNCTION] [--target_contract TARGET_CONTRACT] file

Vulnerability detection tool for EVM

positional arguments:
  file                  File to analyze

optional arguments:
  -h, --help            show this help message and exit
  --solidity-file, -s   Use this option when the file is a Solidity file instead of EVM bytecode hex string. By default, it is unset
  --vuln-type VULN_TYPE, -vt VULN_TYPE
                        Default = reentrancy
  --timeout TIMEOUT, -t TIMEOUT
                        Timeout for Z3 Solver. Default = 300
  --target_function TARGET_FUNCTION, -tf TARGET_FUNCTION
                        The target function to analyze
  --target_contract TARGET_CONTRACT, -tc TARGET_CONTRACT
                        The target contract to analyze
```

```plaintext
# To analyze contracts within an entire file
python SliSE.py -s <filename> -vt reentrancy
python SliSE.py -s input/smartbugs_all/0x7b368c4e805c3870b6c49a3f1f49f69af8662cf3 -vt reentrancy

# Verification of path reachability
python SliSE.py -s <filename> -c <contract filename> -func <function name> -r 
python SliSE.py -f input/smartbugs_all/0x7b368c4e805c3870b6c49a3f1f49f69af8662cf3 -tc 'W_WALLET' -tf 'Collect(uint256)'
```
