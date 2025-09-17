"""
Created on Wed Dec 18, 2024
Modified   Jan  5, 2025: added plot function
Modified  June 19, 2025: added option to plot
Modified  July 14, 2025: added isoProp
Modified  July 21, 2025: added edge property "span"
Modified  July 23, 2025: added edge property "substance"
Modified  Sept  7, 2025: added Hf

@author: mfrenklach

"""

"""
Modified Sept 8, 2025: 
- installed importlib.resources module to locate hf.json
- graph generation changed to g = ig.Graph.TupleList(edges, directed=True)
- changed >>> pr.plot("pv") to >>> fig2 = pr.plot("pv")
This was done to stop the images from displaying twice in a Jupyter notebook
One could also add a semicolon after pr.plot("pv")

@author: tschutzius

"""

from . import units
from . import plots
from . import utils
import CoolProp
import igraph as ig
import numpy as np
import json
import importlib.resources as res

info = lambda : print(state.__doc__)

class state:
    """stateObject = state(fluidName, property1=value1, property2, value2, name="A")
    
    fluidName = 'water, 'r134a', 'air', ''nitrogen', etc.
    property1 and property2 are two independent intensive properties
    value1 and value2 are property values (in base units; see >>> th.state.units)
    
    Examples:
        >>> import thermo as th
        >>> th.state.units
        >>> st1 = th.state('water', p=(1,'bar'), v=0.1, name="1")
        >>> st1.plot("Pv")
        >>> st2 = th.state('R134a', x=1, t=300, name="B")
        >>> fig1 = st2.plot("Ts",isoProp="v")
        >>> fig1.savefig("figure_1.jpg")
        >>> st3 = th.state('air', p=(1,'Mpa'), t=(10,'c'))
        >>> st3.name = "2a"
    """
    fluidSet = {}        # container of fluid factories
    # phases = {0: "liquid", 1: "supercritical", 2: "supercritical_gas",
    #           3: "supercritical_liquid", 5: "gas", 6: "twophase"}
    phases = {0:"liquid", 1:"liquid", 2:"gas", 3:"liquid", 5:"gas", 6:"twophase"}
    units = units.base
    propList = ("p","t","v","u","h","s")
    
    def __init__(self,fluidName, **props):
        self.fluidName = fluidName
        if fluidName not in self.fluidSet:
            self.fluidSet[fluidName] = CoolProp.AbstractState("HEOS", fluidName)
        fluid = self.fluidSet[fluidName]
        self.name = ""
        argIn = ();
        for prop, val in props.items():
            if prop == "name":
                self.name = val
                continue
            if isinstance(val,(list,tuple)) and len(val)==2:
                valIn = units.convertToBase(prop,val[0],val[1],self.molW)
            else:
                valIn = val;
            propUp = prop.upper()
            match propUp:
                case 'P':
                    propIn = "iP"
                    valIn *= 1000;
                case 'T':
                    propIn = "iT"
                case 'V':
                    propIn = "iDmass"
                    valIn = 1/valIn
                case 'U'|'H'|'S':
                    propIn = "i" + propUp + "mass"
                    valIn *= 1000
                case 'X':
                    propIn = "iQ"
                case _:
                    raise ValueError("unmatched property " + prop)
            argIn += (getattr(CoolProp,propIn), valIn)
        propPair = CoolProp.CoolProp.generate_update_pair(*argIn)
        fluid.update(*propPair)
        self.T = fluid.T()
        self.p = fluid.p() * 0.001
        self.v = 1/fluid.rhomass()
        self.u = fluid.umass() * 0.001  # J to kJ
        self.h = fluid.hmass() * 0.001
        self.s = fluid.smass() * 0.001
        self.x = fluid.Q()
        self.cp = fluid.cpmass() * 0.001
        self.cv = fluid.cvmass() * 0.001
        self.phase = fluid.phase()
    
    def __str__(self):
        s = f"""
        {self.fluidName}: {self.phases[self.phase]+"   "+self.name}
        molar mass: {round(self.molW,3)}  (kg/kmol)
        R: {round(8.314/self.molW,3)}  (kJ/kg K)
        T: {round(self.T,2)}  (K)
        p: {round(self.p,2)}  (kPa)
        v: {round(self.v,4)}  (m3/kg)
        u: {round(self.u,1)}  (kJ/kg)
        h: {round(self.h,1)}  (kJ/kg)
        s: {round(self.s,4)}  (kJ/kg K)"""
        if self.x > -1.0:
            s += f"""\n        x: {round(self.x,3)}"""
        # s += f"""
        # cp: {round(self.cp,3)}  (kJ/kg K)
        # cv: {round(self.cv,3)}  (kJ/kg K)"""
        return s
    
    def plot(self, opt, isoProp=''):
        h = plots.plotState(self,opt,isoProp)
        return h
        
    @property
    def substance(self):
        return self.fluidName
    @property
    def molW(self):
        return 1000 * self.fluidSet[self.fluidName].molar_mass()
    @property
    def R(self):
        return 8.314/self.molW
    @property
    def P(self):
        return self.p
    @property
    def t(self):
        return self.T
    @property
    def prop_array(self):
        return np.array([self.p,self.t,self.v,self.u,self.h,self.s])
    
