import os
import glob
import configparser

class SimRun:
    def __init__(self, config, stats):
        self.config_file = config
        self.stats_file = stats   
        self.cpu_type = ''
        self.clock_speed = 0
        self.sim_seconds = 0
        self.l1i = 0
        self.l1d = 0
        self.l2= 0
        self.l1direct = False


    def parse_run_files(self):
        # Parse the config file using configparser
        config = configparser.ConfigParser()
        config.read(self.config_file)
        # Extract the CPU type from the [system.cpu] section
        self.cpu_type = config.get('system.cpu', 'type')
        self.clock_speed= config.get('system.clk_domain','clock')


        # Read the stats file for simSeconds
        with open(self.stats_file, 'r') as stats:
            for line in stats:
                if 'simSeconds' in line:
                    self.sim_seconds = line.split()[1]  # Extract the value of simSeconds
                    break



def process_directory(directory):
    # Find all config*.ini and stats*.txt files
    config_files = glob.glob(os.path.join(directory, 'config*.ini'))
    stats_files = glob.glob(os.path.join(directory, 'stats*.txt'))

    # Create a dictionary to match config files with corresponding stats files
    file_pairs = {}

    # Iterate through config files and match with stats files
    for config_file in config_files:
        # Extract the wildcard part (i.e., the * in config*.ini)
        base_name = os.path.basename(config_file).replace('config', '').replace('.ini', '')

        # Find the corresponding stats*.txt file
        matching_stats_file = [f for f in stats_files if f'/{base_name}.txt' in f]
        if matching_stats_file:
            file_pairs[config_file] = matching_stats_file[0]

    return file_pairs


# Directory containing the config*.ini and stats*.txt files
x86Directory = './X86'
riscDirectory = './RISCV'

# Process the directory
x86FilePairs = process_directory(x86Directory)
riscFilePairs = process_directory(riscDirectory)

x86Runs = []
for config_file,stats_file in x86FilePairs.items():
    run = SimRun(config_file, stats_file)
    run.parse_run_files()
    x86Runs.append(run)

riscRuns = []
for config_file,stats_file in riscFilePairs.items():
    run = SimRun(config_file, stats_file)
    run.parse_run_files()
    riscRuns.append(run)