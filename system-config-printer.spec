%define use_gitsnap 0
%{?_no_gitsnap: %{expand: %%global use_gitsnap 0}}
%if %{use_gitsnap}
%define gitsnap 200809231700
%endif

# disable the requires on gnome-python-gnomekeyring when it's not avaialable
# gnome-python-desktop requires s-c-p indirectly and the build fails otherwise
%define pygnomekeyring 1

Name:			system-config-printer
Summary:		A printer administration tool
Version:		1.3.12
Release:		12
Url:			http://cyberelk.net/tim/software/system-config-printer/
License:		LGPLv2+
Group:			System/Configuration/Printing
Source0:		http://cyberelk.net/tim/data/system-config-printer/1.3/%{name}-%{version}%{?gitsnap:-%gitsnap}.tar.xz
Source1:		system-config-printer.pam
Source2:		system-config-printer.console
Source3:		po-mdv.tar.bz2
Source4:		mdv_printer_custom.py
#Source5:        hp-makeuri-mdv.c
#Source6:        mdv_backend
Source7:		69-printers_lp_user_fix.rules
Source100:		system-config-printer.rpmlintrc
#Patch0:         system-config-printer-1.3.4-mdv_custom-applet.patch
Patch2:			system-config-printer-1.3.3-mdv_custom-system-config-printer.patch
Patch3:			system-config-printer-1.3.1-start-applet.patch
Patch4:			system-config-printer-1.3.11-udev-configure-printer-mdv.patch
Patch5:			system-config-printer-1.3.11-mdv_custom-embedded_window.patch
Patch6:			system-config-printer-1.3.11-cups-version.patch
# Fedora patches
Patch200:		system-config-printer-no-job-notifications.patch
Patch201:		system-config-printer-dnssd-crash.patch
Patch203:		system-config-printer-systemd.patch

# Mageia patches
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
BuildRequires:	libusb-devel
BuildRequires:	libhpip-devel
BuildRequires:	dbus-devel
BuildRequires:	dbus-glib-devel
BuildRequires:	systemd-units >= 37

Obsoletes:		desktop-printing
Obsoletes:		printerdrake
Provides:		printerdrake
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
#Requires:	packagekit
#Requires:   typelib(PackageKitGlib)
# nmap is required to scan the network, just like 
# printerdrake used to do.
Requires:		nmap
Requires:		python-smbc
# Why? kdeutils4-printer-applet reqires system-config-printer...
#Conflicts:      kdeutils4-printer-applet
Suggests:		samba-client
%if %{pygnomekeyring}
Requires:		gnome-python-gnomekeyring
%endif
# Required for CheckUSBPermissions.py
Requires:		acl

%description
system-config-printer is a graphical user interface that allows
the user to configure a CUPS print server.

%files
%doc ChangeLog README
%{_bindir}/%{name}
%{_bindir}/scp-dbus-service
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
%{_unitdir}/configure-printer.service
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
#patch0 -p1 -b .mdv_custom-applet
%patch2 -p1 -b .mdv_custom-system-config-printer
%patch3 -p1 -b .start_applet
%patch4 -p1 -b .udev-configue-printer-mdv
%patch5 -p1 -b .mdv_custom-embedded-window
%patch6 -p1 -b .cups_version
# Don't show job notifications.
%patch200 -p1 -b .no-job-notifications
%patch201 -p1 -b .ddns
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
#gcc %{SOURCE5} -o hp-makeuri-mdv -lhpmud

%install
rm -rf %buildroot
%makeinstall_std udevrulesdir=/lib/udev/rules.d  udevhelperdir=/lib/udev

mkdir -p %{buildroot}%{_mozillaextpath}
mkdir -p %{buildroot}%{py_platsitedir}
mkdir -p %{buildroot}%{_bindir}
#cp -f hp-makeuri-mdv %{buildroot}%{_bindir}
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

#rename service
mv -f %buildroot%{_unitdir}/configure-printer@.service %buildroot%{_unitdir}/configure-printer.service

%find_lang system-config-printer


