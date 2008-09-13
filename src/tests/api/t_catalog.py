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

# Copyright 2008 Sun Microsystems, Inc.  All rights reserved.
# Use is subject to license terms.

import unittest
import shutil
import tempfile
import os
import datetime
import time
import sys

# Set the path so that modules above can be found
path_to_parent = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, path_to_parent)

import pkg5unittest

import pkg.fmri as fmri
import pkg.catalog as catalog
import pkg.updatelog as updatelog

class TestCatalog(pkg5unittest.Pkg5TestCase):
        def setUp(self):
                self.cpath = tempfile.mkdtemp()
                self.c = catalog.Catalog(self.cpath)
                self.npkgs = 0

                for f in [
                    fmri.PkgFmri("pkg:/test@1.0,5.11-1:20000101T120000Z", None),
                    fmri.PkgFmri("pkg:/test@1.0,5.11-1:20000101T120010Z", None),
                    fmri.PkgFmri("pkg:/test@1.0,5.11-1.1:20000101T120020Z", None),
                    fmri.PkgFmri("pkg:/test@1.0,5.11-1.2:20000101T120030Z", None),
                    fmri.PkgFmri("pkg:/test@1.0,5.11-2:20000101T120040Z", None),
                    fmri.PkgFmri("pkg:/test@1.1,5.11-1:20000101T120040Z", None),
                    fmri.PkgFmri("pkg:/apkg@1.0,5.11-1:20000101T120040Z", None),
                    fmri.PkgFmri("pkg:/zpkg@1.0,5.11-1:20000101T120040Z", None)
                ]:
                        self.c.add_fmri(f)
                        self.npkgs += 1

        def tearDown(self):
                shutil.rmtree(self.cpath)

        def testnpkgs(self):
                self.assert_(self.npkgs == self.c.npkgs())

        def testcatalogfmris1(self):
                cf = fmri.PkgFmri("pkg:/test@1.0,5.10-1:20070101T120000Z")
                cl = self.c.get_matching_fmris(cf)

                self.assert_(len(cl) == 4)

        def testcatalogfmris2(self):
                cf = fmri.PkgFmri("pkg:/test@1.0,5.11-1:20061231T120000Z")
                cl = self.c.get_matching_fmris(cf)

                self.assert_(len(cl) == 4)

        def testcatalogfmris3(self):
                cf = fmri.PkgFmri("pkg:/test@1.0,5.11-2")
                cl = self.c.get_matching_fmris(cf)

                self.assert_(len(cl) == 2)

        def testcatalogfmris4(self):
                cf = fmri.PkgFmri("pkg:/test@1.0,5.11-3")
                cl = self.c.get_matching_fmris(cf)

                self.assert_(len(cl) == 1)

class TestEmptyCatalog(pkg5unittest.Pkg5TestCase):
        def setUp(self):
                self.cpath = tempfile.mkdtemp()
                self.c = catalog.Catalog(self.cpath)
		self.nullf = file(os.devnull, "w")

        def tearDown(self):
                shutil.rmtree(self.cpath)
                self.nullf.close()

        def testmatchingfmris(self):
                cf = fmri.PkgFmri("pkg:/test@1.0,5.11-1:20061231T120000Z")
                cl = self.c.get_matching_fmris(cf)

                self.assert_(len(cl) == 0)

        def testfmris(self):
                r = []

                for f in self.c.fmris():
                        r.append(f)

                self.assert_(len(r) == 0)

        def testloadattrs(self):
                self.c.load_attrs()

        def testsend(self):
                self.c.send(self.nullf)

