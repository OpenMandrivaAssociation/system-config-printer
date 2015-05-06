#!/bin/env python3
# Tiago Salem Herrmann <salem@mandriva.com>
# Philippe Makowski <philippem@mageia.org>
import dbus, sys, os, time, signal, re
import traceback
import cups, cupshelpers
import socket
import struct
import fcntl
import math
import ctypes
import ipaddress
import subprocess
import platform

SIOCGIFNETMASK = 0x891B
SIOCGIFADDR = 0x8915

def make2simplename(make):
    make1 = make.lower().strip()
    hp = ["hp", "hewlett packard", "hewlett-packard", "hewlett_packard", "hewlettpackard"]
    epson = ["Epson"]
    if hp.count(make1):
        return "hp"
    if epson.count(make1):
        return "epson"
    return make.strip().lower()

def reload_parport():
    has_ppdev=False
    if os.system("/sbin/rmmod ppdev"):
        has_ppdev=True
    os.system("/sbin/rmmod lp")
    os.system("/sbin/rmmod parport_pc")
    os.system("/sbin/rmmod parport")
    os.system("/sbin/modprobe lp")
    if has_ppdev:
        os.system("/sbin/modprobe ppdev")

def is_installed_packages(packages):
    signal.signal (signal.SIGCHLD, signal.SIG_DFL)

    all_packages = ""
    for package in packages:
        all_packages += " "+ package
    if all_packages.__len__() == 0:
        return False

    if os.system("/bin/rpm -q " + all_packages) == 0:
        return True
    else:
        return False

def install_packages(packages):
    all_packages = ""
    for package in packages:
        all_packages += " "+ package
    if all_packages.__len__() == 0:
        return False

    os.system("gurpmi "+all_packages)
    if is_installed_packages(packages):
        return True
    else:
        return False

def guess_driver_packages(make, model):
    task_printing_misc = ["alps", "anitech", "apollo", "apple", "avery", "brother", "citizen", "citoh", "compaq", "dec", "dell", "dymo", "fujitsu", "ibm", "imagen", "infotec", "kodak", "kyocera", "minolta", "mitsubishi", "nec", "oce", "olivetti", "panasonic", "pcpi", "pentax", "qms", "ricoh", "samsung", "star", "tektronix", "xerox"]
    task_printing_hp = ["hp", "hewlett packard", "hewlett-packard", "hewlett_packard", "hewlettpackard"]
    task_printing_canon = ["canon"]
    task_printing_lexmark = ["lexmark"]
    task_printing_epson = ["epson"]
    task_printing_okidata = ["okidata", "oki", "oki data corp", "oki data"]
    make1 = make.lower().strip()
    model1 = model.lower().strip()
    packages = []
    if task_printing_hp.count(make1):
        packages.append("task-printing-hp")
        make1 = "hp"
    elif task_printing_misc.count(make1):
        packages.append("task-printing-misc")
    elif task_printing_canon.count(make1):
        packages.append("task-printing-canon")
    elif task_printing_lexmark.count(make1):
        packages.append("task-printing-lexmark")
    elif task_printing_epson.count(make1):
        packages.append("task-printing-epson")
    elif task_printing_okidata.count(make1):
        packages.append("task-printing-okidata")

    # check scanning capabilities
    if is_scanning_capable(make1, model1):
        if task_printing_hp.count(make1):
            if platform.machine() == 'x86_64':
                lib="lib64"
            else:
                lib="lib"
            packages.append(lib+"sane-hpaio1")
            packages.append("simple-scan")

    if packages:
        return packages

def probe_parport_info(uri):
    # uri[-1] must return a number between 0 and 9
    number=uri[-1]
    if not os.access("/proc/sys/dev/parport/parport"+str(number),os.F_OK):
        return (None, None)
    path = "ls /proc/sys/dev/parport/parport"+str(number)+"/autoprobe*"
    fd = os.popen(path)
    try:
        arqs = fd.readlines()
    except:
        return (None, None)

    make = ""
    model = ""
    for arq in arqs:
        arq = arq.replace("\n","")
        a = open(arq)
        try:
            b = a.readlines()
        except:
            return (None, None)

        for i in b:
            i=i.replace(";","")
            i=i.replace("\n","")
            if i.count(":") != 0:
                (field, data) = i.split(":")
                if field.startswith("CLASS"):
                    if data != "PRINTER":
                        return (None, None)
                else:
                    if field.startswith("MODEL"):
                        model = data.strip()
                    if field.startswith("MANUFACTURER"):
                        make = data.strip()
        return (make, model)

