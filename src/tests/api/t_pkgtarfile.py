#!/usr/bin/python2.4
#
# CDDL HEADER START
#
# The contents of this file are subject to the terms of the
# Common Development and Distribution License (the "License").
# You may not use this file except in compliance with the License.
#
# You can obtain a copy of the license at usr/src/OPENSOLARIS.LICENSE
# or http://www.opensolaris.org/os/licensing.
# See the License for the specific language governing permissions
# and limitations under the License.
#
# When distributing Covered Code, include this CDDL HEADER in each
# file and include the License file at usr/src/OPENSOLARIS.LICENSE.
# If applicable, add the following below this CDDL HEADER, with the
# fields enclosed by brackets "[]" replaced with your own identifying
# information: Portions Copyright [yyyy] [name of copyright owner]
#
# CDDL HEADER END
#

#
# Copyright 2008 Sun Microsystems, Inc.  All rights reserved.
# Use is subject to license terms.
#

import unittest
import sys
import os
import tempfile
import shutil
import tarfile
import pkg.portable as portable
import pkg.pkgtarfile as pkgtarfile

# Set the path so that modules above can be found
path_to_parent = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, path_to_parent)
import pkg5unittest

class TestPkgTarFile(pkg5unittest.Pkg5TestCase):

        def setUp(self):
                self.tpath = tempfile.mkdtemp()

                cpath = tempfile.mkdtemp()
                filepath = os.path.join(cpath, "foo/bar")
                filename = "baz"
                create_path = os.path.join(filepath, filename)
                os.makedirs(filepath)
                wfp = file(create_path, "wb")
                buf = os.urandom(8192)
                wfp.write(buf)
                wfp.close()

                self.tarfile = os.path.join(self.tpath, "test.tar")

                tarfp = tarfile.open(self.tarfile, 'w')
                tarfp.add(create_path, "foo/bar/baz")
                tarfp.close()
                shutil.rmtree(cpath)
                
        def tearDown(self):
                shutil.rmtree(self.tpath)

        def testerrorlevelIsCorrect(self):
                p = pkgtarfile.PkgTarFile(self.tarfile, 'r')

                # "read-only" folders on Windows are not actually read-only so
                # the test below doesn't cause the exception to be raised
                if portable.is_admin() or portable.util.get_canonical_os_type() == "windows":
                        self.assert_(p.errorlevel == 2)
                        p.close()
                        return

                extractpath = os.path.join(self.tpath, "foo/bar")
                os.makedirs(extractpath)
                os.chmod(extractpath, 0555)
                self.assertRaises(IOError, p.extract, "foo/bar/baz",
                    self.tpath)
                p.close()
                os.chmod(extractpath, 777)


if __name__ == "__main__":
        unittest.main()
