Summary:	Jajcus' Net Backup - remote backup system
Summary(pl):	Jajcus' Net Backup - system zdalnych backup'ów
Name:		jnbackup
Version:	0.1
Release:	1
License:	GPL
Buildarch:  	noarch
Group:		Applications/Archiving
Group(de):	Applikationen/Archivierung
Group(pl):	Aplikacje/Archiwizacja
Vendor:		Jacek Konieczny <jajcus@pld.org.pl>
Source0:	%{name}-%{version}.tar.gz
Source1:	%{name}.crontab
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Jajcus' Net Backup - remote backup system.

%description -l pl
Jajcys' Net Backup - system zdalnych backup'ów.

%package server
Summary:	Jajcus' Net Backup server - remote backup system - server
Summary(pl):	Jajcus' Net Backup - system zdalnych backup'ów - serwer
Group:		Applications/Archiving
Group(de):	Applikationen/Archivierung
Group(pl):	Aplikacje/Archiwizacja
Prereq:		openssh
Requires:	openssh-clients
Requires:	time

%description server
Server of Jajcus' Net Backup - remote backup system.

%description -l pl server
Serwer Jajcys' Net Backup - system zdalnych backup'ów.

%package client
Summary:	Jajcus' Net Backup server - remote backup system - client 
Summary(pl):	Jajcus' Net Backup - system zdalnych backup'ów - klient
Group:		Applications/Archiving
Group(de):	Applikationen/Archivierung
Group(pl):	Aplikacje/Archiwizacja
Requires:	openssh-server
Requires:	awk
Requires:	sudo
Requires:	tar
Prereq:		sudo

%description client
Client of Jajcus' Net Backup - remote backup system.

%description -l pl client
Klient Jajcus' Net Backup - system zdalnych backup'ów.

%prep
%setup  -q

%build
%configure 
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install DESTDIR=$RPM_BUILD_ROOT

echo "# you should put your servers' public ssh key here" > $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/client/authorized_keys

install -d $RPM_BUILD_ROOT/etc/cron.d/
install %{SOURCE1} $RPM_BUILD_ROOT/etc/cron.d/backups

gzip -9nf README ChangeLog 

%pre client
if [ "$1" = 1 ]; then
	getgid backupc >/dev/null 2>&1 || %{_sbindir}/groupadd -r -g 42 -f backupc
	id -u backupc >/dev/null 2>&1 || %{_sbindir}/useradd -r -g backupc -u 42 \
		-c "JNBackup client" -d /var/lib/%{name}/client -s %{_bindir}/backupc backupc
fi

%post client
echo 'backupc ALL=(ALL) NOPASSWD: %{_datadir}/jnbackup/client/backupc-slave' >> %{_sysconfdir}/sudoers
echo "Notice: %{_sysconfdir}/sudoers file changed"

%pre server
if [ "$1" = 1 ]; then
	getgid backups >/dev/null 2>&1 || %{_sbindir}/groupadd -r -g 41 -f backups
	id -u backups >/dev/null 2>&1 || %{_sbindir}/useradd -r -g backups -u 41 \
		-c "JNBackup client" -d /var/lib/%{name}/server backups
fi

%post server
if [ ! -f %{_sysconfdir}/jnbackup/server/identity ] ; then
ssh-keygen -N "" -C "backups@`hostname`" -f %{_sysconfdir}/jnbackup/server/identity
chown backups.backups %{_sysconfdir}/jnbackup/server/identity*
chmod 600 %{_sysconfdir}/jnbackup/server/identity
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files server
%defattr(644,root,root,755)
%doc *.gz
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/backups
%{_datadir}/%{name}/server
%attr(750,backups,backups) %dir /var/lib/%{name}/server
%attr(750,backups,backups) %dir /var/lib/%{name}/server/.ssh
%attr(750,backups,backups) %dir /var/lib/%{name}/server/backups
/var/lib/%{name}/server/.ssh/*
%config(noreplace) %verify(not md5 size mtime) %attr(640,root,root) /etc/cron.d/backups
%dir %{_sysconfdir}/%{name}/server
%dir %{_sysconfdir}/%{name}/server/profiles
%config(noreplace) %verify(not md5 size mtime) %attr(640,root,backups) %{_sysconfdir}/%{name}/server/config
%config(noreplace) %verify(not md5 size mtime) %attr(640,root,backups) %{_sysconfdir}/%{name}/server/profiles/*

%files client
%defattr(644,root,root,755)
%doc *.gz
%defattr(644,root,root,755)
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
%config(noreplace) %verify(not md5 size mtime) %attr(640,root,backupc) %{_sysconfdir}/%{name}/client/authorized_keys
%config(noreplace) %verify(not md5 size mtime) %attr(640,root,backupc) %{_sysconfdir}/%{name}/client/backups/*
