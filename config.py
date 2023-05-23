import argparse
# import the m5 (gem5) library
import m5
# import all of the SimObjects
from m5.objects import *
from m5.util import addToPath

addToPath("./")
addToPath("../")

import options

parser = argparse.ArgumentParser()
options.addSEOptions(parser)
options.addCommonOptions(parser)

args = parser.parse_args()

class L1Cache(Cache):
    # Simple L1 Cache with default values
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20
    assoc = 4
    
    def __init__(self, options = None):
        super(L1Cache, self).__init__()

    def connectBus(self, bus):
        # Connect this cache to a memory-side bus
        self.mem_side = bus.cpu_side_ports

    def connectCPU(self, cpu):
        raise NotImplementedError
        
class L1ICache(L1Cache):
    # Simple L1 instruction cache with default values
    size = args.l1i_size

    def __init__(self, opts=None):
        super(L1ICache, self).__init__(opts)
        pass
        
    def connectCPU(self, cpu):
        # Connect this cache's port to a CPU icache port
        self.cpu_side = cpu.icache_port
        
class L1DCache(L1Cache):
    # Simple L1 data cache with default values
    size = args.l1d_size
    
    def __init__(self, opts=None):
        super(L1DCache, self).__init__(opts)
        
    def connectCPU(self, cpu):
        # Connect this cache's port to a CPU dcache port
        self.cpu_side = cpu.dcache_port
        
class L2Cache(Cache):
    # Simple L2 Cache with default values
    # Default parameters
    tag_latency = 20
    data_latency = 20
    response_latency = 20
    mshrs = 20
    tgts_per_mshr = 12
    assoc = 8
    
    size = args.l2_size

    def __init__(self, opts=None):
        super(L2Cache, self).__init__()
        
    def connectCPUSideBus(self, bus):
        self.cpu_side = bus.mem_side_ports

    def connectMemSideBus(self, bus):
        self.mem_side = bus.cpu_side_ports

# Create the system to be simulated
system = System()

# Set the clock frequency of the system (and all of its children)
system.clk_domain = SrcClockDomain()                # Clock domain
system.clk_domain.clock = '2GHz'                    # Clock frequency
system.clk_domain.voltage_domain = VoltageDomain()  # Voltage domain

# Set the memory mode of the system
system.mem_mode = 'timing'                          # Use timing access mode

# Set the memory range of the system
# Add 1GB of memory (single memory range)
system.mem_ranges = [AddrRange('1GB')]

# Create a CPU for the system
system.cpu = DerivO3CPU()                           # Use the DerivO3CPU

system.cache_line_size = 64                         # Set the cache line size
system.cpu.icache = L1ICache()                      # Create the L1 instr cache
system.cpu.dcache = L1DCache()                      # Create the L1 data cache
system.cpu.l2cache = L2Cache()                      # Create the L2 cache

# Create a system bus for the system, a system crossbar in this case
system.membus = SystemXBar()

# Create a memory bus, a coherent crossbar, in this case
system.l2bus = L2XBar()

# Connect the instruction and data caches to the CPU
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

# Hook the CPU ports up to the l2bus
system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)

# Create an L2 cache and connect it to the l2bus
system.cpu.l2cache.connectCPUSideBus(system.l2bus)

# Connect the L2 cache to the membus
system.cpu.l2cache.connectMemSideBus(system.membus)

# Create the interrupt controller for the CPU and connect to the membus
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

system.system_port = system.membus.cpu_side_ports

# Create a memory controller for the system
system.mem_ctrl = MemCtrl()                          # Use the MemCtrl
system.mem_ctrl.dram = DDR3_1600_8x8()               # Use the DDR3_1600_8x8 DRAM
system.mem_ctrl.dram.range = system.mem_ranges[0]    # Set the memory range
system.mem_ctrl.port = system.membus.mem_side_ports  # Set the memory port


system.cpu.numRobs = 1                              # Number of ROBs

system.cpu.LQEntries = args.LQEntries               # Number of load queue Entries
system.cpu.SQEntries = args.SQEntries               # Number of store queue Entries
system.cpu.numIQEntries = args.numIQEntries         # Number of instruction queue entries
system.cpu.numROBEntries = args.ROBEntries          # Number of reorder buffer entries

if args.bp_type == 'TournamentBP':                  # Branch predictor type
    system.cpu.branchPred = TournamentBP()          # Use the TournamentBP
elif args.bp_type == 'BimodalBP':                   # Branch predictor type
    system.cpu.branchPred = BimodalBP()             # Use the BimodalBP

binary = args.cmd

system.workload = SEWorkload.init_compatible(binary)

# Create a process for a simple "Hello World" application
process = Process()

# Set the command
# cmd is a list which begins with the executable (like argv)
process.cmd = [binary]

# Set the cpu to use the process as its workload and create thread contexts
system.cpu.workload = process
system.cpu.createThreads()

# set up the root SimObject and start the simulation
root = Root(full_system=False, system=system)

# instantiate all of the objects we've created above
m5.instantiate()

print("Beginning simulation!")
exit_event = m5.simulate()
print('Exiting @ tick %i because %s' % (m5.curTick(), exit_event.getCause()))

