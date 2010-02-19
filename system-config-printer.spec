%define use_gitsnap 0
%{?_no_gitsnap: %{expand: %%global use_gitsnap 0}}
%if %{use_gitsnap}
%define gitsnap 200809231700
%endif

# needs porting of Mandriva specific features from hal-cups-utils to s-c-p-udev
%define         obsolete_hal_cups_utils 0

Name:           system-config-printer
Summary:        A printer administration tool
Version:        1.1.17
Release:        %mkrel 1
Url:            http://cyberelk.net/tim/software/system-config-printer/
License:        LGPLv2+
Group:          System/Configuration/Printing
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
Source0:        http://cyberelk.net/tim/data/system-config-printer/1.1/%{name}-%{version}%{?gitsnap:-%gitsnap}.tar.xz
Source1:        system-config-printer.pam
Source2:        system-config-printer.console
Source3:        po-mdv.tar.bz2
Patch0:         system-config-printer-1.1.12-mdv_custom-applet.patch
Patch1:         system-config-printer-1.1.12-mdv_custom-embedded_window.patch
Patch2:         system-config-printer-1.1.17-mdv_custom-system-config-printer.patch
Patch3:         system-config-printer-1.1.17-start-applet.patch
# Ubuntu patches
# use hpcups instead of hpijs for HP printers, like in
# previous versions. hpijs is obsolete and hpcup is mature now
Patch101:	50_give-priority-to-hpcups.patch
# when comparing usb uris, deal with the difference between the obsolete
# usblp and the new libusb back-end
Patch102:	67_match-usb-uris-of-usblp-and-libusb.patch
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
%{_bindir}/%{name}-applet
%{_bindir}/my-default-printer
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*.py*
%{_datadir}/%{name}/troubleshoot
%{_datadir}/%{name}/glade/*.glade
%{_datadir}/%{name}/icons
%{_datadir}/applications/system-config-printer.desktop
%{_datadir}/applications/manage-print-jobs.desktop
%{_datadir}/applications/my-default-printer.desktop
%{_sysconfdir}/xdg/autostart/print-applet.desktop
%{_mandir}/man1/*

#---------------------------------------------------------------------
%if %obsolete_hal_cups_utils
%package udev
Summary: Rules for udev for automatic configuration of USB printers
Group:    System/Configuration/Hardware
Requires: system-config-printer-libs = %{version}-%{release}
Obsoletes: hal-cups-utils <= 0.6.20

%description udev
The udev rules and helper programs for automatically configuring USB
printers.

%files udev
%defattr(-,root,root,-)
%{_sysconfdir}/udev/rules.d/*.rules
/lib/udev/*
%dir %{_localstatedir}/run/udev-configure-printer
%verify(not md5 size mtime) %config(noreplace,missingok) %attr(0644,root,root) %{_localstatedir}/run/udev-configure-printer/usb-uris
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
%dir %{python_sitelib}/cupshelpers
%{python_sitelib}/cupshelpers/__init__.py*
%{python_sitelib}/cupshelpers/cupshelpers.py*
%{python_sitelib}/cupshelpers/openprinting.py*
%{python_sitelib}/cupshelpers/ppds.py*
%{python_sitelib}/*.egg-info

#--------------------------------------------------------------------

%prep
%setup -q 
%patch0 -p1 -b .mdv_custom-applet
%patch1 -p1 -b .mdv_custom-embedded-window
%patch2 -p0 -b .mdv_custom-system-config-printer
%patch3 -p0 -b .start_applet
%patch101 -p1 -b .hpcupsprio
%patch102 -p1 -b .libusb

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
./configure --prefix=%{_prefix} \
	--sysconfdir=%{_sysconfdir} \
%if %obsolete_hal_cups_utils
	--with-udev-rules \
%endif
	--with-polkit-1
%make

%install
rm -rf %buildroot
make DESTDIR=%buildroot install

# Make sure pyc files are generated, otherwise we can get
# difficult to debug problems
pushd %{buildroot}%{_datadir}/%{name}
python -m compileall .
popd

%if %obsolete_hal_cups_utils
%{__mkdir_p} %buildroot%{_localstatedir}/run/udev-configure-printer
touch %buildroot%{_localstatedir}/run/udev-configure-printer/usb-uris
%endif

%find_lang system-config-printer

%clean
%{__rm} -rf "%{buildroot}"
