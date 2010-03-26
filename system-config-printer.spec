%define use_gitsnap 0
%{?_no_gitsnap: %{expand: %%global use_gitsnap 0}}
%if %{use_gitsnap}
%define gitsnap 200809231700
%endif

# needs porting of Mandriva specific features from hal-cups-utils to s-c-p-udev
%define         obsolete_hal_cups_utils 1

Name:           system-config-printer
Summary:        A printer administration tool
Version:        1.2.0
Release:        %mkrel 3
Url:            http://cyberelk.net/tim/software/system-config-printer/
License:        LGPLv2+
Group:          System/Configuration/Printing
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
Source0:        http://cyberelk.net/tim/data/system-config-printer/1.2/%{name}-%{version}%{?gitsnap:-%gitsnap}.tar.xz
Source1:        system-config-printer.pam
Source2:        system-config-printer.console
Source3:        po-mdv.tar.bz2
Source4:        mdv_printer_custom.py
Source5:        hp-makeuri-mdv.c
Source6:        mdv_backend
# Let printers have an ACL allowing rw for user lp, as our CUPS runs backends as lp:sys (bug 49407)
Source7:        69-printers_lp_user_fix.rules
Patch0:         system-config-printer-1.1.12-mdv_custom-applet.patch
Patch1:         system-config-printer-1.1.12-mdv_custom-embedded_window.patch
Patch2:         system-config-printer-1.1.91-mdv_custom-system-config-printer.patch
Patch3:         system-config-printer-1.1.17-start-applet.patch
Patch4:         system-config-printer-1.2.0-udev-configure-printer-mdv.patch
# Ubuntu patches
# use hpcups instead of hpijs for HP printers, like in
# previous versions. hpijs is obsolete and hpcup is mature now
Patch101:  50_give-priority-to-hpcups.patch
# when comparing usb uris, deal with the difference between the obsolete
# usblp and the new libusb back-end
Patch102:  67_match-usb-uris-of-usblp-and-libusb.patch
# Fedora patches
Patch200: system-config-printer-lowercase-mfg-mdl.patch
#Patch204: system-config-printer-cupsconnection-dealloc.patch

BuildRequires:  cups-devel >= 1.2
BuildRequires:  python-devel >= 2.4
BuildRequires:  desktop-file-utils >= 0.2.92
BuildRequires:  gettext-devel
BuildRequires:  intltool
BuildRequires:  xmlto
BuildRequires:  docbook-dtd412-xml
BuildRequires:  docbook-style-xsl
%if %obsolete_hal_cups_utils
BuildRequires:  udev-devel
BuildRequires:  libusb-devel
BuildRequires:  libhpip-devel
BuildRequires:  dbus-devel
BuildRequires:  dbus-glib-devel
%endif
Obsoletes:      desktop-printing
Obsoletes:      printerdrake
Provides:       printerdrake
Requires:       pygtk2 >= 2.4.0
Requires:       pygtk2.0-libglade
Requires:       python-gobject
Requires:       libxml2-python
Requires:       desktop-file-utils >= 0.2.92
Requires:       dbus-x11
Requires:       system-config-printer-libs = %{version}-%{release}
%if %obsolete_hal_cups_utils
Requires:       system-config-printer-udev = %{version}-%{release}
%else
Requires:       hal-cups-utils
Obsoletes:	system-config-printer-udev < 1.1.13-11mdv
%endif
Requires:       gnome-icon-theme
Requires:       gnome-python
Requires:       virtual-notification-daemon
Requires:       python-cups
Requires:       python-rhpl
Requires:       python-dbus
Requires:       python-notify
%if %obsolete_hal_cups_utils
Requires:       hplip-model-data
# nmap is required to scan the network, just like 
# printerdrake used to do.
Requires:       nmap
Requires:       python-smbc
%endif
Conflicts:      kdeutils4-printer-applet
Suggests:       samba-client

%description
system-config-printer is a graphical user interface that allows
the user to configure a CUPS print server.

