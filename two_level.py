import m5
from m5.objects import *
from caches import *
import argparse

from m5.util import addToPath

addToPath("../../")

thispath = os.path.dirname(os.path.realpath(__file__))
default_binary = os.path.join(
    thispath,
    "../../../",
    "tests/test-progs/hello/bin/x86/linux/hello",
)
riscv_default_binary = os.path.join(
    thispath,
    "../../../",
    "tests/test-progs/hello/bin/riscv/linux/hello",
)
default_clock = "1GHz"


from common import Options

parser = argparse.ArgumentParser()
Options.addCommonOptions(parser)
Options.addSEOptions(parser)


parser.add_argument(
    "--cpu",
    default="Simple",
    type=str,
    help="""Specify the CPU model ie simple, minor""",
)
parser.add_argument(
    "--riscv",
    default=False,
    type=bool,
    help="""Specify RISC-V Arch, X86 when false""",
)

parser.add_argument(
    "--clock",
    default=default_clock,
    type=str,
    help="""Specify the CPU model ie simple, minor""",
)

options = parser.parse_args()

if (not options.cmd):
    if(not options.riscv): options.cmd = default_binary 
    else: options.cmd = riscv_default_binary
#print(options.caches)
system = System()

system.clk_domain = SrcClockDomain()
system.clk_domain.clock = options.clock
system.clk_domain.voltage_domain = VoltageDomain()

system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

#CPU
if(not options.riscv):
    if(options.cpu == "minor"):
        system.cpu = X86MinorCPU()
    else:
        system.cpu = X86TimingSimpleCPU()
else:
    if(options.cpu == "minor"):
        system.cpu = RiscvMinorCPU()
    else:
        system.cpu = RiscvTimingSimpleCPU()

#system.cpu_clk_domain = SrcClockDomain(clock=options.clock, voltage_domain=system.clk_domain.voltage_domain)
#apparently this does nothing, all runs gave  the same result

if(not options.caches):
    system.membus = SystemXBar()

    system.cpu.icache_port = system.membus.cpu_side_ports
    system.cpu.dcache_port = system.membus.cpu_side_ports

else:
    #L1
    system.cpu.icache = L1ICache(options)
    system.cpu.dcache = L1DCache(options)

    #Connect L1
    system.cpu.icache.connectCPU(system.cpu)
    system.cpu.dcache.connectCPU(system.cpu)

    #L2
    system.l2bus = L2XBar()

    system.cpu.icache.connectBus(system.l2bus)
    system.cpu.dcache.connectBus(system.l2bus)

    system.l2cache = L2Cache(options)
    system.l2cache.connectCPUSideBus(system.l2bus)
    #membus created first so we can connect L2 to it
    system.membus = SystemXBar()
    system.l2cache.connectMemSideBus(system.membus)


#####################################################

system.cpu.createInterruptController()

######################################
#X86 only
if(not  options.riscv ):
    system.cpu.interrupts[0].pio = system.membus.mem_side_ports
    system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
    system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports
#######################################

system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

system.system_port = system.membus.cpu_side_ports



# for gem5 V21 and beyond
system.workload = SEWorkload.init_compatible(options.cmd)

process = Process()
process.cmd = [options.cmd,options.options]
system.cpu.workload = process
system.cpu.createThreads()

root = Root(full_system = False, system = system)
m5.instantiate()

print("Beginning simulation!")
exit_event = m5.simulate()

print('Exiting @ tick {} because {}'
      .format(m5.curTick(), exit_event.getCause()))