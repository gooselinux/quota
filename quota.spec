#allow remote set quota by defined rpcsetquota to 1(set to 0 to disabled it)
%{!?rpcsetquota:%define rpcsetquota 1}

Name: quota
Summary: System administration tools for monitoring users' disk usage
Epoch: 1
Version: 3.17
Release: 10%{?dist}
License: BSD and GPLv2+
URL: http://sourceforge.net/projects/linuxquota/
Group: System Environment/Base
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires: initscripts >= 6.38 tcp_wrappers e2fsprogs
Conflicts: kernel < 2.4
BuildRequires: e2fsprogs-devel gettext tcp_wrappers-devel nss-devel
BuildRequires: openldap-devel openssl-devel dbus-devel libnl-devel
Source0: http://downloads.sourceforge.net/linuxquota/%{name}-%{version}.tar.gz
Patch0:	quota-3.06-warnquota.patch
Patch1: quota-3.06-no-stripping.patch
Patch2: quota-3.06-man-page.patch
Patch3: quota-3.06-pie.patch
Patch4: quota-3.13-wrong-ports.patch
Patch5: quota-3.16-helpoption.patch
Patch6: quota-3.16-quotaoffhelp.patch
Patch7: quota-3.17-quotactlmanpage.patch
Patch8: quota-3.17-goodclient.patch
# Bug #589478, included in upstream 4.00_pre2
Patch9: quota-3.17-quotactl_null_corruption.patch

%description
The quota package contains system administration tools for monitoring
and limiting user and or group disk usage per filesystem.

%package devel
Summary: Development files for quota
Group: System Environment/Base
Requires: quota =  %{epoch}:%{version}-%{release}

%description devel
The quota package contains system administration tools for monitoring
and limiting user and or group disk usage per filesystem.

This package contains development header files for implementing quotas
on remote machines.


%prep
%setup -q -n quota-tools
%patch0 -p1
%patch1 -p1
%patch2 -p1
%ifnarch ppc ppc64
%patch3 -p1
%endif
%patch4 -p1
%patch5 -p1
%patch6 -p1 -b .usage
%patch7 -p1 -b .quotactlman
%patch8 -p1 -b .goodclient
%patch9 -p1 -b .quota_null_corruption

