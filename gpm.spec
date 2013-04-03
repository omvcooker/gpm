%bcond_without	ncurses
%bcond_without	uclibc

# this defines the library version that this package builds.
%define	major	2
%define	libname	%mklibname %{name} %{major}
%define	devname	%mklibname %{name} -d

Summary:	A mouse server for the Linux console
Name:		gpm
Version:	1.20.7
Release:	3
License:	GPLv2+
Group:		System/Servers
URL:		http://www.nico.schottelius.org/software/gpm/
Source0:	http://www.nico.schottelius.org/software/gpm/archives/%{name}-%{version}.tar.lzma
#(proyvind): please don't remove, still used by DrakX micro environment
Source1:	gpm.init
Source2:	inputattach.c
Source3:	gpm.service
# fedora patches (gpm-1.20.5-1.fc10.src.rpm)
Patch1:		gpm-1.20.1-multilib.patch
Patch2:		gpm-1.20.1-lib-silent.patch
Patch4:		gpm-1.20.5-close-fds.patch
Patch5:		gpm-1.20.7-weak-wgetch.patch
# mdv patches
Patch50:	gpm-1.20.5-nodebug.patch
Patch51:	gpm-1.20.0-docfix.patch
Patch52:	gpm-1.20.7-do_not_build_it_twice.diff
Patch53:	gpm-1.20.5-format_not_a_string_literal_and_no_format_arguments.diff
# these automake files are utter crap, so just let's rip out the stuff that really doesn't belong
# there, we don't use and that's causing problem..
Patch54:	gpm-1.20.7-fix-out-of-source-build.patch

BuildRequires:	byacc
%if %{with ncurses}
BuildRequires:	pkgconfig(ncursesw)
%endif
%if %{with uclibc}
BuildRequires:	uClibc-devel >= 0.9.33.2-3
%endif
BuildRequires:	texinfo
BuildRequires:	autoconf
Requires(post):	chkconfig, rpm-helper
Requires(preun):chkconfig, rpm-helper

%description
Gpm provides mouse support to text-based Linux applications like the
emacs editor, the Midnight Commander file management system, and other
programs.  Gpm also provides console cut-and-paste operations using
the mouse and includes a program to allow pop-up menus to appear at
the click of a mouse button.

Gpm should be installed if you intend to use a mouse with your
MandrivaLinux system.

%package -n	uclibc-%{name}
Summary:	A mouse server for the Linux console (uClibc build)
Group:		System/Servers

%description -n	uclibc-%{name}
Gpm provides mouse support to text-based Linux applications like the
emacs editor, the Midnight Commander file management system, and other
programs.  Gpm also provides console cut-and-paste operations using
the mouse and includes a program to allow pop-up menus to appear at
the click of a mouse button.

%package -n	%{libname}
Summary:	Libraries and header files for developing mouse driven programs
Group:		System/Libraries

%description -n	%{libname}
Library used by the gpm program.

Install %{libname}dev if you need to develop text-mode programs which 
will use the mouse. You'll also need to install the gpm package.

%package -n	uclibc-%{libname}
Summary:	Libraries and header files for developing mouse driven programs (uClibc build)
Group:		System/Libraries

%description -n	uclibc-%{libname}
Library used by the gpm program.

%package -n	%{devname}
Summary:	Libraries and header files for developing mouse driven programs
Group:		Development/C
Requires:	%{libname} = %{version}
%if %{with uclibc}
Requires:	uclibc-%{libname} = %{version}
%endif
Provides:	gpm-devel = %{version}-%{release}

%description -n	%{devname}
The %{devname} package contains the libraries and header files needed
for development of mouse driven programs.  This package allows you to
develop text-mode programs which use the mouse.

Install %{devname} if you need to develop text-mode programs which
will use the mouse. You'll also need to install the gpm package.

%prep
%setup -q
find -name \*.c |xargs chmod 644
    
# fedora patches
%patch1 -p1 -b .multilib~
%patch2 -p1 -b .lib-silent́~
%patch4 -p1 -b .close-fd~
%patch5 -p1 -b .weak-wgetch~

# mdv patches
%patch50 -p1 -b .nodebug~
%patch51 -p1 -b .docfix~
%patch52 -p1 -b .do_not_build_it_twice~
%patch53 -p0 -b .format_not_a_string_literal_and_no_format_arguments~
%patch54 -p1 -b .out_of_source~

cp %{SOURCE2} inputattach.c

./autogen.sh

%if %{with uclibc}
mkdir .uclibc
cp -a * .uclibc
%endif

%build
export ac_cv_path_emacs=no

%if %{with uclibc}
pushd .uclibc
CFLAGS="%{uclibc_cflags}" \
%uclibc_configure \
		--disable-static	
%if !%{with ncurses}
		--without-curses
%endif

%make
unset CFLAGS
popd
%endif

%configure2_5x \
%if !%{with ncurses}
		--without-curses
%endif

%make

%{__cc} %{optflags} %{ldflags} -o inputattach inputattach.c

