#!/bin/env python
# Tiago Salem Herrmann <salem@mandriva.com>
import dbus, sys, os, time, signal, re
import traceback
import cups, cupshelpers
import csv

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
            if sys.arch == 'x86_64':
                lib="lib64"
            else:
                lib="lib"
            packages.append(lib+"sane-hpaio1")
            packages.append("xsane")

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
    while True:
        try:
            b = a.next()
        except:
            b = None

        if b:
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
        else:
            break

    return db

def is_scanning_capable(make, model):
    make1 = make.lower().strip()
    model1 = model.lower().strip()
    model1 = model1.replace(" ", "_")
    if make2simplename(make1) == "hp":
        a = read_hplip_db()
        if a and a.has_key(model1) and a[model1].has_key('scan-type'):
            if a[model1]['scan-type'] != '0':
                return True
        elif a and a.has_key(model1+"_series") and a[model1+"_series"].has_key('scan-type'):
            if a[model1+"_series"]['scan-type'] != '0':
                return True
    return False

def is_fax_capable(make, model):
    make1 = make.lower().strip()
    model1 = model.lower().strip()
    model1 = model1.replace(" ", "_")
    if make2simplename(make1) == "hp":
        a = read_hplip_db()
        if a and a.has_key(model1) and a[model1].has_key('fax-type'):
            if a[model1]['fax-type'] != '0':
                return True
        elif a and a.has_key(model1+"_series") and a[model1+"_series"].has_key('fax-type'):
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

def detect_network_printers():
    printers_final = []
    try:
        a = open("/proc/net/route")
        defaultiface = None
        for i in csv.DictReader(a, delimiter="\t"):
            if long(i['Destination'], 16) == 0:
                defaultiface = i['Iface']
        else:
            return printers_final
    except:
        return printers_final

    # TODO: write in a better way
    try:
        addrsline = os.popen("LC_ALL=C /sbin/ifconfig "+defaultiface+" | grep 'inet addr:' | sed 's/:/\\n/g' | grep '[0-9]' | sed 's/[^0-9\.]//g'")
        c = addrsline.readlines()
        ip = c[0].strip()
        bcast = c[1].strip()
        mask = c[2].strip()
    except:
        return printers_final

    try:
        pingres = os.popen("LC_ALL=C ping -b -c 2 "+bcast+ " | sed 's/.*bytes from \(.*\):.*/\\1/g' | grep '^[0-9].*[0-9]$' | uniq")
        hostlist=""
        for i in pingres.readlines():
            if i.strip() == ip:
                continue
            if not hostlist:
                hostlist = i.strip()
            else:
                hostlist += ("\n"+i.strip())
    except:
        return printers_final

    try:
        nmapresult = os.popen("echo -e '"+hostlist+"' | LC_ALL=C nmap -n -r -v -P0 --max-retries 1 --host_timeout 16000ms --initial_rtt_timeout 8000ms -p 9100 -d0 -iL - 2>/dev/null | grep -vE '(PORT|Host)'")
        reg = re.compile(r"Nmap scan report for (.*[0-9])")
        printers = []
        while True:
            try:
                i = nmapresult.next()
            except:
                break
    
            try:
                try:
                    ip = reg.findall(i)[0]
                except:
                    continue
                a = nmapresult.next()
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

