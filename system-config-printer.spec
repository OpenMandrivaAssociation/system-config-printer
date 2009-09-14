%define use_gitsnap 0
%{?_no_gitsnap: %{expand: %%global use_gitsnap 0}}
%if %{use_gitsnap}
%define gitsnap 200809231700
%endif

Name:           system-config-printer
Summary:        A printer administration tool
Version:        1.1.13
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
Patch2:         system-config-printer-1.1.12-mdv_custom-system-config-printer.patch
Patch3:         system-config-printer-1.0.16-revert-27ddb74-start_applet_for_kde4.patch
BuildRequires:  cups-devel >= 1.2
BuildRequires:  python-devel >= 2.4
BuildRequires:  desktop-file-utils >= 0.2.92
BuildRequires:  gettext-devel
BuildRequires:  intltool
BuildRequires:  xmlto
BuildRequires:  docbook-dtd412-xml
BuildRequires:  docbook-style-xsl
BuildArch:	    noarch
Obsoletes:      desktop-printing
Obsoletes:      printerdrake
Provides:       printerdrake

Requires:       pygtk2 >= 2.4.0
Requires:       pygtk2.0-libglade
Requires:       python-gobject
Requires:       usermode >= 1.94
Requires:       desktop-file-utils >= 0.2.92
Requires:       dbus-x11
Requires:       system-config-printer-libs = %{version}-%{release}
Requires:       gnome-icon-theme
Requires:       gnome-python
Requires:       virtual-notification-daemon
Requires:       python-cups
Requires:       python-rhpl
Requires:       python-dbus
Requires:       hal-cups-utils
Requires:	    python-notify
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
%{_sbindir}/%{name}
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*.py*
%{_datadir}/%{name}/troubleshoot
%{_datadir}/%{name}/glade/*.glade
%{_datadir}/%{name}/icons
%{_datadir}/applications/system-config-printer.desktop
%{_datadir}/applications/manage-print-jobs.desktop
%{_datadir}/applications/my-default-printer.desktop
%{_sysconfdir}/xdg/autostart/print-applet.desktop
%config(noreplace) %{_sysconfdir}/pam.d/%{name}
%config(noreplace) %{_sysconfdir}/security/console.apps/%{name}
%{_mandir}/man1/*

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
%patch2 -p1 -b .mdv_custom-system-config-printer
%patch3 -p0 -b .start_applet_for_kde4

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
./configure --prefix=%{_prefix} --sysconfdir=%{_sysconfdir}
make

%install
rm -rf %buildroot
make DESTDIR=%buildroot install

# Make sure pyc files are generated, otherwise we can get
# difficult to debug problems
pushd %{buildroot}%{_datadir}/%{name}
python -m compileall .
popd

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
