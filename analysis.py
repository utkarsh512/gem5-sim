import os
import re
import shutil
import csv

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns


OP_FOLDER = os.path.join(os.getcwd(), "outputs")
TOP_10_FOLDER = os.path.join(os.getcwd(), "m5out")
PLOTS_FOLDER = os.path.join(os.getcwd(), "plots")
CONFIGS_CSV_FILE = os.path.join(os.getcwd(), "best_10_configs.csv")

params = {
    'system.cpu.cpi': 'cpi',
    'system.cpu.iew.branchMispredicts': 'mispred_exec',
    'system.cpu.iew.predictedNotTakenIncorrect': 'pred_NT_incorrect',
    'system.cpu.iew.predictedTakenIncorrect': 'pred_T_incorrect',
    'system.cpu.ipc': 'ipc',
    'system.cpu.branchPred.BTBHitRatio': 'btb_hit_ratio',
    'system.cpu.rob.reads': 'rob_reads',
    'system.cpu.rob.writes': 'rob_writes',
    'system.cpu.iew.lsqFullEvents': 'lsq_full_stall',
    'system.cpu.lsq0.forwLoads': 'ld_st_data_fwd',
    'system.cpu.lsq0.blockedByCache': 'cache_blocked_memfail',

    'system.cpu.icache.overallMissRate::total': 'overall_miss_rate_icache',
    'system.cpu.l2cache.overallMissRate::total': 'overall_miss_rate_l2cache',
    'system.cpu.dcache.overallMissRate::total': 'overall_miss_rate_dcache',

    'system.cpu.dcache.overallAvgMissLatency::total': 'overall_avg_miss_lat_dcache',
    'system.cpu.icache.overallAvgMissLatency::total': 'overall_avg_miss_lat_icache',
    'system.cpu.l2cache.overallAvgMissLatency::total': 'overall_avg_miss_lat_l2cache',

    'system.cpu.dcache.overallMisses::total': 'overall_miss_cycle_dcache',
    'system.cpu.icache.overallMisses::total': 'overall_miss_cycle_icache',
    'system.cpu.l2cache.overallMisses::total': 'overall_miss_cycle_l2cache',
}

def get_stats_from_file(file_path):
    if not os.path.isfile(file_path):
        raise Exception("File doesn't exist")
    
    stats = {}
    with open(file_path, 'r') as fin:
        lines = fin.readlines()

        for line in lines:
            line = re.sub("\s+", " ", line)
            
            words = line.split(" ")
            if words[0] in params:
                stats[params[words[0]]] = float(words[1])

    return stats

def extract_parameters(config_str):
    '''
    Expects an input of the form output_LQEntries_32....
    and returns a directory of the form {"LQEntries": "32", ...}
    '''
    words = config_str.split("_")
    
    config_dict = dict()
    idx = 1

    config_dict["LQEntries"] = words[2]
    config_dict["SQEntries"] = words[4]
    config_dict["l1d_size"] = words[7]
    config_dict["l1i_size"] = words[10]
    config_dict["l2_size"] = words[13]
    config_dict["bp_type"] = words[16]
    config_dict["ROBEntries"] = words[18]
    config_dict["numIQEntries"] = words[20]
    

    return config_dict


config_to_stats = []

# This segment of code populates config_to_stats which is a list 
# of tuples (filename, dictionary of stats)
for dir in os.listdir(OP_FOLDER):
    dir_path = os.path.join(OP_FOLDER, dir)

    if os.path.isdir(dir_path):
        filepath = os.path.join(dir_path, "stats.txt")

        config_to_stats.append((dir, get_stats_from_file(filepath)))


# Here config_to_stats is sorted based on CPI
config_to_stats.sort(key = lambda config: config[1]["cpi"])

# We have a list of configs and their stats, sorted from best to worst CPI
# We copy the top 10 such sub-directories inside 
if not os.path.exists(TOP_10_FOLDER):
    os.makedirs(TOP_10_FOLDER)

for dir, _ in config_to_stats[:10]:
    orig_dir_path = os.path.join(OP_FOLDER, dir)
    copy_dir_path = os.path.join(TOP_10_FOLDER, dir)

    if not os.path.exists(copy_dir_path):
        os.makedirs(copy_dir_path)
        shutil.copyfile(os.path.join(orig_dir_path, "stats.txt"), os.path.join(copy_dir_path, "stats.txt"))

# Create a CSV of configs and CPI corresponding to best 10 configs
fields = []
rows = []
for dir, stats in config_to_stats[:10]:
    parameters = extract_parameters(dir)
    if len(fields) == 0:
        fields = list(parameters.keys())
        fields.append("cpi")
    
    values = list(parameters.values())
    values.append(stats["cpi"])
    rows.append(values)

with open(CONFIGS_CSV_FILE, 'w') as f:
    # using csv.writer method from CSV package
    write = csv.writer(f)
      
    write.writerow(fields)
    write.writerows(rows) 

# Make plots for each of the stats
if not os.path.exists(PLOTS_FOLDER):
    os.makedirs(PLOTS_FOLDER)

for key in params.values():
    values = []

    for _, stats in config_to_stats[:10]:
        values.append(stats[key])

    x = list(range(1, len(values)+1))

    sns.set_style("darkgrid", {"grid.color": ".4", "grid.linestyle": ":"})
    plt.figure(figsize= (10, 8))

    ax = plt.gca()

    y_formatter = mticker.ScalarFormatter(useOffset=False)
    ax.yaxis.set_major_formatter(y_formatter)

    plt.plot(x, values, marker= 'o')
    plt.xlabel("configs")
    plt.ylabel(key)
    plt.xticks(x)
    plt.title(key + " for top 10 configs by CPI")
    plt.savefig(os.path.join(PLOTS_FOLDER,key+".png"))
    
