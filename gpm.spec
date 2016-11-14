%bcond_without	ncurses

# this defines the library version that this package builds.
%define	major 2
%define	libname %mklibname %{name} %{major}
%define	devname %mklibname %{name} -d
%define gitrev	g1fd1941
# do NOT upgrade to 1.99.7 as it's development releases not maintained
# since 2010..
%define	ver	1.20.7

Summary:	A mouse server for the Linux console
Name:		gpm
Version:	%{ver}~%{gitrev}
Epoch:		1
Release:	1
License:	GPLv2+
Group:		System/Servers
Url:		http://www.nico.schottelius.org/software/gpm/
Source0:	http://www.nico.schottelius.org/software/gpm/archives/%{name}-%{ver}-27-%{gitrev}.tar.xz
Source2:	inputattach.c
Source3:	gpm.service
# fedora patches (gpm-1.20.5-1.fc10.src.rpm)
Patch1:		gpm-1.20.1-multilib.patch
Patch2:		gpm-1.20.7-27-g1fd1941-lib-silent.patch
Patch4:		gpm-1.20.7-27-g1fd1941-close-fds.patch
Patch5:		gpm-1.20.7-27-g1fd1941-weak-wgetch.patch
# mdv patches
Patch51:	gpm-1.20.0-docfix.patch
Patch52:	gpm-1.20.7-27-g1fd1941-do_not_build_it_twice.diff
# from debian
Patch58:	070_struct_ucred.diff

BuildRequires:	byacc
BuildRequires:	texinfo
%if %{with ncurses}
BuildRequires:	pkgconfig(ncursesw)
%endif

%description
Gpm provides mouse support to text-based Linux applications like the
emacs editor, the Midnight Commander file management system, and other
programs.  Gpm also provides console cut-and-paste operations using
the mouse and includes a program to allow pop-up menus to appear at
the click of a mouse button.

Gpm should be installed if you intend to use a mouse with your
OpenMandriva Lx system.

%package -n	%{libname}
Summary:	Libraries and header files for developing mouse driven programs
Group:		System/Libraries

%description -n	%{libname}
Library used by the gpm program.

Install %{libname}dev if you need to develop text-mode programs which 
will use the mouse. You'll also need to install the gpm package.

%package -n	%{devname}
Summary:	Libraries and header files for developing mouse driven programs
Group:		Development/C
Requires:	%{libname} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}

%description -n	%{devname}
The %{devname} package contains the libraries and header files needed
for development of mouse driven programs.  This package allows you to
develop text-mode programs which use the mouse.

Install %{devname} if you need to develop text-mode programs which
will use the mouse. You'll also need to install the gpm package.

%prep
%setup -q -n %{name}-%{ver}-27-%{gitrev}
%apply_patches

cp %{SOURCE2} inputattach.c

./autogen.sh

%build
# Heavy use of nested functions
export CC=gcc
export CXX=g++

%configure \
	--enable-static \
%if !%{with ncurses}
	--without-curses
%endif

%make

%{__cc} %{optflags} %{ldflags} -o inputattach inputattach.c

%install
%makeinstall_std

install -m644 conf/gpm-root.conf -D %{buildroot}%{_sysconfdir}/gpm-root.conf
install -m755 inputattach -D %{buildroot}%{_sbindir}/inputattach

mkdir -p %{buildroot}/%{_lib}
mv %{buildroot}%{_libdir}/libgpm.so.%{major}* %{buildroot}/%{_lib}
ln -srf %{buildroot}/%{_lib}/libgpm.so.%{major}.*.* %{buildroot}%{_libdir}/libgpm.so

# systemd
install -m644 %{SOURCE3} -D %{buildroot}%{_unitdir}/gpm.service

rm -f %{buildroot}%{uclibc_root}%{_libdir}/*.a

%files
%config(noreplace) %{_sysconfdir}/gpm-root.conf
%{_unitdir}/gpm.service
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
/%{_lib}/libgpm.so.%{major}*

%files -n %{devname}
%{_libdir}/libgpm.a
%{_libdir}/libgpm.so
%{_includedir}/gpm.h
