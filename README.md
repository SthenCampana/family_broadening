# family_broadening
Family_broadening (FB) simulates families on founders to increase the breadth of the family pedigree. This gives us all possible cousins of an individual within a family where we would otherwise be missing the full family of one of the parents.

## Usage
FB takes in a family pedigree as a networkx directed graph. These files are required to run:
1. A child distribution file containing the number of expected children for each generation. We provide an example file ("impumps_nchild_nozero_mean_sd.txt") that is based on US census data. This can be edited or replaced to fit the users needs
2. If the user inputs their own family pedigree, the file needs to be in a .nx file format. The contents should list parent to child relationships for each individual. The user also need to provide a corrisponding profiles file in a .txt format. The profiles should contain (ID Sex Gen) and list all individuals with their sex and generation year.
Some examples:
main_family.nx
```
1 3 {}
1 24 {}
3 5 {}
3 8 {}
......
```
main_family_profiles.txt
```
ID	Sex	Gen
1	male	NA
3	male	1850
2	female	NA
5	female	1860
4	female	1850
```

## Install Conda Environment
You will need to have conda installed on your system. To install conda/mini conda onto your system follow this 
[link](https://conda.io/projects/conda/en/latest/user-guide/install/index.html).

Once you have conda installed on your system, check its working by the simple command
```bash
conda info
```

This repo includes a `ped_sim.yml` file that includes a virtual conda environment of all the software that is needed. 
Once you clone the repo to you directory, create and load the conda environment as follows.

```
cd ped_sim
conda env create -f ped_sim_env.yml
conda activate ped_sim
python setup.py install

#check pipeline interface is working though run_ped_sim.py
python run_ped_sim.py -h
```

# Sample Run

1. To perform the test run first we make sure we activate our conda enviornment
```
conda activate ped_sim
```

2. Make sure you are in the correct dirrectory
```
cd family_broadening-main
```

3. Now we can run our simulation with:
```
python fb_wrapper.py -c impumps_nchild_nozero_mean_sd.txt -y 1850 1860 1870
```
-c is the file containg our children distribution accross different generations

-y is our generation years we want to sample from

## Output

The final family out put will be by dault labeled as "joint_family.nx" and "joint_family_profiles.txt". The output file names can be specified using the `-o` flag

## Features
`-y` Years we want to sample from. 

`-c` File containing the distrubution of children accross generations.

`-o` Output file name. by default the output file will be called "joint_family"

`-mf` Main family that is specified by user. Must be a .nx file

`-s` Seed

