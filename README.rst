Libryum - lightweight Lbry client
=====================================

::

  Licence: GNU GPL v3
  Author: Thomas Voegtlin
  Language: Python
  Homepage: https://electrum.org/


1. GETTING STARTED
------------------

To run Libryum from this directory, just do::

    ./libryum

If you install Libryum on your system, you can run it from any
directory.


2. HOW OFFICIAL PACKAGES ARE CREATED
------------------------------------

On Linux/Windows::

    pyrcc4 icons.qrc -o gui/qt/icons_rc.py
    python setup.py sdist --format=zip,gztar

On Mac OS X::

    # On port based installs
    sudo python setup-release.py py2app

    # On brew installs
    ARCHFLAGS="-arch i386 -arch x86_64" sudo python setup-release.py py2app --includes sip

    sudo hdiutil create -fs HFS+ -volname "Libryum" -srcfolder dist/Libryum.app dist/libryum-VERSION-macosx.dmg
