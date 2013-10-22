Name:		system-config-printer
Summary:	A printer administration tool
Version:	1.4.2
Release:	8
Url:		http://cyberelk.net/tim/software/system-config-printer/
License:	LGPLv2+
Group:		System/Configuration/Printing
Source0:	http://cyberelk.net/tim/data/system-config-printer/1.4/%{name}-%{version}%{?gitsnap:-%gitsnap}.tar.xz
Source1:	system-config-printer.pam
Source2:	system-config-printer.console
Source3:	po-mdv.tar.bz2
Source5:	hp-makeuri-mdv.c
# (tpg) from Mageia
Source4:	mdv_printer_custom.py
Source6:	mdv_backend

Source100:	system-config-printer.rpmlintrc
Patch3:		system-config-printer-1.3.1-start-applet.patch

# Fedora patches
Patch200:	system-config-printer-no-job-notifications.patch
Patch203:	system-config-printer-systemd.patch

# patches based Mageia patches
Patch0:		system-config-printer-1.4.2-mdv_custom-applet.patch
Patch2:		system-config-printer-1.4.2-mdv_custom-system-config-printer.patch
Patch4:		system-config-printer-1.3.12-udev-configure-printer-mdv.patch
Patch5:		system-config-printer-1.4.2-mdv_custom-embedded_window.patch
Patch300:	system-config-printer-1.3.7-remove-Brother-HL-2030-blacklist.patch

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

%rename		desktop-printing
%rename		printerdrake
%rename		system-config-printer-libs
%rename		system-config-printer-udev
Conflicts:	system-config-printer-gui < 1.4.2-7
Requires:	python-gobject
Requires:	libxml2-python
#Requires:	gnome-python-gnomekeyring
Requires:	virtual-notification-daemon
Requires:	python-dbus
Requires:	python-pyinotify
Requires:	python-curl
Requires:	hplip-model-data
#We now use packagekit
#Requires:	packagekit
#Requires:	typelib(PackageKitGlib)
# nmap is required to scan the network, just like
# printerdrake used to do.
Requires:	nmap
Requires:	python-smbc
# Why? kdeutils4-printer-applet reqires system-config-printer...
#Conflicts:	kdeutils4-printer-applet
Suggests:	samba-client
# Required for CheckUSBPermissions.py
Requires:	acl
Requires:	python-notify
Requires(post,postun):	rpm-helper
Requires:	python
Requires:	foomatic
Requires:	python-cups
Requires:	python-gi
Obsoletes:	hal-cups-utils <= 0.6.20
Conflicts:	cups < 1.4.2-6

%description
system-config-printer is a user interface that allows
the user to configure a CUPS print server.

%package gui
Summary:	GTK frontend for %{name}
Group:		System/Configuration/Hardware
Requires:	system-config-printer = %{version}-%{release}
Conflicts:	system-config-printer < 1.4.2-7
Requires:	gnome-icon-theme
Requires:	dbus-x11
Requires:	pygtk2 >= 2.4.0
Requires:	pygtk2.0-libglade
Requires:	typelib(xlib) = 2.0
Requires:	typelib(Gdk) = 3.0
Requires:	typelib(Notify) = 0.7
Requires:	typelib(GnomeKeyring) = 1.0
Requires:	typelib(Gtk) = 3.0
Requires:	typelib(cairo) = 1.0
Requires:	typelib(Pango) = 1.0
Requires:	typelib(Atk) = 1.0

%description gui
This package provides the GTK frontend.

%prep
%setup -q
%patch0 -p1 -b .mdv_custom-applet
%patch2 -p1 -b .mdv_custom-system-config-printer
%patch3 -p1 -b .start_applet
%patch4 -p1 -b .udev-configue-printer-mdv
%patch5 -p1 -b .mdv_custom-embedded-window
# Don't show job notifications.
%patch200 -p1 -b .no-job-notifications
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

%{__mkdir_p} %{buildroot}%{_localstatedir}/run/udev-configure-printer
touch %{buildroot}%{_localstatedir}/run/udev-configure-printer/usb-uris
%{__mkdir_p} %{buildroot}%{_prefix}/lib/cups/backend
cp -f %{SOURCE6} %{buildroot}%{_prefix}/lib/cups/backend

mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_sysconfdir}/pam.d
mkdir -p %{buildroot}%{_sysconfdir}/security/console.apps
install -p -m0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/pam.d/%{name}
install -p -m0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/security/console.apps/%{name}
mv %{buildroot}%{_bindir}/%{name} %{buildroot}%{_sbindir}/%{name}
ln -s consolehelper %{buildroot}%{_bindir}/%{name}

