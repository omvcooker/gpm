%define version	1.20.1
%define release %mkrel 15
%define url 	ftp://arcana.linux.it/pub/gpm/

# Allow first build without ncurses support
%define build_curses %{?_without_curses:0}%{!?_without_curses:1}

# this defines the library version that this package builds.
%define LIBMAJ 1
%define LIBVER %{LIBMAJ}.19.0
%define libname %mklibname %name %LIBMAJ
%define libnamedev %{libname}-devel

Summary:	A mouse server for the Linux console
Name:		gpm
Version:	%{version}
Release:	%{release}
License:	GPL
Group:		System/Servers
BuildRequires:	byacc
BuildRequires:	emacs-bin
%if %{build_curses}
BuildRequires:	ncurses-devel
%endif
BuildRequires:	texinfo autoconf2.1

URL:		%{url}
Source:		%{url}/gpm-%{version}.tar.bz2
Source1:	gpm.init
Patch0:		gpm-1.20.0-nodebug.patch
Patch1:		gpm-1.20.1-no-dumb-error-messages.patch
Patch2:		gpm-1.20.0-docfix.patch
Patch3:		gpm-1.20.1-libm.patch
Patch4:		gpm-1.20.1-weak-wgetch.patch
Patch5: 	gpm-1.19.6-secenhance.patch
Patch6: 	gpm-1.20.0-limits.patch
Patch7:		gpm-1.20.1-serialconsole.patch
Patch8:		gpm-1.20.1-basename.patch
Patch9:		gpm-1.20.1-consolename.patch
Patch10:	gpm-1.20.1-deps.patch

Requires(post): /sbin/chkconfig, info-install, rpm-helper
Requires(preun): /sbin/chkconfig, info-install, rpm-helper

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Gpm provides mouse support to text-based Linux applications like the
emacs editor, the Midnight Commander file management system, and other
programs.  Gpm also provides console cut-and-paste operations using
the mouse and includes a program to allow pop-up menus to appear at
the click of a mouse button.

Gpm should be installed if you intend to use a mouse with your
MandrivaLinux system.

%package -n %libnamedev
Requires:	%libname = %{version}
Summary:	Libraries and header files for developing mouse driven programs
Group:		Development/C
Provides:	gpm-devel libgpm-devel
Obsoletes:	gpm-devel
URL:		%{url}

%description -n %libnamedev
The %libnamedev package contains the libraries and header files needed
for development of mouse driven programs.  This package allows you to
develop text-mode programs which use the mouse.

Install %libnamedev if you need to develop text-mode programs which will use
the mouse.  You'll also need to install the gpm package.

%package -n %libname
Summary:	Libraries and header files for developing mouse driven programs
Group:		System/Libraries
URL:		%{url}

%description -n %libname
Library used by the gpm program.

Install %libnamedev if you need to develop text-mode programs which will use
the mouse.  You'll also need to install the gpm package.

%prep
%setup -q
%patch0 -p1 -b .nodebug
%patch1 -p1 -b .no-dumb-error-messages
%patch2 -p1 -b .docfix
%patch3 -p1 -b .libm
%patch4 -p1 -b .weak-wgetch
%patch5 -p1 -b .secenhance
%patch6 -p1 -b .limits
%patch7 -p1 -b .serial
%patch8 -p1 -b .basename
%patch9 -p1 -b .consolename
%patch10 -p1 -b .deps

# handle patch1 mods
autoconf

# file is missing, copy in from the rpm package
cp -p %{_prefix}/lib/rpm/mkinstalldirs .

# emacs stuff needs to be in two places at once...
cp -p contrib/emacs/*.el contrib

cp %{SOURCE1} gpm.init

%build
%serverbuild
CFLAGS="-D_GNU_SOURCE $RPM_OPT_FLAGS -DPIC -fPIC" \
lispdir=$RPM_BUILD_ROOT%{_datadir}/emacs/site-lisp \
%configure %{?_without_curses}
%make

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_sysconfdir}
mkdir -p %{buildroot}/%{_lib}

PATH=/sbin:$PATH:%{_sbindir}:$PATH

%makeinstall lispdir=%{buildroot}%{_datadir}/emacs/site-lisp

install -m644 doc/gpm-root.1 %{buildroot}%{_mandir}/man1
install -m644 conf/gpm-root.conf %{buildroot}%{_sysconfdir}
#install -s -m755 src/hltest %{buildroot}%{_bindir}
install -d 755 %{buildroot}%{_datadir}/emacs/site-lisp
#install -m644 contrib/t-mouse.el* %{buildroot}%{_datadir}/emacs/site-lisp

ln -sf ../../%{_lib}/libgpm.so.%{LIBVER} %{buildroot}%{_libdir}/libgpm.so
ln -sf libgpm.so.%{LIBVER} %{buildroot}/%{_lib}/libgpm.so.%{LIBMAJ}
mv %{buildroot}%{_libdir}/libgpm.so.* %{buildroot}/%{_lib}

mkdir -p %{buildroot}%{_initrddir}  
install -m0755 gpm.init %{buildroot}%{_initrddir}/gpm

perl -pi -e "s|/etc/rc.d/init.d|%{_initrddir}|" $RPM_BUILD_ROOT%{_initrddir}/*

%clean
rm -rf %{buildroot}

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

%post -n %libname -p /sbin/ldconfig

%postun -n %libname -p /sbin/ldconfig

%files
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/gpm-root.conf
%{_initrddir}/gpm
%{_bindir}/mev
%{_bindir}/gpm-root
%{_bindir}/hltest
%{_bindir}/mouse-test
%{_bindir}/disable-paste
%{_sbindir}/gpm
%{_datadir}/emacs/site-lisp/t-mouse.el
%{_datadir}/emacs/site-lisp/t-mouse.elc
%{_infodir}/gpm.info*
%{_mandir}/man1/mev.1*
%{_mandir}/man1/mouse-test.1*
%{_mandir}/man1/gpm-root.1*
%{_mandir}/man7/gpm-types.7*
%{_mandir}/man8/gpm.8*

%files -n %libname
%defattr(-,root,root)
/%{_lib}/libgpm.so.*

%files -n %libnamedev
%defattr(-,root,root)
%{_libdir}/libgpm.a
%{_includedir}/gpm.h
%{_libdir}/libgpm.so


