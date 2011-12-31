# Copyright 1999-2011 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI=3
PYTHON_DEPEND="2"

inherit distutils

DESCRIPTION="Blik Cloud Manager Plugins for Node Agent"
HOMEPAGE=""
SRC_URI="ftp://blik-mirror/distfiles/${PF}.tar"

LICENSE="GPL-3"
SLOT="0"
KEYWORDS="amd64 x86"
IUSE=""

DEPEND="blik-products/node-agent"

RDEPEND="${DEPEND}"

src_compile() {

}

src_install() {
	plugin-installer --operations --agent node_agent_plugins/
}

pkg_postinst() {

}

