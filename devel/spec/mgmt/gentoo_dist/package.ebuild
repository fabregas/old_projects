# Copyright 1999-2011 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI=3
PYTHON_DEPEND="2"

inherit eutils

DESCRIPTION="Blik Cloud Manager Plugins"
HOMEPAGE=""
SRC_URI="ftp://blik-mirror/distfiles/${PF}.tar"

LICENSE="GPL-3"
SLOT="0"
KEYWORDS="amd64 x86"
IUSE=""

DEPEND="blik-products/nodes-manager"

RDEPEND="${DEPEND}"

src_install() {
	for spec in clusters_spec/*.yaml
	do
		/opt/blik/bin/cluster-type-installer $spec || die "cluster type installation failed"
	done

	for spec in nodes_spec/*.yaml
	do
		/opt/blik/bin/node-type-installer $spec || die "node type installation failed"
	done

	for spec in operations_spec/*.yaml
	do
		/opt/blik/bin/operations-installer $spec || die "operations installation failed"
	done

	/opt/blik/bin/plugin-installer --operations --management
	nodes_manager_plugins/ || die "installation of nodes manager plugins failed"
	/opt/blik/bin/plugin-installer --console console_ext/ || die "installation of blik console failed"
}


