%{?_javapackages_macros:%_javapackages_macros}
%if 0%{?fedora}
%else
# Mandriva has it as /usr/com
%define _sharedstatedir /var/lib
%endif
Name:           derby
Version:        10.9.1.0
Release:        6.0%{?dist}
Summary:        Relational database implemented entirely in Java


License:        ASL 2.0
URL:            http://db.apache.org/derby/
Source0:        http://archive.apache.org/dist/db/%{name}/db-%{name}-%{version}/db-%{name}-%{version}-src.tar.gz
Source1:        derby-script
Source2:        derby.service

Source10:       http://repo1.maven.org/maven2/org/apache/%{name}/derby/%{version}/derby-%{version}.pom
Source11:       http://repo1.maven.org/maven2/org/apache/%{name}/derby-project/%{version}/derby-project-%{version}.pom
Source12:       http://repo1.maven.org/maven2/org/apache/%{name}/derbyLocale_cs/%{version}/derbyLocale_cs-%{version}.pom
Source13:       http://repo1.maven.org/maven2/org/apache/%{name}/derbyLocale_de_DE/%{version}/derbyLocale_de_DE-%{version}.pom
Source14:       http://repo1.maven.org/maven2/org/apache/%{name}/derbyLocale_es/%{version}/derbyLocale_es-%{version}.pom
Source15:       http://repo1.maven.org/maven2/org/apache/%{name}/derbyLocale_fr/%{version}/derbyLocale_fr-%{version}.pom
Source16:       http://repo1.maven.org/maven2/org/apache/%{name}/derbyLocale_hu/%{version}/derbyLocale_hu-%{version}.pom
Source17:       http://repo1.maven.org/maven2/org/apache/%{name}/derbyLocale_it/%{version}/derbyLocale_it-%{version}.pom
Source18:       http://repo1.maven.org/maven2/org/apache/%{name}/derbyLocale_ja_JP/%{version}/derbyLocale_ja_JP-%{version}.pom
Source19:       http://repo1.maven.org/maven2/org/apache/%{name}/derbyLocale_ko_KR/%{version}/derbyLocale_ko_KR-%{version}.pom
Source20:       http://repo1.maven.org/maven2/org/apache/%{name}/derbyLocale_pl/%{version}/derbyLocale_pl-%{version}.pom
Source21:       http://repo1.maven.org/maven2/org/apache/%{name}/derbyLocale_pt_BR/%{version}/derbyLocale_pt_BR-%{version}.pom
Source22:       http://repo1.maven.org/maven2/org/apache/%{name}/derbyLocale_ru/%{version}/derbyLocale_ru-%{version}.pom
Source23:       http://repo1.maven.org/maven2/org/apache/%{name}/derbyLocale_zh_CN/%{version}/derbyLocale_zh_CN-%{version}.pom
Source24:       http://repo1.maven.org/maven2/org/apache/%{name}/derbyLocale_zh_TW/%{version}/derbyLocale_zh_TW-%{version}.pom
Source25:       http://repo1.maven.org/maven2/org/apache/%{name}/derbyclient/%{version}/derbyclient-%{version}.pom
Source26:       http://repo1.maven.org/maven2/org/apache/%{name}/derbynet/%{version}/derbynet-%{version}.pom
Source27:       http://repo1.maven.org/maven2/org/apache/%{name}/derbytools/%{version}/derbytools-%{version}.pom

# https://issues.apache.org/jira/browse/DERBY-5125
Patch1: derby-javacc5.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=830661
Patch2: derby-net.patch

BuildRequires:  java-devel >= 1.6
BuildRequires:  jpackage-utils
BuildRequires:  servlet3
BuildRequires:  jakarta-oro
BuildRequires:  javacc
BuildRequires:  junit4
BuildRequires:  xalan-j2
BuildRequires:  xerces-j2
BuildRequires:  ant
BuildRequires:  systemd-units
Requires:       java
Requires(pre):  shadow-utils
Requires(preun): systemd-units
Requires(post): systemd-units

BuildArch:      noarch

%description
Apache Derby, an Apache DB sub-project, is a relational database implemented
entirely in Java. Some key advantages include a small footprint, conformance
to Java, JDBC, and SQL standards and embedded JDBC driver.


%prep
%setup -q -c
pushd db-%{name}-%{version}-src
rm java/engine/org/apache/derby/impl/sql/compile/Token.java
%patch1 -p0
popd
%patch2 -p1 -F1

%build
cd db-%{name}-%{version}-src
find -name '*.jar' -delete

