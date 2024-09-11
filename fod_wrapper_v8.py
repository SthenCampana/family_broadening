import networkx as nx
import subprocess
import argparse
import os
import sys
import numpy as np
import pandas as pd
import time
import shutil
from family_on_demand_gen import *
from networkx.relabel import convert_node_labels_to_integers
from networkx.algorithms.operators.binary import disjoint_union
from networkx.algorithms.traversal.depth_first_search import dfs_predecessors


#ex: python fod_wrapper_v8.py -c impumps_nchild_nozero_mean_sd.txt -y 1850 1860 1870 -ss True -75774
# if a main family is given, the root founder generation needs to be ommited in the -y flag

# record start time
start = time.time()

def load_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--years_to_sample', nargs='+', type=int)
    parser.add_argument('-c', '--census_filepath', type=str)
    parser.add_argument('-o', '--output_prefix', type=str, default = 'joint_family')
    parser.add_argument('-mo', '--main_family_output_prefix', type=str, default = 'main_family')
    parser.add_argument('-mf', '--main_family', type=str, default = 'None')
    parser.add_argument('-ss', '--step_by_step', type=bool, default = False)
    parser.add_argument('-s', '--seed', type=int, default=np.random.randint(10000, size=1))
    return parser.parse_args()

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def fam_check_gen(family):
    '''
    check the family profile and returns the number of generations
    '''

    #list all indiv generations 
    fam = pd.read_csv(f'{family}', sep='\t')
    df = pd.DataFrame(fam)
    gen = df.Gen.unique()

    return(len(gen)-1)

if __name__ == '__main__':
    #load in user arguments
    user_args = load_args()
    u_years = user_args.years_to_sample
    u_census = user_args.census_filepath
    u_main_family = user_args.main_family
    u_main_family_output = user_args.main_family_output_prefix
    u_output = user_args.output_prefix
    u_step = user_args.step_by_step
    u_seed = user_args.seed

    # set seed
    # np.random.seed(user_args.seed)
    # input_seed = np.random.randint(10000, size=1)[0]
    # print('seed: ', input_seed)

    #sets up years to run as a terminal command
    years_str = f'-y'
    for i in u_years:
        years_str += f' {i}'

    #create or load in main family
    count = 1
    if u_main_family == 'None':
        num_gen = 0
        while num_gen < len(u_years):
            # Create main family
            sim_ped_cmd = f'python sim_pedigree.py {years_str} -c {u_census} -o {u_main_family_output}'# -s {input_seed}'
            subprocess.run(sim_ped_cmd, shell=True)
            main_family = nx.read_edgelist(f'{u_main_family_output}.nx', create_using = nx.DiGraph())
            print('main family created')
            num_gen = fam_check_gen(f'{u_main_family_output}_profiles.txt')
            print(num_gen, len(u_years), u_seed)
        
    else:
        #if user imputs main family, the user must have a profiles file ex. main_family_profiles.txt
        main_family = nx.read_edgelist(u_main_family, create_using = nx.DiGraph())
        if len(main_family) < len(u_years):
            print('Number of generations in submitted family (-mf) does not match number of generations requested (-y)')
            exit()

        num_gen = fam_check_gen(f'{u_main_family_output}_profiles.txt')
        count = count + 1
        print(count)

    #find founders in main family
    founders = find_founders(main_family)
    founders = founders[2:]
    print(founders)
    kill = 0
    #initialize joint family
    sim_ped_cmd = f'python sim_pedigree.py {years_str} -c {u_census} -o fam0' # -s {input_seed}'
    subprocess.run(sim_ped_cmd, shell=True, capture_output=True)
    join_cmd = f'python family_on_demand_gen.py -n1 main_family.nx -n2 fam0.nx -p1 main_family_profiles.txt -p2 fam0_profiles.txt -o {u_output} -cf {founders[0]}'
    # runs the subprocess command to joing family.
    errorcode = subprocess.run(join_cmd, shell=True, capture_output=True)
    # if an error occurs, new family is created 
    while errorcode.returncode == 1:
        sim_ped_cmd = f'python sim_pedigree.py {years_str} -c {u_census} -o fam0' # -s {input_seed}'
        subprocess.run(sim_ped_cmd, shell=True, capture_output=True)
        if u_main_family == 'None':
            join_cmd = f'python family_on_demand_gen.py -n1 main_family.nx -n2 fam0.nx -p1 main_family_profiles.txt -p2 fam0_profiles.txt -o {u_output} -cf {founders[0]}'
        else:
            mf = u_main_family.replace('.nx','')
            join_cmd = f'python family_on_demand_gen.py -n1 {mf}.nx -n2 fam0.nx -p1 {mf}_profiles.txt -p2 fam0_profiles.txt -o {u_output} -cf {founders[0]}'
        errorcode = subprocess.run(join_cmd, shell=True, capture_output=True)
        # suppose to prevent an infinite loop
        kill = kill + 1
        if kill == 10:
            python = sys.executable
            os.execl(python, python, *sys.argv)

    # loops throught the remaining founders, simulates families then attaches to main family
    # we do this so that we can mainting the origional main family
    count=1
    for i in founders[1:]:
        # set random seed for each iteration if none is specified
        joint_seed = np.random.randint(10000, size=1)[0]
        # create family to join main family
        sim_ped_cmd = f'python sim_pedigree.py {years_str} -c {u_census} -o fam{count} -s {joint_seed}'
        subprocess.run(sim_ped_cmd, shell=True, capture_output=True)
        join_cmd = f'python family_on_demand_gen.py -n1 {u_output}.nx -n2 fam{count}.nx -p1 {u_output}_profiles.txt -p2 fam{count}_profiles.txt -o {u_output} -cf {i}'
        errorcode = subprocess.run(join_cmd, shell=True, capture_output=True)
        while errorcode.returncode == 1:
            sim_ped_cmd = f'python sim_pedigree.py {years_str} -c {u_census} -o fam{count}' # -s {input_seed}'
            subprocess.run(sim_ped_cmd, shell=True, capture_output=True)
            join_cmd = f'python family_on_demand_gen.py -n1 {u_output}.nx -n2 fam{count}.nx -p1 {u_output}_profiles.txt -p2 fam{count}_profiles.txt -o {u_output} -cf {i}'
            errorcode = subprocess.run(join_cmd, shell=True, capture_output=True)
            print('creating new fam')
        print(f'connection successful for fam{count} at founder', i)

        count += 1
