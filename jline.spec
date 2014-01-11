%{?_javapackages_macros:%_javapackages_macros}
# Copyright (c) 2000-2005, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

Name:           jline
Version:        1.0
Release:        7.1%{?dist}
Summary:        Java library for reading and editing user input in console applications
License:        BSD
URL:            http://jline.sourceforge.net/

Source0:        http://download.sourceforge.net/sourceforge/jline/jline-%{version}.zip
Source1:        CatalogManager.properties
Patch1:         %{name}-0.9.94-crosslink.patch

Requires:      bash
# for /bin/stty
Requires:      coreutils
Requires:      jpackage-utils

BuildRequires: jpackage-utils
BuildRequires: maven-local
BuildRequires: maven-assembly-plugin
BuildRequires: maven-compiler-plugin
BuildRequires: maven-install-plugin
BuildRequires: maven-jar-plugin
BuildRequires: maven-javadoc-plugin
BuildRequires: maven-resources-plugin
BuildRequires: maven-site-plugin
BuildRequires: maven-surefire-plugin
BuildRequires: maven-surefire-provider-junit
BuildRequires: java-javadoc

BuildArch:     noarch

%description
JLine is a java library for reading and editing user input in console
applications. It features tab-completion, command history, password
masking, configurable key-bindings, and pass-through handlers to use to
chain to other console applications.

%package        demo
Summary:        Demos for %{name}

Requires:       %{name} = %{version}-%{release}

%description    demo
Demonstrations and samples for %{name}.

%package        javadoc
Summary:        Javadoc for %{name}

Requires:       java-javadoc

%description    javadoc
Javadoc for %{name}.

%prep
%setup -q
%patch1 -p1

# Make sure upstream hasn't sneaked in any jars we don't know about
find -name '*.class' -exec rm -f '{}' \;
find -name '*.jar' -exec rm -f '{}' \;

# Remove pre-built Windows-only binary artifacts
rm src/src/main/resources/jline/jline*.dll

# Use locally installed DTDs
mkdir build
cp -p %{SOURCE1} build/

%build
# Use locally installed DTDs
export CLASSPATH=%{_builddir}/%{name}-%{version}/build

cd src/

mvn-rpmbuild install javadoc:javadoc

%install
# jars
install -pD -T -m 644 src/target/%{name}-%{version}.jar \
  %{buildroot}%{_javadir}/%{name}.jar

# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}
cp -pr src/target/site/apidocs/* %{buildroot}%{_javadocdir}/%{name}

# demo
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/%{name}
cp -pr examples %{buildroot}%{_datadir}/%{name}

# pom
install -pD -T -m 644 src/pom.xml %{buildroot}%{_mavenpomdir}/JPP-%{name}.pom
%add_maven_depmap JPP-%{name}.pom %{name}.jar

%pre javadoc
# workaround for rpm bug, can be removed in F-17
[ $1 -gt 1 ] && [ -L %{_javadocdir}/%{name} ] && \
rm -rf $(readlink -f %{_javadocdir}/%{name}) %{_javadocdir}/%{name} || :

%files
%{_javadir}/%{name}.jar
%{_mavendepmapfragdir}/*
%{_mavenpomdir}/*
%doc LICENSE.txt src/src/main/resources/jline/keybindings.properties

%files demo
%{_datadir}/%{name}

%files javadoc
%doc LICENSE.txt
%{_javadocdir}/*

%changelog
* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 1.0-3
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Feb 1 2012 Alexander Kurtakov <akurtako@redhat.com> 1.0-1
- Update to 1.0.

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.94-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Dec 13 2011 Alexander Kurtakov <akurtako@redhat.com> 0.9.94-6
- Build with maven 3.x.

* Sat Oct 15 2011 Ville Skyttä <ville.skytta@iki.fi> - 0.9.94-5
- BuildRequire maven2.

* Sat Oct 15 2011 Ville Skyttä <ville.skytta@iki.fi> - 0.9.94-4
- Patch delete to actually behave as delete instead of backspace, include
  keybindings.properties in docs (#720170).
- Drop executable bit from jar.
- Crosslink with local javadocs.
- Include LICENSE.txt in -javadoc.

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.94-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sat Dec 18 2010 Mat Booth <fedora@matbooth.co.uk> - 0.9.94-2
- Remove pre-built Windows-only binary artifacts.
- Demo package was defined but never built for some reason.
- Don't also package jar in the javadoc package!
- Drop versioned java and javadocs.

* Sat Dec 18 2010 Mat Booth <fedora@matbooth.co.uk> - 0.9.94-1
- Remove bundled jars in %%prep phase.
- Tidy up spec file, fix some rpmlint warnings.
- Add pom and depmaps.

* Mon Mar  8 2010 Peter Lemenkov <lemenkov@gmail.com> - 0:0.9.94-0.6
- Added missing Requires: jpackage-utils (%%{_javadir} and %%{_javadocdir})

* Tue Jan 12 2010 Alexander Kurtakov <akurtako@redhat.com> 0:0.9.94-0.5
- Fix BRs.
- Drop gcj_support.

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:0.9.94-0.4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:0.9.94-0.3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Jul  9 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0:9.94-0.2
- drop repotag

* Mon Mar 24 2008 Matt Wringe <mwringe@redhat.com> - 0:9.94-0jpp.1
- Update to 0.9.94 (BZ #436204)

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0:0.9.9-2jpp.1
- Autorebuild for GCC 4.3

* Tue Mar 06 2007 Matt Wringe <mwringe@redhat.com> - 0:0.9.9-1jpp.1
- Add option to build with ant.
- Fix various rpmlint issues
- Specify proper license

* Thu May 04 2006 Alexander Kurtakov <akurtkov at gmail.com> - 0:0.9.9-1jpp
- Upgrade to 0.9.9

* Thu May 04 2006 Ralph Apel <r.apel at r-apel.de> - 0:0.9.5-1jpp
- Upgrade to 0.9.5
- First JPP-1.7 release

* Mon Apr 25 2005 Fernando Nasser <fnasser@redhat.com> - 0:0.9.1-1jpp
- Upgrade to 0.9.1
- Disable attempt to include external jars

* Mon Apr 25 2005 Fernando Nasser <fnasser@redhat.com> - 0:0.8.1-3jpp
- Changes to use locally installed DTDs
- Do not try and access sun site for linking javadoc

* Sun Aug 23 2004 Randy Watler <rwatler at finali.com> - 0:0.8.1-2jpp
- Rebuild with ant-1.6.2

* Mon Jan 26 2004 David Walluck <david@anti-microsoft.org> 0:0.8.1-1jpp
- release