# tools/ant/properties/extrapath.properties
ln -sf $(build-classpath javacc) tools/java/javacc.jar
ln -sf $(build-classpath servlet25) \
        tools/java/geronimo-spec-servlet-2.4-rc4.jar
ln -sf $(build-classpath xalan-j2) tools/java/xalan.jar
ln -sf $(build-classpath oro) tools/java/jakarta-oro-2.0.8.jar
ln -sf $(build-classpath xerces-j2) tools/java/xercesImpl.jar
ln -sf $(build-classpath xalan-j2-serializer) tools/java/serializer.jar
ln -sf $(build-classpath junit4) tools/java/junit.jar

# Using generics
find -name build.xml |xargs sed '
        s/target="1.4"/target="1.6"/
        s/source="1.4"/source="1.6"/
        /Class-Path/d
' -i

# Fire
ant -verbose clobber buildsource buildjars


%install
cd db-%{name}-%{version}-src

# Library
install -d $RPM_BUILD_ROOT%{_javadir}/%{name}
for i in jars/sane/*.jar
do
        B=$(basename $i |sed 's/.jar$//')
        install -m644 $i $RPM_BUILD_ROOT%{_javadir}/%{name}/$B.jar
done

# Wrapper scripts
install -d $RPM_BUILD_ROOT%{_bindir}
install -p -m755 %{SOURCE1} $RPM_BUILD_ROOT%{_bindir}/%{name}-ij
for P in sysinfo NetworkServerControl startNetworkServer stopNetworkServer
do
        ln $RPM_BUILD_ROOT%{_bindir}/%{name}-ij \
                $RPM_BUILD_ROOT%{_bindir}/%{name}-$P
done

# POMs
install -d $RPM_BUILD_ROOT%{_mavenpomdir}
install -p -m644 %{SOURCE10} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.derby-derby.pom
install -p -m644 %{SOURCE11} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.derby-derby-project.pom
install -p -m644 %{SOURCE12} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.derby-derbyLocale_cs.pom
install -p -m644 %{SOURCE13} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.derby-derbyLocale_de_DE.pom
install -p -m644 %{SOURCE14} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.derby-derbyLocale_es.pom
install -p -m644 %{SOURCE15} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.derby-derbyLocale_fr.pom
install -p -m644 %{SOURCE16} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.derby-derbyLocale_hu.pom
install -p -m644 %{SOURCE17} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.derby-derbyLocale_it.pom
install -p -m644 %{SOURCE18} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.derby-derbyLocale_ja_JP.pom
install -p -m644 %{SOURCE19} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.derby-derbyLocale_ko_KR.pom
install -p -m644 %{SOURCE20} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.derby-derbyLocale_pl.pom
install -p -m644 %{SOURCE21} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.derby-derbyLocale_pt_BR.pom
install -p -m644 %{SOURCE22} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.derby-derbyLocale_ru.pom
install -p -m644 %{SOURCE23} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.derby-derbyLocale_zh_CN.pom
install -p -m644 %{SOURCE24} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.derby-derbyLocale_zh_TW.pom
install -p -m644 %{SOURCE25} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.derby-derbyclient.pom
install -p -m644 %{SOURCE26} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.derby-derbynet.pom
install -p -m644 %{SOURCE27} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.derby-derbytools.pom

# Dependency maps
for pom in $RPM_BUILD_ROOT%{_mavenpomdir}/*.pom ; do
        B=$(basename $pom | sed -e 's/JPP.%{name}-//' -e 's/.pom$//')
	if [ -f "$RPM_BUILD_ROOT%{_javadir}/%{name}/$B.jar" ] ; then
		%add_maven_depmap JPP.%{name}-$B.pom %{name}/$B.jar
	else
		%add_maven_depmap JPP.%{name}-$B.pom
	fi
done

# Systemd unit
mkdir -p $RPM_BUILD_ROOT%{_unitdir}
install -p -m 644 %{SOURCE2} \
        $RPM_BUILD_ROOT%{_unitdir}/%{name}.service

# Derby home dir
install -dm 755 $RPM_BUILD_ROOT/var/lib/derby

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

%files
%{_bindir}/*
%{_javadir}/%{name}
%doc db-%{name}-%{version}-src/LICENSE
%doc db-%{name}-%{version}-src/NOTICE
%doc db-%{name}-%{version}-src/published_api_overview.html
%doc db-%{name}-%{version}-src/RELEASE-NOTES.html
%doc db-%{name}-%{version}-src/README
%{_mavenpomdir}/*.pom
%{_mavendepmapfragdir}/%{name}
%{_unitdir}/%{name}.service
%attr(755,derby,derby) %{_sharedstatedir}/%{name}


%changelog
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
