# Copyright 1999-2011 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI=3
PYTHON_DEPEND="2"

inherit distutils

DESCRIPTION="Blik Cloud Manager Plugins"
HOMEPAGE=""
SRC_URI="ftp://blik-mirror/distfiles/${PF}.tar"

LICENSE="GPL-3"
SLOT="0"
KEYWORDS="amd64 x86"
IUSE=""

DEPEND="blik-products/nodes-manager"

RDEPEND="${DEPEND}"

src_compile() {

}

src_install() {
	for spec in clusters_spec/*.yaml
	do
		cluster-type-installer $spec
	done

	for spec in nodes_spec/*.yaml
	do
		node-type-installer $spec
	done

	for spec in operations_spec/*.yaml
	do
		operations-installer $spec
	done

	plugin-installer --operations --management nodes_manager_plugins/
	plugin-installer --console console_ext/
}

pkg_postinst() {

}