%find_lang system-config-printer

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

%files -f system-config-printer.lang
%doc ChangeLog README
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/xml
%dir %{_sysconfdir}/cupshelpers/
%dir %{_localstatedir}/run/udev-configure-printer
%dir %{python_sitelib}/cupshelpers
%config(noreplace) %{_sysconfdir}/pam.d/%{name}
%config(noreplace) %{_sysconfdir}/security/console.apps/%{name}
%config(noreplace) %{_sysconfdir}/cupshelpers/preferreddrivers.xml
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/com.redhat.NewPrinterNotification.conf
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/com.redhat.PrinterDriversInstaller.conf
%config(noreplace) %{_datadir}/dbus-1/interfaces/org.fedoraproject.Config.Printing.xml
%config(noreplace) %{_datadir}/dbus-1/services/org.fedoraproject.Config.Printing.service
%verify(not md5 size mtime) %config(noreplace,missingok) %attr(0644,root,root) %{_localstatedir}/run/udev-configure-printer/usb-uris
/lib/udev/*
%{_unitdir}/configure-printer@.service
%{_bindir}/scp-dbus-service
%{_bindir}/hp-makeuri-mdv
%{_datadir}/%{name}/asyncconn.py*
%{_datadir}/%{name}/asyncpk1.py*
%{_datadir}/%{name}/check-device-ids.py*
%{_datadir}/%{name}/config.py*
%{_datadir}/%{name}/debug.py*
%{_datadir}/%{name}/dnssdresolve.py*
%{_datadir}/%{name}/firewallsettings.py*
%{_datadir}/%{name}/installpackage.py*
%{_datadir}/%{name}/monitor.py*
%{_datadir}/%{name}/PhysicalDevice.py*
%{_datadir}/%{name}/ppdippstr.py*
%{_datadir}/%{name}/probe_printer.py*
%{_datadir}/%{name}/pysmb.py*
%{_datadir}/%{name}/scp-dbus-service.py*
%{_datadir}/%{name}/SearchCriterion.py*
%{_datadir}/%{name}/smburi.py*
%{_datadir}/%{name}/statereason.py*
%{_datadir}/%{name}/xml/*
%{python_sitelib}/cupshelpers/__init__.py*
%{python_sitelib}/cupshelpers/cupshelpers.py*
%{python_sitelib}/cupshelpers/openprinting.py*
%{python_sitelib}/cupshelpers/ppds.py*
%{python_sitelib}/cupshelpers/config.py*
%{python_sitelib}/cupshelpers/installdriver.py*
%{python_sitelib}/cupshelpers/xmldriverprefs.py*
%{_prefix}/lib/cups/backend/mdv_backend
%{py_platsitedir}/mdv_printer_custom.py*
%{python_sitelib}/*.egg-info

%files gui
%dir %{_datadir}/%{name}/ui
%dir %{_datadir}/%{name}/troubleshoot
%dir %{_datadir}/%{name}/icons
%{_sysconfdir}/xdg/autostart/print-applet.desktop
%{_bindir}/%{name}
%{_sbindir}/%{name}
%{_bindir}/install-printerdriver
%{_bindir}/%{name}-applet
%{_datadir}/%{name}/applet.py*
%{_datadir}/%{name}/asyncipp.py*
%{_datadir}/%{name}/authconn.py*
%{_datadir}/%{name}/cupspk.py*
%{_datadir}/%{name}/errordialogs.py*
%{_datadir}/%{name}/gtkinklevel.py*
%{_datadir}/%{name}/gui.py*
%{_datadir}/%{name}/HIG.py*
%{_datadir}/%{name}/install-printerdriver.py*
%{_datadir}/%{name}/jobviewer.py*
%{_datadir}/%{name}/newprinter.py*
%{_datadir}/%{name}/options.py*
%{_datadir}/%{name}/optionwidgets.py*
%{_datadir}/%{name}/ppdcache.py*
%{_datadir}/%{name}/ppdsloader.py*
%{_datadir}/%{name}/printerproperties.py*
%{_datadir}/%{name}/serversettings.py*
%{_datadir}/%{name}/system-config-printer.py*
%{_datadir}/%{name}/timedops.py*
%{_datadir}/%{name}/ToolbarSearchEntry.py*
%{_datadir}/%{name}/userdefault.py*
%{_datadir}/%{name}/troubleshoot/*.py*
%{_datadir}/%{name}/icons/*.png
%{_datadir}/%{name}/ui/*.ui
%{_datadir}/applications/system-config-printer.desktop
%{_mandir}/man1/*
