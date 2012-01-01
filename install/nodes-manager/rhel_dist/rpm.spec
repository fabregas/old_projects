%define name nodes-manager
%define version vNNN
%define unmangled_version vVVV
%define unmangled_version vVVV
%define release vRRR

Summary: Nodes Manager module of BlikCloud management system
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
Requires: blik-utils
Requires: boot-manager
Requires: dbus-python
Requires: django
Requires: cherrypy

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


mkdir -p $RPM_BUILD_ROOT/etc/init.d/
mkdir -p $RPM_BUILD_ROOT/etc/dbus-1/system.d/

cp -pv init_scripts/nodes-manager $RPM_BUILD_ROOT/etc/init.d/nodes-manager
cp -pv init_scripts/cloud-manager-console $RPM_BUILD_ROOT/etc/init.d/cloud-manager-console
cp -pv config/com.blik.nodesManager.conf $RPM_BUILD_ROOT/etc/dbus-1/system.d/com.blik.nodesManager.conf


%post
#!/bin/bash 
echo 'FIXME: rc-update add nodes-manager default'
echo 'FIXME: rc-update add cloud-manager-console default'

#FIXME: python dictionaries.py || exit 1

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
%attr(555,root,root) /etc/init.d/nodes-manager
%attr(555,root,root) /etc/init.d/cloud-manager-console
%attr(555,root,root) /etc/dbus-1/system.d/com.blik.nodesManager.conf
