import argparse
import subprocess
import os
import shutil
#runs family
#ex python run_some.py -y 1850 1860 1870 -i 10
def load_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--years_to_sample', nargs='+', type=int)
    parser.add_argument('-c', '--census_filepath', type=str)
    parser.add_argument('-o', '--output_prefix', type=str, default = 'joint_family')
    parser.add_argument('-mf', '--main_family', type=str, default = 'None')
    parser.add_argument('-i', '--iterations', type = int, default = 100)
    return parser.parse_args()

if __name__ == '__main__':
    #set user erguments
    user_args = load_args()
    u_years = user_args.years_to_sample
    u_census = user_args.census_filepath
    u_main_family = user_args.main_family
    u_output = user_args.output_prefix
    u_iterations = user_args.iterations
    
    years_str = f'-y'
    for i in u_years:
        years_str += f' {i}'
    print(years_str)
    
    for i in  range(1, u_iterations + 1):
        #create simulated family
        sim_ped_cmd = f'python fod_wrapper_v8.py -c impumps_nchild_nozero_mean_sd.txt {years_str}'#-s{i}'
        subprocess.run(sim_ped_cmd, shell=True)

        #save main family profiles.txt , main family.nx, joint family.nx 
        new_fod = 'results_fod_wrapper'
        if not os.path.exists(new_fod):
            print("creating new folder")
            os.makedirs(new_fod)

        
        shutil.move('main_family.nx', f'{new_fod}/main_family{i}.nx')
        shutil.move('main_family_profiles.txt', f'{new_fod}/main_family_profiles{i}.txt')
        shutil.move('joint_family.nx', f'{new_fod}/joint_family{i}.nx')

        #run enur_fam on main and joint family. file saved in new_fod
        print(f'enur main {i}')
        sim_enur_cmd = f'python enur_fam.py -n {new_fod}/main_family{i}.nx'
        subprocess.run(sim_enur_cmd, shell=True)
        print(f'enur joint {i}')
        sim_enur_cmd = f'python enur_fam.py -n {new_fod}/joint_family{i}.nx'
        subprocess.run(sim_enur_cmd, shell=True)
        

        # results_command = f'move joint_family.nx results/joint_family{i}.nx'
        # subprocess.run(results_command, shell=True)
        # results_command_mf = f'move main_family.nx results/main_family{i}.nx'
        # subprocess.run(results_command_mf, shell=True)
        # profiles_command = f'move main_family_profiles.txt results/main_family{i}_profiles.txt'
        # subprocess.run(profiles_command, shell=True)
        # print(f'fam{i} done')
    if not os.path.exists("family_folder"):
        print("creating new folder")
        os.makedirs("family_folder")
    for count in range(1, u_iterations + 1):
        shutil.move(f'fam{count}.nx', f"family_folder/")
        shutil.move(f'fam{count}_profiles.txt', f"family_folder/")
        print('file moved')