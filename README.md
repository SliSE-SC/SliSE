# Efficient Detection of Reentrancy Vulnerabilities in Complex Smart Contracts

This repository provides an introduction to the SliSE Tool, Experimental Data, and Datasets.

## SliSE_tool

The SliSE_tool directory contains the source code and relevant documentation for the SliSE tool, including the following contents:

- **README.md:** Documentation explaining how to install and use SliSE.
- **Source Code:** The source code for the tool.
- **examples:** This directory contains smart contract files.

## Experimental_data

The experimental data mainly consists of experimental data for RQ1, RQ2, RQ3, and RQ4:

- **RQ1:** Analysis of SliSE's detection capabilities and efficiency for complex contract Reentrancy vulnerability detection on dataset DB1, compared to eight other tools (Slither, Mythril, Securify, Smartian, Sailfish, Oyente, Osiris, and Manticore).

- **RQ2:** Comparative experiments on datasets DB2 and DB3 to assess SliSE's ability to detect Reentrancy vulnerabilities on Ethereum compared to eight other tools.

- **RQ3:** Evaluating the impact of Stage II path pruning on the overall detection process in two modes: Stage II and Stage I & II (representing with and without Stage I).

- **RQ4:** Assessing the impact of Stage II symbolic execution verification on the overall detection process in two modes: Stage I and Stage I & II (representing with and without Stage II).

- **Complexity Metrics:** Quantitative statistics on the complexity metrics of the experimental datasets.

- **RawOutput:** Contains raw output data from various experiments with different tools.

## Datasets

### DB1 Dataset

[Zheng et al](https://github.com/InPlusLab/DAppSCAN/) compiled a complex contract dataset that includes 895 vulnerabilities from 1,322 open-source DApp audit projects provided by 30 blockchain security companies. This dataset contains a total of 81 positive labels for Reentrancy vulnerabilities.

### DB2 Dataset

[Zheng et al](https://github.com/InPlusLab/ReentrancyStudy-Data) used existing detection tools to analyze 230,548 verified contracts from Etherscan and obtained this dataset through manual inspection. The dataset includes 21,212 contracts identified as positive for Reentrancy vulnerabilities using six Reentrancy detection tools, with 41 contracts manually verified as true positives.

### DB3 Dataset

The [SmartBugs](https://github.com/smartbugs/smartbugs-curated) Dataset is a widely used dataset containing 143 contracts. Among these contracts, 31 were identified as containing Reentrancy vulnerabilities.