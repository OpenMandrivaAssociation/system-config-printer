%define         svn   800427

Name:           system-config-printer
Summary:        A printer administration tool
Version:        0.9.90
Release:        %mkrel 1
Url:            http://cyberelk.net/tim/software/system-config-printer/
License:        LGPLv2+
Group:          TODO
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
Source0:        %name-%{version}.tar.bz2
Source1:        pycups-1.9.38.tar.bz2
Source2:        system-config-printer.pam
Source3:        system-config-printer.console
BuildRequires:  cups-devel >= 1.2
BuildRequires:  python-devel >= 2.4
BuildRequires:  desktop-file-utils >= 0.2.92
BuildRequires:  gettext-devel
BuildRequires:  intltool
BuildRequires:  xmlto
BuildRequires:  epydoc

Requires:       pygtk2 >= 2.4.0
Requires:       pygobject2
Requires:       usermode >= 1.94
Requires:       desktop-file-utils >= 0.2.92
Requires:       dbus-x11
Requires:       system-config-printer-libs = %{version}-%{release}
Requires:       gnome-icon-theme
Requires:       gnome-python2
Requires:       notification-daemon

%description
system-config-printer is a graphical user interface that allows
the user to configure a CUPS print server.

%files
%defattr(-,root,root)
%doc ChangeLog README TODO
%{_bindir}/%{name}
%{_bindir}/%{name}-applet
%{_bindir}/my-default-printer
%{_sbindir}/%{name}
%{_datadir}/%{name}/authconn.py*
%{_datadir}/%{name}/config.py*
%{_datadir}/%{name}/contextmenu.py*
%{_datadir}/%{name}/debug.py*
%{_datadir}/%{name}/jobviewer.py*
%{_datadir}/%{name}/monitor.py*
%{_datadir}/%{name}/my-default-printer.py*
%{_datadir}/%{name}/openprinting.py*
%{_datadir}/%{name}/options.py*
%{_datadir}/%{name}/optionwidgets.py*
%{_datadir}/%{name}/probe_printer.py*
%{_datadir}/%{name}/pysmb.py*
%{_datadir}/%{name}/smburi.py*
%{_datadir}/%{name}/statereason.py*
%{_datadir}/%{name}/system-config-printer.py*
%{_datadir}/%{name}/gtk_label_autowrap.py*
%{_datadir}/%{name}/gtk_treeviewtooltips.py*
%{_datadir}/%{name}/applet.py*
%{_datadir}/%{name}/troubleshoot
%{_datadir}/%{name}/*.glade
%{_datadir}/%{name}/icons
%{_datadir}/applications/redhat-system-config-printer.desktop
%{_datadir}/applications/redhat-manage-print-jobs.desktop
%{_datadir}/applications/redhat-my-default-printer.desktop
%config(noreplace) %{_sysconfdir}/pam.d/%{name}
%config(noreplace) %{_sysconfdir}/security/console.apps/%{name}
%{_sysconfdir}/xdg/autostart/redhat-print-applet.desktop
%{_mandir}/man1/*

#---------------------------------------------------------------------

%package  libs
Summary:  Common code for the graphical and non-graphical pieces
Group:    System Environment/Base
Requires: python
Requires: foomatic
Provides: pycups = %{pycups_version}

%description libs
The common code used by both the graphical and non-graphical parts of
the configuration tool.

%files libs -f system-config-printer.lang
%defattr(-,root,root,-)
%doc --parents pycups-1.9.38/{ChangeLog,README,NEWS,TODO,examples,html}
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/newprinternotification.conf
%{python_sitearch}/cups.so
%{python_sitearch}/cups-1.0-py2.5.egg-info
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/cupshelpers.py*
%{_datadir}/%{name}/ppds.py*

#--------------------------------------------------------------------

%prep
%setup -q -a 1

%build
%configure

pushd pycups-1.9.38
make
make doc
popd

%install
rm -rf %buildroot
make DESTDIR=%buildroot install

pushd pycups-1.9.38
chmod 644 examples/cupstree.py
make DESTDIR=%buildroot install
popd

mkdir -p %buildroot%{_bindir}
mkdir -p %buildroot%{_sysconfdir}/pam.d
mkdir -p %buildroot%{_sysconfdir}/security/console.apps
install -p -m0644 %{SOURCE2} %buildroot%{_sysconfdir}/pam.d/%{name}
install -p -m0644 %{SOURCE3} %buildroot%{_sysconfdir}/security/console.apps/%{name}
ln -s consolehelper %buildroot%{_bindir}/%{name}

%find_lang system-config-printer

%clean
%{__rm} -rf "%{buildroot}"
