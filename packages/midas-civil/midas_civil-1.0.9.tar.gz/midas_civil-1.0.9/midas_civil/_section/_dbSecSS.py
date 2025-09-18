from ._offsetSS import Offset
from ._offsetSS import _common

class _SS_DBUSER(_common):

    """ Create Standard USER DEFINED sections"""

    def __init__(self,Name='',Shape='',parameters:list=[],Offset=Offset(),useShear=True,use7Dof=False,id:int=0):  
        """ Shape = 'SB' 'SR' for rectangle \n For cylinder"""
        self.ID = id
        self.NAME = Name
        self.TYPE = 'DBUSER'
        self.SHAPE = Shape
        self.PARAMS = parameters
        self.OFFSET = Offset
        self.USESHEAR = useShear
        self.USE7DOF = use7Dof
        self.DATATYPE = 2
    
    def __str__(self):
         return f'  >  ID = {self.ID}   |  USER DEFINED STANDARD SECTION \nJSON = {self.toJSON()}\n'


    def toJSON(sect):
        js =  {
                "SECTTYPE": "DBUSER",
                "SECT_NAME": sect.NAME,
                "SECT_BEFORE": {
                    "SHAPE": sect.SHAPE,
                    "DATATYPE": sect.DATATYPE,
                    "SECT_I": {
                        "vSIZE": sect.PARAMS
                    }
                }
            }
        js['SECT_BEFORE'].update(sect.OFFSET.JS)
        js['SECT_BEFORE']['USE_SHEAR_DEFORM'] = sect.USESHEAR
        js['SECT_BEFORE']['USE_WARPING_EFFECT'] = sect.USE7DOF
        return js
    
    @staticmethod
    def _objectify(id,name,type,shape,offset,uShear,u7DOF,js):
        return _SS_DBUSER(name,shape,js['SECT_BEFORE']['SECT_I']['vSIZE'],offset,uShear,u7DOF,id)
    
    def _centerLine(shape):
        H = shape.PARAMS[0]
        B = shape.PARAMS[1]
        tw = shape.PARAMS[2]
        tf = shape.PARAMS[3]

        sect_lin_con = [[1,2],[3,1]]

        sect_cg = [0,0]

        sect_shape = [[0,0],[B,0],[0,-H]]
        sect_thk = [tf,tw]
        sect_thk_off = [-tf/2,-tw/2]