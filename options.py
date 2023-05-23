from m5.objects import *
from common.Benchmarks import *
from common import ObjectList

vio_9p_help = """\
Enable the Virtio 9P device and set the path to share. The default 9p path is
m5ou5/9p/share, and it can be changed by setting VirtIO9p.root with --param. A
sample guest mount command is: "mount -t 9p -o
trans=virtio,version=9p2000.L,aname=<host-full-path> gem5 /mnt/9p" where
"<host-full-path>" is the full path being shared on the host, and "gem5" is a
fixed mount tag. This option requires the diod 9P server to be installed in the
host PATH or selected with with: VirtIO9PDiod.diod.
"""

# Add the very basic options that work also in the case of the no ISA
# being used, and consequently no CPUs, but rather various types of
# testers and traffic generators.

def addNoISAOptions(parser):
    # Cache Options
    parser.add_argument("--l1d_size", type=str, default="32kB")
    parser.add_argument("--l1i_size", type=str, default="8kB")
    parser.add_argument("--l2_size", type=str, default="256kB")

# Add common options that assume a non-NULL ISA.

def addCommonOptions(parser):
    # start by adding the base options that do not assume an ISA
    addNoISAOptions(parser)

    parser.add_argument(
        "--LQEntries", 
        default=32, 
        help="Number of Load Queue entries", 
        type=int
    )
    parser.add_argument(
        "--SQEntries", 
        default=32,
        help="Number of Store Queue entries", 
        type=int
    )
    parser.add_argument(
        "--bp_type",
        default="TournamentBP",
        choices=ObjectList.bp_list.get_names(),
        help="Type of branch predictor to run the cpu with",
    )
    parser.add_argument(
        "--ROBEntries", 
        default=128, 
        help="Number of Reorder Buffer entries", 
        type=int
    )
    parser.add_argument(
        "--numIQEntries", 
        default=16, 
        help="Number of Instruction Queue entries", 
        type=int
    )
    parser.add_argument(
        "--stats-root",
        action="append",
        default=[],
        help="If given, dump only stats of objects under the given SimObject. "
        "SimObjects are identified with Python notation as in: "
        "system.cpu[0].mmu. All elements of an array can be selected at "
        "once with: system.cpu[:].mmu. If given multiple times, dump stats "
        "that are present under any of the roots. If not given, dump all "
        "stats. ",
    )

def addSEOptions(parser):
    # Benchmark options
    parser.add_argument(
        "-c",
        "--cmd",
        default="",
        help="The binary to run in syscall emulation mode.",
    )
    parser.add_argument(
        "-o",
        "--options",
        default="",
        help="""The options to pass to the binary, use " "
                              around the entire string""",
    )
    parser.add_argument(
        "-e",
        "--env",
        default="",
        help="Initialize workload environment from text file.",
    )
    parser.add_argument(
        "-i", 
        "--input", 
        default="", 
        help="Read stdin from a file."
    )
    parser.add_argument(
        "--output", 
        default="", 
        help="Redirect stdout to a file."
    )
    parser.add_argument(
        "--errout", 
        default="", 
        help="Redirect stderr to a file."
    )
    parser.add_argument(
        "--chroot",
        action="store",
        type=str,
        default=None,
        help="The chroot option allows a user to alter the "
        "search path for processes running in SE mode. "
        "Normally, the search path would begin at the "
        "root of the filesystem (i.e. /). With chroot, "
        "a user can force the process to begin looking at"
        "some other location (i.e. /home/user/rand_dir)."
        "The intended use is to trick sophisticated "
        "software which queries the __HOST__ filesystem "
        "for information or functionality. Instead of "
        "finding files on the __HOST__ filesystem, the "
        "process will find the user's replacment files.",
    )
    parser.add_argument(
        "--interp-dir",
        action="store",
        type=str,
        default=None,
        help="The interp-dir option is used for "
        "setting the interpreter's path. This will "
        "allow to load the guest dynamic linker/loader "
        "itself from the elf binary. The option points to "
        "the parent folder of the guest /lib in the "
        "host fs",
    )

    parser.add_argument(
        "--redirects",
        action="append",
        type=str,
        default=[],
        help="A collection of one or more redirect paths "
        "to be used in syscall emulation."
        "Usage: gem5.opt [...] --redirects /dir1=/path/"
        "to/host/dir1 --redirects /dir2=/path/to/host/dir2",
    )
    parser.add_argument(
        "--wait-gdb",
        default=False,
        action="store_true",
        help="Wait for remote GDB to connect.",
    )