%files
%defattr(-,root,root)
%doc ChangeLog README
%{_bindir}/%{name}
%{_sbindir}/%{name}
%{_bindir}/hp-makeuri-mdv
%{_bindir}/%{name}-applet
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*.py*
%{_datadir}/%{name}/troubleshoot
%{_datadir}/%{name}/ui/*.glade
%{_datadir}/%{name}/icons
%{_datadir}/applications/system-config-printer.desktop
%{_datadir}/applications/manage-print-jobs.desktop
%{_sysconfdir}/xdg/autostart/print-applet.desktop
%config(noreplace) %{_sysconfdir}/pam.d/%{name}
%config(noreplace) %{_sysconfdir}/security/console.apps/%{name}
%{_mandir}/man1/*

#---------------------------------------------------------------------
%if %obsolete_hal_cups_utils
%package udev
Summary: Rules for udev for automatic configuration of USB printers
Group:    System/Configuration/Hardware
Requires: system-config-printer-libs = %{version}-%{release}
Obsoletes: hal-cups-utils <= 0.6.20
Conflicts: cups < 1.4.2-6

%description udev
The udev rules and helper programs for automatically configuring USB
printers.

%post
# disable old printer detection system
if [ -f /etc/sysconfig/printing ]; then
    if grep -q ^AUTO_SETUP_QUEUES_ON_PRINTER_CONNECTED= /etc/sysconfig/printing; then
        sed -i 's/AUTO_SETUP_QUEUES_ON_PRINTER_CONNECTED=.*/AUTO_SETUP_QUEUES_ON_PRINTER_CONNECTED=no/g' /etc/sysconfig/printing
    else
        echo AUTO_SETUP_QUEUES_ON_PRINTER_CONNECTED=no >> /etc/sysconfig/printing
    fi
    if grep -q ^ENABLE_QUEUES_ON_PRINTER_CONNECTED= /etc/sysconfig/printing; then
        sed -i 's/ENABLE_QUEUES_ON_PRINTER_CONNECTED=.*/ENABLE_QUEUES_ON_PRINTER_CONNECTED=no/g' /etc/sysconfig/printing
    else
        echo ENABLE_QUEUES_ON_PRINTER_CONNECTED=no >> /etc/sysconfig/printing
    fi
else
    echo AUTO_SETUP_QUEUES_ON_PRINTER_CONNECTED=no >> /etc/sysconfig/printing
    echo ENABLE_QUEUES_ON_PRINTER_CONNECTED=no >> /etc/sysconfig/printing
fi

%postun
# enable old printer detection system
if [ -f /etc/sysconfig/printing ]; then
    if grep -q ^AUTO_SETUP_QUEUES_ON_PRINTER_CONNECTED= /etc/sysconfig/printing; then
        sed -i 's/AUTO_SETUP_QUEUES_ON_PRINTER_CONNECTED=.*/AUTO_SETUP_QUEUES_ON_PRINTER_CONNECTED=yes/g' /etc/sysconfig/printing
    fi
    if grep -q ^ENABLE_QUEUES_ON_PRINTER_CONNECTED= /etc/sysconfig/printing; then
        sed -i 's/ENABLE_QUEUES_ON_PRINTER_CONNECTED=.*/ENABLE_QUEUES_ON_PRINTER_CONNECTED=yes/g' /etc/sysconfig/printing
    fi
fi

