%bcond_with	gcj_support
%bcond_with	maven

Summary:	Java library for reading and editing user input in console applications
Name:		jline
Version:	1.0
Release:	4
License:	BSD
Url:		http://jline.sf.net/
Group:		Development/Java
Source0:	http://superb-east.dl.sourceforge.net/sourceforge/jline/jline-%{version}.zip
Source1:	CatalogManager.properties
Source2:	jline-build.xml
%if !%{with gcj_support}
BuildArch:	noarch
%else
BuildRequires:	java-gcj-compat-devel
%endif
BuildRequires:	java-rpmbuild >= 0:1.7
%if %{with maven}
BuildRequires:	xml-commons-resolver
BuildRequires:	maven2
BuildRequires:	maven2-plugin-resources
BuildRequires:	maven2-plugin-compiler
BuildRequires:	maven-surefire-plugin
BuildRequires:	maven2-plugin-jar
BuildRequires:	maven2-plugin-install
BuildRequires:	maven2-plugin-site
BuildRequires:	maven2-plugin-assembly
BuildRequires:	maven2-plugin-javadoc
BuildRequires:	ant-apache-resolver
%else
BuildRequires:	ant
BuildRequires:	junit
%endif
Requires:	bash
# For stty
Requires:	coreutils

%description
JLine is a java library for reading and editing user input in console
applications. It features tab-completion, command history, password
masking, customizable keybindings, and pass-through handlers to use to
chain to other console applications.

%package        demo
Summary:	Demos for %{name}
Group:		Development/Java

%description    demo
Demonstrations and samples for %{name}.

# FIXME:	the maven ant:ant generated build.xml file does not contain 
#        a javadoc task
%if %{with maven}
%package        javadoc
Summary:	Javadoc for %{name}
Group:		Development/Java

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
%ant \
	-Dbuild.sysclasspath="only" \
	-Duser.home=$(pwd) 
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
%update_gcjdb

%postun
%clean_gcjdb
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

#FIXME:	add javadoc support to generated build.xml

%if %{with gcj_support}
%dir %attr(-,root,root) %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/jline-%{version}.jar.*
%endif
