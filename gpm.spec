# Allow first build without ncurses support
%define build_curses %{?_without_curses:0}%{!?_without_curses:1}

# this defines the library version that this package builds.
%define LIBMAJ 2
%define LIBVER %{LIBMAJ}.1.0
%define libname %mklibname %{name} %LIBMAJ
%define develname %mklibname %{name} -d

Summary:	A mouse server for the Linux console
Name:		gpm
Version:	1.20.6
Release:	%mkrel 1
License:	GPLv2+
Group:		System/Servers
URL:		ftp://arcana.linux.it/pub/gpm/
Source0:	http://ftp.linux.it/pub/People/rubini/gpm/%{name}-%{version}.tar.lzma
Source1:	gpm.init
Source2:	inputattach.c
# fedora patches (gpm-1.20.5-1.fc10.src.rpm)
Patch1: gpm-1.20.1-multilib.patch
Patch2: gpm-1.20.1-lib-silent.patch
Patch3: gpm-1.20.3-gcc4.3.patch
Patch4: gpm-1.20.5-close-fds.patch
Patch5: gpm-1.20.1-weak-wgetch.patch
# mdv patches
Patch50:	gpm-1.20.5-nodebug.patch
Patch51:	gpm-1.20.0-docfix.patch
Patch52:	gpm-1.20.5-do_not_build_it_twice.diff
Patch53:	gpm-1.20.5-format_not_a_string_literal_and_no_format_arguments.diff
Requires(post): chkconfig, info-install, rpm-helper
Requires(preun): chkconfig, info-install, rpm-helper
BuildRequires:	byacc
%if %{build_curses}
BuildRequires:	ncurses-devel
%endif
#BuildRequires:	texinfo autoconf2.1
BuildRequires:	autoconf
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Gpm provides mouse support to text-based Linux applications like the
emacs editor, the Midnight Commander file management system, and other
programs.  Gpm also provides console cut-and-paste operations using
the mouse and includes a program to allow pop-up menus to appear at
the click of a mouse button.

Gpm should be installed if you intend to use a mouse with your
MandrivaLinux system.

%package -n	%{libname}
Summary:	Libraries and header files for developing mouse driven programs
Group:		System/Libraries

%description -n	%{libname}
Library used by the gpm program.

Install %{libname}dev if you need to develop text-mode programs which will use
the mouse.  You'll also need to install the gpm package.

%package -n	%{develname}
Summary:	Libraries and header files for developing mouse driven programs
Group:		Development/C
Requires:	%{libname} = %{version}
Provides:	gpm-devel libgpm-devel
Obsoletes:	gpm-devel
Provides:	%{mklibname %{name} 1 -d} = %{version}
Obsoletes:	%{mklibname %{name} 1 -d}

%description -n	%{develname}
The %{develname} package contains the libraries and header files needed
for development of mouse driven programs.  This package allows you to
develop text-mode programs which use the mouse.

Install %{develname} if you need to develop text-mode programs which will use
the mouse.  You'll also need to install the gpm package.

%prep

%setup -q

for i in `find . -type d -name CVS` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -rf $i; fi >&/dev/null
done
    
# fedora patches
%patch1 -p1 -b .multilib
%patch2 -p1 -b .lib-silent
%patch3 -p1 -b .gcc4.3
%patch4 -p1 -b .close-fds
%patch5 -p1 -b .weak-wgetch

# mdv patches
%patch50 -p1 -b .nodebug
%patch51 -p1 -b .docfix
%patch52 -p1 -b .do_not_build_it_twice
%patch53 -p0 -b .format_not_a_string_literal_and_no_format_arguments

# file is missing, copy in from the rpm package
cp -p %{_prefix}/lib/rpm/mkinstalldirs .

cp %{SOURCE1} gpm.init
cp %{SOURCE2} inputattach.c

%build
%serverbuild

CFLAGS="$CFLAGS -D_GNU_SOURCE -DPIC -fPIC" \
%configure2_5x %{?_without_curses}
make

gcc $CFLAGS -o inputattach inputattach.c

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}
install -d %{buildroot}%{_initrddir}  
install -d %{buildroot}/%{_lib}
install -d %{buildroot}%{_datadir}/emacs/site-lisp

PATH=/sbin:$PATH:%{_sbindir}:$PATH

%makeinstall

install -m0644 doc/gpm-root.1 %{buildroot}%{_mandir}/man1
install -m0644 conf/gpm-root.conf %{buildroot}%{_sysconfdir}
#install -m0755 src/hltest %{buildroot}%{_bindir}
install -m0755 inputattach %{buildroot}/%{_sbindir}

ln -sf /%{_lib}/libgpm.so.%{LIBVER} %{buildroot}%{_libdir}/libgpm.so
ln -sf libgpm.so.%{LIBVER} %{buildroot}/%{_lib}/libgpm.so.%{LIBMAJ}
mv %{buildroot}%{_libdir}/libgpm.so.* %{buildroot}/%{_lib}

install -m0755 gpm.init %{buildroot}%{_initrddir}/gpm

perl -pi -e "s|/etc/rc.d/init.d|%{_initrddir}|" %{buildroot}%{_initrddir}/*

# cleanup
rm -rf %{buildroot}%{_datadir}/emacs/site-lisp

%post
%_post_service gpm
if [ -x "/sbin/install-info" ]; then
%_install_info %{name}.info
fi

# handle init sequence change
if [ -f /etc/rc5.d/S85gpm ]; then
	/sbin/chkconfig --add gpm
fi

%preun
%_preun_service gpm
%_remove_install_info %{name}.info

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/gpm-root.conf
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

%files -n %{libname}
%defattr(-,root,root)
%attr(0755,root,root) /%{_lib}/libgpm.so.%{LIBMAJ}*

%files -n %{develname}
%defattr(-,root,root)
%{_libdir}/libgpm.a
%{_includedir}/gpm.h
%{_libdir}/libgpm.so
