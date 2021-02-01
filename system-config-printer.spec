Name:		system-config-printer
Summary:	A printer administration tool
Version:	1.5.15
Release:	1
Url:		https://github.com/OpenPrinting/system-config-printer
License:	LGPLv2+
Group:		System/Configuration/Printing
Source0:	https://github.com/OpenPrinting/system-config-printer/archive/%{name}-%{version}.tar.xz
Source100:	system-config-printer.rpmlintrc

BuildRequires:	cups-devel >= 1.2
BuildRequires:	pkgconfig(python3)
BuildRequires:	desktop-file-utils >= 0.2.92
BuildRequires:	gettext-devel
BuildRequires:	intltool
BuildRequires:	xmlto
BuildRequires:	docbook-dtd412-xml
BuildRequires:	docbook-style-xsl
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(libusb-1.0)
BuildRequires:	libhpip-devel
BuildRequires:	pkgconfig(dbus-1)
BuildRequires:	pkgconfig(dbus-glib-1)
BuildRequires:	pkgconfig(systemd)
BuildRequires:	pkgconfig(udev)

%rename		desktop-printing
%rename		printerdrake
%rename		system-config-printer-libs
%rename		system-config-printer-udev

Conflicts:	system-config-printer-gui < 1.4.2-7
Requires:	libxml2-python
Requires:	virtual-notification-daemon
Requires:	python3-dbus
Requires:	python-curl
Requires:	hplip-model-data
Requires:	python-smbc
Suggests:	samba-client
# Required for CheckUSBPermissions.py
Requires:	acl
Requires(post,postun):	rpm-helper
Requires:	python >= 3
Requires:	foomatic
Requires:	python-cups
Requires:	python-gi
Requires:	python-requests >= 2.3.0-3
Obsoletes:	hal-cups-utils <= 0.6.20
Conflicts:	cups < 1.4.2-6
# Detection
Requires:	%mklibname secret-gir 1

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
Requires:	typelib(xlib) = 2.0
Requires:	typelib(Gdk) = 3.0
Requires:	typelib(Notify) = 0.7
Requires:	typelib(GnomeKeyring) = 1.0
Requires:	typelib(Gtk) = 3.0
Requires:	typelib(cairo) = 1.0
Requires:	typelib(Pango) = 1.0
Requires:	typelib(Atk) = 1.0
Requires:	python-cairo

%description gui
This package provides the GTK frontend.

%prep
%autosetup -p1


./bootstrap

%build
%configure \
  --with-systemdsystemunitdir=%{_unitdir} \
  --with-udevdir="/lib/udev" \
  --with-udev-rules

%make_build

%install
%make_install

mkdir -p %{buildroot}%{_mozillaextpath}
mkdir -p %{buildroot}%{py_platsitedir}
mkdir -p %{buildroot}%{_bindir}
# Make sure pyc files are generated first
cd %{buildroot}%{_datadir}/%{name}
python -m compileall .
cd -
mkdir -p %{buildroot}%{py_platsitedir}
cd %{buildroot}%{py_puresitedir}/cupshelpers
python -m compileall .
cd -

%{__mkdir_p} %{buildroot}%{_localstatedir}/run/udev-configure-printer
touch %{buildroot}%{_localstatedir}/run/udev-configure-printer/usb-uris

%find_lang system-config-printer

%files -f system-config-printer.lang
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/__pycache__
%dir %{_datadir}/%{name}/xml
%dir %{_sysconfdir}/cupshelpers/
%dir %{_localstatedir}/run/udev-configure-printer
%dir %{python_sitelib}/cupshelpers
# (crazy) why noreplace ?
%config(noreplace) %{_sysconfdir}/cupshelpers/preferreddrivers.xml
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/com.redhat.NewPrinterNotification.conf
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/com.redhat.PrinterDriversInstaller.conf
%{_datadir}/dbus-1/interfaces/org.fedoraproject.Config.Printing.xml
%{_datadir}/dbus-1/services/org.fedoraproject.Config.Printing.service
# uhm what ?
%verify(not md5 size mtime) %config(noreplace,missingok) %attr(0644,root,root) %{_localstatedir}/run/udev-configure-printer/usb-uris
/lib/udev/*
%{_unitdir}/configure-printer@.service
%{_bindir}/scp-dbus-service
%{_datadir}/%{name}/asyncconn.py*
%{_datadir}/%{name}/asyncpk1.py*
%{_datadir}/%{name}/check-device-ids.py*
%{_datadir}/%{name}/config.py*
%{_datadir}/%{name}/debug.py*
%{_datadir}/%{name}/dnssdresolve.py*
%{_datadir}/%{name}/firewallsettings.py*
%{_datadir}/%{name}/installpackage.py*
%{_datadir}/%{name}/killtimer.py*
%{_datadir}/%{name}/monitor.py*
%{_datadir}/%{name}/OpenPrintingRequest.py*
%{_datadir}/%{name}/PhysicalDevice.py*
%{_datadir}/%{name}/ppdippstr.py*
%{_datadir}/%{name}/probe_printer.py*
%{_datadir}/%{name}/pysmb.py*
%{_datadir}/%{name}/scp-dbus-service.py*
%{_datadir}/%{name}/SearchCriterion.py*
%{_datadir}/%{name}/smburi.py*
%{_datadir}/%{name}/statereason.py*
%{_datadir}/%{name}/xml/*
%{_datadir}/%{name}/__pycache__/OpenPrintingRequest.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/PhysicalDevice.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/SearchCriterion.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/asyncconn.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/asyncpk1.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/config.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/dnssdresolve.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/killtimer.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/monitor.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/ppdippstr.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/probe_printer.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/pysmb.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/scp-dbus-service.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/smburi.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/statereason.cpython-*.pyc
%{python_sitelib}/cupshelpers/__init__.py*
%{python_sitelib}/cupshelpers/cupshelpers.py*
%{python_sitelib}/cupshelpers/openprinting.py*
%{python_sitelib}/cupshelpers/ppds.py*
%{python_sitelib}/cupshelpers/config.py*
%{python_sitelib}/cupshelpers/installdriver.py*
%{python_sitelib}/cupshelpers/xmldriverprefs.py*
%{python_sitelib}/cupshelpers/__pycache__
%{python_sitelib}/*.egg-info

%files gui
%dir %{_datadir}/%{name}/ui
%dir %{_datadir}/%{name}/troubleshoot
%dir %{_datadir}/%{name}/icons
%{_sysconfdir}/xdg/autostart/print-applet.desktop
%{_bindir}/%{name}
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
%{_datadir}/%{name}/troubleshoot/__pycache__
%{_datadir}/%{name}/icons/*.png
%{_datadir}/%{name}/ui/*.ui
%{_datadir}/%{name}/__pycache__/ToolbarSearchEntry.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/applet.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/asyncipp.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/authconn.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/check-device-ids.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/cupspk.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/debug.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/errordialogs.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/firewallsettings.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/gtkinklevel.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/gui.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/HIG.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/install-printerdriver.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/installpackage.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/jobviewer.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/newprinter.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/options.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/optionwidgets.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/ppdcache.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/ppdsloader.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/printerproperties.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/serversettings.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/%{name}.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/timedops.cpython-*.pyc
%{_datadir}/%{name}/__pycache__/userdefault.cpython-*.pyc
%{_datadir}/applications/system-config-printer.desktop
%{_datadir}/metainfo/*.appdata.xml
%{_mandir}/man1/*