class TestCatalogRename(pkg5unittest.Pkg5TestCase):
        def setUp(self):
		self.cpath = tempfile.mkdtemp()
                self.c = catalog.Catalog(self.cpath)
                self.npkgs = 0

                for f in [
                    fmri.PkgFmri("pkg:/test@1.0,5.11-2:20000101T120040Z", None),
                    fmri.PkgFmri("pkg:/test@1.1,5.11-1:20000101T120040Z", None),
                    fmri.PkgFmri("pkg:/test@1.1,5.11-2:20000101T120040Z", None),
                ]:
                        self.c.add_fmri(f)
                        self.npkgs += 1

	def tearDown(self):
		shutil.rmtree(self.cpath)

        def testFMRIValidator(self):
                fa = fmri.PkgFmri("pkg:/Foo@1.2,5.11-1:20000101T120040Z", None)
                self.c.add_fmri(fa)
                self.npkgs += 1

                ts, rr = self.c.rename_package("test",
                    "1.2,5.11-1:20000101T120040Z", "Foo",
                    "1.2,5.11-1:20000101T120040Z")

                f1 = fmri.PkgFmri("pkg:/test@1.1,5.11-3:20000101T120040Z", None)
                f2 = fmri.PkgFmri("pkg:/Foo@1.3,5.11-1:20000101T120040Z", None)
                f3 = fmri.PkgFmri("pkg:/test@1.2,5.11-1:20000101T120040Z", None)

                self.assert_(self.c.valid_new_fmri(f1))
                self.assert_(self.c.valid_new_fmri(f2))
                self.failIf(self.c.valid_new_fmri(f3))

        def testMissingDest(self):
                self.assertRaises(catalog.CatalogException,
                    self.c.rename_package, "test",
                    "1.2,5.11-1:20000101T120040Z", "Foo",
                    "1.2,5.11-1:20000101T120040Z")

        def testPresentSrc(self):
                fa = fmri.PkgFmri("pkg:/test@1.2,5.11-1:20000101T120040Z", None)
                self.c.add_fmri(fa)
                self.npkgs += 1

                self.assertRaises(catalog.CatalogException,
                    self.c.rename_package, "test",
                    "1.2,5.11-1:20000101T120040Z", "Foo",
                    "1.2,5.11-1:20000101T120040Z")

        def testDuplicateRename(self):
                fa = fmri.PkgFmri("pkg:/Foo@1.2,5.11-1:20000101T120040Z", None)
                self.c.add_fmri(fa)
                self.npkgs += 1

                ts, rr = self.c.rename_package("test",
                    "1.2,5.11-1:20000101T120040Z", "Foo",
                    "1.2,5.11-1:20000101T120040Z")

                self.assertRaises(catalog.CatalogException,
                    self.c.rename_package, "test",
                    "1.2,5.11-1:20000101T120040Z", "Foo",
                    "1.2,5.11-1:20000101T120040Z")

        def testRenameConstraints(self):
                added_fmris = [
                    fmri.PkgFmri("pkg:/Foo@1.2,5.11-1:20000101T120040Z", None),
                    fmri.PkgFmri("pkg:/Moo@1.1,5.11-1:20000101T120040Z", None),
                    fmri.PkgFmri("pkg:/Woo@1.1,5.11-1:20000101T120040Z", None),
                ]
 
                for f in added_fmris:
                        self.c.add_fmri(f)
                        self.npkgs += 1

                ts, rr = self.c.rename_package("test",
                    "1.2,5.11-1:20000101T120040Z", "Foo",
                    "1.2,5.11-1:20000101T120040Z")

                self.assert_(self.c.fmri_renamed_dest(added_fmris[0]))

                ts, rr = self.c.rename_package("Foo",
                    "1.3,5.11-1:20000101T120040Z", "Moo",
                    "1.1,5.11-1:20000101T120040Z")

                self.assert_(self.c.fmri_renamed_dest(added_fmris[1]))

                ts, rr = self.c.rename_package("Moo",
                    "1.2,5.11-1:20000101T120040Z", "Woo",
                    "1.1,5.11-1:20000101T120040Z")

                self.assert_(self.c.fmri_renamed_dest(added_fmris[2]))

                self.assertRaises(catalog.RenameException,
                    self.c.rename_package, "Moo",
                    "1.2,5.11-1:20000101T120040Z", "Foo",
                    "1.2,5.11-1:20000101T120040Z")

                newfmris = [
                    fmri.PkgFmri("pkg:/Foo@1.1,5.11-1:20000101T120040Z", None),
                    fmri.PkgFmri("pkg:/Moo@1.0,5.11-1:20000101T120040Z", None),
                    fmri.PkgFmri("pkg:/Moo@1.1,5.11-2:20000101T120040Z", None),
                    fmri.PkgFmri("pkg:/Woo@1.2,5.11-1:20000101T120040Z", None),
                ]

                for f in newfmris:
                        self.c.add_fmri(f)
                        self.npkgs += 1

                # Make sure successors are correctly identified.
                tfmri = newfmris[3]
                self.assert_(self.c.rename_is_successor(tfmri, newfmris[2]))
                self.assert_(self.c.rename_is_successor(tfmri, newfmris[1]))
                self.assert_(self.c.rename_is_successor(tfmri, newfmris[0]))

                tfmri = newfmris[2]
                self.assert_(self.c.rename_is_successor(tfmri, newfmris[0]))

                # Note that this is a successor by version number, but not
                # by rename.
                self.failIf(self.c.rename_is_successor(tfmri, newfmris[1]))

                self.failIf(self.c.rename_is_successor(tfmri, newfmris[2]))
                self.failIf(self.c.rename_is_successor(tfmri, newfmris[3]))

                rec = self.c.fmri_renamed_dest(newfmris[1])
                lrec = [f for f in rec]
                self.failIf(len(lrec) > 0)

                rec = self.c.fmri_renamed_dest(newfmris[0])
                lrec = [f for f in rec]
                self.failIf(len(lrec) > 0)

                # Check that we can correctly identify predecessors, too
                tfmri = newfmris[3]
                self.assert_(self.c.rename_is_predecessor(newfmris[2], tfmri))
                self.assert_(self.c.rename_is_predecessor(newfmris[0], tfmri))
                self.failIf(self.c.rename_is_predecessor(tfmri, newfmris[0]))

                # Test that test@1.0 finds 3 renames that would be newer
                tfmri = fmri.PkgFmri("pkg:/test@1.0,5.11-2:20000101T120040Z",
                    None) 
                pkgs = self.c.rename_newer_pkgs(tfmri)
                self.assert_(len(pkgs) == 3)

                # Verify that the packages that have been renamed can be
                # considered equivalent by rename_is_same_pkg
                self.assert_(self.c.rename_is_same_pkg(added_fmris[0],
                        added_fmris[1]))
                self.assert_(self.c.rename_is_same_pkg(added_fmris[0],
                        added_fmris[2]))
                self.assert_(self.c.rename_is_same_pkg(added_fmris[1],
                        added_fmris[0]))
                self.assert_(self.c.rename_is_same_pkg(added_fmris[1],
                        added_fmris[2]))
                self.assert_(self.c.rename_is_same_pkg(added_fmris[2],
                        added_fmris[0]))
                self.assert_(self.c.rename_is_same_pkg(added_fmris[2],
                        added_fmris[1]))
                self.assert_(self.c.rename_is_same_pkg(newfmris[3],
                        newfmris[0]))

                # Make sure rename_is_same_pkg doesn't return false positive
                tfmri = fmri.PkgFmri("pkg:/zpkg@1.0,5.11-1:20000101T120040Z",
                    None)
                self.failIf(self.c.rename_is_same_pkg(tfmri, added_fmris[1]))