%files udev
%defattr(-,root,root,-)
/lib/udev/*
%dir %{_localstatedir}/run/udev-configure-printer
%verify(not md5 size mtime) %config(noreplace,missingok) %attr(0644,root,root) %{_localstatedir}/run/udev-configure-printer/usb-uris
%{_sysconfdir}/udev/rules.d/*
%endif #obsolete_hal_cups_utils

#---------------------------------------------------------------------

%package  libs
Summary:  Common code for the graphical and non-graphical pieces
Group:    System/Libraries 
Requires: python
Requires: foomatic

%description libs
The common code used by both the graphical and non-graphical parts of
the configuration tool.

%files libs -f system-config-printer.lang
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/newprinternotification.conf
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/printerdriversinstaller.conf
%dir %{python_sitelib}/cupshelpers
%{python_sitelib}/cupshelpers/__init__.py*
%{python_sitelib}/cupshelpers/cupshelpers.py*
%{python_sitelib}/cupshelpers/openprinting.py*
%{python_sitelib}/cupshelpers/ppds.py*
%{_libdir}/cups/backend/mdv_backend
%{py_platsitedir}/mdv_printer_custom.py*
%{python_sitelib}/*.egg-info

#--------------------------------------------------------------------

%prep
%setup -q 
%patch0 -p1 -b .mdv_custom-applet
%patch1 -p1 -b .mdv_custom-embedded-window
%patch2 -p0 -b .mdv_custom-system-config-printer
%patch3 -p0 -b .start_applet
%patch4 -p1 -b .udev-configue-printer-mdv
%patch101 -p1 -b .hpcupsprio
%patch102 -p1 -b .libusb
# Convert InstallPrinterDriver requests to lower-case.
%patch200 -p1 -b .lowercase-mfg-mdl


# update mdv custom translation
tar xvjf %{SOURCE3}
pushd po
for i in *.po; do
    if [ ! -f ../po-mdv/$i ]; then
        continue
    fi
    msgcat $i ../po-mdv/$i > ../po-mdv/$i-new
    rm -f $i
    mv ../po-mdv/$i-new $i
done
popd

%build
%if %{use_gitsnap}
./bootstrap
%endif
%configure2_5x \
%if %obsolete_hal_cups_utils
	--with-udev-rules
%endif

make
%if %obsolete_hal_cups_utils
# (salem) this hack avoids requiring hplip
gcc %{SOURCE5} -o hp-makeuri-mdv -lhpmud
%endif

%install
rm -rf %buildroot
%makeinstall_std

%if %obsolete_hal_cups_utils
mkdir -p %{buildroot}%{_mozillaextpath}
mkdir -p %{buildroot}%{py_platsitedir}
mkdir -p %{buildroot}%{_bindir}
cp -f hp-makeuri-mdv %{buildroot}%{_bindir}
# Make sure pyc files are generated, otherwise we can get
# difficult to debug problems
pushd %{buildroot}%{_datadir}/%{name}
python -m compileall .
popd
mkdir -p %{buildroot}%{py_platsitedir}
cp -fv %{SOURCE4} %{buildroot}%{py_platsitedir}
pushd %{buildroot}%{py_platsitedir}
python -m compileall .
popd

%{__mkdir_p} %buildroot%{_localstatedir}/run/udev-configure-printer
touch %buildroot%{_localstatedir}/run/udev-configure-printer/usb-uris
%{__mkdir_p} %{buildroot}%{_libdir}/cups/backend
cp -f %{SOURCE6} %{buildroot}%{_libdir}/cups/backend

# Install udev rules for letting backends access the printer devices.  Once
# CUPS runs backends as group 'lp', instead of 'sys, we may remove this.
mkdir -p %{buildroot}%{_sysconfdir}/udev/rules.d
install -m 644 %{SOURCE7} %{buildroot}%{_sysconfdir}/udev/rules.d/


%endif

mkdir -p %buildroot%{_bindir}
mkdir -p %buildroot%{_sbindir}
mkdir -p %buildroot%{_sysconfdir}/pam.d
mkdir -p %buildroot%{_sysconfdir}/security/console.apps
install -p -m0644 %{SOURCE1} %buildroot%{_sysconfdir}/pam.d/%{name}
install -p -m0644 %{SOURCE2} %buildroot%{_sysconfdir}/security/console.apps/%{name}
mv %buildroot%{_bindir}/%{name} %buildroot%{_sbindir}/%{name}
ln -s consolehelper %buildroot%{_bindir}/%{name}


%find_lang system-config-printer

%clean
%{__rm} -rf "%{buildroot}"
