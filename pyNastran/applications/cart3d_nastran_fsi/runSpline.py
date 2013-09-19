import os
import sys
from numpy import pi,zeros,array,matrix #,float64,memmap
from numpy import log as naturalLog
from numpy.linalg import inv
from mapping.FEM_Mesh import FEM_Mesh
from grom.py2matlab import MatPrint

from mapping.logger import dummyLogger
loggerObj = dummyLogger()
log = loggerObj.startLog('debug') # or info


def readF06(infile):
    from mapping.f06 import F06Reader
    reader = F06Reader(infile)
    displacements = reader.readDisplacement()
    return displacements

def readOP2(infilename):
    from mapping.op2Reader.Op2Reader import OP2Reader
    log().info('---starting deflectionReader.init of %s---' %(infilename) )
    op2 = OP2Reader(infilename)
    terms = ['force','stress','stress_comp','strain','strain_comp','displacement','grid_point_forces']
    op2.read(terms)
    displacements = op2.nastranModel.displacement
    #op2.nastranModel.printDisplacement()
    displacements = convertDisplacements(displacements)
    log().info('---finished deflectionReader.init of %s---' %(infilename))
    return displacements

def convertDisplacements(displacements):
    """
    converts the deflecions from the op2reader to the format used for mapping
    """
    case = '_SUBCASE 1'
    log().info("displacement.keys() = %s" %(displacements.keys()))
    results = displacements[case]

    deflections = {}
    for gridID,result in results.items():
        #print "gridID = %s" %(gridID)
        layers = result.getLayers()

        for layer in layers:
            #print "layer = ",layer
            #print "  disp.mag = ",layer.mag
            deflections[gridID] = array(layer.mag)
    return deflections

def readCart3dPoints(cfdGridFile):
    """return half model points to shrink xK matrix"""
    from mapping.cart3d_reader import Cart3DReader
    cart = Cart3DReader(cfdGridFile)
    (points,elements,regions,loads) = cart.read()
    (points,elements,regions,loads) = cart.makeHalfModel(points,elements,regions,loads)
    return points

def writeNewCart3dMesh(cfdGridFile,cfdGridFile2,wA):
    """takes in half model wA, and baseline cart3d model, updates full model grids"""
    log().info("---starting writeNewCart3dMesh---")
    from mapping.cart3d_reader import Cart3DReader

    # make half model
    cart = Cart3DReader(cfdGridFile)
    (points,elements,regions,loads) = cart.read() # reading full model
    (points,elements,regions,loads) = cart.makeHalfModel(points,elements,regions,loads)

    # adjusting points
    points2 = {}
    for (iPoint,point) in sorted(points.items()):
        wai = wA[iPoint]
        (x,y,z) = point
        points2[iPoint] = [x,y,z+wai]
    ###

    (points,elements,regions,loads) = cart.makeMirrorModel(points2,elements,regions,loads)  # mirroring model
    cart.writeOutfile(cfdGridFile2,points,elements,regions) # writing half model  (cleans up leftover parameters)

    log().info("---finished writeNewCart3dMesh---")
    sys.stdout.flush()


def removeDuplicateNodes(nodeList,mesh):
    """
    Removes nodes that have the same (x,y) coordinate.
    Note that if 2 nodes with different z values are found, only 1 is returned.
    This is intentional.   splineSurface = f(x,y)
    """
    nodeList.sort()
    log().info("nodeListA = %s" %(nodeList))
    nodeDict = {}
    for iNode in nodeList:
        (x,y,z) = mesh.Node(iNode).Position()
        nodeDict[(x,y)] = iNode
    nodeList = nodeDict.values()
    nodeList.sort()
    log().info("nodeListB = %s" %(nodeList))
    sys.stdout.flush()
    return nodeList

def run(nodeList,bdf,f06,cart3d,cart3d2):
    mesh = FEM_Mesh(bdf)
    mesh.read()
    
    nodeList    = removeDuplicateNodes(nodeList,mesh)
    C           = getCmatrix(nodeList,mesh)
    #deflections = readOP2(op2)
    deflections = readF06(f06)
    wS          = getWS(nodeList,deflections)
    del deflections
    
    aPoints = readCart3dPoints(cart3d)
    wA = getWA(nodeList,C,wS,mesh,aPoints)
    del C
    #del wS
    del mesh
    
    writeNewCart3dMesh(cart3d,cart3d2,wA)
    return (wA,wS)

def getWA(nodeList,C,wS,mesh,aPoints):
    log().info('---starting getWA---')
    MatPrint(sys.stdout,C)

    C  = inv(C)*wS  # Cws matrix, P matrix
    #P = solve(C,wS)
    #C*P=wS
    #P = C^-1*wS

    wA = getXK_Matrix(C,nodeList,mesh,aPoints)
    #wA = xK*C*wS
    log().info('---finished getWA---')
    sys.stdout.flush()
    return wA

