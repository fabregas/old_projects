%define name blik-utils
%define version vNNN
%define unmangled_version vVVV
%define unmangled_version vVVV
%define release vRRR

Summary: Blik utilities for BlikCloud system
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar
License: GPLv3
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Konstantin Andrusenko <blikproject@gmail.com>

%description
UNKNOWN

%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install \
        -O1 \
        --prefix=/opt/blik \
        --install-lib=/opt/blik/python \
        --install-scripts=/opt/blik/bin \
        --single-version-externally-managed \
        --root=$RPM_BUILD_ROOT \
        --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
