%include %{_sourcedir}/common.inc

Name:     colorama
Version:  0.3.3
Release:  1%{?dist}
Summary:  Cross-platform colored terminal text
Source:   %{name}-%{version}.tar.gz
Source1:  common.inc

License:  BSD
Group:    Development/Libraries
URL:      https://pypi.python.org/pypi/colorama
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: python
BuildArch: noarch

%description
Makes ANSI escape character sequences for producing colored terminal text and cursor positioning work under MS Windows.

ANSI escape character sequences have long been used to produce colored terminal text and cursor positioning on Unix and Macs. Colorama makes this work on Windows, too, by wrapping stdout, stripping ANSI sequences it finds (which otherwise show up as gobbledygook in your output), and converting them into the appropriate win32 calls to modify the state of the terminal. On other platforms, Colorama does nothing.

Colorama also provides some shortcuts to help generate ANSI sequences but works fine in conjunction with any other ANSI sequence generation library, such as Termcolor (http://pypi.python.org/pypi/termcolor.)

This has the upshot of providing a simple cross-platform API for printing colored terminal text from Python, and has the happy side-effect that existing applications or libraries which use ANSI sequences to produce colored output on Linux or Macs can now also work on Windows, simply by calling colorama.init().

An alternative approach is to install ‘ansi.sys’ on Windows machines, which provides the same behaviour for all applications running in terminals. Colorama is intended for situations where that isn’t easy (e.g. maybe your app doesn’t have an installer.)

%prep
%setup -q -n %{name}-%{version}

%build
env CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{_datadir} --single-version-externally-managed --record=/dev/null

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/
