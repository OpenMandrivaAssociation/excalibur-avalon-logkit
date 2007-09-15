# Copyright (c) 2000-2007, JPackage Project
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

# If you don't want to build with maven, and use straight ant instead,
# give rpmbuild option '--without maven'

%define _without_maven 1
%define with_maven %{!?_without_maven:1}%{?_without_maven:0}
%define without_maven %{?_without_maven:1}%{!?_without_maven:0}

%define section free
%define grname  excalibur
%define usname  avalon-logkit

Name:           excalibur-avalon-logkit
Version:        2.1
Release:        %mkrel 10.0.3
Epoch:          0
Summary:        Excalibur's Logkit package
License:        Apache Software License 
Url:            http://excalibur.apache.org/
Group:          Development/Java
Source0:        http://www.apache.org/dist/excalibur/avalon-logkit/source/avalon-logkit-2.1-src.tar.gz
Source1:        pom-maven2jpp-depcat.xsl
Source2:        pom-maven2jpp-newdepmap.xsl
Source3:        pom-maven2jpp-mapdeps.xsl
Source4:        excalibur-avalon-logkit-2.1-jpp-depmap.xml
Source5:        excalibur-avalon-logkit-project-common.xml
Source6:        excalibur-buildsystem.tar.gz
Source7:        excalibur-avalon-logkit-build.xml
Patch0:         excalibur-avalon-logkit-2.1-project_xml.patch

Requires:       javamail
Requires:       log4j
Requires:       servletapi5
Obsoletes:      avalon-logkit < %{epoch}:%{version}-%{release}
Provides:       avalon-logkit = %{epoch}:%{version}-%{release}
%if %{with_maven}
BuildRequires:  maven >= 0:1.1
BuildRequires:  saxon
BuildRequires:  saxon-scripts
%else
BuildRequires:  ant >= 0:1.6
%endif
BuildRequires:  junit
BuildRequires:  jpackage-utils >= 0:1.6
BuildRequires:  geronimo-javamail-1.3.1-api
BuildRequires:  geronimo-jms-1.1-api
BuildRequires:  log4j
BuildRequires:  servletapi5

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root
%if ! %{gcj_support}
BuildArch:      noarch
%endif
%if %{gcj_support}
BuildRequires:    java-gcj-compat-devel
%endif

%description
LogKit is a logging toolkit designed for secure performance orientated
logging in applications. To get started using LogKit, it is recomended
that you read the whitepaper and browse the API docs.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java
Obsoletes:      avalon-logkit-javadoc < %{epoch}:%{version}-%{release}
Provides:       avalon-logkit-javadoc = %{epoch}:%{version}-%{release}

%description javadoc
%{summary}.

%package manual
Summary:        Documents for %{name}
Group:          Development/java

%description manual
%{summary}.

%prep
%setup -q -n %{usname}-%{version}
gzip -dc %{SOURCE6} | tar xf -
# remove all binary libs
find . -name "*.jar" -exec rm -f {} \;
#for j in $(find . -name "*.jar"); do
#      mv $j $j.no
#done
cp -a %{SOURCE5} project-common.xml
cp -a %{SOURCE7} build.xml

%patch0 -b .sav

%build
%if %{with_maven}
export DEPCAT=$(pwd)/excalibur-avalon-logkit-2.1-depcat.new.xml
echo '<?xml version="1.0" standalone="yes"?>' > $DEPCAT
echo '<depset>' >> $DEPCAT
for p in $(find . -name project.xml); do
    pushd $(dirname $p)
    /usr/bin/saxon project.xml %{SOURCE1} >> $DEPCAT
    popd
done
echo >> $DEPCAT
echo '</depset>' >> $DEPCAT
/usr/bin/saxon $DEPCAT %{SOURCE2} > excalibur-avalon-logkit-2.1-depmap.new.xml
for p in $(find . -name project.xml); do
    pushd $(dirname $p)
    cp project.xml project.xml.orig
    /usr/bin/saxon -o project.xml project.xml.orig %{SOURCE3} map=%{SOURCE4}
    popd
done

export MAVEN_HOME_LOCAL=$(pwd)/.maven

maven \
        -Dmaven.repo.remote=file:/usr/share/maven/repository \
        -Dmaven.home.local=$MAVEN_HOME_LOCAL \
        jar javadoc 
%else
export OPT_JAR_LIST=:
export CLASSPATH=$(build-classpath geronimo-javamail-1.3.1-api geronimo-jms-1.1-api log4j servletapi5):target/classes:target/test-classes
%ant -Dbuild.sysclasspath=only jar javadoc
%endif

%install
rm -rf $RPM_BUILD_ROOT

install -d -m 755 $RPM_BUILD_ROOT%{_javadir}/%{grname}
install -m 644 target/%{usname}-%{version}.jar \
        $RPM_BUILD_ROOT%{_javadir}/%{grname}/%{usname}-%{version}.jar

# create unversioned symlinks
(cd $RPM_BUILD_ROOT%{_javadir}/%{grname} && for jar in *-%{version}*; do ln -sf ${jar} ${jar/-%{version}/}; done)
pushd $RPM_BUILD_ROOT%{_javadir}
ln -sf %{grname}/%{usname}.jar %{usname}.jar
popd

install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
%if %{with_maven}
cp -pr target/docs/apidocs/* \
        $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
%else
cp -pr dist/docs/api/* \
        $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
%endif
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name} # ghost symlink

install -d -m 755 $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
cp LICENSE.txt $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%files 
%defattr(0644,root,root,0755)
%doc %{_docdir}/%{name}-%{version}/LICENSE.txt
%{_javadir}/%{grname}/*.jar
%{_javadir}/*.jar
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/%{usname}-%{version}.jar.*
%endif

%files javadoc
%defattr(0644,root,root,0755)
%doc %{_javadocdir}/%{name}-%{version}
%doc %{_javadocdir}/%{name}
