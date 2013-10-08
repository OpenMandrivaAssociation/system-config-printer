%define use_gitsnap 0
%{?_no_gitsnap: %{expand: %%global use_gitsnap 0}}
%if %{use_gitsnap}
%define gitsnap 200809231700
%endif

# disable the requires on gnome-python-gnomekeyring when it's not avaialable
# gnome-python-desktop requires s-c-p indirectly and the build fails otherwise
%define pygnomekeyring 1

Name:		system-config-printer
Summary:		A printer administration tool
Version:		1.4.2
Release:		1
Url:			http://cyberelk.net/tim/software/system-config-printer/
License:		LGPLv2+
Group:			System/Configuration/Printing
Source0:		http://cyberelk.net/tim/data/system-config-printer/1.3/%{name}-%{version}%{?gitsnap:-%gitsnap}.tar.xz
Source1:		system-config-printer.pam
Source2:		system-config-printer.console
Source3:		po-mdv.tar.bz2
Source5:		hp-makeuri-mdv.c
# (tpg) from Mageia
Source4:		mga_printer_custom.py
Source6:		mga_backend

Source100:		system-config-printer.rpmlintrc
Patch3:			system-config-printer-1.3.1-start-applet.patch

# Fedora patches
Patch200:		system-config-printer-no-job-notifications.patch
Patch203:		system-config-printer-systemd.patch

# Mageia patches
Patch0:			system-config-printer-1.4.2-mga_custom-applet.patch
Patch2:			system-config-printer-1.4.2-mga_custom-system-config-printer.patch
Patch4:			system-config-printer-1.3.12-udev-configure-printer-mga.patch
Patch5:			system-config-printer-1.4.2-mga_custom-embedded_window.patch
Patch300:		system-config-printer-1.3.7-remove-Brother-HL-2030-blacklist.patch

BuildRequires:	cups-devel >= 1.2
BuildRequires:	python-devel >= 2.4
BuildRequires:	desktop-file-utils >= 0.2.92
BuildRequires:	gettext-devel
BuildRequires:	intltool
BuildRequires:	xmlto
BuildRequires:	docbook-dtd412-xml
BuildRequires:	docbook-style-xsl
BuildRequires:	udev-devel
BuildRequires:	pkgconfig(libusb-1.0)
BuildRequires:	libhpip-devel
BuildRequires:	pkgconfig(dbus-1)
BuildRequires:	pkgconfig(dbus-glib-1)
BuildRequires:	pkgconfig(systemd)

%rename			desktop-printing
%rename			printerdrake
Requires:		pygtk2 >= 2.4.0
Requires:		pygtk2.0-libglade
Requires:		python-gobject
Requires:		libxml2-python
Requires:		desktop-file-utils >= 0.2.92
Requires:		dbus-x11
Requires:		system-config-printer-libs = %{version}-%{release}
Requires:		system-config-printer-udev = %{version}-%{release}
Requires:		gnome-icon-theme
Requires:		gnome-python-gnomekeyring
Requires:		virtual-notification-daemon
Requires:		python-dbus
Requires:		python-pyinotify
Requires:		python-curl
Requires:		hplip-model-data
#We now use packagekit
#Requires:		packagekit
#Requires:		typelib(PackageKitGlib)
# nmap is required to scan the network, just like 
# printerdrake used to do.
Requires:		nmap
Requires:		python-smbc
# Why? kdeutils4-printer-applet reqires system-config-printer...
#Conflicts:		kdeutils4-printer-applet
Suggests:		samba-client
%if %{pygnomekeyring}
Requires:		gnome-python-gnomekeyring
%endif
# Required for CheckUSBPermissions.py
Requires:		acl
Requires:		python-notify
Requires(post,postun):	rpm-helper

%description
system-config-printer is a graphical user interface that allows
the user to configure a CUPS print server.