%changelog
* Sun Nov 25 2012 Arkady L. Shane <ashejn@rosalab.ru> 1.3.12-6
- R: typelib(PackageKitGlib)

* Sat Nov 24 2012 akdengi <akdengi> 1.3.12-1
- 1.3.12
- add latest Fedora patch
- drop unused Fedora patch
- run udev-detect service on setup
- check in udev service if cups installed and running.
- rediff patches

* Fri Sep 07 2012 akdengi <akdengi> 1.3.11-1
- 1.3.11
- sync with Mageia patch. Big thanks guys for hard work!
- Add patch from Fedora to avoid using deprecated udev function
- fix duplicated lines in udev-add-printer added by
  mdv_custom-system-config-printer.patch which caused automatic
  printer configuration to not work properly; the bug was probably a result of an
  erroneus rediff)
- do not install task-printing instead of task-printing-server, which
  was a non-working workaround for the above issue
- don't query packagekit for drivers, it would just produce a scary error
  while we have a separate hook to install task-printing-foobar
- fix task-printing-foobar hook to use self.remotecupsqueue instead of
  not-yet-populated self.auto_make to trigger package installation
- fork udev-configure-printer before trying to install printing server
  as long-running processes should not be run under udev
- fix cups backend directory on x86_64
- Add missing python-curl Requires
- Own %%{_sysconfdir}/cupshelpers/
- Change task-printing-server require into task-printing
- Enable systemd at build
- Fix file list
- Fix udev installation path

* Fri May 06 2011 Oden Eriksson <oeriksson@mandriva.com> 1.2.0-14mdv2011.0
+ Revision: 670258
- mass rebuild

* Tue Nov 02 2010 Crispin Boylan <crisb@mandriva.org> 1.2.0-13mdv2011.0
+ Revision: 592032
- Rebuild

* Wed Apr 14 2010 Tiago Salem <salem@mandriva.com.br> 1.2.0-12mdv2010.1
+ Revision: 534931
- fix the dbus timeout problem, changes the default 25 seconds to 360
- bump release

* Mon Apr 12 2010 Tiago Salem <salem@mandriva.com.br> 1.2.0-11mdv2010.1
+ Revision: 533718
- remove old patch
- merge debug patch with udev-configure-printer patch
- add more methods to applet.py to better control the installation of packages
- bump release

* Fri Apr 09 2010 Tiago Salem <salem@mandriva.com.br> 1.2.0-10mdv2010.1
+ Revision: 533500
- fix udev rules for the parallel printers
- bump release

* Wed Apr 07 2010 Tiago Salem <salem@mandriva.com.br> 1.2.0-9mdv2010.1
+ Revision: 532807
- fix for hp printers that require firmware upload
- bump release

* Tue Apr 06 2010 Nicolas Lécureuil <nlecureuil@mandriva.com> 1.2.0-8mdv2010.1
+ Revision: 531912
- Add back the debug patch
  As cups is fixed, allow back to install driver in the udev C file

* Mon Apr 05 2010 Tiago Salem <salem@mandriva.com.br> 1.2.0-7mdv2010.1
+ Revision: 531859
- update to the last git version
- removing some old firmware upload code
- updating old patches to the last git code
- bump release
- oops, now commiting the right fix for the device permission bug in udev
- fix variable name to set the right permission the the usb device

* Sat Apr 03 2010 Nicolas Lécureuil <nlecureuil@mandriva.com> 1.2.0-6mdv2010.1
+ Revision: 530858
- Disable install functions in the udev part ( for now )

  + Tiago Salem <salem@mandriva.com.br>
    - removing some self's from the old hal-cups-utils code
    - only apply the setfacl on printers

* Mon Mar 29 2010 Tiago Salem <salem@mandriva.com.br> 1.2.0-5mdv2010.1
+ Revision: 528922
- temporarily disable some notifications, as we cannot get the printer name yet
- disable redundant notification.
- bump release

  + Nicolas Lécureuil <nlecureuil@mandriva.com>
    - Patch6: cleanup

