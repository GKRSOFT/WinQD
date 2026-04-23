## WinQD: Windows in Qemu on Docker Sandbox
    This documentaion is for installing on Unbuntu 22.04
        QEMU: hxxps://documentation.ubuntu.com/server/how-to/virtualisation/qemu/
        Remmina VNC: hxxps://remmina.org
        Qemus/qemu: hxxps://github.com/qemus/qemu
        api.py from Cuckoo Sandbox - hxxp://www.cuckoosandbox.org
           with modifications from B9Software
	Additional programs, documents & configurations are Copyrighted 2026 B9Software
	NOTE: Qemu and Reminna VNC software must be installed first.

#### WARNING: Sandbox may be used for MALWARE ANALYSIS ENVIRONMENT
This software could be used for analyzing malicious software. Files submitted to this sandbox are executed in a virtualized containerized environment. While isolated, malware can potentially break out of virtualization (sandbox escape), infect the host machine, or attack the local network.

* WARNING: Use at your own risk: The software is provided "as is" without any warranties.
    Isolation: Ensure this environment is properly isolated from production networks.
    Responsibility: The user assumes all responsibility for any damage, data loss, or security breaches resulting from the use of this tool.


### WinQD Instalallation:
	cd WinQD
	wget hxxps://github.com/qemus/qemu/archive/refs/heads/master.zip
	unzip master.zip .
	cd qemu-master
	rm compose.yml kubernetes.yml readme.md
	cd ..
	mv qemu-master/* .
	rm *.zip
	rm -r qemu-master
	cd src
	
## Modify file src/entry.sh and save:
	coment out lines 15,16 & 30
	add line exec ./api.py
	
## Modify file src/server.sh and save:
	change line 6 "8006" to "8000"
	change line 46 nginx -e stderr to nginx

## Modify file src/config.sh and save:
	change blank line 3 to : "${DISK_OPTS:=""}"
		
## Replace file web/conf/nginx.conf:
	mv web/conf/nginx.conf web/conf/nginx.orig
	cp nginx.conf  web/conf/

## Create folders:
	mkdir image
	mkdir iso
	
### Search and download files from internet to the iso folder:
* 	Win10_1909_English_x64.iso
* 	virtio-win-0.1.285.iso
  
### Create a qemu hard drive image:
   qemu-img create -f qcow2 image/hdd.img 40G

### Create Qemu install Windows on the hard drive image: 
	sudo qemu-system-x86_64 -enable-kvm \
      -machine q35 -smp sockets=1,cores=1,threads=2 -m 2048 \
      -usb -device usb-kbd -device usb-tablet -rtc base=localtime \
      -net nic,model=virtio -net user,hostfwd=tcp::4444-:4444 \
      -drive file=image/hdd.img,media=disk,if=virtio \
      -drive file=iso/Win10_1909_English_x64.iso,media=cdrom \
      -drive file=iso/virtio-win-0.1.285.iso,media=cdrom

### Make the following changes:
    Add the VirtIO drivers durring windows creation from the E:\viostor\w10\amd64 
    Upgrade Internet Explorer 11 to Microsoft Edge
    Install the agent software 
    Shutdown the virtual machine

### Create the snapshot:
	qemu-img create -f qcow2 -b image/hdd.img -F qcow2 snapshot.img
    qemu-img create -f qcow2 -b image/hdd.img -F qcow2 snapshot2.img
    qemu-system-x86_64 -enable-kvm \
      -machine q35 -vnc :0 -cpu host -smp sockets=1,cores=1,threads=2 -m 2048 \
      -usb -device usb-kbd -device usb-tablet -rtc base=localtime \
      -net nic,model=virtio -net user,hostfwd=tcp::4444-:4444 \
      -drive file=snapshot.img,media=disk,if=virtio \
      -monitor stdio
        
### Final steps:
	Open Remmina vnc software for 127.0.0.1:5900
    Login to windows and prepare and start agent software on port 8008
    In the terminal type at the qemu prompt:
	    (qemu) savevm windows
    
    Then type quit to stop VM:
        (qemu) quit
        
### Build the Docker file and Image:
## Change: 
   		#FROM debian:trixie-slim
		FROM ubuntu:22.04 
		
## Add the following lines:
		# WinQD
		RUN ln -s /image/hdd.img /hdd.img
		COPY --chmod=664 snapshot.img /
		COPY --chmod=664 snapshot2.img /
		RUN set -eu && \
			apt-get update && \
			apt-get --no-install-recommends -y install \
				python3-pip \
				usbutils && \
			python3 -m pip install bottle
		COPY --chmod=755 ./api.py /run/
		COPY --chmod=744 nginx.conf /etc/nginx/default.conf
   
## NOTE: 
Comment out ENTRYPOINT line in Dockerfile for interactive mode

## Create Sandbox:
		docker build -t WinQD/sandbox .         

### Running container interactive:
    docker run -it --rm  -p 8000:8000 --device=/dev/kvm --device=/dev/net/tun --cap-add NET_ADMIN --stop-timeout 120 -v `pwd`/image:/image WinQD/sandbox /bin/bash

### Running container in the background:
    docker run --rm -d   -p 8000:8000 --device=/dev/kvm --device=/dev/net/tun --cap-add NET_ADMIN --stop-timeout 120 -v `pwd`/image:/image WinQD/sandbox

### Docker Alias:
	alias dockerNode="docker inspect $(docker ps -q ) --format='{{.Name}} {{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}'"
	alias dockerip="echo `dockerNode`| cut -d ' ' -f 2"
       
### Docker Compose Scale Container:
   docker compose up --scale Sandbox=1 -d
   dockerip

### Open browser:
   firefox `echo $(dockerip)":8000\addUSB"`
   firefox `echo $(dockerip)":8000"`
   
