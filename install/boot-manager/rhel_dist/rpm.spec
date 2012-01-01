%define name boot-manager
%define version vNNN
%define unmangled_version vVVV
%define unmangled_version vVVV
%define release vRRR

Summary: Blik Cloud boot manager
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
Requires: pyyaml
Requires: pexpect
Requires: ntp
Requires: dhcp
Requires: bind
Requires: tftp-hpa
Requires: syslinux
Requires: syslog-ng
Requires: postgresql-server-9.0
Requires: psycopg
Requires: glusterfs

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
mkdir -p $RPM_BUILD_ROOT/etc/dhcp/
mkdir -p $RPM_BUILD_ROOT/etc/bind/pri
mkdir -p $RPM_BUILD_ROOT/etc/glusterfs/
mkdir -p $RPM_BUILD_ROOT/etc/syslog-ng/

cp -pv config/dhcpd.conf $RPM_BUILD_ROOT/etc/dhcp/dhcpd.conf
cp -pv config/named.conf $RPM_BUILD_ROOT/etc/bind/named.conf
cp -pv config/blik.zone $RPM_BUILD_ROOT/etc/bind/pri/blik.zone
cp -pv config/192.168.87.zone $RPM_BUILD_ROOT/etc/bind/pri/192.168.87.zone

cp -pv init_scripts/boot-event-listener $RPM_BUILD_ROOT/etc/init.d/boot-event-listener
cp -pv config/postgresql-9.0.confd  $RPM_BUILD_ROOT/etc/conf.d/postgresql-9.0
cp -pv config/in.tftpd  $RPM_BUILD_ROOT/etc/conf.d/in.tftpd
cp -pv config/ntp.conf  $RPM_BUILD_ROOT/etc/ntp.conf
cp -pv config/resolv.conf.head  $RPM_BUILD_ROOT/etc/resolv.conf.head
cp -pv config/glusterfsd.vol  $RPM_BUILD_ROOT/etc/glusterfs/glusterfsd.vol
cp -pv config/glusterfs.vol  $RPM_BUILD_ROOT/etc/glusterfs/glusterfs.vol
cp -pv config/farnsworth-syslog-ng.conf  $RPM_BUILD_ROOT/etc/syslog-ng/syslog-ng.conf

%post
#!/bin/bash 
echo 'FIXME: emerge postgresql-server --config || die'
#	if [ ! -d "/var/lib/postgresql/9.0/data" ] ; then
#        emerge postgresql-server --config || die
#	fi

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
%attr(555,root,root) /etc/dhcp/dhcpd.conf
%attr(555,root,root) /etc/bind/named.conf
%attr(555,root,root) /etc/bind/pri/blik.zone
%attr(555,root,root) /etc/bind/pri/192.168.87.zone
%attr(555,root,root) /etc/init.d/boot-event-listener
%attr(555,root,root) /etc/conf.d/postgresql-9.0
%attr(555,root,root) /etc/conf.d/in.tftpd
%attr(555,root,root) /etc/ntp.conf
%attr(555,root,root) /etc/resolv.conf.head
%attr(555,root,root) /etc/glusterfs/glusterfsd.vol
%attr(555,root,root) /etc/glusterfs/glusterfs.vol
%attr(555,root,root) /etc/syslog-ng/syslog-ng.conf