%files
%doc ChangeLog README
%{_bindir}/%{name}
%{_bindir}/scp-dbus-service
%{_bindir}/install-printerdriver
%{_sbindir}/%{name}
#{_bindir}/hp-makeuri-mdv
%{_bindir}/%{name}-applet
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*.py*
%{_datadir}/%{name}/troubleshoot
%{_datadir}/%{name}/ui/*.ui
%{_datadir}/%{name}/xml/*
%{_datadir}/%{name}/icons
%{_datadir}/applications/system-config-printer.desktop
#%{_datadir}/applications/manage-print-jobs.desktop
%{_sysconfdir}/xdg/autostart/print-applet.desktop
%config(noreplace) %{_sysconfdir}/pam.d/%{name}
%config(noreplace) %{_sysconfdir}/security/console.apps/%{name}
%{_mandir}/man1/*

#---------------------------------------------------------------------
%package udev
Summary:		Rules for udev for automatic configuration of USB printers
Group:			System/Configuration/Hardware
Requires:		system-config-printer-libs = %{version}-%{release}
Requires(post):	rpm-helper >= 0.24.1
Requires(preun):	rpm-helper >= 0.24.1
Obsoletes:		hal-cups-utils <= 0.6.20
Conflicts:		cups < 1.4.2-6

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
/lib/udev/*
%dir %{_localstatedir}/run/udev-configure-printer
%verify(not md5 size mtime) %config(noreplace,missingok) %attr(0644,root,root) %{_localstatedir}/run/udev-configure-printer/usb-uris
%{_unitdir}/configure-printer@.service
%{_sysconfdir}/udev/rules.d/69-printers_lp_user_fix.rules

#---------------------------------------------------------------------

%package libs
Summary:	Common code for the graphical and non-graphical pieces
Group:		System/Libraries 
Requires:	python
Requires:	foomatic
Requires:	python-cups

%description libs
The common code used by both the graphical and non-graphical parts of
the configuration tool.

%files libs -f system-config-printer.lang
%dir %{_sysconfdir}/cupshelpers/
%config(noreplace) %{_sysconfdir}/cupshelpers/preferreddrivers.xml
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/com.redhat.NewPrinterNotification.conf
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/com.redhat.PrinterDriversInstaller.conf
%config(noreplace) %{_datadir}/dbus-1/interfaces/org.fedoraproject.Config.Printing.xml
%config(noreplace) %{_datadir}/dbus-1/services/org.fedoraproject.Config.Printing.service
%dir %{python_sitelib}/cupshelpers
%{python_sitelib}/cupshelpers/__init__.py*
%{python_sitelib}/cupshelpers/cupshelpers.py*
%{python_sitelib}/cupshelpers/openprinting.py*
%{python_sitelib}/cupshelpers/ppds.py*
%{python_sitelib}/cupshelpers/config.py*
%{python_sitelib}/cupshelpers/installdriver.py*
%{python_sitelib}/cupshelpers/xmldriverprefs.py*
#{_prefix}/lib/cups/backend/mdv_backend
%{py_platsitedir}/mdv_printer_custom.py*
%{python_sitelib}/*.egg-info

#--------------------------------------------------------------------

%prep
%setup -q 
%patch0 -p1 -b .mga_custom-applet
%patch2 -p1 -b .mga_custom-system-config-printer
%patch3 -p1 -b .start_applet
%patch4 -p1 -b .udev-configue-printer-mga
%patch5 -p1 -b .mga_custom-embedded-window
# Don't show job notifications.
%patch200 -p1 -b .no-job-notifications
%patch203 -p1 -b .systemd
%patch300 -p0 -b .mdv-1349

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

autoreconf -fi

%build
%if %{use_gitsnap}
./bootstrap
%endif

%configure2_5x \
  --with-systemdsystemunitdir=%{_unitdir} \
  --with-udev-rules

make
# (salem) this hack avoids requiring hplip
gcc %{SOURCE5} -o hp-makeuri-mdv -lhpmud

%install
%makeinstall_std udevrulesdir=/lib/udev/rules.d  udevhelperdir=/lib/udev

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
#%{__mkdir_p} %{buildroot}%{_prefix}/lib/cups/backend
#cp -f %{SOURCE6} %{buildroot}%{_prefix}/lib/cups/backend

%{__mkdir_p} %{buildroot}%{_sysconfdir}/udev/rules.d/
cp -f %{SOURCE7} %{buildroot}%{_sysconfdir}/udev/rules.d/

mkdir -p %buildroot%{_bindir}
mkdir -p %buildroot%{_sbindir}
mkdir -p %buildroot%{_sysconfdir}/pam.d
mkdir -p %buildroot%{_sysconfdir}/security/console.apps
install -p -m0644 %{SOURCE1} %buildroot%{_sysconfdir}/pam.d/%{name}
install -p -m0644 %{SOURCE2} %buildroot%{_sysconfdir}/security/console.apps/%{name}
mv %buildroot%{_bindir}/%{name} %buildroot%{_sbindir}/%{name}
ln -s consolehelper %buildroot%{_bindir}/%{name}

%find_lang system-config-printer