* Sat Mar 27 2010 Nicolas Lécureuil <nlecureuil@mandriva.com> 1.2.0-4mdv2010.1
+ Revision: 527893
- Add debug in the udev file

* Fri Mar 26 2010 Tiago Salem <salem@mandriva.com.br> 1.2.0-3mdv2010.1
+ Revision: 527856
- fixing conflicts tag
- many fixes concering hal -> udev migration
- moving udev rule from cups package to system-config-printer-udev
- add conflicts to system-config-printer-udev package
- bump release

  + Nicolas Lécureuil <nlecureuil@mandriva.com>
    - Fix requires (Bug# 58383)

* Mon Mar 22 2010 Tiago Salem <salem@mandriva.com.br> 1.2.0-2mdv2010.1
+ Revision: 526633
- fix identation issue preventing udev-add-printer from working properly.
- bump release

* Thu Mar 18 2010 Funda Wang <fwang@mandriva.org> 1.2.0-1mdv2010.1
+ Revision: 524767
- New verison 1.2.0 final
- drop merged patches

* Mon Mar 08 2010 Nicolas Lécureuil <nlecureuil@mandriva.com> 1.1.93-4mdv2010.1
+ Revision: 516038
- Add Fedora patches
- Restart Cups after printer installed (Bug #53138)

* Tue Mar 02 2010 Tiago Salem <salem@mandriva.com.br> 1.1.93-3mdv2010.1
+ Revision: 513669
- add missing BuildRequires
- disable parallel building. s-c-p is failing to build this way.

  + Nicolas Lécureuil <nlecureuil@mandriva.com>
    - Add dbus-devel as BuildRequire
    - Install cups if needed

* Mon Mar 01 2010 Nicolas Lécureuil <nlecureuil@mandriva.com> 1.1.93-2mdv2010.1
+ Revision: 512919
- Fix install
  Fix file lists

* Mon Mar 01 2010 Nicolas Lécureuil <nlecureuil@mandriva.com> 1.1.93-1mdv2010.1
+ Revision: 512886
- Rediff patch2
- Update to version 1.1.93
- Bump release
- Remove unneeded action
- Fix file list
- Fix system-config-printer-1.1.92-try-to-start-cups.patch
- Fix call to service to make it works
- If cups is not started, try to start it before exit()
- Add files needed for the udev part ( from hal utils )
  Remove not existing polkit configure option
- Start to port the hal utils part into udev
- Fix Requires

* Mon Feb 22 2010 Nicolas Lécureuil <nlecureuil@mandriva.com> 1.1.92-1mdv2010.1
+ Revision: 509571
- Update to version 1.1.92
  Refiff mdv patch
  Fix file list
- Add back consolehelper, this is needed because of our patch that restart cups service

* Fri Feb 19 2010 Frederik Himpe <fhimpe@mandriva.org> 1.1.17-2mdv2010.1
+ Revision: 508459
- Merge a few Ubuntu patches:
  * Delay start-up of applet in GNOME for 30 seconds to accelerate
    login
  * Prefer hpcups driver above hpijs, like in 2010.0: hpijs is obsolete
    and hpcups is mature now
  * When comparing printer URIs, deal with the different URIs used by the
    old usblp back-end and the new libusb back-end

* Fri Feb 19 2010 Nicolas Lécureuil <nlecureuil@mandriva.com> 1.1.17-1mdv2010.1
+ Revision: 508346
- fix system-config-printer-1.1.17-mdv_custom-system-config-printer.patch
- Update to s-c-p 1.1.17
  Remove merged patches

* Wed Oct 28 2009 Frederic Crozat <fcrozat@mandriva.com> 1.1.13-12mdv2010.0
+ Revision: 459648
- Fix upgrade from 2010.0 RC1/2

* Wed Oct 28 2009 Gustavo De Nardin <gustavodn@mandriva.com> 1.1.13-11mdv2010.0
+ Revision: 459628
- dropped system-config-printer-udev, it is not ready to obsolete
  hal-cups-utils yet; all changes for system-config-printer-udev were made
  conditional for now
- dropped mdv_backend and mdv_printer_custom.py, they'll still be provided
  by hal-cups-utils for now

* Fri Oct 23 2009 Gustavo De Nardin <gustavodn@mandriva.com> 1.1.13-10mdv2010.0
+ Revision: 459118
- mdv_custom-system-config-printer fixed by Tiago Salem Herrmann, to use the
  correct data for the printer detection, should fix bug 46940 and others
- no need to require nor provide hal-cups-utils anymore

* Fri Oct 09 2009 Frederik Himpe <fhimpe@mandriva.org> 1.1.13-9mdv2010.0
+ Revision: 456412
- Requires nmap (for network printer detection) and hplip-model-data
  (for HP printer detection). Both Requires are moved here because
  hal-cups-utils which required them, is now obsoleted

* Wed Oct 07 2009 Nicolas Lécureuil <nlecureuil@mandriva.com> 1.1.13-8mdv2010.0
+ Revision: 455653
- Create %%{py_platsitedir}
- Fix file list
- add mdv_printer_custom python module

* Wed Oct 07 2009 Nicolas Lécureuil <nlecureuil@mandriva.com> 1.1.13-6mdv2010.0
+ Revision: 455513
- Fix group
- Obsolete hal-cups-utils
  Add an udev subpackage
  add udev stuffs from fedora

* Mon Oct 05 2009 Nicolas Lécureuil <nlecureuil@mandriva.com> 1.1.13-4mdv2010.0
+ Revision: 453913
- do not use consolehelper  as we use polkit-1

* Mon Oct 05 2009 Nicolas Lécureuil <nlecureuil@mandriva.com> 1.1.13-3mdv2010.0
+ Revision: 453738
- Fix buildrequires: libusb-devel
- Add patches from fedora
- not noarched now
- Package udev files

* Mon Sep 28 2009 Olivier Blin <oblin@mandriva.com> 1.1.13-2mdv2010.0
+ Revision: 450549
- require libxml2-python (#53975)

* Mon Sep 14 2009 Frederik Himpe <fhimpe@mandriva.org> 1.1.13-1mdv2010.0
+ Revision: 440692
- Update to new version 1.1.13

* Sun Sep 06 2009 Gustavo De Nardin <gustavodn@mandriva.com> 1.1.12-1mdv2010.0
+ Revision: 432080
- new version, 1.1.12
- removed patches mdv_custom-jobviewer and mdv_custom-popup_menu, s-c-p
  1.1.x implements on_icon_configure_printers_activate() with the same
  purpose
- patches rediffed for s-c-p 1.1.12: mdv_custom-applet,
  mdv_custom-embedded_window, mdv_custom-system-config-printer
- BuildRequires docbook-style-xsl for manpages/docbook.xsl for
  man/system-config-printer.xml

* Thu Sep 03 2009 Christophe Fergeau <cfergeau@mandriva.com> 1.0.16-5mdv2010.0
+ Revision: 428451
- add docbook dtd to BuildRequires
- rebuild

* Thu Apr 16 2009 Gustavo De Nardin <gustavodn@mandriva.com> 1.0.16-4mdv2009.1
+ Revision: 367600
- P5: start system-config-printer-applet in KDE4
- python is patched to fix gettext.py, no more need to strip comments from
  po files
- updated mdv-po/pt_BR.po

* Wed Apr 15 2009 Thierry Vignaud <tv@mandriva.org> 1.0.16-3mdv2009.1
+ Revision: 367444
- translation updates

* Sun Apr 12 2009 Gustavo De Nardin <gustavodn@mandriva.com> 1.0.16-2mdv2009.1
+ Revision: 366456
- improved workaround for gettext.py bug when parsing "Plural-Forms:"
  header; fixes crash when LANGUAGE=nl (bug #49475)

* Sat Mar 14 2009 Frederik Himpe <fhimpe@mandriva.org> 1.0.16-1mdv2009.1
+ Revision: 354854
- Update to new version 1.0.16

* Thu Feb 19 2009 Frederik Himpe <fhimpe@mandriva.org> 1.0.15-1mdv2009.1
+ Revision: 342999
- update to new version 1.0.15

* Wed Feb 11 2009 Frederik Himpe <fhimpe@mandriva.org> 1.0.14-1mdv2009.1
+ Revision: 339615
- Update to new version 1.0.14
- Rediff mdv_custom-system-config-printer.patch

* Sat Jan 31 2009 Frederik Himpe <fhimpe@mandriva.org> 1.0.13-1mdv2009.1
+ Revision: 335727
- Update to new version 1.0.13

* Fri Dec 26 2008 Adam Williamson <awilliamson@mandriva.org> 1.0.12-3mdv2009.1
+ Revision: 319524
- rediff mdv_custom-applet.patch
- rebuild with python 2.6

  + Funda Wang <fwang@mandriva.org>
    - rebuild for new python

* Fri Dec 05 2008 Leonardo de Amaral Vidal <leonardoav@mandriva.com> 1.0.12-1mdv2009.1
+ Revision: 310781
- New version 1.0,12

* Thu Nov 27 2008 Leonardo de Amaral Vidal <leonardoav@mandriva.com> 1.0.11-1mdv2009.1
+ Revision: 307298
- New version 1.0.11

* Thu Nov 20 2008 Leonardo de Amaral Vidal <leonardoav@mandriva.com> 1.0.10-1mdv2009.1
+ Revision: 305240
- New version 1.0.10
- New version 1.0.10

* Wed Oct 01 2008 Funda Wang <fwang@mandriva.org> 1.0.7-13mdv2009.0
+ Revision: 290491
- new translation snapshot

* Mon Sep 29 2008 Tiago Salem <salem@mandriva.com.br> 1.0.7-12mdv2009.0
+ Revision: 289446
- update po-mdv tarball
- bump release

* Wed Sep 24 2008 Tiago Salem <salem@mandriva.com.br> 1.0.7-11mdv2009.0
+ Revision: 287941
- fix translation issue in system-config-printer-applet
- bump release

* Tue Sep 23 2008 Tiago Salem <salem@mandriva.com.br> 1.0.7-10mdv2009.0
+ Revision: 287630
- update to the latest git version
- bump release

* Tue Sep 23 2008 Tiago Salem <salem@mandriva.com.br> 1.0.7-9mdv2009.0
+ Revision: 287580
- remove custom network printer detection.
  This is done by mdv_backend in hal-cups-utils now.
- bump release

* Mon Sep 22 2008 Tiago Salem <salem@mandriva.com.br> 1.0.7-8mdv2009.0
+ Revision: 287024
- update mdv-po tarball
- remove some comments from po files generated by msgcat (fix #44088)
- bump release

* Mon Sep 22 2008 Tiago Salem <salem@mandriva.com.br> 1.0.7-7mdv2009.0
+ Revision: 286917
- add network printer detection (#43488 and #43285)
- bump release

* Mon Sep 15 2008 Tiago Salem <salem@mandriva.com.br> 1.0.7-6mdv2009.0
+ Revision: 285067
- changing spec to support git snapshots
- add git snapshot tarball to merge current translation files and some fixes
- remove upstream code
- bump release

* Thu Sep 11 2008 Tiago Salem <salem@mandriva.com.br> 1.0.7-5mdv2009.0
+ Revision: 283789
- merge upstream and custom mdv po files
- bump release

* Wed Sep 10 2008 Tiago Salem <salem@mandriva.com.br> 1.0.7-4mdv2009.0
+ Revision: 283572
- Obsoletes/Provides printerdrake.
- bump release

* Fri Sep 05 2008 Frederic Crozat <fcrozat@mandriva.com> 1.0.7-3mdv2009.0
+ Revision: 281070
- Add missing dependency on python-notify

* Tue Sep 02 2008 Tiago Salem <salem@mandriva.com.br> 1.0.7-2mdv2009.0
+ Revision: 279119
- fix bug https://bugzilla.redhat.com/show_bug.cgi?id=460670
- bump release
- re-enabling attach_to_status_icon() as it was fixed in python-cups

* Mon Sep 01 2008 Tiago Salem <salem@mandriva.com.br> 1.0.7-1mdv2009.0
+ Revision: 278409
- version 1.0.7
- Fix message typos
- prevent installing drivers for some network printers

* Tue Aug 26 2008 Tiago Salem <salem@mandriva.com.br> 1.0.6-2mdv2009.0
+ Revision: 276342
- fix icon in applet
- fix auto-select make and model for parallel printers
- auto install task-printing-hp, many commands from hplip
  are needed by system-config-printer (hp-info, hp-makeuri)
- bump release

* Mon Aug 25 2008 Tiago Salem <salem@mandriva.com.br> 1.0.6-1mdv2009.0
+ Revision: 275926
- new version 1.0.6
- rediff patches to the new version
- adapt spec to the new version

* Mon Aug 25 2008 Tiago Salem <salem@mandriva.com.br> 1.0.4-7mdv2009.0
+ Revision: 275778
- fix page bug order on wizard window (#43119)
- bump release

* Fri Aug 22 2008 Tiago Salem <salem@mandriva.com.br> 1.0.4-6mdv2009.0
+ Revision: 275232
- change patches 3 and 4 order
- add function call to reload parallel kernel modules
- add missing translation tags
- fix printer name when a custom ppd is provided
- bump release

* Wed Aug 20 2008 Tiago Salem <salem@mandriva.com.br> 1.0.4-5mdv2009.0
+ Revision: 274437
- make system-config-printer ask for task-printing-server
- bump release

* Wed Aug 20 2008 Tiago Salem <salem@mandriva.com.br> 1.0.4-4mdv2009.0
+ Revision: 274255
- add patch to be able to embed system-config-printer in mcc.
- bump release
- add obsoletes to desktop-printing package

* Thu Aug 07 2008 Tiago Salem <salem@mandriva.com.br> 1.0.4-3mdv2009.0
+ Revision: 267204
- bump release
- adding mandriva custom stuff
- bump release

* Thu Aug 07 2008 Frederik Himpe <fhimpe@mandriva.org> 1.0.4-2mdv2009.0
+ Revision: 266831
- Also create byte-compiled files for the files
  in /usr/share/system-config-printer, otherwise they can be created
  at run-time and cause trouble when the package is updated later on

* Wed Aug 06 2008 Frederik Himpe <fhimpe@mandriva.org> 1.0.4-1mdv2009.0
+ Revision: 264746
- New version 1.0.4
- Fix file list

  + Funda Wang <fwang@mandriva.org>
    - should be noarch

* Sat Jun 21 2008 Nicolas Lécureuil <nlecureuil@mandriva.com> 1.0.2-1mdv2009.0
+ Revision: 227707
- New version 1.0.2

* Fri Jun 06 2008 Tiago Salem <salem@mandriva.com.br> 0.9.93-1mdv2009.0
+ Revision: 216485
- Version 0.9.93
- add missing requires: python-rhpl

* Fri May 16 2008 Thierry Vignaud <tv@mandriva.org> 0.9.90-3mdv2009.0
+ Revision: 208172
- fix notification-daemon require so that it cohabites with notification-daemon-xfce

* Wed May 14 2008 Anssi Hannula <anssi@mandriva.org> 0.9.90-2mdv2009.0
+ Revision: 207238
- remove bogus buildrequires on epydoc

  + Nicolas Lécureuil <nlecureuil@mandriva.com>
    - Fix Requires ( big thanks to Anssi )

* Sun May 11 2008 Nicolas Lécureuil <nlecureuil@mandriva.com> 0.9.90-1mdv2009.0
+ Revision: 205935
- Fix Provides
- Fix groups
- Fix Groups
- Fix source naming
- Requires python-cups
- pycups is now on its own package
- Fix Requires
- Fix Requires
- import system-config-printer