class TestUpdateLog(pkg5unittest.Pkg5TestCase):
        def setUp(self):
                self.cpath = tempfile.mkdtemp()
                self.c = catalog.Catalog(self.cpath)
                self.upath = tempfile.mkdtemp()
                self.ul = updatelog.UpdateLog(self.upath, self.c)
                self.npkgs = 0

                for f in [
                    fmri.PkgFmri("pkg:/test@1.0,5.11-1:20000101T120000Z", None),
                    fmri.PkgFmri("pkg:/test@1.0,5.11-1:20000101T120010Z", None),
                    fmri.PkgFmri("pkg:/test@1.0,5.11-1.1:20000101T120020Z", None),
                    fmri.PkgFmri("pkg:/test@1.0,5.11-1.2:20000101T120030Z", None),
                    fmri.PkgFmri("pkg:/test@1.0,5.11-2:20000101T120040Z", None),
                    fmri.PkgFmri("pkg:/test@1.1,5.11-1:20000101T120040Z", None),
                    fmri.PkgFmri("pkg:/apkg@1.0,5.11-1:20000101T120040Z", None),
                    fmri.PkgFmri("pkg:/zpkg@1.0,5.11-1:20000101T120040Z", None)
                ]:
                        self.ul.add_package(f)
                        self.npkgs += 1

                delta = datetime.timedelta(seconds = 1)
                self.ts1 = self.ul.first_update - delta
                self.ts2 = datetime.datetime.now()


        def tearDown(self):
                # python does not guarantee that destructors will
                # ever be called, so we explicitly call it here to
                # clean up the UpdateLog's internal state files.
                del(self.ul)
                shutil.rmtree(self.upath)
                shutil.rmtree(self.cpath)

        def testnohist(self):
                self.failIf(self.ul.enough_history(self.ts1))
                self.assert_(self.ul.enough_history(self.ts2))

        def testnotuptodate(self):
                self.assert_(self.ul.up_to_date(self.ts2))
                self.failIf(self.ul.up_to_date(self.ts1))

        def testoneupdate(self):
                # Create new catalog
                cnp = tempfile.mkdtemp()
                cfd, cfpath = tempfile.mkstemp()
                cfp = os.fdopen(cfd, "w")

                # send original catalog
                self.c.send(cfp)
                cfp.close()
                # recv the sent catalog
                cfp = file(cfpath, "r")
                catalog.recv(cfp, cnp)
                # Cleanup cfp
                cfp.close()
                cfp = None
                cfd = None
                os.remove(cfpath)
                cfpath = None

                # Instantiate Catalog object based upon recd. catalog
                cnew = catalog.Catalog(cnp)

                # Verify original packages present
                cf = fmri.PkgFmri("pkg:/test@1.0,5.10-1:20070101T120000Z")
                cl = cnew.get_matching_fmris(cf)

                self.assert_(len(cl) == 4)
                # a sleep here is needed on Windows to make sure that the time
                # of the update is different from the time of the original catalog
                time.sleep(0.5)
                
                # Add new FMRI
                fnew = fmri.PkgFmri("pkg:/test@1.0,5.11-3:20000101T120040Z")
                self.ul.add_package(fnew)

                # Send an update
                cfd, cfpath = tempfile.mkstemp()
                cfp = os.fdopen(cfd, "w")

                lastmod = catalog.ts_to_datetime(cnew.last_modified())
                self.ul._send_updates(lastmod, cfp)
                cfp.close()

                # Recv the update
                cfp = file(cfpath, "r")
                updatelog.UpdateLog._recv_updates(cfp, cnp, cnew.last_modified())
                cfp.close()
                cfp = None
                cfd = None
                os.remove(cfpath)
                cfpath = None

                # Reload the catalog
                cnew = catalog.Catalog(cnp)

                # Verify new package present
                cf = fmri.PkgFmri("pkg:/test@1.0,5.11-3:20000101T120040Z")
                cl = cnew.get_matching_fmris(cf)

                self.assert_(len(cl) == 2)

                # Cleanup new catalog
                shutil.rmtree(cnp)

        def testsequentialupdate(self):
                # Create new catalog
                cnp = tempfile.mkdtemp()
                cfd, cfpath = tempfile.mkstemp()
                cfp = os.fdopen(cfd, "w")

                # send original catalog
                self.c.send(cfp)
                cfp.close()
                # recv the sent catalog
                cfp = file(cfpath, "r")
                catalog.recv(cfp, cnp)
                # Cleanup cfp
                cfp.close()
                cfp = None
                cfd = None
                os.remove(cfpath)
                cfpath = None

                # Instantiate Catalog object based upon recd. catalog
                cnew = catalog.Catalog(cnp)

                # Verify original packages present
                cf = fmri.PkgFmri("pkg:/test@1.0,5.10-1:20070101T120000Z")
                cl = cnew.get_matching_fmris(cf)

                self.assert_(len(cl) == 4)
                # a sleep here is needed on Windows to make sure that the time
                # of the update is different from the time of the original catalog
                time.sleep(0.5)
                
                # Add new FMRI
                fnew = fmri.PkgFmri("pkg:/bpkg@1.0,5.11-3:20000101T120040Z")
                self.ul.add_package(fnew)

                # Send an update
                cfd, cfpath = tempfile.mkstemp()
                cfp = os.fdopen(cfd, "w")

                lastmod = catalog.ts_to_datetime(cnew.last_modified())
                self.ul._send_updates(lastmod, cfp)
                cfp.close()

                # Recv the update
                cfp = file(cfpath, "r")
                updatelog.UpdateLog._recv_updates(cfp, cnp, cnew.last_modified())
                cfp.close()
                cfp = None
                cfd = None
                os.remove(cfpath)
                cfpath = None

                # Reload the catalog
                cnew = catalog.Catalog(cnp)

                # Verify new package present
                cf = fmri.PkgFmri("pkg:/bpkg@1.0,5.11-3:20000101T120040Z")
                cl = cnew.get_matching_fmris(cf)

                self.assert_(len(cl) == 1)
                # a sleep here is needed on Windows to make sure that the time
                # of the update is different from the time of the original catalog
                time.sleep(0.5)
                
                # Add a pair of FMRIs
                f2 = fmri.PkgFmri("pkg:/cpkg@1.0,5.11-3:20000101T120040Z")
                f3 = fmri.PkgFmri("pkg:/dpkg@1.0,5.11-3:20000101T120040Z")
                self.ul.add_package(f2)
                self.ul.add_package(f3)

                # Send another update
                cfd, cfpath = tempfile.mkstemp()
                cfp = os.fdopen(cfd, "w")

                lastmod = catalog.ts_to_datetime(cnew.last_modified())
                self.ul._send_updates(lastmod, cfp)
                cfp.close()

                # Recv the update
                cfp = file(cfpath, "r")
                updatelog.UpdateLog._recv_updates(cfp, cnp, cnew.last_modified())
                cfp.close()
                cfp = None
                cfd = None
                os.remove(cfpath)
                cfpath = None

                # Reload catalog
                cnew = catalog.Catalog(cnp)

                # Verify New packages present
                cf = fmri.PkgFmri("pkg:/cpkg@1.0,5.11-3:20000101T120040Z")
                cl = cnew.get_matching_fmris(cf)
                
                self.assert_(len(cl) == 1)

                cf = fmri.PkgFmri("pkg:/dpkg@1.0,5.11-3:20000101T120040Z")
                cl = cnew.get_matching_fmris(cf)

                self.assert_(len(cl) == 1)

                # Cleanup new catalog
                shutil.rmtree(cnp)

        def testrolllogfiles(self):
                # Write files with out-of-date timestamps into the updatelog
                # directory

                for i in range(2001010100, 2001010111, 1):
                        f = file(os.path.join(self.upath, "%s" % i), "w")
                        f.close()

                # Reload UpdateLog with maxfiles set to 1
                self.ul = updatelog.UpdateLog(self.upath, self.c, 1)

                # Adding a package should open a new logfile, and remove the
                # extra old ones
                cf = fmri.PkgFmri("pkg:/cpkg@1.0,5.11-3:20000101T120040Z")
                self.ul.add_package(cf)

                # Check that only one file remains in the directory
                dl = os.listdir(self.upath)
                self.assert_(len(dl) == 1)

if __name__ == "__main__":
        unittest.main()
