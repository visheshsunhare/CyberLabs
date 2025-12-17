# CyberLabs
Minimal Runtime Container Project

mDocker is a simple version of Docker built from scratch to learn how containers work. It uses core Linux features to create an isolated "box" where applications can run safely without touching the main system.

# How to Set Up
Before running the script, you need a "RootFS" folder (the container's hard drive).

Create a folder and download Alpine Linux:

  mkdir my_rootfs
  
  cd my_rootfs 
  
  wget https://dl-cdn.alpinelinux.org/alpine/v3.19/releases/x86_64/alpine-minirootfs-3.19.1-x86_64.tar.gz
  
  tar -xvf alpine-minirootfs-3.19.1-x86_64.tar.gz
  
  cd ..
  
# How to Run
You must use sudo because the script needs permission to create new namespaces

#Usage: sudo python3 mdocker.py run <path_to_rootfs> <command>

sudo python3 mdocker.py run ./my_rootfs /bin/sh

# Verification
Once inside the container shell, try these commands:

hostname: Should show mDocker-box.

ls /: Should show only the container files.

ps: Should show your shell as PID 1.
