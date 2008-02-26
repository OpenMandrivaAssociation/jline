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

%define _with_gcj_support 1

%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

%define _without_maven 0

%define with_maven %{!?_without_maven:0}%{?_without_maven:1}
%define without_maven %{?_without_maven:1}%{!?_without_maven:0}

%define cvs_version 0.9.93
%define repo_dir    .m2/repository

Name:           jline
Version:        0.9.94
Release:        %mkrel 0.0.1
Epoch:          0
Summary:        Java library for reading and editing user input in console applications
License:        BSD
URL:            http://jline.sf.net/
Group:          Development/Java
Source0:        http://superb-east.dl.sourceforge.net/sourceforge/jline/jline-%{cvs_version}.zip
Source1:        CatalogManager.properties
Source2:        jline-build.xml
Requires:       /bin/sh
Requires:       /bin/stty
BuildRequires:  java-rpmbuild >= 0:1.7
%if %{with_maven}
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
%if ! %{gcj_support}
BuildArch:      noarch
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%if %{gcj_support}
BuildRequires:          java-gcj-compat-devel
%endif

%description
JLine is a java library for reading and editing user input in console
applications. It features tab-completion, command history, password
masking, customizable keybindings, and pass-through handlers to use to
chain to other console applications.

%package        demo
Summary:        Demos for %{name}
Group:          Development/Java

%if %{gcj_support}
BuildRequires:          java-gcj-compat-devel
%endif

%description    demo
Demonstrations and samples for %{name}.

# FIXME: the maven ant:ant generated build.xml file does not contain 
#        a javadoc task
%if %{with_maven}
%package        javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%if %{gcj_support}
BuildRequires:          java-gcj-compat-devel
%endif

%description    javadoc
Javadoc for %{name}.
%endif

%prep
# BEWARE: The jar file META-INF is not under the subdir
%setup -q -c -n %{name}-%{cvs_version}
cp -pr %{name}-%{cvs_version}/* .
rm -fr %{name}-%{cvs_version}

# Use locally installed DTDs
mkdir %{_builddir}/%{name}-%{cvs_version}/build
cp -p %SOURCE1 %{_builddir}/%{name}-%{cvs_version}/build/

cp -p %{SOURCE2} src/build.xml

%{__perl} -pi -e 's/^import com\.sun\.jmx\.snmp\.ThreadContext\;$//' src/src/main/java/jline/Terminal.java

%build
mkdir -p native
# Now done by Patch0 for documentation purposes
#perl -p -i -e 's|^.*<attribute name="Class-Path".*||' build.xml

# Use locally installed DTDs
export CLASSPATH=$(pwd)/build:$(pwd)/src/target/test-classes

cd src/

%if %{with_maven}
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
rm -rf $RPM_BUILD_ROOT
# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
for jar in $(find -type f -name "*.jar" | grep -E target/.*.jar); do
        install -m 644 $jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
done
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do \
ln -sf ${jar} ${jar/-%{version}/}; done)

# the maven ant:ant task did not generate a build.xml file with a javadoc task
%if %{with_maven}
# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
for target in $(find -type d -name target); do
        install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}/`basename \`dirname $target\` | sed -e s:jline-::g`
        cp -pr $target/site/apidocs/* $jar $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}/`basename \`dirname $target\` | sed -e s:jline-::g`
done
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name} 
%endif

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT
rm -rf $RPM_BUILD_DIR/META-INF

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%files
%defattr(0644,root,root,0755)
%{_javadir}/%{name}.jar
%{_javadir}/%{name}-%{version}.jar
%doc LICENSE.txt

%if %{with_maven}
%if %{gcj_support}
%dir %attr(-,root,root) %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/jline-%{version}.jar.*
%endif

%files javadoc
%defattr(0644,root,root,0755)
%doc %{_javadocdir}/*
%endif

#FIXME: add javadoc support to generated build.xml

%if %{gcj_support}
%dir %attr(-,root,root) %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/jline-%{version}.jar.*
%endif
