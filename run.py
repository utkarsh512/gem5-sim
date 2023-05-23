import os
import subprocess

LQEntries_List = [32, 64]
SQEntries_List = [32, 64]
l1d_size_List = ["32kB", "64kB"]
l1i_size_List = ["8kB", "16kB"]
l2_size_List = ["256kB", "512kB"]
bp_type_List = ["TournamentBP", "BiModeBP"]
ROBEntries_List = [128, 192]
numIQEntries_List = [16, 64]


OP_FOLDER = "~/gem5/configs/HPCA_GRP_01_ASSGN/outputs"
CONFIG_PATH = "~/gem5/configs/HPCA_GRP_01_ASSGN/config.py"
CPP_FILE = "~/gem5/configs/HPCA_GRP_01_ASSGN/blocked-matmul"

if not os.path.exists(os.path.expanduser(OP_FOLDER)):
    os.makedirs(os.path.expanduser(OP_FOLDER))

for i in range(0, 256):
    mask_i = [(i >> j) & 1 for j in range(8)]

    LQEntries = LQEntries_List[mask_i[7]]
    SQEntries = SQEntries_List[mask_i[6]]
    l1d_size = l1d_size_List[mask_i[5]]
    l1i_size = l1i_size_List[mask_i[4]]
    l2_size = l2_size_List[mask_i[3]]
    bp_type = bp_type_List[mask_i[2]]
    ROBEntries = ROBEntries_List[mask_i[1]]
    numIQEntries = numIQEntries_List[mask_i[0]]
    
    curOPFolder = f"{OP_FOLDER}/output_LQEntries_{LQEntries}_SQEntries_{SQEntries}_l1d_size_{l1d_size}_l1i_size_{l1i_size}_l2_size_{l2_size}_bp_type_{bp_type}_ROBEntries_{ROBEntries}_numIQEntries_{numIQEntries}"
        
    if not os.path.exists(os.path.expanduser(curOPFolder)):        
        os.makedirs(os.path.expanduser(curOPFolder))
    else:
        print("Skipping simulation for index because folder already exists : ", i)
        continue
    
    command = [
                os.path.expanduser("~/gem5/build/X86/gem5.opt"), 
                "-d", os.path.expanduser(curOPFolder), 
                os.path.expanduser(CONFIG_PATH), 
                "-c", os.path.expanduser(CPP_FILE),
                f"--LQEntries={LQEntries}",
                f"--SQEntries={SQEntries}",
                f"--l1d_size={l1d_size}",
                f"--l1i_size={l1i_size}",
                f"--l2_size={l2_size}",
                f"--bp_type={bp_type}",
                f"--ROBEntries={ROBEntries}",
                f"--numIQEntries={numIQEntries}"
            ]
    
    print("\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
    print("Index : ", i)
    print("Starting simulation with command", " ".join(command), flush=True)
    
    command_output = subprocess.run(command, capture_output=True)
    
    with open(os.path.expanduser(f"{curOPFolder}/command_output.txt"), "w") as f:
        print(command_output.stdout, file = f)
            
    print("Simulation finished with return code", command_output.returncode, flush=True)
    print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    if command_output.returncode != 0:
        break

