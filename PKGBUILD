# Maintainer: Ralf Stemmer <ralf.stemmer@gmx.net>
pkgname=musicdb
pkgver=8.0.0
pkgrel=1
epoch=
pkgdesc="A music manager with web-bases UI that focus on music"
arch=("any")
url="https://github.com/rstemmer/musicdb"
license=('GPL3')
groups=()
depends=("python>=3.8"
    "ffmpeg"
    "libshout"
    "gstreamer"
    "gst-plugins-base"
    "gst-plugins-base-libs"
    "gst-plugins-good"
    "gst-plugins-bad"
    "gst-plugins-bad-libs"
    "sqlite"
    "python-gobject"
    "python-autobahn"
    "python-systemd"
    "python-levenshtein"
    "python-mutagen"
    "python-fuzzywuzzy"
    "python-pillow"
    "python-tqdm"
)
makedepends=("python-setuptools" "python-build")
checkdepends=()
optdepends=("logrotate: for log file management"
    "apache: for serving the web front end"
    "icecast: for providing a performant and encrypted audio stream"
    )
provides=()
conflicts=()
replaces=()
backup=("etc/musicdb.ini"
    "etc/logrotate.d/musicdb"
    "etc/httpd/conf/extra/musicdb.conf"
    )
options=()
install=
changelog=
source=("$pkgname-$pkgver-src.tar.zst::file://$(pwd)/dist/$pkgname-$pkgver-src.tar.zst")
noextract=()
md5sums=("SKIP")
validpgpkeys=()

#prepare() {
#	cd "$pkgname-$pkgver"
#	patch -p1 -i "$srcdir/$pkgname-$pkgver.patch"
#}

build() {
    #ls > /tmp/mkpkg/ls.txt
    #pwd > /tmp/mkpkg/pwd.txt
    #echo $pkgdir > /tmp/mkpkg/echo.txt
	cd "$pkgname-$pkgver-src"
    python3 setup.py build
}

#check() {
#	cd "$pkgname-$pkgver"
#	make -k check
#}

package() {
	cd "$pkgname-$pkgver-src"
    # Back End
    python setup.py install --root="$pkgdir" --skip-build --optimize=1
    python -m compileall --invalidation-mode=checked-hash "$pkgdir"

    # Front End
    install -dm 755 "$pkgdir/usr/share/webapps/$pkgname"
    cp -r -a --no-preserve=ownership webui/* "$pkgdir/usr/share/webapps/$pkgname"

    # Shared Data
    install -dm 755 "$pkgdir/usr/share/$pkgname"
    cp -r -a --no-preserve=ownership share/*   "$pkgdir/usr/share/$pkgname"
    cp -r -a --no-preserve=ownership sql       "$pkgdir/usr/share/$pkgname"

    # MusicDB Configuration
    install -Dm 644 "share/musicdb.ini"        "$pkgdir/etc/musicdb.ini"

    # System Configuration
    install -Dm 644 "share/logrotate.conf"     "$pkgdir/etc/logrotate.d/$pkgname"
    install -Dm 644 "share/apache.conf"        "$pkgdir/etc/httpd/conf/extra/$pkgname.conf"
    install -Dm 644 "share/musicdb.service"    "$pkgdir/usr/lib/systemd/system/$pkgname.service"
    install -Dm 644 "share/sysusers.conf"      "$pkgdir/usr/lib/sysusers.d/$pkgname.conf"
    install -Dm 644 "share/tmpfiles.conf"      "$pkgdir/usr/lib/tmpfiles.d/$pkgname.conf"

    # Meta Data
    install -Dm 644 LICENSE "$pkgdir"/usr/share/licenses/$pkgname/LICENSE
}

# vim: nospell

