%{?_javapackages_macros:%_javapackages_macros}
Name:           derby
Version:        10.10.2.0
Release:        1.3
Summary:        Relational database implemented entirely in Java

Group:          Databases
License:        ASL 2.0
URL:            http://db.apache.org/derby/
Source0:        http://apache.mirror.anlx.net//db/derby/db-derby-%{version}/db-derby-%{version}-src.tar.gz
Source1:        derby-script
Source2:        derby.service

# https://issues.apache.org/jira/browse/DERBY-5125
Patch1: derby-javacc5.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=830661
Patch2: derby-net.patch

BuildRequires:	mvn(org.apache:apache:pom:)
BuildRequires:  java-devel >= 1.6
BuildRequires:  javapackages-local
BuildRequires:  servlet3
BuildRequires:  jakarta-oro
BuildRequires:  javacc
BuildRequires:  junit
BuildRequires:  xalan-j2
BuildRequires:  ant
BuildRequires:  systemd-units
Requires(pre):  shadow-utils
Requires(preun): systemd-units
Requires(post): systemd-units

BuildArch:      noarch

%description
Apache Derby, an Apache DB sub-project, is a relational database implemented
entirely in Java. Some key advantages include a small footprint, conformance
to Java, JDBC, and SQL standards and embedded JDBC driver.

%package javadoc
Summary: API documentation for derby.

%description javadoc
%{summary}.

%prep
%setup -q -c

find -name '*.jar' -delete
find -name '*.class' -delete

pushd db-derby-%{version}-src
rm java/engine/org/apache/derby/impl/sql/compile/Token.java
%patch1 -p0
%patch2 -p0
popd

%build
cd db-derby-%{version}-src

# tools/ant/properties/extrapath.properties
ln -sf $(build-classpath javacc) tools/java/javacc.jar
ln -sf $(build-classpath servlet25) \
        tools/java/geronimo-spec-servlet-2.4-rc4.jar
ln -sf $(build-classpath xalan-j2) tools/java/xalan.jar
ln -sf $(build-classpath xalan-j2-serializer) tools/java/serializer.jar
ln -sf $(build-classpath oro) tools/java/jakarta-oro-2.0.8.jar
ln -sf $(build-classpath junit) tools/java/junit.jar

# Using generics
find -name build.xml |xargs sed '
        s/target="1.4"/target="1.6"/
        s/source="1.4"/source="1.6"/
        /Class-Path/d
' -i

# Fire
ant buildsource buildjars javadoc

# Generate maven poms
find maven2 -name pom.xml | xargs sed -i -e 's|ALPHA_VERSION|%{version}|'

