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

%bcond_with	gcj_support
%bcond_with	maven

Name:           jline
Version:        1.0
Release:        1
Summary:        Java library for reading and editing user input in console applications
License:        BSD
URL:            http://jline.sf.net/
Group:          Development/Java
Source0:        http://superb-east.dl.sourceforge.net/sourceforge/jline/jline-%{version}.zip
Source1:        CatalogManager.properties
Source2:        jline-build.xml
Requires:       /bin/sh
Requires:       /bin/stty
BuildRequires:  java-rpmbuild >= 0:1.7
%if %{with maven}
BuildRequires:  xml-commons-resolver
BuildRequires:  maven2
BuildRequires:  maven2-plugin-resources
BuildRequires:  maven2-plugin-compiler
BuildRequires:  maven-surefire-plugin
BuildRequires:  maven2-plugin-jar
BuildRequires:  maven2-plugin-install
BuildRequires:  maven2-plugin-site
BuildRequires:  maven2-plugin-assembly
BuildRequires:  maven2-plugin-javadoc
BuildRequires:  ant-apache-resolver
%else
BuildRequires:  ant
BuildRequires:  junit
%endif
%if %{with gcj_support}
BuildRequires:          java-gcj-compat-devel
%else
BuildArch:      noarch
%endif

%description
JLine is a java library for reading and editing user input in console
applications. It features tab-completion, command history, password
masking, customizable keybindings, and pass-through handlers to use to
chain to other console applications.

%package        demo
Summary:        Demos for %{name}
Group:          Development/Java

%description    demo
Demonstrations and samples for %{name}.

# FIXME: the maven ant:ant generated build.xml file does not contain 
#        a javadoc task
%if %{with maven}
%package        javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description    javadoc
Javadoc for %{name}.
%endif

%prep
%setup -q
%remove_java_binaries

cp %{SOURCE2} src/build.xml

#%{__perl} -pi -e 's/^import com\.sun\.jmx\.snmp\.ThreadContext\;$//' src/src/main/java/jline/Terminal.java

%build
# Now done by Patch0 for documentation purposes
#perl -p -i -e 's|^.*<attribute name="Class-Path".*||' build.xml

# Use locally installed DTDs
export CLASSPATH=$(pwd)/build:$(pwd)/src/target/test-classes

cd src/

%if %{with maven}
export MAVEN_REPO_LOCAL=$(pwd)/.m2/repository
mkdir -p $MAVEN_REPO_LOCAL

mvn-jpp \
        -e \
                -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
                -Dmaven.test.failure.ignore=true \
        install javadoc:javadoc
%else
mkdir -p $(pwd)/.m2/repository
build-jar-repository $(pwd)/.m2/repository junit
export CLASSPATH=$(pwd)/target/classes:$(pwd)/target/test-classes
%{ant} -Dbuild.sysclasspath="only" -Duser.home=$(pwd) 
%endif

%install
# jars
for jar in $(find -type f -name "*.jar"); do
	install -m644 $jar -D %{buildroot}%{_javadir}/%{name}-%{version}.jar
	jar -i %{buildroot}%{_javadir}/%{name}-%{version}.jar
done
%create_jar_links

# the maven ant:ant task did not generate a build.xml file with a javadoc task
%if %{with maven}
# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
for target in $(find -type d -name target); do
        install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}/`basename \`dirname $target\` | sed -e s:jline-::g`
        cp -pr $target/site/apidocs/* $jar $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}/`basename \`dirname $target\` | sed -e s:jline-::g`
done
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name} 
%endif

%if %{with gcj_support}
%{_bindir}/aot-compile-rpm

%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%files
%doc LICENSE.txt
%{_javadir}/%{name}.jar
%{_javadir}/%{name}-%{version}.jar
%doc LICENSE.txt

%if %{with maven}
%if %{with gcj_support}
%dir %attr(-,root,root) %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/jline-%{version}.jar.*
%endif

%files javadoc
%doc %{_javadocdir}/*
%endif

#FIXME: add javadoc support to generated build.xml

%if %{with gcj_support}
%dir %attr(-,root,root) %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/jline-%{version}.jar.*
%endif


%changelog
* Wed May 11 2011 Per Øyvind Karlsen <peroyvind@mandriva.org> 1.0-1
+ Revision: 673389
- update to 1.0 and do some heavy cleaning

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild

* Tue Feb 26 2008 Alexander Kurtakov <akurtakov@mandriva.org> 0:0.9.94-0.0.1mdv2008.1
+ Revision: 175316
- new version and build with maven

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Sun Dec 16 2007 Anssi Hannula <anssi@mandriva.org> 0:0.9.93-0.0.2mdv2008.1
+ Revision: 120949
- buildrequire java-rpmbuild, i.e. build with icedtea on x86(_64)

* Wed Nov 14 2007 David Walluck <walluck@mandriva.org> 0:0.9.93-0.0.1mdv2008.1
+ Revision: 108566
- 0.9.93 (upstream versioning, not jpackage)

* Sat Sep 15 2007 Anssi Hannula <anssi@mandriva.org> 0:0.9.9.1-1.0.2mdv2008.0
+ Revision: 87438
- rebuild to filter out autorequires of GCJ AOT objects
- remove unnecessary Requires(post) on java-gcj-compat

* Sat Aug 04 2007 David Walluck <walluck@mandriva.org> 0:0.9.9.1-1.0.1mdv2008.0
+ Revision: 58826
- 0.9.9.1

* Wed Jul 04 2007 David Walluck <walluck@mandriva.org> 0:0.9.9-1.1.1mdv2008.0
+ Revision: 47871
- Import jline



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
