#!/usr/bin/env python
import os
import numpy
from util import unformatted, blocked, full
from basinfo import BasInfo

class SiriusRestart(unformatted.FortranBinary):
    def __init__(self, name="SIRIUS.RST"):
        unformatted.FortranBinary.__init__(self, name)
        self.basinfo = BasInfo(name)
        self.cmo = self.getcmo()
        #self.close()

    def __str__(self):
        retstr=""
        retstr+="\nNSYM : " + str(self.basinfo.nsym)
        retstr+="\nNBAS : " + str(self.basinfo.nbas)
        retstr+="\nNBAST: " + str(self.basinfo.nbast)
        retstr+="\nNORB : " + str(self.basinfo.norb)
        retstr+="\nNORBT: " + str(self.basinfo.norbt)
        retstr+="\nNRHF : " + str(self.basinfo.nrhf)
        retstr+="\nIOPRHF:" + str(self.basinfo.ioprhf)
        retstr+="\nCMO:   " + str(self.cmo)
        return retstr

    def getcmo(self):
        self.find("NEWORB")
        ncmot4=max(self.basinfo.ncmot,4)
        cmo_rec=self.next()
        assert cmo_rec.reclen/8 == numpy.dot(self.basinfo.nbas, self.basinfo.norb)
        n=0
        cmo=blocked.BlockDiagonalMatrix(self.basinfo.nbas, self.basinfo.norb)
        for isym in range(self.basinfo.nsym):
            cmoi = numpy.array(cmo_rec.read(self.basinfo.nbas[isym]*self.basinfo.norb[isym],'d')
                   ).reshape((self.basinfo.nbas[isym], self.basinfo.norb[isym]), order='F')
            cmo.subblock[isym] = cmoi.view(full.matrix)
        return cmo

def cmo_from_targz(targz):
    """Extract cmo from SIRIUS.RST in tar ball"""

    tempdir = unpack_file_in_tempdir(targz, 'SIRIUS.RST')

    sirius_rst = SiriusRestart(os.path.join(tempdir, 'SIRIUS.RST'))
    cmo = sirius_rst.cmo

    os.remove(sirius_rst.name)
    os.rmdir(tempdir)

    return cmo

def unpack_file_in_tempdir(targz, filename):

    import tarfile, tempfile
    tempdir = tempfile.mkdtemp()
    tarball = tarfile.open(targz, 'r:gz')
    tarball.extract('SIRIUS.RST', tempdir)

    return tempdir

if __name__ == "__main__":
    import os, sys
    try:
        rst=SiriusRestart(sys.argv[1])
    except IndexError:
        print "Usage: %s [<path>/]SIRIUS.RST"
        sys.exit(1)
    print rst

