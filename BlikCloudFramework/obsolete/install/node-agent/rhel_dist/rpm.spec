%define name node-agent
%define version vNNN
%define unmangled_version vVVV
%define unmangled_version vVVV
%define release vRRR

Summary: Node Agent for BlikCloud management system
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
Requires: syslog-ng
Requires: dbus-python
Requires: dmidecode

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
mkdir -p $RPM_BUILD_ROOT/etc/conf.d/
mkdir -p $RPM_BUILD_ROOT/etc/dbus-1/system.d/
mkdir -p $RPM_BUILD_ROOT/etc/syslog-ng/

cp -pv init_scripts/node-agent $RPM_BUILD_ROOT/etc/init.d/node-agent
cp -pv config/com.blik.nodeAgent.conf $RPM_BUILD_ROOT/etc/dbus-1/system.d/com.blik.nodeAgent.conf
cp -pv config/node-syslog-ng.conf $RPM_BUILD_ROOT/etc/syslog-ng/syslog-ng.conf
cp -pv config/ntp-client $RPM_BUILD_ROOT/etc/conf.d/ntp-client

%post
#!/bin/bash 
echo "FIXME: rc-update add node-agent default"

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
%attr(555,root,root) /etc/init.d/node-agent
%attr(555,root,root) /etc/dbus-1/system.d/com.blik.nodeAgent.conf
%attr(555,root,root) /etc/syslog-ng/syslog-ng.conf
%attr(555,root,root) /etc/conf.d/ntp-client
