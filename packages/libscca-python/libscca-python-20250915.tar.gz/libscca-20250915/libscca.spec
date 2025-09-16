Name: libscca
Version: 20250915
Release: 1
Summary: Library to access the Windows Prefetch File (PF) format
Group: System Environment/Libraries
License: LGPL-3.0-or-later
Source: %{name}-%{version}.tar.gz
URL: https://github.com/libyal/libscca
               
BuildRequires: gcc               

%description -n libscca
Library to access the Windows Prefetch File (PF) format

%package -n libscca-static
Summary: Library to access the Windows Prefetch File (PF) format
Group: Development/Libraries
Requires: libscca = %{version}-%{release}

%description -n libscca-static
Static library version of libscca.

%package -n libscca-devel
Summary: Header files and libraries for developing applications for libscca
Group: Development/Libraries
Requires: libscca = %{version}-%{release}

%description -n libscca-devel
Header files and libraries for developing applications for libscca.

%package -n libscca-python3
Summary: Python 3 bindings for libscca
Group: System Environment/Libraries
Requires: libscca = %{version}-%{release} python3
BuildRequires: python3-devel python3-setuptools

%description -n libscca-python3
Python 3 bindings for libscca

%package -n libscca-tools
Summary: Several tools for reading Windows Prefetch Files (PF)
Group: Applications/System
Requires: libscca = %{version}-%{release}

%description -n libscca-tools
Several tools for reading Windows Prefetch Files (PF)

%prep
%setup -q

%build
%configure --prefix=/usr --libdir=%{_libdir} --mandir=%{_mandir} --enable-python
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
%make_install

%clean
rm -rf %{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files -n libscca
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/*.so.*

%files -n libscca-static
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/*.a

%files -n libscca-devel
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/*.so
%{_libdir}/pkgconfig/libscca.pc
%{_includedir}/*
%{_mandir}/man3/*

%files -n libscca-python3
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/python3*/site-packages/*.a
%{_libdir}/python3*/site-packages/*.so

%files -n libscca-tools
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_bindir}/*
%{_mandir}/man1/*

%changelog
* Mon Sep 15 2025 Joachim Metz <joachim.metz@gmail.com> 20250915-1
- Auto-generated

