# Maintainer: Dane Hobrecht <76x5l22l@anonaddy.me>

pkgname=shadowtube
pkgver=1.0
pkgrel=1
pkgdesc="A YouTube shadowban detection program."
arch=('any')
url="https://github.com/danehobrecht/shadowtube"
license=('GPL')
depends=('python' 'requests' 'pysocks' 'cssselect' 'lxml' 'stem' 'argparse')

source=("https://github.com/danehobrecht/shadowtube/releases/${pkgname}-${pkgver}.tar.gz")
sha256sums=('put_sha256sum_here')

package() {
	cd "$srcdir"
	install -Dm755 main.py "$pkgdir/usr/bin/shadowtube"
	install -Dm644 LICENSE.txt "$pkgdir/usr/share/licenses/$pkgname/LICENSE.txt"
	install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
	install -Dm644 settings.json "$pkgdir/etc/shadowtube/settings.json"
}