def getXK_Matrix(Cws,nodeList,mesh,aPoints):
    log().info('---starting getXK_matrix---')
    D = 1.
    piD16 = pi*D*16.

    nNodes = len(nodeList)
    nPoints = len(aPoints.keys())
    wa = {}
    i = 0
    for (iAero,aNode) in sorted(aPoints.items()):
        xK = zeros(nNodes+3,'d')
        #nodeI = mesh.Node(iNode)
        
        xa,ya,za = aNode

        xK[0] = 1.
        xK[1] = xa
        xK[2] = ya

        j = 3
        for jNode in nodeList:
            sNode = mesh.Node(jNode)
            (xs,ys,zs) = sNode.Position()

            Rij2 = (xa-xs)**2. + (ya-ys)**2  # Rij^2
            if Rij2==0.:
                xK[j] = 0.
            else:
                Kij = Rij2*naturalLog(Rij2)/piD16
                xK[j] = Kij
            j += 1
            ###
        ###
        wai = xK*Cws
        wa[iAero] = wai[0,0]
        #print "w[%s]=%s" %(iAero,wi[0,0])
        i += 1
    ###
    #print '---wa---'
    #print 'wa = ',wa
    log().info('---finished getXK_matrix---')
    sys.stdout.flush()
    return wa

def getWS(nodeList,deflections):
    log().info('---staring WS---')
    nNodes = len(nodeList)
    Wcolumn = matrix(zeros((3+nNodes,1),'d'))
    i = 3
    for iNode in nodeList:
        (dx,dy,dz) = deflections[iNode]
        Wcolumn[i]=dz
        log().info("wS[%s=%s]=%s" %(iNode,i,dz))
        i+=1
    ###
    print max(Wcolumn)
    log().info('---finished getWS---')
    sys.stdout.flush()

    wSmax = max(Wcolumn)
    print "wSmax = ",wSmax[0,0]
    return Wcolumn
    
def getCmatrix(nodeList,mesh):
    log().info('---starting getCmatrix---')
    D = 1.
    piD16 = pi*D*16.

    nNodes = len(nodeList)
    i = 3
    #C = memmap('Cmatrix.map',dtype='float64',mode='write',shape=(3+nNodes,3+nNodes) )
    log().info('nNodes=%s' %(nNodes))
    sys.stdout.flush()
    C = matrix(zeros((3+nNodes,3+nNodes),'d'))
    for iNode in nodeList:
        nodeI = mesh.Node(iNode)
        #i = iNode+3
        (xi,yi,zi) = nodeI.Position()
        #x,y,z = p

        C[0,i] = 1.
        C[1,i] = xi
        C[2,i] = yi

        C[i,0] = 1.
        C[i,1] = xi
        C[i,2] = yi

        j = 3
        for (jNode) in nodeList:
            #j = 3+jNode
            nodeJ = mesh.Node(jNode)
            (xj,yj,zj) = nodeJ.Position()
            if i==j:
                C[i,j] = 0.
            else:
                Rij2 = (xi-xj)**2. + (yi-yj)**2  # Rij^2
                if Rij2==0.:
                    C[i,j] = 0.
                else:
                    Kij = Rij2*naturalLog(Rij2)/piD16
                    C[i,j] = Kij
                    #msg = "i=%s j=%s xi=%s xj=%s yi=%s yj=%s Rij2=%s Kij=%s" %(i,j,xi,xj,yi,yj,Rij2,Kij)
                    #assert isinstance(Kij,float64),msg
            ###
            j += 1
        ###
        i += 1
    ###
    log().info('---finished getCmatrix---')
    sys.stdout.flush()
    return C
###


if __name__=='__main__':
    basepath = os.getcwd()
    configpath = os.path.join(basepath,'inputs')
    workpath   = os.path.join(basepath,'outputsFinal')

    bdf    = os.path.join(configpath,'fem3.bdf')
    op2    = os.path.join(workpath,'fem3.f06')
    cart3d = os.path.join(configpath,'Cart3d_bwb.i.tri')
    nodeList = [20037, 21140, 21787, 21028, 1151, 1886, 2018, 1477, 1023, 1116, 1201, 1116, 1201, 1828, 2589, 1373, 1315, 1571, 1507, 1532, 1317, 1327, 2011, 1445, 2352, 1564, 1878, 1402, 1196, 1234, 1252, 1679, 1926, 1274, 2060, 2365, 21486, 20018, 20890, 20035, 1393, 2350, 1487, 1530, 1698, 1782]
    #nodeList = [1001,1002,1003,1004,1005,1006]  # these are the hard points
    #nodeList = mesh.getNodeIDs() # [0:200]
    cart3d2 = cart3d+'_deflected'

    (wA,wS) = run(nodeList,bdf,op2,cart3d,cart3d2)
    print "wAero=",wA
    wSmax = max(wS)
    print "wSmax = ",wSmax[0,0]