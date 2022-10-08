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
# -----------------------------------------------------------------------------
# ChallengePromptMaker is a docker that  generates drawing challenge prompts  #
# from a list of categories along side a four color - color palette           #
# in split complementary color scheme.                                        #
# -----------------------------------------------------------------------------
    
  
 
from krita import *
import  os,random, json
from datetime import datetime

 
from PyQt5.QtCore import ( Qt, QSize,  QTimer )
 

from PyQt5.QtWidgets import ( 
        QVBoxLayout, QWidget, QLabel,  QGridLayout,  QToolButton  
)


from .CPM_ColorManager import *
from .CPM_CategoryList import *

#from .GLColorBox  import GLColorBox

DOCKER_NAME = 'ChallengePromptMaker'
DOCKER_ID = 'pykrita_ChallengePromptMaker'


class ChallengePromptMaker(DockWidget): 
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Challenge Prompt Maker")  
        
        self.roll_limit = 4

        self.loadCategoryList()
        self.loadSettings()
        self.loadDefault() 
        
        self.color_manager = ColorGenerator(self.settings)   
        self.category_dialog = NONE
        self.setUI()
    
    #Settings
    def reloadRequired(self): 
        self.loadCategoryList()
        self.loadSettings()
        self.loadDefault()
        self.timerReset()  
        self.color_manager.reloadSettings(self.settings)

    def loadCategoryList(self):
        self.json_cat = open(os.path.dirname(os.path.realpath(__file__)) + '/category.json')
        self.category_list = json.load(self.json_cat)
        self.json_cat.close() 

    def loadSettings(self):
        self.json_setting = open(os.path.dirname(os.path.realpath(__file__)) + '/settings.json')
        self.settings = json.load(self.json_setting)
        self.json_setting.close() 

    def loadDefault(self):
        if(self.settings["timer_limit"] > 1800 ): self.settings["timer_limit"] = 1800
        if(self.settings["roll_count"] > 4 ): self.settings["roll_count"] = 4

        self.default_time = self.settings["timer_limit"] 
        self.time_limit   = self.default_time #minutes
        self.timer_status = 0

        self.roll_count   = self.settings["roll_count"] 

         
        
        
    def getActiveCategory(self):
        active_category = [] 
        for i in range(0, self.roll_limit ): 
            slot = self.settings["category_slots"][str(i+1)] 
            categories = list( slot )
            active_category.append([])
            for cat in categories:
                if slot[cat]  == 1: active_category[i].append(cat) 
        return active_category

    # UI LAYOUT
    def setUI(self):
        self.base_widget = QWidget()
        

        self.challenge_container = QVBoxLayout()
        self.challenge_container.setContentsMargins(1, 1, 1, 1)

        self.base_widget.setLayout(self.challenge_container)
        self.setWidget(self.base_widget)
        
        self.base_widget.setMinimumSize(QSize(125,200))
        self.base_widget.setMaximumSize(QSize(250,250))

        #PROMPT SECTION
        self.prompt_widget = QWidget()
        self.prompt_container = QGridLayout() 
        self.prompt_widget.setLayout(self.prompt_container)

        self.label_prompt       = QLabel(self)
        self.label_prompt.setText("Challenge\nPrompt\nHere!")
        self.label_prompt.setAlignment(Qt.AlignCenter)
        self.label_prompt.setStyleSheet("border: 1px dashed #666666")
        self.label_prompt.setWordWrap(True)
        
        self.label_time        = QLabel(self)
        self.label_time.setText("HH:MM:SS")
        self.label_time.setAlignment(Qt.AlignCenter) 
        self.label_time.setStyleSheet("font-size: 12px; font-weight:bold; ")
        self.label_time.setWordWrap(True)

        self.colorbox1 = ColorBox()
        self.colorbox2 = ColorBox()
        self.colorbox3 = ColorBox()
        self.colorbox4 = ColorBox()
        
        self.button_generate =  QToolButton()
        self.button_configure =  QToolButton() 
        self.button_time_s =  QToolButton()  
        self.button_time_r =  QToolButton()  
        self.button_color =  QToolButton()  
        
        self.button_generate.setIcon( Krita.instance().icon("document-new") )     
        self.button_configure.setIcon( Krita.instance().icon("configure") )          
        self.button_time_s.setIcon( Krita.instance().icon("animation_play") )    
        self.button_time_r.setIcon( Krita.instance().icon("reload-preset") )    
        self.button_color.setIcon( Krita.instance().icon("config-color-manage") )    

        self.prompt_container.addWidget(self.label_prompt, 0, 0, 3, 4) 

        self.prompt_container.addWidget(self.label_time, 3, 0, 1, 2) 
        self.prompt_container.addWidget(self.button_time_s, 3, 2, 1, 1)   
        self.prompt_container.addWidget(self.button_time_r, 3, 3, 1, 1)    

        self.prompt_container.addWidget(self.colorbox1, 4, 0) 
        self.prompt_container.addWidget(self.colorbox2, 4, 1) 
        self.prompt_container.addWidget(self.colorbox3, 4, 2) 
        self.prompt_container.addWidget(self.colorbox4, 4, 3) 

        self.prompt_container.addWidget(self.button_generate, 6, 0, 1, 1)   
        self.prompt_container.addWidget(self.button_color, 6, 1, 1, 1)   
        self.prompt_container.addWidget(self.button_configure, 6, 3, 1, 1)   

        self.prompt_container.setRowStretch(0, 3)
        self.prompt_container.setRowStretch(4, 2) 

        self.connectButtons()  

       
        self.challenge_container.addWidget(self.prompt_widget)
    
        self.timer = QTimer() 
        self.setTime(self.label_time)
        self.timer.timeout.connect(lambda: self.setTime(self.label_time, -1))
 
 
    #CANVS EVENT
    def resizeEvent(self, event):    
        pass 

    def canvasChanged(self, canvas):
        if canvas:       
            if canvas.view():
                self.connectButtons()
            else: 
                self.disconnectButtons() 
        else: 
            self.disconnectButtons() 


    def connectButtons(self): 
        self.button_generate.clicked.connect(lambda: self.generateChallenge()) 
        self.button_time_s.clicked.connect(lambda: self.timerStartPause()) 
        self.button_time_r.clicked.connect(lambda: self.timerReset() ) 
        self.button_color.clicked.connect(lambda: self.generatePalette())
        self.button_configure.clicked.connect(lambda: self.openCategoryBox())

        self.colorbox1.clicked.connect(lambda: self.setFGColor(self.colorbox1))
        self.colorbox2.clicked.connect(lambda: self.setFGColor(self.colorbox2))
        self.colorbox3.clicked.connect(lambda: self.setFGColor(self.colorbox3))
        self.colorbox4.clicked.connect(lambda: self.setFGColor(self.colorbox4))

    def disconnectButtons(self):
        self.button_generate.disconnect() 
        self.button_time_s.disconnect() 
        self.button_time_r.disconnect() 
        self.button_color.disconnect() 

        self.colorbox1.disconnect() 
        self.colorbox2.disconnect() 
        self.colorbox3.disconnect() 
        self.colorbox4.disconnect()  

    #TIMER SETTING
    def setTime(self,label_box, step = 0):
        sec = self.time_limit 
        hr  = sec // 3600
        min = (sec - (hr * 3600)) // 60 
        sec = sec - ((min * 60) + (hr * 3600))

        time_text = str(min).rjust(2,"0")+":"+str(sec).rjust(2,"0")
        if(hr > 0):  time_text = str(hr).rjust(2,"0")+":"+time_text

        label_box.setText(time_text)

        self.time_limit = self.time_limit + step

    def timerReset(self): 
        self.timer.stop()
        self.time_limit = self.default_time #resets time.
        self.setTime(self.label_time)
        self.timer_status = 0  
        self.button_time_s.setIcon( Krita.instance().icon("animation_play") )    

    def timerStartPause(self):
        if(self.timer_status == 0):
            self.timer.start(1000)
            self.timer_status = 1 
            self.button_time_s.setIcon( Krita.instance().icon("animation_pause") )    
        else:
            self.timer_status = 0
            self.timer.stop()
            self.button_time_s.setIcon( Krita.instance().icon("animation_play") )    
             

        
        
    #CATEGORY SETTING
    def openCategoryBox(self):   
        if self.category_dialog == NONE:
            self.category_dialog = CategoryDialog(self, "Settings", self.roll_limit)
            self.category_dialog.finished.connect(self.reloadRequired)
 
            self.category_dialog.show() 
        elif self.category_dialog.isVisible() == False : 
            self.category_dialog.show() 
            self.category_dialog.loadDefault()
        else:
            pass
 

    #CHALLENGE RANDOMIZER
    def generateChallenge(self):
        self.generatePalette()
        self.timerReset()

        self.label_prompt.setText("")
        self.generateTextChallenge() 
 

    def generateTextChallenge(self):
        slot = []
        for i in range(0,self.roll_count): 
            slot.append(i)
        
        category_slot = self.getActiveCategory()

        for i in range(0,self.roll_count):   
            sel_cat = i
            category = ""

            if self.settings["slot_in_sequence"] == 0:
                sel_cat =  slot.pop([random.randint(0, len(slot)-1)]) 

            if len(category_slot[sel_cat]) > 0:
                random.seed(datetime.now())
                category = category_slot[sel_cat][random.randint(0, len(category_slot[sel_cat])-1)]

            if category in self.category_list: 
                random.seed(datetime.now())
                items = self.category_list[category]
                selected_item = items[random.randint(0, len(items)-1)]

                self.label_prompt.setText(self.label_prompt.text()+selected_item+"\n")

                for i in range(0,self.roll_count): 
                    if category in category_slot[i]:
                        category_slot[i].remove(category)

        self.label_prompt.setText(self.label_prompt.text().rstrip("\n"))  


    def generatePalette(self): 
        cm =  self.color_manager
        hue = cm.pickHue()
        sat = cm.pickSat() 
        val = cm.pickVal() 

        #Main Color
        random.seed(datetime.now())
        self.colorbox1.changeColorHSV(  hue, sat, val) 

        #Analogous Color
        random.seed(datetime.now())
        self.colorbox2.changeColorHSV( cm.pickHue(hue, random.randint(15, 40)) , cm.pickSat(sat, True), cm.pickVal(val, True) ) 
        self.colorbox3.changeColorHSV( cm.pickHue(hue, -1 * random.randint(15, 40)) , cm.pickSat(sat, True), cm.pickVal(val, True) ) 
         
        #Complementary Color
        random.seed(datetime.now())
        self.colorbox4.changeColorHSV( cm.pickHue(hue, random.randint(170, 190)), cm.pickSat(sat, True), cm.pickVal(val, True))
        
        


    
    def setFGColor(self,ColorBox):   
        color_to_set = self.color_manager.setupColor(ColorBox.color.redF(), ColorBox.color.greenF(), ColorBox.color.blueF(), ColorBox.color.alphaF()) 
        Krita.instance().activeWindow().activeView().setForeGroundColor(color_to_set) 

  
 
instance = Krita.instance()
dock_widget_factory = DockWidgetFactory(DOCKER_ID,
                                        DockWidgetFactoryBase.DockRight,
                                        ChallengePromptMaker)

instance.addDockWidgetFactory(dock_widget_factory)