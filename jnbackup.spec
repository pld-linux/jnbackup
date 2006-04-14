Summary:	Jajcus' Net Backup - remote backup system
Summary(pl):	Jajcus' Net Backup - system zdalnych kopii zapasowych
Name:		jnbackup
Version:	0.6
Release:	2
License:	GPL
Vendor:		Jacek Konieczny <jajcus@pld.org.pl>
Group:		Applications/Archiving
Source0:	%{name}-%{version}.tar.gz
# Source0-md5:	aa21a7cad3e15e379c52be25d37ebabe
Source1:	%{name}.crontab
BuildRequires:	rpmbuild(macros) >= 1.202
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Jajcus' Net Backup - remote backup system.

%description -l pl
Jajcus' Net Backup - system zdalnych kopii zapasowych.

%package server
Summary:	Jajcus' Net Backup server - remote backup system - server
Summary(pl):	Jajcus' Net Backup - system zdalnych kopii zapasowych - serwer
Group:		Applications/Archiving
Requires(post):	/bin/hostname
Requires(post):	fileutils
Requires(post):	openssh
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	crondaemon
Requires:	openssh-clients
Requires:	time
Provides:	group(backups)
Provides:	user(backups)

%description server
Server of Jajcus' Net Backup - remote backup system.

%description server -l pl
Serwer Jajcus' Net Backup - systemu zdalnych kopii zapasowych.

%package client
Summary:	Jajcus' Net Backup server - remote backup system - client
Summary(pl):	Jajcus' Net Backup - system zdalnych kopii zapasowych - klient
Group:		Applications/Archiving
Requires(post):	grep
Requires(post):	sudo
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	awk
Requires:	openssh-server
Requires:	sudo
Requires:	tar
Provides:	group(backupc)
Provides:	user(backupc)

%description client
Client of Jajcus' Net Backup - remote backup system.

%description client -l pl
Klient Jajcus' Net Backup - systemu zdalnych kopii zapasowych.

%prep
%setup  -q

%build
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/cron.d

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

echo "# you should put your servers' public ssh key here" > $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/client/authorized_keys

install %{SOURCE1} $RPM_BUILD_ROOT/etc/cron.d/backups

%clean
rm -rf $RPM_BUILD_ROOT

%pre client
%groupadd -g 105 backupc
%useradd -g backupc -u 105 -c "JNBackup client" -d /var/lib/%{name}/client -s %{_bindir}/backupc backupc

%post client
if [ "$1" = 1 ]; then
	if ! grep -q "backupc" %{_sysconfdir}/sudoers; then
		echo 'backupc ALL=(ALL) NOPASSWD: %{_datadir}/jnbackup/client/backupc-slave' >> %{_sysconfdir}/sudoers
		echo "Notice: %{_sysconfdir}/sudoers file changed"
	fi
fi

%postun client
if [ "$1" = "0" ]; then
	%userremove backupc
	%groupremove backupc
fi

%pre server
%groupadd -g 113 backups
%useradd -g backups -u 113 -c "JNBackup client" -d /var/lib/%{name}/server backups

%post server
if [ ! -f %{_sysconfdir}/jnbackup/server/identity ]; then
	ssh-keygen -t rsa1 -N "" -C "backups@`hostname`" -f %{_sysconfdir}/jnbackup/server/identity
	chown backups:backups %{_sysconfdir}/jnbackup/server/identity*
	chmod 600 %{_sysconfdir}/jnbackup/server/identity
fi

%postun server
if [ "$1" = "0" ]; then
	%userremove backups
	%groupremove backups
fi

%files server
%defattr(644,root,root,755)
%doc README ChangeLog
%attr(755,root,root) %{_bindir}/backups
%{_datadir}/%{name}/server
%attr(750,backups,backups) %dir /var/lib/%{name}/server
%attr(750,backups,backups) %dir /var/lib/%{name}/server/.ssh
%attr(750,backups,backups) %dir /var/lib/%{name}/server/backups
/var/lib/%{name}/server/.ssh/*
%config(noreplace) %verify(not md5 mtime size) %attr(640,root,root) /etc/cron.d/backups
%dir %{_sysconfdir}/%{name}/server
%dir %{_sysconfdir}/%{name}/server/profiles
%config(noreplace) %verify(not md5 mtime size) %attr(640,root,backups) %{_sysconfdir}/%{name}/server/config
%config(noreplace) %verify(not md5 mtime size) %attr(640,root,backups) %{_sysconfdir}/%{name}/server/profiles/*
# common dirs?
%dir %{_datadir}/%{name}
%dir /var/lib/%{name}
%dir %{_sysconfdir}/%{name}

%files client
%defattr(644,root,root,755)
%doc README ChangeLog
%attr(755,root,root) %{_bindir}/backupc
%dir %{_datadir}/%{name}/client
%{_datadir}/%{name}/client/*.tool
%{_datadir}/%{name}/client/*.sh
%{_datadir}/%{name}/client/functions
%attr(755,root,root) %{_datadir}/%{name}/client/backupc-slave
%attr(750,backupc,backupc) %dir /var/lib/%{name}/client
%attr(750,backupc,backupc) %dir /var/lib/%{name}/client/.ssh
/var/lib/%{name}/client/.ssh/*
%dir %{_sysconfdir}/%{name}/client
%dir %{_sysconfdir}/%{name}/client/backups
%config(noreplace) %verify(not md5 mtime size) %attr(640,root,backupc) %{_sysconfdir}/%{name}/client/authorized_keys
%config(noreplace) %verify(not md5 mtime size) %attr(640,root,backupc) %{_sysconfdir}/%{name}/client/backups/*
# common dirs?
%dir %{_datadir}/%{name}
%dir /var/lib/%{name}
%dir %{_sysconfdir}/%{name}
