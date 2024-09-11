import pandas as pd

#ex python file_comp_v4.py
max_id = 0
final_df = []
profile = 'main_family'
file = 'results_fod_wrapper/'
relations_m = 'main_family'
relations_j = "joint_family"
for i in range(1, 10):
    try:
        rel_table = pd.read_csv(file + profile + f"_profiles{i}.txt", sep='\t')
    except FileNotFoundError:
        print(file + profile + f"_profiles{i}.txt not found. Skipping...")
        continue

    rel_table = rel_table[rel_table['Gen'] == 1870]

    indivs = rel_table['ID'].to_list()

    # Read in main family relationship file
    try:
        rel_file_main = pd.read_csv(file + relations_m + f'{i}_rel.csv')
    except FileNotFoundError:
        print(file + relations_m + f'{i}_rel.csv not found. Skipping...')
        continue
        
    # Read in joint family relationship file
    try:
        rel_file_joint = pd.read_csv(file + relations_j + f'{i}_rel.csv')
    except FileNotFoundError:
        print(file + relations_j + f'{i}_rel.csv not found. Skipping...')
        continue

    for indiv in indivs:
        # Count number of first cousins in main family.
    
        ## 1) Subset relationships file to indiv of intrest
        # subs_main_id1 = rel_file_main[rel_file_main['ID1'] == indiv]
        # subs_main_id2 = rel_file_main[rel_file_main['ID2'] == indiv]
        # subs_main = pd.concat([subs_main_id1, subs_main_id2])
        subs_main = rel_file_main[(rel_file_main['ID1'] == indiv) | (rel_file_main['ID2'] == indiv)]
        ## 2) Subset relationship file to relationship of intrest
        subs_main = subs_main[subs_main['RC'] == 'Full First Cousin']
        n_subs_main = len(subs_main)
        # Count number of first cousins in joint family.
        
        ## 1) Subset relationships file to indiv of intrest
        # subs_joint = rel_file_joint[(rel_file_joint['ID1'] == indiv) & (rel_file_joint['RC'] == 'Full First Cousin')]
        subs_joint = rel_file_joint[(rel_file_joint['ID1'] == indiv) | (rel_file_joint['ID2'] == indiv)]
        ## 2) Subset relationship file to relationship of intrest
        subs_joint = subs_joint[subs_joint['RC'] == 'Full First Cousin']
        n_subs_joint = len(subs_joint)
        # row = [Family ID (i), Individual ID (indiv), Num of First Cousin (Main), Num of First Cousin (Joint)]
        row = [i, indiv + max_id, n_subs_main, n_subs_joint, indiv]
        # final_df.append(row)
        final_df.append(row)
        # set new max id
    print(relations_m)
    if len(rel_file_main['ID1']) == 0:
        continue
    max_id_1 = max(rel_file_joint['ID1'])
    max_id_2 = max(rel_file_joint['ID2'])
    if max_id_1 > max_id_2:
        max_id = max_id + max_id_1
    else:
        max_id = max_id + max_id_2
    print(max_id)

# final_df = pd.DataFrame(final_df, columns = ['Fam_ID', 'Indiv_ID', 'count(main)', 'count(joint)'])
final_df = pd.DataFrame(final_df,columns = ['Fam_ID', 'Indiv_ID', 'count(main)', 'count(joint)', 'original ID'])
final_df.to_csv('final_data.csv', index=False)