def read_hplip_db():
    a = open("/usr/share/hplip/data/models/models.dat")
    if not a:
        return None

    re_entry_title = re.compile("^\[")
    re_comment = re.compile("^#")
    db = {}
    current_entry=None
    for b in a:
        if re_entry_title.match(b):
            b = b.strip()
            b = b.lower()
            current_entry=b[1:-1]
            db[current_entry] = {}
            continue
        if re_comment.match(b):
            continue
        try:
            (entry,data) = b.split("=")
        except:
            continue
        db[current_entry][entry] = data.strip().lower()

    a.close();
    return db

def is_scanning_capable(make, model):
    make1 = make.lower().strip()
    model1 = model.lower().strip()
    model1 = model1.replace(" ", "_")
    if make2simplename(make1) == "hp":
        a = read_hplip_db()
        if a and model1 in a and 'scan-type' in a[model1]:
            if a[model1]['scan-type'] != '0':
                return True
        elif a and (model1+"_series") in a and 'scan-type' in a[model1+"_series"]:
            if a[model1+"_series"]['scan-type'] != '0':
                return True
    return False

def is_fax_capable(make, model):
    make1 = make.lower().strip()
    model1 = model.lower().strip()
    model1 = model1.replace(" ", "_")
    if make2simplename(make1) == "hp":
        a = read_hplip_db()
        if a and model1 in a and 'fax-type' in a[model1]:
            if a[model1]['fax-type'] != '0':
                return True
        elif a and (model1+"_series") in a and 'fax-type' in a[model1+"_series"]:
            if a[model1+"_series"]['fax-type'] != '0':
                return True
    return False

def uri2make(uri):
    import urllib
    # when using hp, return hp. uri from hp backend is different
    if uri.startswith('hp:'):
        return "HP"
    exp = re.compile(':/?/(.*)/')
    res = exp.findall(uri)
    if res:
        return urllib.unquote(res[0]).strip()

def uri2model(uri):
    import urllib
    exp = re.compile(':/?/.*/(.*)\?')
    res = exp.findall(uri)
    if res:
        return urllib.unquote(res[0]).strip()

def is_firmware_present(make, model):
    model1 = model.lower().strip()
    make1 = make.lower().strip()

    if make2simplename(make1) == "hp":
        if os.path.isdir("/usr/share/hplip/data/firmware/"):
            a = os.path.os.listdir("/usr/share/hplip/data/firmware/")
            # hp-setup always download all the firmwares
            if len(a) == 0:
                return False
            else:
                return True
    return False

    # foo2zjs doesnt work anymore without usblp
    """
    if make2simplename(make1) == "hp":
        firmware_dir = "/usr/share/foo2zjs/firmware/"
        exp = re.compile('laserjet.*(1000|1005|1018|1020)')
        res = exp.findall(model1)
        if res:
            hp_model = res[0]
            fw_name = "sihp%s.dl" % hp_model
            fw_full_path = firmware_dir+fw_name
            return os.path.exists(fw_full_path)

    return False
    """

def is_firmware_needed(make, model):
    model1 = model.lower().strip()
    make1 = make.lower().strip()
    if make2simplename(make1) == "hp":
        exp = re.compile('laser.*jet.*(1000|1005|p1005|p1006|p1007|p1008|p1009|1018|1020|p1505)')
        res = exp.findall(model1)
        if res:
            return True
    return False

