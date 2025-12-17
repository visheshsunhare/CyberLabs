import os, sys
import ctypes
import argparse

# These are special numbers Linux uses to turn on isolation
CLONE_NEWNS   = 0x00020000 # For isolating files
CLONE_NEWUTS  = 0x04000000 # For isolating the hostname
CLONE_NEWPID  = 0x20000000 # For isolating process IDs

class MDockerRuntime:
    def __init__(self, rootfs_path):
        # Save the path to the folder we are using as a hard drive
        self.root_path = os.path.abspath(rootfs_path)
        # Bridge to run C commands from Python
        self.libc = ctypes.CDLL('libc.so.6')

    def setup_isolation(self):
        # This part tricks the app into thinking it's on a new computer
        print("[*] Hiding the host system using Namespaces...")
        
        # Tell the kernel to start a new private "box"
        self.libc.unshare(CLONE_NEWNS | CLONE_NEWUTS | CLONE_NEWPID)
        
        # Change the computer name inside the box
        self.libc.sethostname(b"mDocker-box", 11)

    def mount_and_pivot(self):
        # This locks the app inside its own little folder
        print(f"[*] Locking the app into: {self.root_path}")
        
        # Make the folder the new "root" (/)
        os.chroot(self.root_path)
        os.chdir("/")
        
        # We need this folder so things like 'ps' work
        if not os.path.exists("/proc"):
            os.makedirs("/proc")
        
        # Connect the process info to the container
        self.libc.mount(b"proc", b"/proc", b"proc", 0, None)

    def start(self, user_args):
        # Run the isolation logic first
        self.setup_isolation()

        # Split the program into two so the child can be PID 1
        # A process doesn't see its new PID namespace until it has a child
        pid = os.fork()
        
        if pid == 0:
            # This is the "child" running inside the box
            self.mount_and_pivot()
            
            print(f"[*] Starting your app: {' '.join(user_args)}")
            try:
                # Actually run the command (like /bin/sh)
                os.execvp(user_args[0], user_args)
            except Exception as e:
                print(f"Oops, it failed to start: {e}")
                sys.exit(1)
        else:
            # The "parent" just waits for the container to finish
            _, status = os.waitpid(pid, 0)
            print(f"\n[*] mDocker is done. (Exit Status: {status})")

def main():
    # Setup the command line tool
    parser = argparse.ArgumentParser(description="mDocker - My Simple Docker Clone")
    commands = parser.add_subparsers(dest="action")

    # The 'run' command
    run_cmd = commands.add_parser("run")
    run_cmd.add_argument("fs_path", help="Folder for the RootFS")
    run_cmd.add_argument("command", nargs="+", help="The command to run inside")

    args = parser.parse_args()

    if args.action == "run":
        # Check if we are running as root
        if os.geteuid() != 0:
            print("Error: You need to use sudo to run this!")
            sys.exit(1)
            
        runtime = MDockerRuntime(args.fs_path)
        runtime.start(args.command)

if __name__ == "__main__":
    main()