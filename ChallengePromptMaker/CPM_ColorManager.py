#-----------------------------------------------------------------------------#
# Prompt Generator - Copyright (c) 2021 - kaichi1342                          #
# ----------------------------------------------------------------------------#
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
# ----------------------------------------------------------------------------#
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                        #
# See the GNU General Public License for more details.                        #
#-----------------------------------------------------------------------------#
# You should have received a copy of the GNU General Public License           #
# along with this program.                                                    #
# If not, see https://www.gnu.org/licenses/                                   #
# ----------------------------------------------------------------------------# 
# ChallengePromptMaker is a docker that  generates drawing challenge prompts  #
# from a list of categories along side a four slot color palette              #
# in split complementary color scheme.                                        #
# -----------------------------------------------------------------------------
 
  

from krita import *  
import random, time
from datetime import datetime

from PyQt5.QtCore import ( pyqtSignal)

from PyQt5.QtGui import (QPainter, QColor)

from PyQt5.QtWidgets import (QWidget)
 

class ColorBox(QWidget):
    clicked = pyqtSignal() 
    def __init__(self):  
        self.color = QColor(200, 200, 200)
        super().__init__() 
 
    def paintEvent(self, e):
        self.qp = QPainter()
        self.qp.begin(self)
        self.drawRectangles()
        self.qp.end()

    def drawRectangles(self):  
        self.qp.setBrush(self.color)
        self.qp.drawRect(-1, -1, self.geometry().width()+1, self.geometry().height()+1)
 
    def changeColorHSV(self,h,s,v):
        self.color.setHsv(h,s,v,255)
        self.update()

    

    def toString():
        return "Red "+str(self.color.red())+" Green "+str(self.color.green())+" Blue "+str(self.color.blue())+" Alpha "+str(self.color.alpha())

    def mousePressEvent(self, e):
        self.clicked.emit()

class ColorGenerator(): 

    def __init__(self, settings):  
        self.hue = 0
        self.sat = 0
        self.val = 0

        self.settings = settings
        self.sat_limit = self.settings["saturation_cutoff"]
        self.val_limit = self.settings["value_cutoff"]
        self.sat_cutoff = self.setCutOffPoint(self.settings["saturation_priority"])
        self.sat_cutoff = self.setCutOffPoint(self.settings["value_priority"])
        
        super().__init__() 

    def reloadSettings(self, settings):
        self.settings = settings
        self.sat_limit = self.settings["saturation_cutoff"]
        self.val_limit = self.settings["value_cutoff"]
        self.sat_cutoff = self.setCutOffPoint(self.settings["saturation_priority"])
        self.sat_cutoff = self.setCutOffPoint(self.settings["value_priority"])

    def pickHue(self, hue = -1, offset = 0):
            if(hue < 0 ): 
                random.seed()
                return random.randint(0, 360) 
            else:
                if(hue + offset > 360):
                    return (hue + offset) % 360
                elif(hue + offset < 0):
                    return (360 + (hue + offset ) )  % 360
                else:
                    return hue + offset
        
    def pickSat(self, sat = -1, w_offset = False):
        self.sat_cutoff = self.setCutOffPoint(self.settings["saturation_priority"])
        if(sat < 0 ): 
            random.seed()
            cutoff = random.randint(0, 100)
            if cutoff <= self.sat_cutoff[0]:
                return random.randint(self.sat_limit["low"],self.sat_limit["mid"])
            elif cutoff > self.sat_cutoff[1]:
                return random.randint(self.sat_limit["mid"],self.sat_limit["lim"])
            else: 
                return random.randint(self.sat_limit["mid"],self.sat_limit["high"])
        else:
            offset = 0
            if(w_offset): 
                offset = self.randomizedOffset() 
           
            if(sat + offset > self.sat_limit["lim"]):
                return  sat - abs(offset)
            elif(sat + offset < self.sat_limit["low"]):
                return  sat + abs(offset)
            else:
                return sat + offset

    def pickVal(self, val = -1, w_offset = False):
        self.val_cutoff = self.setCutOffPoint(self.settings["value_priority"])
        if(val < 0 ): 
            random.seed()
            cutoff = random.randint(0, 100)
            if cutoff <= self.val_cutoff[0]:
                return random.randint(self.val_limit["low"],self.val_limit["mid"])
            elif cutoff > self.val_cutoff[1]:
                return random.randint(self.val_limit["high"],self.val_limit["lim"])
            else: 
                return random.randint(self.val_limit["mid"],self.val_limit["high"])
        else:
            offset = 0
            if(w_offset): 
                offset = self.randomizedOffset() 

            if(val + offset > self.val_limit["lim"]):
                return val - abs(offset)
            elif(val + offset < self.val_limit["low"]):
                return val + abs(offset)
            else:
                return val + offset
    
    def randomizedOffset(self):
        random.seed() 
        if ( random.randint(1, 500) % 2 == 0 ):
            return random.randint(5,20)
        else: 
             return -1 * random.randint(5,20)

    def setCutOffPoint(self, t):
        if t == "Low":
            return [90,95]
        elif t == "High":
            return [5,10]
        elif t == "Mid":
            return [5,95]
        elif t == "Normal":
            return [14,86]
        else:
            return [33,66]

    def setupColor(self, r, g, b, a): 
        doc = Krita.instance().activeDocument()
        item = { 
                "red"   : r,
                "green" : g,
                "blue"  : b,
                "alpha" : a,
                "color05" : -1
        }

        color_to_set = ManagedColor(doc.colorModel(), doc.colorDepth(), doc.colorProfile())
        colorComponents = color_to_set.components()
        if (item["blue"] >= 0)  : colorComponents[0] = item["blue"]
        if (item["green"] >= 0): colorComponents[1] = item["green"]
        if (item["red"] >= 0) : colorComponents[2] = item["red"]
        if (item["alpha"] >= 0): colorComponents[3] = item["alpha"]
        if (item["color05"] >= 0): colorComponents[4] = item["color05"]
  
        color_to_set.setComponents(colorComponents)
        return color_to_set 