%install
%if %{with uclibc}
%makeinstall_std -C .uclibc
mkdir -p %{buildroot}%{uclibc_root}/%{_lib}
mv %{buildroot}%{uclibc_root}%{_libdir}/libgpm.so.%{major}* %{buildroot}%{uclibc_root}/%{_lib}
ln -srf %{buildroot}%{uclibc_root}/%{_lib}/libgpm.so.%{major}.* %{buildroot}%{uclibc_root}%{_libdir}/libgpm.so
%endif

%makeinstall_std

install -m644 conf/gpm-root.conf -D %{buildroot}%{_sysconfdir}/gpm-root.conf
install -m755 inputattach -D %{buildroot}%{_sbindir}/inputattach

mkdir -p %{buildroot}/%{_lib}
mv %{buildroot}%{_libdir}/libgpm.so.%{major}* %{buildroot}/%{_lib}
ln -srf %{buildroot}/%{_lib}/libgpm.so.%{major}.*.* %{buildroot}%{_libdir}/libgpm.so

install -m755 %{SOURCE1} -D %{buildroot}%{_initrddir}/gpm
install -m644 %{SOURCE3} -D %{buildroot}%{_unitdir}/gpm.service

%post
%_post_service gpm
# handle init sequence change
if [ -f /etc/rc5.d/S85gpm ]; then
    /sbin/chkconfig --add gpm
fi

%preun
%_preun_service gpm

%files
%config(noreplace) %{_sysconfdir}/gpm-root.conf
%{_unitdir}/gpm.service
%{_initrddir}/gpm
%{_bindir}/display-buttons
%{_bindir}/display-coords
%{_bindir}/mev
%{_bindir}/gpm-root
%{_bindir}/hltest
%{_bindir}/mouse-test
%{_bindir}/disable-paste
%{_bindir}/get-versions
%{_sbindir}/gpm
%{_sbindir}/inputattach
%{_infodir}/gpm.info*
%{_mandir}/man1/mev.1*
%{_mandir}/man1/mouse-test.1*
%{_mandir}/man1/gpm-root.1*
%{_mandir}/man7/gpm-types.7*
%{_mandir}/man8/gpm.8*

%if %{with uclibc}
%files -n uclibc-%{name}
%{uclibc_root}%{_bindir}/display-buttons
%{uclibc_root}%{_bindir}/display-coords
%{uclibc_root}%{_bindir}/mev
%{uclibc_root}%{_bindir}/gpm-root
%{uclibc_root}%{_bindir}/hltest
%{uclibc_root}%{_bindir}/mouse-test
%{uclibc_root}%{_bindir}/disable-paste
%{uclibc_root}%{_bindir}/get-versions
%{uclibc_root}%{_sbindir}/gpm
%endif

%files -n %{libname}
/%{_lib}/libgpm.so.%{major}*

%if %{with uclibc}
%files -n uclibc-%{libname}
%{uclibc_root}/%{_lib}/libgpm.so.%{major}*
%endif

%files -n %{devname}
%{_libdir}/libgpm.a
%{_libdir}/libgpm.so
%if %{with uclibc}
%{uclibc_root}%{_libdir}/libgpm.so
%endif
%{_includedir}/gpm.h

%changelog
* Wed Dec 12 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 1.20.7-3
- rebuild on abf

* Sat Nov 03 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 1.20.7-2
+ Revision: 821717
- set a default mousetype in sysv init script
- allow to execute sysv init script with default configuration
- update default mouse device in sysv initscript to /dev/input/mice

* Wed Oct 31 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 1.20.7-1
+ Revision: 821442
- drop ancient obsoletes
- drop bogus libgpm-devel provides
- do a full uclibc build
- add dependency on texinfo
- cleanups
- update path for systemd service file to be installed
- drop systemd scriptlets (they're now handled by triggers)
- new version

* Wed Sep 05 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 1.20.6-9
+ Revision: 816378
- fix file permissions (also fixing stripping of library)
- cosmetics
- fix use of %%optflags & %%ldflags
- cleanup a bit
- drop missing header messing with dependencies rule (P55)
- do uclibc build
- drop rather useless %%serverbuild macro

  + Andrey Bondrov <abondrov@mandriva.org>
    - Drop some legacy junk

* Thu Nov 10 2011 Zé <ze@mandriva.org> 1.20.6-7
+ Revision: 729606
- no need to have requires to release
- fix ncurses build
- we safelly allow to use all cpus to build

* Thu Nov 10 2011 Zé <ze@mandriva.org> 1.20.6-6
+ Revision: 729575
- use %%with (avoid using without according with rpm polycies
- add systemd support to enable mouse in cli since currently that is not possible
- clean BR and defattr
- remove clean section

* Sun May 08 2011 Funda Wang <fwang@mandriva.org> 1.20.6-5
+ Revision: 672466
- fix build

  + Oden Eriksson <oeriksson@mandriva.com>
    - mass rebuild

* Thu Dec 02 2010 Oden Eriksson <oeriksson@mandriva.com> 1.20.6-4mdv2011.0
+ Revision: 605496
- rebuild

* Sun Mar 14 2010 Oden Eriksson <oeriksson@mandriva.com> 1.20.6-3mdv2010.1
+ Revision: 519006
- rebuild

