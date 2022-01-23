Name:       musicdb
Version:    8.0.0
Release:    1%{?dist}
Summary:    A music manager with web-bases UI that focus on music
Vendor:     Ralf Stemmer <ralf.stemmer@gmx.net>

License:    GPLv3
URL:        https://github.com/rstemmer/%{name}
Source0:    %{name}-%{version}-src.tar.zst
Source1:    musicdb.sysusers

BuildArch:  noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-build
BuildRequires:  /usr/bin/pathfix.py
BuildRequires:  systemd-rpm-macros

Requires: python3 >= 3.9
Requires: ffmpeg
Requires: libshout
Requires: gstreamer1
Requires: gstreamer1-plugins-base
Requires: gstreamer1-plugins-bad-free
Requires: gstreamer1-plugins-good
Requires: sqlite
Requires: openssl
Requires: python3-gobject
Requires: python3-autobahn
Requires: python3-systemd
Requires: python3-Levenshtein
Requires: python3-mutagen
Requires: python3-fuzzywuzzy
Requires: python3-pillow
Requires: python3-tqdm

Recommends: logrotate
Recommends: httpd
Recommends: icecast


%description
MusicDB is a music manager with focus on remote access to your music collection using a web-based user interface. It allows you to manage an audio stream based on a song-queue. The WebUI is focusing on being a presentation of your music rather than being a database front-end.


%prep
%setup -q -n %{name}-%{version}-src


%build
python3 setup.py build


%install
# Back End
python setup.py install --root="%{buildroot}" --skip-build --optimize=1 --record=INSTALLED_FILES
python -m compileall --invalidation-mode=checked-hash "%{buildroot}"

# See https://fedoraproject.org/wiki/Changes/Make_ambiguous_python_shebangs_error
pathfix.py -pni "%{__python3} %{py3_shbang_opts}" %{buildroot}%{python3_sitelib} %{buildroot}%{_bindir}/*

# Front End
install -dm 755 "%{buildroot}%{_datadir}/webapps/%{name}"
cp -r -a --no-preserve=ownership webui/* "%{buildroot}%{_datadir}/webapps/%{name}"

# Shared Data
install -dm 755 "%{buildroot}%{_datadir}/%{name}"
cp -r -a --no-preserve=ownership share/*   "%{buildroot}%{_datadir}/%{name}"
cp -r -a --no-preserve=ownership sql       "%{buildroot}%{_datadir}/%{name}"

# MusicDB Configuration
install -Dm 644 "share/musicdb.ini"        "%{buildroot}%{_sysconfdir}/musicdb.ini"

# System Configuration
install -Dm 644 "share/logrotate.conf"     "%{buildroot}%{_sysconfdir}/logrotate.d/%{name}"
install -Dm 644 "share/apache.conf"        "%{buildroot}%{_sysconfdir}/httpd/conf/%{name}.conf"
install -Dm 644 "share/musicdb.service"    "%{buildroot}%{_unitdir}/%{name}.service"
install -Dm 644 "share/tmpfiles.conf"      "%{buildroot}%{_tmpfilesdir}/%{name}.conf"

install -p -Dm 0644 %{SOURCE1} %{buildroot}%{_sysusersdir}/%{name}.conf

# Meta Data
install -Dm 644 LICENSE "%{buildroot}%{_datadir}/licenses/%{name}/LICENSE"


%pre
%sysusers_create_compat %{SOURCE1}

%post
semanage fcontext -a -t httpd_sys_content_t '%{_datadir}/webapps/%{name}(/.*)?' 2>/dev/null
restorecon -R %{_datadir}/webapps/%{name}

%files -f INSTALLED_FILES
%license %{_datadir}/licenses/%{name}/LICENSE

%config %{_sysconfdir}/musicdb.ini
%config %{_sysconfdir}/logrotate.d/%{name}
%config %{_sysconfdir}/httpd/conf/%{name}.conf
%config %{_unitdir}/%{name}.service

%dir %{python3_sitelib}/%{name}
%dir %{_datadir}/%{name}
%dir %{_datadir}/webapps/%{name}

%{_datadir}/%{name}/*
%{_datadir}/webapps/%{name}/*
%{_sysusersdir}/%{name}.conf
%{_tmpfilesdir}/%{name}.conf


%changelog
* Sun Nov 07 2021 Ralf Stemmer <ralf.stemmer@gmx.net>
- MusicDB 8.0.0 Release


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nospell

