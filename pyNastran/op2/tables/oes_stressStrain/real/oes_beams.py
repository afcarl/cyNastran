from __future__ import (nested_scopes, generators, division, absolute_import,
                        print_function, unicode_literals)

from .oes_objects import StressObject, StrainObject
from pyNastran.f06.f06_formatting import writeFloats13E


class RealBeamStress(StressObject):
    """
    ::

      [1,0,0]
                   S T R E S S E S   I N   B E A M   E L E M E N T S        ( C B E A M )
                        STAT DIST/
       ELEMENT-ID  GRID   LENGTH    SXC           SXD           SXE           SXF           S-MAX         S-MIN         M.S.-T   M.S.-C
              1       1   0.000   -3.125000E+04 -3.125000E+04 -3.125000E+04 -3.125000E+04 -3.125000E+04 -3.125000E+04
                      2   1.000   -3.125000E+04 -3.125000E+04 -3.125000E+04 -3.125000E+04 -3.125000E+04 -3.125000E+04
    """
    def __init__(self, data_code, is_sort1, isubcase, dt):
        StressObject.__init__(self, data_code, isubcase)
        self.eType = 'CBEAM'

        self.code = [self.format_code, self.sort_code, self.s_code]
        self.xxb = {}
        self.grids = {}
        self.smax = {}
        self.smin = {}
        self.MS_tension = {}
        self.MS_compression = {}

        self.sxc = {}
        self.sxd = {}
        self.sxe = {}
        self.sxf = {}
        #self.isImaginary = False

        self.dt = dt
        if is_sort1:
            if dt is not None:
                self.add = self.add_sort1
                self.add_new_eid = self.add_new_eid_sort1
        #else:
            #assert dt is not None
            #self.add = self.add_sort2
            #self.add_new_eid = self.add_new_eid_sort2

    def get_stats(self):
        msg = self.get_data_code()
        if self.dt is not None:  # transient
            ntimes = len(self.smax)
            s0 = self.smax.keys()[0]
            nelements = len(self.smax[s0])
            msg.append('  type=%s ntimes=%s nelements=%s\n'
                       % (self.__class__.__name__, ntimes, nelements))
        else:
            nelements = len(self.smax)
            msg.append('  type=%s nelements=%s\n' % (self.__class__.__name__,
                                                     nelements))
        msg.append('  eType, xxb, grids, smax, smin, MS_tension, '
                   'MS_compression, sxc, sxd, sxe, sxf\n')
        return msg

    def getLengthTotal(self):
        return 444  # 44+10*40   (11 nodes)

    def getLength1(self):
        return (44, 'ifffffffff')

    def getLength2(self):
        return (40, 'ifffffffff')

    def delete_transient(self, dt):
        del self.sxc[dt]
        del self.sxd[dt]
        del self.sxe[dt]
        del self.sxf[dt]
        del self.smax[dt]
        del self.smin[dt]
        del self.MS_tension[dt]
        del self.MS_compression[dt]

    def get_transients(self):
        k = self.smax.keys()
        k.sort()
        return k

    def add_new_transient(self, dt):
        """
        initializes the transient variables
        """
        #print "addNewTransient_beam+1+0"
        self.dt = dt
        self.sxc[dt] = {}
        self.sxd[dt] = {}
        self.sxe[dt] = {}
        self.sxf[dt] = {}
        self.smax[dt] = {}
        self.smin[dt] = {}
        self.MS_tension[dt] = {}
        self.MS_compression[dt] = {}

    def add_new_eid(self, dt, eid, out):
        #print "Beam Stress add_new_eid..."
        (grid, sd, sxc, sxd, sxe, sxf, smax, smin, mst, msc) = out
        #print "eid=%s grid=%s" %(eid,grid)
        assert eid >= 0
        #assert isinstance(eid,int)
        #assert isinstance(grid,int)
        self.grids[eid] = [grid]
        self.xxb[eid] = [sd]
        self.sxc[eid] = [sxc]
        self.sxd[eid] = [sxd]
        self.sxe[eid] = [sxe]
        self.sxf[eid] = [sxf]
        self.smax[eid] = [smax]
        self.smin[eid] = [smin]
        self.MS_tension[eid] = [mst]
        self.MS_compression[eid] = [msc]
        return eid

    def add_f06_data(self, data, dt):
        if dt is not None:
            raise NotImplementedError(dt)
        for datai in data:
            (eid, grid, sd, sxc, sxd, sxe, sxf, smax, smin, mst, msc) = datai
            if eid in self.grids:
                self.grids[eid].append(grid)
                self.xxb[eid].append(sd)
                self.sxc[eid].append(sxc)
                self.sxd[eid].append(sxd)
                self.sxe[eid].append(sxe)
                self.sxf[eid].append(sxf)
                self.smax[eid].append(smax)
                self.smin[eid].append(smin)
                self.MS_tension[eid].append(mst)
                self.MS_compression[eid].append(msc)
            else:
                self.grids[eid] = [grid]
                self.xxb[eid] = [sd]
                self.sxc[eid] = [sxc]
                self.sxd[eid] = [sxd]
                self.sxe[eid] = [sxe]
                self.sxf[eid] = [sxf]
                self.smax[eid] = [smax]
                self.smin[eid] = [smin]
                self.MS_tension[eid] = [mst]
                self.MS_compression[eid] = [msc]

    def add_new_eid_sort1(self, dt, eid, out):
        #print "Beam Transient Stress add_new_eid..."
        (grid, sd, sxc, sxd, sxe, sxf, smax, smin, mst, msc) = out

        assert eid >= 0
        if dt not in self.sxc:
            self.add_new_transient(dt)
        self.grids[eid] = [grid]
        self.xxb[eid] = [sd]
        self.sxc[dt][eid] = [sxc]
        self.sxd[dt][eid] = [sxd]
        self.sxe[dt][eid] = [sxe]
        self.sxf[dt][eid] = [sxf]
        self.smax[dt][eid] = [smax]
        self.smin[dt][eid] = [smin]
        self.MS_tension[dt][eid] = [mst]
        self.MS_compression[dt][eid] = [msc]
        return eid

    def add(self, dt, eid, out):
        #print "Beam Stress add..."
        (grid, sd, sxc, sxd, sxe, sxf, smax, smin, mst, msc) = out
        if grid:
            self.grids[eid].append(grid)
            self.xxb[eid].append(sd)
            self.sxc[eid].append(sxc)
            self.sxd[eid].append(sxd)
            self.sxe[eid].append(sxe)
            self.sxf[eid].append(sxf)
            self.smax[eid].append(smax)
            self.smin[eid].append(smin)
            self.MS_tension[eid].append(mst)
            self.MS_compression[eid].append(msc)

    def add_sort1(self, dt, eid, out):
        #print "Beam Transient Stress add..."
        (grid, sd, sxc, sxd, sxe, sxf, smax, smin, mst, msc) = out
        if grid:
            self.grids[eid].append(grid)
            self.xxb[eid].append(sd)
            #self.sd[dt][eid].append(sd)
            self.sxc[dt][eid].append(sxc)
            self.sxd[dt][eid].append(sxd)
            self.sxe[dt][eid].append(sxe)
            self.sxf[dt][eid].append(sxf)
            self.smax[dt][eid].append(smax)
            self.smin[dt][eid].append(smin)
            self.MS_tension[dt][eid].append(mst)
            self.MS_compression[dt][eid].append(msc)

    def write_f06(self, header, pageStamp, page_num=1, f=None, is_mag_phase=False):
        if self.nonlinear_factor is not None:
            return self._write_f06_transient(header, pageStamp, page_num, f)

        msg = header + ['                                  S T R E S S E S   I N   B E A M   E L E M E N T S        ( C B E A M )\n',
                        '                    STAT DIST/\n',
                        '   ELEMENT-ID  GRID   LENGTH    SXC           SXD           SXE           SXF           S-MAX         S-MIN         M.S.-T   M.S.-C\n']

        for eid in sorted(self.smax):
            msg.append('0  %8i\n' % (eid))
            #print self.xxb[eid]
            for i, nid in enumerate(self.grids[eid]):
                #print i,nid
                xxb = self.xxb[eid][i]
                sxc = self.sxc[eid][i]
                sxd = self.sxd[eid][i]
                sxe = self.sxe[eid][i]
                sxf = self.sxf[eid][i]
                sMax = self.smax[eid][i]
                sMin = self.smin[eid][i]
                SMt = self.MS_tension[eid][i]
                SMc = self.MS_compression[eid][i]
                (vals2, is_all_zeros) = writeFloats13E([sxc, sxd, sxe, sxf, sMax, sMin, SMt, SMc])
                (sxc, sxd, sxe, sxf, sMax, sMin, SMt, SMc) = vals2
                msg.append('%19s   %4.3f   %12s %12s %12s %12s %12s %12s %12s %s\n' % (nid, xxb, sxc, sxd, sxe, sxf, sMax, sMin, SMt, SMc.strip()))

        msg.append(pageStamp % page_num)
        f.write(''.join(msg))
        return page_num

    def _write_f06_transient(self, header, pageStamp, page_num=1, f=None, is_mag_phase=False):
        words = ['                                  S T R E S S E S   I N   B E A M   E L E M E N T S        ( C B E A M )\n',
                 '                    STAT DIST/\n',
                 '   ELEMENT-ID  GRID   LENGTH    SXC           SXD           SXE           SXF           S-MAX         S-MIN         M.S.-T   M.S.-C\n']
        msg = []
        for dt, SMaxs in sorted(self.smax.iteritems()):
            header[1] = ' %s = %10.4E\n' % (self.data_code['name'], dt)
            msg += header + words
            for eid, Smax in sorted(SMaxs.iteritems()):
                msg.append('0  %8i\n' % (eid))
                for i, nid in enumerate(self.grids[eid]):
                    xxb = self.xxb[eid][i]
                    #sd  = self.sd[eid][i]
                    sxc = self.sxc[dt][eid][i]
                    sxd = self.sxd[dt][eid][i]
                    sxe = self.sxe[dt][eid][i]
                    sxf = self.sxf[dt][eid][i]
                    sMax = self.smax[dt][eid][i]
                    sMin = self.smin[dt][eid][i]
                    SMt = self.MS_tension[dt][eid][i]
                    SMc = self.MS_compression[dt][eid][i]
                    (vals2, is_all_zeros) = writeFloats13E([sxc, sxd,
                                                          sxe, sxf, sMax, sMin, SMt, SMc])
                    (sxc, sxd, sxe, sxf, sMax, sMin, SMt, SMc) = vals2
                    msg.append('%19s   %4.3f   %12s %12s %12s %12s %12s %12s %12s %s\n' % (nid, xxb, sxc, sxd, sxe, sxf, sMax, sMin, SMt, SMc.strip()))

            msg.append(pageStamp % page_num)
            f.write(''.join(msg))
            msg = ['']
            page_num += 1
        return page_num - 1