def install_firmware(make, model):
    model1 = model.lower().strip()
    make1 = make.lower().strip()

    if make2simplename(make1) == "hp":
        return os.system("/usr/bin/hp-firmware -n")
    return False

    # foo2zjs doesnt work anymore without usblp
    """
    # we need to be root
    if os.getuid() != 0:
        return False

    if make2simplename(make1) == "hp":
        exp = re.compile('laser.*jet.*(1000|1005|1018|1020)')
        res = exp.findall(model1)
        if res:
            hp_model = res[0]
            if os.system("/usr/sbin/hplj" + hp_model) == 0:
                return True

    return False
    """

def download_and_install_firmware(make, model):
    model1 = model.lower().strip()
    make1 = make.lower().strip()

    # foo2zjs doesnt work anymore without usblp
    """
    # we need to be root
    if os.getuid() != 0:
        return False

    # clear old firmware temporary dir
    os.system('rm -f /tmp/firmware_printer.*')

    if make2simplename(make1) == "hp":
        firmware_dir = "/usr/share/foo2zjs/firmware/"
        exp = re.compile('laserjet.*(1000|1005|1018|1020)')
        res = exp.findall(model1)
        if res:
            hp_model = res[0]
            fw_name = "sihp%s.dl" % hp_model
            fw_full_path = firmware_dir+fw_name
            if os.path.exists(fw_full_path):
                return install_firmware(make,model1)

            try:
                dir = os.popen('/bin/mktemp -d /tmp/firmware_printer.XXXXXX').readline()[0:-1]
            except:
                return False
            
            os.chdir(dir)
            os.system("/usr/bin/foo2zjs-getweb " + hp_model)
            if os.path.exists("sihp%s.img" % hp_model):
                if os.system("/usr/bin/arm2hpdl %s > %s" % ("*",fw_full_path)) == 0:
                    os.system("rm -rf "+dir)
                    return install_firmware(make1, model1)

    os.system("rm -rf "+dir)
    return False
    """
def get_default_gateway():
    """Read the default gateway directly from /proc."""
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue

            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))
            
def get_default_iface():
    """Read the default iface directly from /proc."""
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue

            return fields[0]
            
def get_netmask(iface):
    """Get netmask for iface."""
    ifreq = struct.pack(b'16sH14s', iface, socket.AF_INET, b'\x00'*14)
    sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        res = fcntl.ioctl(sockfd, SIOCGIFNETMASK, ifreq)
    except IOError:
        return 0
    netmask = socket.ntohl(struct.unpack(b'16sH2xI8x', res)[2])
    
    sockfd.close()
    return 32 - int(round(
        math.log(ctypes.c_uint32(~netmask).value + 1, 2), 1))

def get_ip(iface):
    """Get ip for iface."""
    ifreq = struct.pack(b'16sH14s', iface, socket.AF_INET, b'\x00'*14)
    sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        res = fcntl.ioctl(sockfd, SIOCGIFADDR, ifreq)
    except IOError:
        return None
    ip = struct.unpack('16sH2x4s8x', res)[2]
    
    sockfd.close()
    return socket.inet_ntoa(ip)

def detect_network_printers():
    """Get network printers IPv4 (jetdirect port)."""
    printers_final = []
    try:
        iface = str.encode(get_default_iface())
        host4 = ipaddress.ip_interface(
                get_ip(iface)+'/'+str(get_netmask(iface)))
            
        p1 = subprocess.Popen("LC_ALL=C nmap -n -r -v -P0 --max-retries 1 --host_timeout 16000ms --initial_rtt_timeout 8000ms -p 9100 -d0 %s - 2>/dev/null | grep -vE '(PORT|Host)'" % host4, stdout=subprocess.PIPE, shell=True)       
        reg = re.compile(r"Nmap scan report for (.*[0-9])")
        printers = []
        nmapresult = iter(p1.communicate()[0].split(b'\n'))
   
        while True:
            try:
                i = bytes.decode(nmapresult.__next__())
            except:
                break

            try:
                try:
                    ip = reg.findall(i)[0]
                except:
                    continue
                a = bytes.decode(nmapresult.__next__())
                port=a.split()[0]
                state=a.split()[1]
                service=a.split()[2]
            
                if a.split()[1] == "open":
                    printers.append([ip,port,state,service])
                    printers_final.append("socket://"+ip)
            except:
                break
        return printers_final
    except:
        return printers_final
    
    

