%bcond_without	ncurses
%bcond_without	uclibc

# this defines the library version that this package builds.
%define	major	2
%define	libver	%{major}.1.0
%define	libname	%mklibname %{name} %{major}
%define	devname	%mklibname %{name} -d

Summary:	A mouse server for the Linux console
Name:		gpm
Version:	1.20.7
Release:	1
License:	GPLv2+
Group:		System/Servers
URL:		http://www.nico.schottelius.org/software/gpm/
Source0:	http://www.nico.schottelius.org/software/gpm/archives/%{name}-%{version}.tar.lzma
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
Patch54:       gpm-1.20.7-fix-out-of-source-build.patch

BuildRequires:	byacc
%if %{with ncurses}
BuildRequires:	ncurses-devel
%endif
%if %{with uclibc}
BuildRequires:	uClibc-devel >= 0.9.33.2-3
%endif
#BuildRequires:	texinfo autoconf2.1
BuildRequires:	autoconf
Requires(post):	systemd-units, chkconfig, rpm-helper
Requires(preun): systemd-units, chkconfig, rpm-helper
Requires(postun):systemd-units

%description
Gpm provides mouse support to text-based Linux applications like the
emacs editor, the Midnight Commander file management system, and other
programs.  Gpm also provides console cut-and-paste operations using
the mouse and includes a program to allow pop-up menus to appear at
the click of a mouse button.

Gpm should be installed if you intend to use a mouse with your
MandrivaLinux system.

#--------------------------------------------------------------------
%package -n	%{libname}
Summary:	Libraries and header files for developing mouse driven programs
Group:		System/Libraries

%description -n	%{libname}
Library used by the gpm program.

Install %{libname}dev if you need to develop text-mode programs which 
will use the mouse. You'll also need to install the gpm package.

#--------------------------------------------------------------------
%package -n	%{devname}
Summary:	Libraries and header files for developing mouse driven programs
Group:		Development/C
Requires:	%{libname} = %{version}
Provides:	libgpm-devel
Obsoletes:	gpm-devel < %{version}-%{release}
Provides:	gpm-devel = %{version}-%{release}
Obsoletes:	%{mklibname %{name} 1 -d} < %{version}-%{release}
Provides:	%{mklibname %{name} 1 -d} = %{version}-%{release}

%description -n	%{devname}
The %{devname} package contains the libraries and header files needed
for development of mouse driven programs.  This package allows you to
develop text-mode programs which use the mouse.

Install %{devname} if you need to develop text-mode programs which
will use the mouse. You'll also need to install the gpm package.

#--------------------------------------------------------------------
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

cp %{SOURCE1} gpm.init
cp %{SOURCE2} inputattach.c

./autogen.sh

%build
CFLAGS="%{optflags} -D_GNU_SOURCE -DPIC -fPIC" \
%configure2_5x	\
%if !%{with ncurses}
		--without-curses
%endif

make

gcc %{optflags} %{ldflags} -o inputattach inputattach.c

%if %{with uclibc}
mkdir -p uclibc
pushd uclibc
CONFIGURE_TOP=.. \
CC="%{uclibc_cc}" \
CFLAGS="%{uclibc_cflags} -D_GNU_SOURCE -DPIC -fPIC" \
LDFLAGS="%{ldflags} -Wl,-O2 -flto" \
%configure2_5x	--prefix=%{uclibc_root} \
		--libdir=%{uclibc_root}%{_libdir}
%make -C src/ lib/libgpm.a 
popd
%endif

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

ln -sf /%{_lib}/libgpm.so.%{libver} %{buildroot}%{_libdir}/libgpm.so
ln -sf libgpm.so.%{libver} %{buildroot}/%{_lib}/libgpm.so.%{major}
mv %{buildroot}%{_libdir}/libgpm.so.* %{buildroot}/%{_lib}
chmod 755 %{buildroot}/%{_lib}/libgpm.so.%{libver}

install -m0755 gpm.init %{buildroot}%{_initrddir}/gpm
perl -pi -e "s|/etc/rc.d/init.d|%{_initrddir}|" %{buildroot}%{_initrddir}/*

# Zé: Systemd
install -d -m755 %{buildroot}%{_sysconfdir}/systemd/system/
install -m644 %{S:3} %{buildroot}%{_sysconfdir}/systemd/system/

%if %{with uclibc}
install -m644 uclibc/src/lib/libgpm.a -D %{buildroot}%{uclibc_root}%{_libdir}/libgpm.a
%endif

# cleanup
rm -rf %{buildroot}%{_datadir}/emacs/site-lisp

%post
%_post_service gpm
# Zé: install; upgrade
if [ "$1" -ge 1 ]; then
    /bin/systemctl enable gpm.service
fi
# handle init sequence change
if [ -f /etc/rc5.d/S85gpm ]; then
    /sbin/chkconfig --add gpm
fi

%preun
%_preun_service gpm
# Zé: upgrade, not removal
if [ "$1" -eq 1 ] ; then
    /bin/systemctl try-restart gpm.service
fi

%postun
# Zé: removal
if [ "$1" -eq 0 ]; then
    /bin/systemctl --no-reload gpm.service
    /bin/systemctl stop gpm.service
fi

%files
%config(noreplace) %{_sysconfdir}/gpm-root.conf
%{_sysconfdir}/systemd/system/gpm.service
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
%attr(0755,root,root) /%{_lib}/libgpm.so.%{major}*

%files -n %{devname}
%{_libdir}/libgpm.a
%if %{with uclibc}
%{uclibc_root}%{_libdir}/libgpm.a
%endif
%{_includedir}/gpm.h
%{_libdir}/libgpm.so
