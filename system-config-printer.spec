Name:		system-config-printer
Summary:	A printer administration tool
Version:	1.5.18
Release:	3
Url:		https://github.com/OpenPrinting/system-config-printer
License:	LGPLv2+
Group:		System/Configuration/Printing
Source0:	https://github.com/OpenPrinting/system-config-printer/releases/download/v%{version}/system-config-printer-%{version}.tar.xz
Source100:	system-config-printer.rpmlintrc

BuildRequires:	autoconf
BuildRequires:	autoconf-archive
BuildRequires:	automake
BuildRequires:	libtool
BuildRequires:	make
BuildRequires:	pkgconfig(cups) >= 1.2
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
Requires:	at-spi2-core
Requires:	at-spi2-atk
Requires:	libxml2-python
Requires:	virtual-notification-daemon
Requires:	python%{pyver}dist(dbus-python)
Requires:	python%{pyver}dist(pycurl)
Requires:	python%{pyver}dist(pysmbc)
Requires:	python%{pyver}dist(pycups)
Requires:	python%{pyver}dist(pygobject)
Requires:	python%{pyver}dist(requests) >= 2.3.0
Requires:	hplip-model-data
Suggests:	samba-client
# Required for CheckUSBPermissions.py
Requires:	acl
Requires:	python >= 3
Requires:	foomatic
# Detection
Requires:	%mklibname secret-gir 1

%patchlist
https://github.com/OpenPrinting/system-config-printer/commit/f0bc27ca4f580aa93fa00aca61b516a9dd0e3a6b.patch
https://github.com/OpenPrinting/system-config-printer/commit/399b3334d6519639cfe7f1c0457e2475b8ee5230.patch
https://github.com/OpenPrinting/system-config-printer/commit/77540d0cb539364bbf63e21cfa970e62d9a86ed3.patch

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
Requires:	typelib(Notify)
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
# workaround https://github.com/pypa/setuptools/issues/3143
sed -i 's/setup.py install --prefix=$(DESTDIR)$(prefix)/setup.py install --root $(DESTDIR) --prefix=$(prefix)/' Makefile*

%build
%configure \
	--with-systemdsystemunitdir=%{_unitdir} \
	--with-udevdir="%{_prefix}/lib/udev" \
	--with-udev-rules

%make_build

%install
%make_install

%{__mkdir_p} %{buildroot}%{_localstatedir}/run/udev-configure-printer
touch %{buildroot}%{_localstatedir}/run/udev-configure-printer/usb-uris

%find_lang system-config-printer

%files
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/xml
%dir %{_sysconfdir}/cupshelpers/
%dir %{_localstatedir}/run/udev-configure-printer
# (crazy) why noreplace ?
%config(noreplace) %{_sysconfdir}/cupshelpers/preferreddrivers.xml
%{_sysconfdir}/dbus-1/system.d/com.redhat.NewPrinterNotification.conf
%{_sysconfdir}/dbus-1/system.d/com.redhat.PrinterDriversInstaller.conf
%{_datadir}/dbus-1/interfaces/org.fedoraproject.Config.Printing.xml
%{_datadir}/dbus-1/services/org.fedoraproject.Config.Printing.service
%verify(not md5 size mtime) %config(noreplace,missingok) %attr(0644,root,root) %{_localstatedir}/run/udev-configure-printer/usb-uris
%{_prefix}/lib/udev/*
%{_unitdir}/configure-printer@.service
%{_bindir}/scp-dbus-service
%{_datadir}/%{name}/asyncconn.py*
%{_datadir}/%{name}/asyncipp.py*
%{_datadir}/%{name}/asyncpk1.py*
%{_datadir}/%{name}/authconn.py*
%{_datadir}/%{name}/check-device-ids.py*
%{_datadir}/%{name}/config.py*
%{_datadir}/%{name}/cupspk.py*
%{_datadir}/%{name}/debug.py*
%{_datadir}/%{name}/dnssdresolve.py*
%{_datadir}/%{name}/errordialogs.py*
%{_datadir}/%{name}/firewallsettings.py*
%{_datadir}/%{name}/gtkinklevel.py*
%{_datadir}/%{name}/gui.py*
%{_datadir}/%{name}/installpackage.py*
%{_datadir}/%{name}/jobviewer.py*
%{_datadir}/%{name}/killtimer.py*
%{_datadir}/%{name}/monitor.py*
%{_datadir}/%{name}/newprinter.py*
%{_datadir}/%{name}/options.py*
%{_datadir}/%{name}/optionwidgets.py*
%{_datadir}/%{name}/OpenPrintingRequest.py*
%{_datadir}/%{name}/PhysicalDevice.py*
%{_datadir}/%{name}/ppdcache.py*
%{_datadir}/%{name}/ppdippstr.py*
%{_datadir}/%{name}/ppdsloader.py*
%{_datadir}/%{name}/printerproperties.py*
%{_datadir}/%{name}/probe_printer.py*
%{_datadir}/%{name}/pysmb.py*
%{_datadir}/%{name}/scp-dbus-service.py*
%{_datadir}/%{name}/SearchCriterion.py*
%{_datadir}/%{name}/smburi.py*
%{_datadir}/%{name}/statereason.py*
%{_datadir}/%{name}/timedops.py*
%{_datadir}/%{name}/xml/*
%{py_puresitedir}/cupshelpers
%{py_puresitedir}/cupshelpers*.*-info

%files gui -f system-config-printer.lang
%dir %{_datadir}/%{name}/ui
%dir %{_datadir}/%{name}/troubleshoot
%dir %{_datadir}/%{name}/icons
%{_sysconfdir}/xdg/autostart/print-applet.desktop
%{_bindir}/%{name}
%{_bindir}/install-printerdriver
%{_bindir}/%{name}-applet
%{_datadir}/%{name}/applet.py*
%{_datadir}/%{name}/HIG.py*
%{_datadir}/%{name}/install-printerdriver.py*
%{_datadir}/%{name}/serversettings.py*
%{_datadir}/%{name}/system-config-printer.py*
%{_datadir}/%{name}/ToolbarSearchEntry.py*
%{_datadir}/%{name}/userdefault.py*
%{_datadir}/%{name}/troubleshoot/*.py*
%{_datadir}/%{name}/icons/*.png
%{_datadir}/%{name}/ui/*.ui
%{_datadir}/applications/system-config-printer.desktop
%{_datadir}/metainfo/*.appdata.xml
%{_mandir}/man1/*