class RealBeamStrain(StrainObject):
    def __init__(self, data_code, is_sort1, isubcase, dt):
        StrainObject.__init__(self, data_code, isubcase)
        self.eType = 'CBEAM'  # {} # 'CBEAM/CONBEAM'

        self.code = [self.format_code, self.sort_code, self.s_code]

        self.xxb = {}
        self.grids = {}
        self.sxc = {}
        self.sxd = {}
        self.sxe = {}
        self.sxf = {}
        self.smax = {}
        self.smin = {}
        self.MS_tension = {}
        self.MS_compression = {}

        if is_sort1:
            if dt is not None:
                #self.add_new_transient = self.add_new_transient
                self.add_new_eid = self.add_new_eid_sort1
                self.add = self.add_sort1
                self.add_new_transient(dt)
            #self.add_new_eid = self.add_new_eid
            #self.add = self.add
        #else:
            #raise  RuntimeError("Invalid Code: beamStress - get the format/sort/stressCode=%s" % (self.code))
        #if dt is not None:
            #self.isTransient = True
            #self.dt = self.nonlinear_factor
            #self.add_new_transient(dt)

    def add_f06_data(self, data, dt):
        if dt is not None:
            raise NotImplementedError(dt)
        for datai in data:
            #print('smax', self.smax)
            (eid, grid, sd, sxc, sxd, sxe, sxf, smax, smin, mst, msc) = datai
            #print('(*')
            if eid in self.grids:
                self.grids[eid].append(grid)
                self.xxb[eid].append(sd)
                self.sxc[eid].append(sxc)
                self.sxd[eid].append(sxd)
                self.sxe[eid].append(sxe)
                self.sxf[eid].append(sxf)
                self.smax[eid].append(smax)
                self.smin[eid].append(smin)
                self.MS_tension[eid].append(mst)
                self.MS_compression[eid].append(msc)
            else:
                self.grids[eid] = [grid]
                self.xxb[eid] = [sd]
                self.sxc[eid] = [sxc]
                self.sxd[eid] = [sxd]
                self.sxe[eid] = [sxe]
                self.sxf[eid] = [sxf]
                self.smax[eid] = [smax]
                self.smin[eid] = [smin]
                self.MS_tension[eid] = [mst]
                self.MS_compression[eid] = [msc]
        #print('smax', self.smax)

    def get_stats(self):
        nelements = len(self.eType)

        msg = self.get_data_code()
        if self.dt is not None:  # transient
            ntimes = len(self.smax)
            s0 = self.smax.keys()[0]
            nelements = len(self.smax[s0])
            msg.append('  type=%s ntimes=%s nelements=%s\n'
                       % (self.__class__.__name__, ntimes, nelements))
        else:
            nelements = len(self.smax)
            msg.append('  type=%s nelements=%s\n' % (self.__class__.__name__,
                                                     nelements))
        msg.append('  eType, xxb, grids, smax, smin, MS_tension, '
                   'MS_compression, sxc, sxd, sxe, sxf\n')
        return msg

    def getLengthTotal(self):
        return 444  # 44+10*40   (11 nodes)

    def getLength1(self):
        return (44, 'i9f')

    def getLength2(self):
        return (40, 'i9f')

    def delete_transient(self, dt):
        del self.sxc[dt]
        del self.sxd[dt]
        del self.sxe[dt]
        del self.sxf[dt]
        del self.smax[dt]
        del self.smin[dt]
        del self.MS_tension[dt]
        del self.MS_compression[dt]

    def get_transients(self):
        k = self.smax.keys()
        k.sort()
        return k

    def add_new_transient(self, dt):
        """
        initializes the transient variables
        .. note:: make sure you set self.dt first
        """
        #print "addNewTransient_beam+1+0"
        self.dt = dt
        self.grids = {}
        self.xxb = {}
        self.sxc[dt] = {}
        self.sxd[dt] = {}
        self.sxe[dt] = {}
        self.sxf[dt] = {}
        self.smax[dt] = {}
        self.smin[dt] = {}
        self.MS_tension[dt] = {}
        self.MS_compression[dt] = {}

    def add_new_eid(self, dt, eid, out):
        #print "Beam Stress add_new_eid..."
        (grid, sd, sxc, sxd, sxe, sxf, smax, smin, mst, msc) = out
        #print "eid=%s grid=%s" %(eid,grid)
        assert eid >= 0
        #assert isinstance(eid,int)
        #assert isinstance(grid,int)
        self.grids[eid] = [grid]
        self.xxb[eid] = [sd]
        self.sxc[eid] = [sxc]
        self.sxd[eid] = [sxd]
        self.sxe[eid] = [sxe]
        self.sxf[eid] = [sxf]
        self.smax[eid] = [smax]
        self.smin[eid] = [smin]
        self.MS_tension[eid] = [mst]
        self.MS_compression[eid] = [msc]
        return eid

    def add(self, dt, eid, out):
        #print "Beam Stress add..."
        (grid, sd, sxc, sxd, sxe, sxf, smax, smin, mst, msc) = out
        if grid:
            self.grids[eid].append(grid)
            self.xxb[eid].append(sd)
            self.sxc[eid].append(sxc)
            self.sxd[eid].append(sxd)
            self.sxe[eid].append(sxe)
            self.sxf[eid].append(sxf)
            self.smax[eid].append(smax)
            self.smin[eid].append(smin)
            self.MS_tension[eid].append(mst)
            self.MS_compression[eid].append(msc)

    def add_new_eid_sort1(self, dt, eid, out):
        #print "Beam Transient Stress add_new_eid..."
        (grid, sd, sxc, sxd, sxe, sxf, smax, smin, mst, msc) = out

        assert eid >= 0
        if dt not in self.sxc:
            self.add_new_transient(dt)

        self.grids[eid] = [grid]
        self.xxb[eid] = [sd]
        self.sxc[dt][eid] = [sxc]
        self.sxd[dt][eid] = [sxd]
        self.sxe[dt][eid] = [sxe]
        self.sxf[dt][eid] = [sxf]
        self.smax[dt][eid] = [smax]
        self.smin[dt][eid] = [smin]
        self.MS_tension[dt][eid] = [mst]
        self.MS_compression[dt][eid] = [msc]
        return eid

    def add_sort1(self, dt, eid, out):
        (grid, sd, sxc, sxd, sxe, sxf, smax, smin, mst, msc) = out
        if grid:
            self.grids[eid].append(grid)
            self.xxb[eid].append(sd)
            self.sxc[dt][eid].append(sxc)
            self.sxd[dt][eid].append(sxd)
            self.sxe[dt][eid].append(sxe)
            self.sxf[dt][eid].append(sxf)
            self.smax[dt][eid].append(smax)
            self.smin[dt][eid].append(smin)
            self.MS_tension[dt][eid].append(mst)
            self.MS_compression[dt][eid].append(msc)

    def write_f06(self, header, pageStamp, page_num=1, f=None, is_mag_phase=False):
        if self.nonlinear_factor is not None:
            return self._write_f06_transient(header, pageStamp, page_num, f)

        msg = header + ['                                  S T R A I N S   I N   B E A M   E L E M E N T S        ( C B E A M )\n',
                        '                    STAT DIST/\n',
                        '   ELEMENT-ID  GRID   LENGTH    SXC           SXD           SXE           SXF           S-MAX         S-MIN         M.S.-T   M.S.-C\n']

        for eid in sorted(self.smax):
            msg.append('0  %8i\n' % eid)
            #print self.xxb[eid]
            #print("self.grids =", self.grids)
            #print("eid =", eid)
            for i, nid in enumerate(self.grids[eid]):
                xxb = self.xxb[eid][i]
                sxc = self.sxc[eid][i]
                sxd = self.sxd[eid][i]
                sxe = self.sxe[eid][i]
                sxf = self.sxf[eid][i]
                sMax = self.smax[eid][i]
                sMin = self.smin[eid][i]
                SMt = self.MS_tension[eid][i]
                SMc = self.MS_compression[eid][i]
                (vals2, is_all_zeros) = writeFloats13E([
                    sxc, sxd, sxe, sxf, sMax, sMin, SMt, SMc])
                (sxc, sxd, sxe, sxf, sMax, sMin, SMt, SMc) = vals2
                msg.append('%19s   %4.3f   %12s %12s %12s %12s %12s %12s %12s %s\n' % (nid, xxb, sxc, sxd, sxe, sxf, sMax, sMin, SMt, SMc))

        msg.append(pageStamp % page_num)
        f.write(''.join(msg))
        return page_num

    def _write_f06_transient(self, header, pageStamp, page_num=1, f=None, is_mag_phase=False):
        words = ['                                  S T R A I N S   I N   B E A M   E L E M E N T S        ( C B E A M )\n',
                 '                    STAT DIST/\n',
                 '   ELEMENT-ID  GRID   LENGTH    SXC           SXD           SXE           SXF           S-MAX         S-MIN         M.S.-T   M.S.-C\n']
        msg = []
        for dt, SMaxs in sorted(self.smax.iteritems()):
            header[1] = ' %s = %10.4E\n' % (self.data_code['name'], dt)
            msg += header + words
            for eid, Smax in sorted(SMaxs.iteritems()):
                msg.append('0  %8i\n' % (eid))
                for i, nid in enumerate(self.grids[eid]):
                    xxb = self.xxb[eid][i]
                    sxc = self.sxc[dt][eid][i]
                    sxd = self.sxd[dt][eid][i]
                    sxe = self.sxe[dt][eid][i]
                    sxf = self.sxf[dt][eid][i]
                    sMax = self.smax[dt][eid][i]
                    sMin = self.smin[dt][eid][i]
                    SMt = self.MS_tension[dt][eid][i]
                    SMc = self.MS_compression[dt][eid][i]
                    (vals2, is_all_zeros) = writeFloats13E([sxc, sxd, sxe, sxf,
                                                          sMax, sMin, SMt, SMc])
                    (sxc, sxd, sxe, sxf, sMax, sMin, SMt, SMc) = vals2
                    msg.append('%19s   %4.3f   %12s %12s %12s %12s %12s %12s %12s %s\n' % (nid, xxb, sxc, sxd, sxe, sxf, sMax, sMin, SMt, SMc))

            msg.append(pageStamp % page_num)
            f.write(''.join(msg))
            msg = ['']
            page_num += 1
        return page_num - 1