#fix typos/mistakes in localized documentation
for pofile in $(find ./po/*.p*)
do
   sed -i 's/editting/editing/' "$pofile"
done

%build
%configure \
	--enable-ldapmail=try \
%if %{rpcsetquota}
	--enable-rpcsetquota=yes \
%endif
	--enable-rootsbin \
	--enable-netlink=yes
make


%install
rm -fr %{buildroot}
mkdir -p %{buildroot}/sbin
mkdir -p %{buildroot}%{_sysconfdir}
mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_mandir}/{man1,man2,man3,man8}
make install INSTALL='install -p' ROOTDIR=%{buildroot}
install -m 644 warnquota.conf %{buildroot}%{_sysconfdir}
#
# we don't support XFS yet
#
rm -f %{buildroot}%{_sbindir}/quot
rm -f %{buildroot}%{_sbindir}/xqmstats
rm -f %{buildroot}%{_mandir}/man8/quot.*
rm -f %{buildroot}%{_mandir}/man8/xqmstats.*
ln -s  quotaon.8.gz \
  %{buildroot}%{_mandir}/man8/quotaoff.8
ln -s rquotad.8.gz \
   %{buildroot}%{_mandir}/man8/rpc.rquotad.8

%find_lang %{name}

%clean
rm -rf %{buildroot}


%files -f %{name}.lang
%defattr(-,root,root,-)
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/*
%attr(0755,root,root) /sbin/*
%attr(0755,root,root) %{_bindir}/*
%attr(0755,root,root) %{_sbindir}/*
%attr(0644,root,root) %{_mandir}/man1/*
%attr(0644,root,root) %{_mandir}/man2/*
%attr(0644,root,root) %{_mandir}/man8/*

%files devel
%defattr(-,root,root,-)
%dir %{_includedir}/rpcsvc
%{_includedir}/rpcsvc/*
%attr(0644,root,root) %{_mandir}/man3/*

%changelog
* Tue May 25 2010 Petr Pisar <ppisar@redhat.com> 1:3.17-10
- Do not pass NULL to quotactl(2) (#589478)

* Mon Feb 22 2010 Daniel Novotny <dnovotny@redhat.com> 1:3.17-9
- fix #566718 -  quota: incorrect use of tcp_wrappers

* Wed Sep 30 2009 Ondrej Vasik <ovasik@redhat.com> 1:3.17-8
- add buildrequires for quota_nld, enable-netlink to build
  quota_nld (#526047)

* Fri Sep 18 2009 Ondrej Vasik <ovasik@redhat.com> 1:3.17-7
- Fix headers and structs in quotactl manpage(#524138)

* Fri Aug 28 2009 Ondrej Vasik <ovasik@redhat.com> 1:3.17-6
- symlink manpage for rpc.rquotad

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:3.17-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Mar 13 2009 Ondrej Vasik <ovasik@redhat.com> 1:3.17-4
- clarify statements about LDAP in warnquota conf
  (related to #490106)
- fix parsing issue in warnquota.c(#490125)
- enable rpcsetquota by default(#159292, #469753)

* Fri Mar 13 2009 Ondrej Vasik <ovasik@redhat.com> 1:3.17-3
- add missing buildrequires needed to compile with
  enable-ldapmail=try option with LDAP(#490106)

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:3.17-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Jan 13 2009 Ondrej Vasik <ovasik@redhat.com> 1:3.17-1
- new upstream release, remove already applied patches

* Mon Dec 08 2008 Ondrej Vasik <ovasik@redhat.com> 1:3.16-8
- fix documentation inconsistency (now rpc(3) instead of
  rpc(3N) in rquotad manpage) (#474836)

* Fri Nov 14 2008 Ondrej Vasik <ovasik@redhat.com> 1:3.16-7
- fix quotaoff --help output (was same as quotaon output)

* Thu Oct 30 2008 Ondrej Vasik <ovasik@redhat.com> 1:3.16-6
- fix implementation of ext4 support
  (by Mingming Cao, #469127)

* Wed Sep 10 2008 Ondrej Vasik <ovasik@redhat.com> 1:3.16-5
- fix rpmlint warnings - absolute symlink and not using epoch
  in version in changelog (#226353)
- rquota headers and manpage now in devel subpackage

* Wed Aug 27 2008 Ondrej Vasik <ovasik@redhat.com> 3.16-4
- fix bug in warnquota which could result in bogus hostname
  and domainname (upstream)
- remove IMMUTABLE flag from quota file in quotacheck(upstream)

* Tue Aug 05 2008 Ondrej Vasik <ovasik@redhat.com> 3.16-3
- Add support for -h option (do not show invalid option
  error) at edquota,setquota and quota (#457898)

* Fri Jun 20 2008 Ondrej Vasik <ovasik@redhat.com> 3.16-2
- upstream fix of some typos, string formats + 4TB+ fix
  for repquota
- some additional stripping removal
- change default mode of binaries from 555 to 755
  (strip error messages in build log)

* Wed Apr 23 2008 Ondrej Vasik <ovasik@redhat.com> 3.16-1
- own directory of rpcsvc headers(#442143)
- new upstream release

* Wed Mar 12 2008 Ondrej Vasik <ovasik@redhat.com> 3.15-6
- added enable-ldapmail=try option(wonder how #133207
  got closed by FC-4 without it or warnquota.conf change)
- dropped with-ext2direct=no option - this option is 
  invalid and original bug was fixed in 3.07

* Thu Mar  6 2008 Ondrej Vasik <ovasik@redhat.com> 3.15-5
- added symbolic link for quotaoff man page(#436110)
- don't ship xqmstats.8 man page as we don't ship those
  binaries(#436100)

* Thu Feb 21 2008 Ondrej Vasik <ovasik@redhat.com> 3.15-4
- added pointers to quota_nld and warnquota to some 
  manpages(upstream, #83975)

* Tue Feb 12 2008 Ondrej Vasik <ovasik@redhat.com> 3.15-3
- allow to build with rpcsetquota enabled(disabled by
  default, #159292)
- rebuild for gcc43

* Thu Jan 24 2008 Steve Dickson <SteveD@RedHat.com> 3.15-2
- More review comments:
    - BuiltPreReq to BuiltReq
    - Removed '.' From Summary
    - Added 'GPLv2+' to License Tag
	- Condensed the _sysconfdir entries in to one line

* Thu Jan 24 2008 Steve Dickson <SteveD@RedHat.com> 3.15-1
- Upgraded to version 3.15 
- Updated spec file per Merge Review (bz 226353)

* Thu Feb 15 2007  Steve Dickson <SteveD@RedHat.com> 3.14-1
- Upgraded to version 3.14 (bz# 213641)

* Mon Dec  4 2006 Thomas Woerner <twoerner@redhat.com> 1:3.13-1.3
- tcp_wrappers has a new devel and libs sub package, therefore changing build
  requirement for tcp_wrappers to tcp_wrappers-devel

* Wed Nov  1 2006 Steve Dickson <SteveD@RedHat.com> 1:3.13-1.2.3.2
- Added range checking on -p flag (bz 205145)
- Error message prints garbage characters (bz 201226)

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1:3.13-1.2.3.1
- rebuild

* Fri Jun 30 2006 Steve Dickson <steved@redhat.com> - 1:3.13-1.2.3
- fix 192826 - quota config files should not be overwritten

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1:3.13-1.2.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1:3.13-1.2
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Mon Oct 31 2005 Steve Dickson <steved@redhat.com> 3.13-1
- Upgraded to version 3.13 (bz# 171245)

* Thu Aug 18 2005 Florian La Roche <laroche@redhat.com>
- change the "Requires: kernel" into a "Conflicts:"

* Sun Sep 26 2004 Rik van Riel <riel@redhat.com> 3.12-5
- add URL (bz# 131862)

* Fri Sep 24 2004 Steve Dickson <SteveD@RedHat.com>
- Fixed typos in warnquota.conf patch 
  (bz# 82250 and bz# 83974)

* Mon Sep 13 2004 Steve Dickson <SteveD@RedHat.com>
- upgraded to 3.12

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Jan 27 2004 Florian La Roche <Florian.LaRoche@redhat.de>
- add -pie support
- update to 3.10

* Sat Aug 16 2003  Steve Dickson <SteveD@RedHat.com>
- upgraded to 3.0.9
- added quota-3.09-root_sbindir.patch

* Sun Aug 10 2003 Elliot Lee <sopwith@redhat.com> 3.06-11
- Rebuild

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue May 27 2003 Steve Dickson <SteveD@RedHat.com>
- rebuilt for 7.3 errata

* Tue Feb 25 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Sun Feb 23 2003 Tim Powers <timp@redhat.com>
- add buildprereq on tcp_wrappers

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Mon Nov 18 2002 Tim Powers <timp@redhat.com>
- rebuild on all arches


* Fri Sep 6 2002 Philip Copeland <bryce@redhat.com> 3.06-5
- added --with-ext2direct=no to fix #73244
  without this users with UID's > 65535 will not
  be able to exist on a quota enabled FS

* Wed Aug 7 2002 Philip Copeland <bryce@redhat.com> 3.06-4
- Man page change. #60108

* Tue Aug 6 2002 Philip Copeland <bryce@redhat.com> 3.06-3
- Bah, I'd dropped epoch from the spec file but seems
  we need this if you want to upgrade as the epoch
  number has precedence over the version/release
  numbers.

* Wed Jul 17 2002 Philip Copeland <bryce@redhat.com> 3.06-2
- Lets stop the makefile from stripping the
  binaries as thats rpms job (apparently)

* Mon Jul 01 2002 Philip Copeland <bryce@redhat.com> 3.06-1
- Ditched the 3.01-pre9 src base for 3.06
  Rebuilt without any patchs

============================================================

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu May 23 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Mon Feb 25 2002 Elliot Lee <sopwith@redhat.com>
- IfArch the badkernelinclude patch for ppc-only.
- Update to 3.03

* Wed Dec 12 2001 Guy Streeter <streeter@redhat.com>
- Make #include of kernel header file work on non-x86

* Wed Sep  5 2001 Preston Brown <pbrown@redhat.com>
- require new initscripts

* Thu Aug 30 2001 Preston Brown <pbrown@redhat.com>
- fixed bug #52075 (problem with ext2 labels)
- backup data files off by default in quotacheck, optional backup flag added
- fix bug where giving a bad directory or device would cause 
  quotaon/quotacheck to simulate "-a" behaviour
- if a device name (i.e /dev/hda1) is passed, look up the corresponding mount
  point

* Wed Aug 29 2001 Preston Brown <pbrown@redhat.com>
- return an error code in more cases in convertquota

* Tue Aug 28 2001 Preston Brown <pbrown@redhat.com>
- 3.01pre9

* Fri Jul 20 2001 Preston Brown <pbrown@redhat.com>
- more cleanups on 3.01pre8

* Mon Jul  2 2001 Preston Brown <pbrown@redhat.com>
- 3.01 version, everything has changed again. :(

* Sun Jun 24 2001 Elliot Lee <sopwith@redhat.com>
- Bump release + rebuild.

* Fri Mar 30 2001 Preston Brown <pbrown@redhat.com>
- use rpc.rquotad from here again (#33738)

* Thu Mar 15 2001 Preston Brown <pbrown@redhat.com>
- enable ALT_FORMAT for edquota

* Tue Mar 13 2001 Preston Brown <pbrown@redhat.com>
- I broke passing devices on the cmd line.  Fixed.

* Fri Mar 09 2001 Preston Brown <pbrown@redhat.com>
- quota 3.00 is required by recent kernel 2.4 changes
- no warnquota included this time, not yet ported
- quite a bit of work on quotacheck to make is backwards compatible
- we will likely go back to "quota 2.00" as these projects merge...

* Fri Feb 09 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- use "rm -f" instead of only "rm"

* Wed Feb  7 2001 Preston Brown <pbrown@redhat.com>
- fix quotacheck man page for -a option (#26380)

* Thu Feb  1 2001 Preston Brown <pbrown@redhat.com>
- 2.00 final, rolls in pretty much all our patches. :)
- fix reporting of in use dquot entries from quotastats
- change repquota man page to fix documentation of -v (#10330)
- include warnquota.conf

* Mon Nov 20 2000 Bill Nottingham <notting@redhat.com>
- fix ia64 build

* Mon Aug 21 2000 Jeff Johnson <jbj@redhat.com>
- add LABEL=foo support (#16390).

* Thu Jul 27 2000 Jeff Johnson <jbj@redhat.com>
- remote NFS quotas with different blocksize converted incorrectly (#11932).

* Wed Jul 12 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Thu Jun 15 2000 Jeff Johnson <jbj@redhat.com>
- FHS packaging.

* Wed May 10 2000 Jeff Johnson <jbj@redhat.com>
- apply patch5 (H.J. Lu)

* Wed Feb 02 2000 Cristian Gafton <gafton@redhat.com>
- fix description
- man pages are compressed

* Tue Jan 18 2000 Preston Brown <pbrown@redhat.com>
- quota 2.00 series
- removed unnecessary patches

* Thu Aug  5 1999 Jeff Johnson <jbj@redhat.com>
- fix man page FUD (#4369).

* Thu May 13 1999 Peter Hanecak <hanecak@megaloman.sk>
- changes to allow non-root users to build too (Makefile patch, %%attr)

* Tue Apr 13 1999 Jeff Johnson <jbj@redhat.com>
- fix for sparc64 quotas (#2147)

* Sun Mar 21 1999 Cristian Gafton <gafton@redhat.com> 
- auto rebuild in the new build environment (release 5)

* Mon Dec 28 1998 Cristian Gafton <gafton@redhat.com>
- don't install rpc.rquotad - we will use the one from the knfsd package
  instead

* Thu Dec 17 1998 Jeff Johnson <jbj@redhat.com>
- merge ultrapenguin 1.1.9 changes.

* Thu May 07 1998 Prospector System <bugs@redhat.com>
- translations modified for de, fr, tr

* Thu Apr 30 1998 Cristian Gafton <gafton@redhat.com>
- removed patch for mntent

* Fri Mar 27 1998 Jakub Jelinek <jj@ultra.linux.cz>
- updated to quota 1.66

* Tue Jan 13 1998 Erik Troan <ewt@redhat.com>
- builds rquotad
- installs rpc.rquotad.8 symlink

* Mon Oct 20 1997 Erik Troan <ewt@redhat.com>
- removed /usr/include/rpcsvc/* from filelist
- uses a buildroot and %%attr

* Thu Jun 19 1997 Erik Troan <ewt@redhat.com>
- built against glibc

* Tue Mar 25 1997 Erik Troan <ewt@redhat.com>
- Moved /usr/sbin/quota to /usr/bin/quota
