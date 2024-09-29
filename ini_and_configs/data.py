import os
import re
import glob
import configparser
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd

class SimRun:
    def __init__(self, config, stats, num):
        self.config_file = config
        self.stats_file = stats  
        self.run_num = num  
        self.cpu_type = ''
        self.clock_speed = 0
        self.sim_seconds = 0
        self.l1i = 0
        self.l1iAssoc = 0
        self.l1d = 0
        self.l1dAssoc = 0
        self.l2= 0
     
    def parseRunFiles(self):
        # Parse the config file using configparser
        config = configparser.ConfigParser()
        config.read(self.config_file)
        # Extract the CPU type from the [system.cpu] section
        self.cpu_type       = config.get('system.cpu', 'type')[4:]
        speed = 1000/int(config.get('system.clk_domain','clock'))
        self.clock_speed    = str(round(speed,1))
        self.l1i            = int(int(config.get('system.cpu.icache','size',fallback=self.l1i))/1024)
        self.l1iAssoc       = config.get('system.cpu.icache','assoc',fallback=self.l1iAssoc) 
        self.l1d            = int(int(config.get('system.cpu.dcache','size',fallback=self.l1d)) /1024)
        self.l1iAssoc       = config.get('system.cpu.dcache','assoc',fallback=self.l1dAssoc)
        self.l2             = int(int(config.get('system.l2cache','size',fallback=self.l2)) /1024)

        # Read the stats file for simSeconds
        with open(self.stats_file, 'r') as stats:
            for line in stats:
                if 'simSeconds' in line:
                    self.sim_seconds = line.split()[1]  # Extract the value of simSeconds
                    #print(self.sim_seconds)
                    break

    def getRunProperties(self):
        return [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]



def processDirectory(directory):
    # Find all config*.ini and stats*.txt files
    config_files = glob.glob(os.path.join(directory, 'config*.ini'))
    stats_files = glob.glob(os.path.join(directory, 'stats*.txt'))

    # Create a dictionary to match config files with corresponding stats files
    file_pairs = {}

    # Iterate through config files and match with stats files
    for config_file in config_files:
        # Extract the wildcard part (i.e., the * in config*.ini)
        base_name = os.path.basename(config_file).replace('config', '').replace('.ini', '')
        match = re.search(r'run(\d+)', base_name)
        if match:
            run_num = match.group(1)  # Extract the digits following "run"
        else:
            run_num = None  # Handle case where "run" is not found

        # Find the corresponding stats*.txt file
        matching_stats_file = [f for f in stats_files if f'stats{base_name}.txt' in f]
        if matching_stats_file:
            file_pairs[run_num] = (config_file,matching_stats_file[0])
           
    return file_pairs

# Prepare data from the list of runs
def prepare_plot_data(runs):
    data = {
        'label': [],
        'run_number':[],
        'sim_seconds': [],
        'cpu_type': []
    }

    for i, run in enumerate(runs):
        # Create a label combining cpu_type and clock_speed
        data['run_number'].append(run.run_num)

        cacheStr = ""
        if (run.l1i): 
            cacheStr = f" L1i:{run.l1i:<5} L1d:{run.l1d:<5} L1Assoc:{run.l1iAssoc:<5} L2:{run.l2}"
        label = f"Run {run.run_num:<3}({run.sim_seconds}): {run.cpu_type:<20} {run.clock_speed:<5} MHz {cacheStr}"
        #print(label)
        data['cpu_type'].append(run.cpu_type)
        data['label'].append(label)
        data['sim_seconds'].append(float(run.sim_seconds))
    
    return pd.DataFrame(data)  # Convert to a pandas DataFrame

# Plot the runs
# Plot the runs with labels and continuous Y-axis for sim_seconds
def plot_runs(runs, title='Simulation Runs'):
    df = prepare_plot_data(runs)
    legend_labels = df['label'].tolist()

    
    run3 = df[(df['run_number']=='3')].index
    df = df.drop(run3)

    fig,ax = plt.subplots(figsize=(12,8))

    ax.bar(df['run_number'],df['sim_seconds'], color='b')

    ax.set_xlabel('Run number', fontweight ='bold', fontsize = 15) 
    ax.set_ylabel('Simulated Seconds', fontweight ='bold', fontsize = 15) 
    ax.set_title(title)

    ax.yaxis.set_major_locator(ticker.MultipleLocator(0.1))

    key_text = ""
    for i,label in enumerate(legend_labels):
        key_text += f"{label}\n"

        
    fig.text(0.1, 0, key_text, ha='left', fontsize=10, wrap=True, fontfamily='monospace')

    #plt.legend()
    plt.tight_layout(rect=[0, 0.2, 1, 1])  # Leave space at the bottom for the key
    plt.show()


if __name__=="__main__":
    # Directory containing the config*.ini and stats*.txt files
    x86Directory = './X86'
    riscDirectory = './RISCV'

    # Process the directory
    x86FilePairs = processDirectory(x86Directory)
    riscFilePairs = processDirectory(riscDirectory)

    x86Runs = []
    for run_num,(config_file,stats_file) in x86FilePairs.items():
        run = SimRun(config_file, stats_file,run_num)
        run.parseRunFiles()
        x86Runs.append(run)
        #print(run.stats_file, "\t\t" ,run.sim_seconds)
    x86Runs.sort(key=lambda x: int(x.run_num))

    riscRuns = []
    for run_num,(config_file,stats_file) in riscFilePairs.items():
        run = SimRun(config_file, stats_file,run_num)
        run.parseRunFiles()
        riscRuns.append(run)
        #print(run.stats_file,"\t\t",run.sim_seconds)
    riscRuns.sort(key=lambda x: int(x.run_num))

    x86Runs_no3 = [x for x in x86Runs if not x.run_num == '3' ]
    riscRuns_no3 = [x for x in riscRuns if not x.run_num == '3' ]

    plot_runs(x86Runs, title='X86 Simulation Runs')
    plot_runs(riscRuns, title='RISC-V Simulation Runs')