class process:
    """pr = process([(state1,state2),(state2,state3),...])
    
    Examples:
        >>> import thermo as th
        >>> st1 = th.state('water', p=( 1,'bar'), x=0, name="A")
        >>> st2 = th.state('water', p=(20,'bar'), s=st1.s, name="B")
        >>> pr = th.process([st1,st2])
        >>> fig2 = pr.plot("pv")
        >>> st3 = th.state('water', p=(20,'bar'), x=1,name="C")
        >>> st4 = th.state('water', p=( 1,'bar'), s=st3.s, name="D")
        >>> pr2 = th.process([(st1,st2),(st2,st3),(st3,st4),(st4,st1)])
        >>> fig3 = pr2.plot("Ts")
        >>> fig3.savefig("figure_3.pdf")
    """
    def __init__(self, stateList, **props):
        if isinstance(stateList[0],(list,tuple)):
            # stEg = stateList[0]
            stList = []
            edges = []
            for eg in stateList:
                for st in eg:
                    if st not in stList:
                        stList.extend([st])
            n = len(stList)
            for eg in stateList:
                edges.append((stList.index(eg[0]),stList.index(eg[1])))
        else:
            stList  = stateList
            edges = []
            if stList[0] == stList[-1]:
                del stList[-1]
                n = len(stList)
                for i in range(n-1):
                    edges.append((i,i+1))
                    edges.append((n-1,0))
            else:
                n = len(stList)
                for i in range(n-1):
                    edges.append((i,i+1))
        self.StateList = stList
        # g = ig.Graph(n,edges,directed=True)
        g = ig.Graph.TupleList(edges, directed=True)
        self.StateNet = g
        self.isoProps()
        
    def __str__(self):
        st = self.StateList
        g = self.StateNet
        names = [s.name for s in st[:]]
        s = ""
        for ei in g.es:
            props = ei["isoProp"]
            for prop, val in props.items():
                match prop.lower():
                    case 'p'|'t'|'u'|'h':
                        props[prop] = round(float(val), 1)
                    case 's'|'v'|'x':
                        props[prop] = round(float(val), 3)
            nami = [names[i] for i in ei.tuple]
            s += "process "+nami[0]+"-->"+nami[1]+"  isoProps:  "+str(props) + "\n"
        return s

    def isoProps(self):
        st = self.StateList
        g = self.StateNet
        for eg in g.es:
            yy = np.array([st[i].prop_array for i in eg.tuple])
            ave = np.mean(yy,axis=0)
            dd = np.abs(np.diff(yy,axis=0)) / ave
            pp = [(st[0].propList[i],ave[i]) for i in np.where(dd<0.001)[1].tolist()]
            eg["isoProp"] = dict(pp)
            eg["span"] = dd
            
    def isoProp(self,st1,st2):
        stList = self.StateList
        i1 = stList.index(st1); i2 = stList.index(st2)
        g = self.StateNet
        if g.are_connected(i1,i2):
            ieg = g.get_eid(i1,i2)
        else:
            return {}
        props = g.es[ieg]["isoProp"]
        for prop, val in props.items():
            match prop.lower():
                case 'p'|'t'|'u'|'h':
                    props[prop] = round(float(val), 1)
                case 's'|'v'|'x':
                    props[prop] = round(float(val), 3)
        return props
        
    def plot(self, opt=''):
        h = plots.plotProcess(self, opt)
        return h
    
def getHf(jsonFileName):
    # TS added: importlib.resources, get a path object to the file
    file_path = res.files('pyCalor') / jsonFileName

    # with open(jsonFileName, 'r') as json_file:
    with file_path.open('r') as json_file:
        Hf_data = json.load(json_file)
        by_name = {rec['name']: rec for rec in Hf_data}
        by_formula = {rec['formula']: rec for rec in Hf_data}
        def hf(key):
            """ rec = th.hf_rec(substance)
                returns a record for standard enthalpy of formation of substance @ T=25 C
                substance is either name or formula; e.g., 'methanol vapor' or ch3oh(g)
                rec is a dictionary with 'name', 'formula', 'Hf' in kJ/kmol, and 'molw' in kg/kmol.
                Then, to get Hf, use Hf = rec['Hf'] of Hf = rec.get('Hf'),
                  or, directly, Hf = th.hf_rec('c2h2').get('Hf')
                To see all substance names and formulas, use '>>> th.hf_keys()'
            """
            return by_name.get(key) or by_formula.get(key) or by_formula.get(key+'(g)')
        def hf_keys():
            return [[r['name'],r['formula']] for r in Hf_data]
    return hf, hf_keys, Hf_data
hf_rec, hf_keys, hf_data = getHf('hf.json')