# Request maven installation
%mvn_artifact maven2/pom.xml
for p in engine net client tools \
    derbyLocale_cs derbyLocale_de_DE derbyLocale_es derbyLocale_fr derbyLocale_hu \
    derbyLocale_it derbyLocale_ja_JP derbyLocale_ko_KR derbyLocale_pl derbyLocale_pt_BR \
    derbyLocale_ru derbyLocale_zh_CN derbyLocale_zh_TW ; do
  d=derby${p#derby}
  %mvn_artifact maven2/${p}/pom.xml jars/sane/${d%engine}.jar
done

%install
cd db-derby-%{version}-src

%mvn_install

# Wrapper scripts
install -d $RPM_BUILD_ROOT%{_bindir}
install -p -m755 %{SOURCE1} $RPM_BUILD_ROOT%{_bindir}/%{name}-ij
for P in sysinfo NetworkServerControl startNetworkServer stopNetworkServer
do
        ln $RPM_BUILD_ROOT%{_bindir}/%{name}-ij \
                $RPM_BUILD_ROOT%{_bindir}/%{name}-$P
done

# Systemd unit
mkdir -p $RPM_BUILD_ROOT%{_unitdir}
install -p -m 644 %{SOURCE2} \
        $RPM_BUILD_ROOT%{_unitdir}/%{name}.service

# Derby home dir
install -dm 755 $RPM_BUILD_ROOT/var/lib/derby

# Javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/derby
cp -pr javadoc/* $RPM_BUILD_ROOT%{_javadocdir}/derby

%pre
getent group derby >/dev/null || groupadd -r derby
getent passwd derby >/dev/null || \
    useradd -r -g derby -d /var/lib/derby -s /sbin/nologin \
    -c "Apache Derby service account" derby
exit 0

%preun
%systemd_preun derby.service

%post
%systemd_post derby.service

%files -f  db-derby-%{version}-src/.mfiles
%dir %{_javadir}/%{name}
%{_bindir}/*
%doc db-%{name}-%{version}-src/LICENSE
%doc db-%{name}-%{version}-src/NOTICE
%doc db-%{name}-%{version}-src/published_api_overview.html
%doc db-%{name}-%{version}-src/RELEASE-NOTES.html
%doc db-%{name}-%{version}-src/README
%{_unitdir}/%{name}.service
%attr(755,derby,derby) %{_sharedstatedir}/%{name}

%files javadoc
%doc db-derby-%{version}-src/LICENSE
%doc db-derby-%{version}-src/NOTICE
%{_javadocdir}/derby

%changelog
* Fri Jun 10 2014 Mat Booth <mat.booth@redhat.com> - 10.10.2.0-1
- Update to latest upstream version
- Fix BR: junit4 -> junit
- Install with xmvn
- Package javadocs

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 10.9.1.0-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Mar 04 2014 Stanislav Ochotnicky <sochotnicky@redhat.com> - 10.9.1.0-7
- Use Requires: java-headless rebuild (#1067528)

* Tue Oct 15 2013 Michal Srb <msrb@redhat.com> - 10.9.1.0-6
- Add derbyclient.jar to classpath of derby-ij (Thanks J. Stribny)

* Fri Oct 11 2013 Michal Srb <msrb@redhat.com> - 10.9.1.0-5
- Add more classes to derbynet.jar (related to #830661)
- Create and own derby home dir
- Simplify systemd service file a bit

* Mon Aug 12 2013 Mat Booth <fedora@matbooth.co.uk> - 10.9.1.0-4
- Fix FTBFS rhbz #992123
- Update servlet BR
- Add missing BR on systemd-units
- Drop versioned jars
- Remove use of deprecated add_to_maven_depmap macro

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 10.9.1.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Feb 25 2013 Andy Grimm <agrimm@gmail.com> - 10.9.1.0-2
- Add systemd service unit (RHBZ#741134)

* Mon Feb 25 2013 Andy Grimm <agrimm@gmail.com> - 10.9.1.0-1
- Version bump
- Add classes to derbynet.jar (RHBZ#830661)

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 10.6.2.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Aug 10 2012 Andy Grimm <agrimm@gmail.com> - 10.6.2.1-4
- Add gcj buildreq to fix FTBFS

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 10.6.2.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 10.6.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Nov 29 2011 Alexander Kurtakov <akurtako@redhat.com> 10.6.2.1-1
- Update to newer upstream version.

* Fri Feb 25 2011 Lubomir Rintel <lkundrak@v3.sk> - 10.6.1.0-6
- Fix startup script (Thomas Meyer, #668828)

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 10.6.1.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Nov 26 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 10.6.1.0-4
- Fix pom filenames (Resolves rhbz#655794)

* Tue Jul 27 2010 Lubomir Rintel <lkundrak@v3.sk> - 10.6.1.0-3
- Fix buildrequires

* Tue Jul 27 2010 Lubomir Rintel <lkundrak@v3.sk> - 10.6.1.0-2
- Add tool launchers
- Add POMs

* Mon Jun 28 2010 Lubomir Rintel <lkundrak@v3.sk> - 10.6.1.0-1
- Initial packaging

