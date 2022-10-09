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
# from a list of categories along side a four slot color palette              #
# in split complementary color scheme.                                        #
# -----------------------------------------------------------------------------
    
 
from krita import *  
import os, json  

from PyQt5.QtCore import ( Qt, pyqtSignal, QEvent)

from PyQt5.QtGui import (QStandardItemModel)


from PyQt5.QtWidgets import ( 
        QWidget, QFrame, QDialog, QDoubleSpinBox,
        QVBoxLayout, QHBoxLayout, QGridLayout, QSpacerItem, QSizePolicy,
        QLabel, QPushButton, QToolButton, QComboBox , QCheckBox,
        QListWidget, QLineEdit, QListWidgetItem, QMenu
)


class DoubleSpinBox(QDoubleSpinBox):
    stepChanged = pyqtSignal() 
    
    def __init__(self):
         super(QDoubleSpinBox, self).__init__() 
    
    def __init__(self, low = 0, high = 0, step = 0):
        super(QDoubleSpinBox, self).__init__() 
        self.setRange(low, high)
        self.setSingleStep(step)

    def stepBy(self, step):
        value = self.value()
        super(DoubleSpinBox, self).stepBy(step)
        if self.value() != value:
            self.stepChanged.emit()

    def focusOutEvent(self, e):
        value = self.value() 
        super(DoubleSpinBox, self).focusOutEvent(e)
        self.stepChanged.emit()

class CategoryDialog(QDialog):
    def __init__(self, parent, title = "", roll_limit = 4):
        super().__init__(parent)
        
        self.resize(350,550)
        self.setWindowTitle(title)  

        self.roll_limit  = roll_limit
        self.toEditRow   = None
        self.loadCategoryList()
        self.loadSettings()
        self.setUI()

        self.loadDefault()
        self.connectSignals()

  #Settings
    def loadCategoryList(self):
        json_cat = open(os.path.dirname(os.path.realpath(__file__)) + '/category.json')
        self.category_list = json.load(json_cat)
        json_cat.close() 

    def loadSettings(self):
        json_setting = open(os.path.dirname(os.path.realpath(__file__)) + '/settings.json')
        self.settings = json.load(json_setting)
        json_setting.close() 

    def loadDefault(self): 
        self.dsb_roll_count.setValue(self.evalSettingValue(self.settings["roll_count"], 1, self.roll_limit))
        self.dsb_minutes.setValue(self.evalSettingValue(self.settings["timer_limit"], 0, 1800)/60)

        self.dsb_sat_low.setValue(self.evalSettingValue(self.settings["saturation_cutoff"]["low"], 1, 255))
        self.dsb_sat_mid.setValue(self.evalSettingValue(self.settings["saturation_cutoff"]["mid"], 1, 255))
        self.dsb_sat_high.setValue(self.evalSettingValue(self.settings["saturation_cutoff"]["high"], 1, 255))
        self.dsb_sat_lim.setValue(self.evalSettingValue(self.settings["saturation_cutoff"]["lim"], 1, 255))

        self.dsb_val_low.setValue(self.evalSettingValue(self.settings["value_cutoff"]["low"], 1, 255))
        self.dsb_val_mid.setValue(self.evalSettingValue(self.settings["value_cutoff"]["mid"], 1, 255))
        self.dsb_val_high.setValue(self.evalSettingValue(self.settings["value_cutoff"]["high"], 1, 255))
        self.dsb_val_lim.setValue(self.evalSettingValue(self.settings["value_cutoff"]["lim"], 1, 255))
  
        self.combo_roll_category.clear()
        for option in range(0,self.roll_limit):
            self.combo_roll_category.addItem("Categories in Roll Slot "+ str(option+1))
 
        self.categories =  list( self.category_list.keys())  
       
        self.combo_item_category.clear()
        if len(self.categories) > 0 :
            for cat in self.categories:
                self.combo_item_category.addItem(cat)

            self.loadCategories(0)  
            self.loadItems(self.categories[0])
    
        self.color_priority_option = ["Low", "Mid", "High", "Normal", "Equal"]
       
        self.combo_sat.clear()
        for prio in self.color_priority_option:
            if(prio == "Equal") : self.combo_sat.addItem(prio + " Distribution")
            elif(prio == "Normal") : self.combo_sat.addItem(prio + " Distribution")
            else: self.combo_sat.addItem("More "+ prio + " Saturated Color" )

        self.combo_val.clear()
        for prio in self.color_priority_option: 
            if(prio == "Equal") : self.combo_val.addItem(prio + " Distribution")
            elif(prio == "Normal") : self.combo_val.addItem(prio + " Distribution")
            else: self.combo_val.addItem("More "+ prio + " Value Color" )

        def_sat_idx = self.color_priority_option.index(self.settings["saturation_priority"])
        def_val_idx = self.color_priority_option.index(self.settings["value_priority"])
        if def_sat_idx != -1 : self.combo_sat.setCurrentIndex(def_sat_idx)
        if def_val_idx != -1 : self.combo_val.setCurrentIndex(def_val_idx)
        
        if self.settings["slot_in_sequence"] == 1: 
            self.chk_sequence.setChecked(True)
        else:
            self.chk_sequence.setChecked(False)

        self.txt_category.setText("")
        self.txt_list.setText("")

    def evalSettingValue(self, value, low, high, off_low = 0, off_high = 0 ):
        if value < low: 
            value = low + off_low
        elif value > high:
            value = high + off_high
        else:
            pass
        return value 
    

       
    #User Interface
    def setUI(self):
         
        self.setting_container = QVBoxLayout() 
        self.setting_container.setContentsMargins(10, 10, 10, 10)

        self.setLayout(self.setting_container)  

        self.general_container =  QHBoxLayout()
        self.general_widget = QWidget()
        self.general_widget.setLayout(self.general_container)
        self.general_container.setContentsMargins(0, 0, 0, 0)

        self.setting_container.addWidget(self.general_widget)

        self.uiSettingsInput()
        self.uiCategoryList()
        self.uiActionCategoryList()
        self.uiActionBar()


    def uiSettingsInput(self):
        #ROLL AND COLOR PORTION
        self.roll_container =  QGridLayout()  
        self.roll_container.setContentsMargins(0, 0, 0, 0)

        self.frame_roll_setting = QWidget()
        self.frame_roll_setting.setLayout(self.roll_container) 

        self.label_roll_count = QLabel("Roll Count")
        self.label_minutes    = QLabel("Time Limit (Minutes)")
        self.dsb_roll_count   = DoubleSpinBox(1, 4, 1)
        self.dsb_minutes      = DoubleSpinBox(1, 1800, .25)

        self.label_sat = QLabel("Saturation Randomizer")
        self.label_val = QLabel("Value Randomizer")
        self.combo_sat = QComboBox()
        self.combo_val = QComboBox() 
        self.combo_sat.setToolTip("Set Color Saturation RNG Priority")
        self.combo_val.setToolTip("Set Color Value RNG Priority")     
        
        self.dsb_sat_low  = DoubleSpinBox(1,255,1)
        self.dsb_sat_mid  = DoubleSpinBox(1,255,1)
        self.dsb_sat_high = DoubleSpinBox(1,255,1)
        self.dsb_sat_lim  = DoubleSpinBox(1,255,1)
        self.dsb_val_low  = DoubleSpinBox(1,255,1)
        self.dsb_val_mid  = DoubleSpinBox(1,255,1)
        self.dsb_val_high = DoubleSpinBox(1,255,1)
        self.dsb_val_lim  = DoubleSpinBox(1,255,1)

        self.dsb_sat_low.setToolTip("Saturation Lower Bound Start")
        self.dsb_sat_mid.setToolTip("Saturation Mid Bound Start")
        self.dsb_sat_high.setToolTip("Saturation Upper Bound Start") 
        self.dsb_sat_lim.setToolTip("Saturation Upper Bound Limit") 
        self.dsb_val_low.setToolTip("Value Lower Bound Start")
        self.dsb_val_mid.setToolTip("Value Mid Bound Start")
        self.dsb_val_high.setToolTip("Value Upper Bound Start")
        self.dsb_val_lim.setToolTip("Value Upper Bound Limit") 

        self.roll_container.addWidget(self.label_roll_count , 0, 0, 1, 4)
        self.roll_container.addWidget(self.label_minutes    , 0, 4, 1, 4)
        self.roll_container.addWidget(self.dsb_roll_count   , 1, 0, 1, 4)
        self.roll_container.addWidget(self.dsb_minutes      , 1, 4, 1, 4)

        self.roll_container.addWidget(self.label_sat, 2, 0, 1, 8)
        self.roll_container.addWidget(self.combo_sat, 3, 0, 1, 8)

        self.roll_container.addWidget(self.dsb_sat_low,     4, 0, 1, 2) 
        self.roll_container.addWidget(self.dsb_sat_mid,     4, 2, 1, 2) 
        self.roll_container.addWidget(self.dsb_sat_high,    4, 4, 1, 2)
        self.roll_container.addWidget(self.dsb_sat_lim,     4, 6, 1, 2)
        
        self.roll_container.addWidget(self.label_val, 5, 0, 1, 8)
        self.roll_container.addWidget(self.combo_val, 6, 0, 1, 8)
 
        self.roll_container.addWidget(self.dsb_val_low,     7, 0, 1, 2)
        self.roll_container.addWidget(self.dsb_val_mid,     7, 2, 1, 2)
        self.roll_container.addWidget(self.dsb_val_high,    7, 4, 1, 2)
        self.roll_container.addWidget(self.dsb_val_lim,     7, 6, 1, 2) 
        
        self.general_container.addWidget(self.frame_roll_setting )  


    def uiCategoryList(self):
        self.list_container =  QHBoxLayout()
        self.list_widget = QWidget()
        self.list_widget.setLayout(self.list_container)
        self.list_container.setContentsMargins(0, 0, 0, 0)
    
        self.category_container =  QGridLayout()
        self.category_widget    =  QWidget()
        self.category_widget.setLayout(self.category_container) 
        self.category_container.setContentsMargins(0, 0, 0, 0)
       
        self.label_combo_roll = QLabel("Categories")
        self.combo_roll_category = QComboBox()
        self.combo_roll_category.setObjectName(("Roll Slots"))
        self.list_category = QListWidget()
        self.list_category.installEventFilter(self)

        self.category_container.addWidget(self.label_combo_roll, 0, 0)
        self.category_container.addWidget(self.combo_roll_category, 1, 0)
        self.category_container.addWidget(self.list_category, 2, 0) 
        self.category_container.setRowStretch(2, 10)

        
        self.item_container     =  QGridLayout()
        self.item_widget        =  QWidget()
        self.item_widget.setLayout(self.item_container)
        self.item_container.setContentsMargins(0, 0, 0, 0)

        self.label_item_category = QLabel("Item List")
        self.combo_item_category  = QComboBox()
        self.combo_item_category.setObjectName(("Item List"))
        self.list_item = QListWidget()
        self.list_item.installEventFilter(self)

        self.item_container.addWidget(self.label_item_category, 0, 0)
        self.item_container.addWidget(self.combo_item_category, 1, 0)
        self.item_container.addWidget(self.list_item, 2, 0) 
        self.item_container.setRowStretch(2, 10)
 
        
        self.list_container.addWidget(self.category_widget )  
        self.list_container.addWidget(self.item_widget ) 

        self.setting_container.addWidget(self.list_widget ) 
        

    def uiActionCategoryList(self):
        self.list_action_container =  QHBoxLayout()
        self.list_action_widget = QWidget()
        self.list_action_widget.setLayout(self.list_action_container)
        self.list_action_container.setContentsMargins(0, 0, 0, 0)
  
        self.addto_category_container =  QGridLayout()
        self.addto_category_widget    =  QWidget()
        self.addto_category_widget.setLayout(self.addto_category_container) 
        self.addto_category_container.setContentsMargins(0, 0, 0, 0)

        self.txt_category  = QLineEdit()
        self.button_add_category = QToolButton()
        self.button_add_category.setIcon( Krita.instance().icon("list-add") )    
        self.button_rem_category = QToolButton()
        self.button_rem_category.setIcon( Krita.instance().icon("trash-empty") )    

        self.addto_category_container.addWidget(self.txt_category, 0, 0, 4, 1)
        self.addto_category_container.addWidget(self.button_add_category, 0, 5, 0, 1)  
        self.addto_category_container.addWidget(self.button_rem_category, 0, 6, 0, 1)  

        self.addto_list_container =  QGridLayout()
        self.addto_list_widget    =  QWidget()
        self.addto_list_widget.setLayout(self.addto_list_container) 
        self.addto_list_container.setContentsMargins(0, 0, 0, 0)

        self.txt_list  = QLineEdit()
        self.button_add_list = QToolButton()
        self.button_add_list.setIcon( Krita.instance().icon("list-add") )    
        self.button_rem_list = QToolButton()
        self.button_rem_list.setIcon( Krita.instance().icon("trash-empty") )  
 
        
        self.addto_list_container.addWidget(self.txt_list, 0, 0, 5, 1)
        self.addto_list_container.addWidget(self.button_add_list, 0, 5, 0, 1)  
        self.addto_list_container.addWidget(self.button_rem_list, 0, 6, 0, 1)  
        
        
        self.list_action_container.addWidget(self.addto_category_widget )  
        self.list_action_container.addWidget(self.addto_list_widget ) 
        self.setting_container.addWidget(self.list_action_widget ) 
         

    def uiActionBar(self): 

        self.action_container =  QGridLayout()
        self.action_widget = QWidget()
        self.action_widget.setLayout(self.action_container)
        self.action_widget.setContentsMargins(0, 0, 0, 0)
 

        self.chk_sequence   = QCheckBox("&Pick Slots In Sequence")
        self.button_ok      = QPushButton("&OK")
        self.button_cancel  = QPushButton("&Cancel") 
        
        self.action_container.addWidget(self.chk_sequence, 0, 0, 1, 2 )   
        
        self.action_container.addWidget(self.button_ok, 0, 2 )  
        self.action_container.addWidget(self.button_cancel, 0, 3 )  

        
        self.setting_container.addWidget(self.action_widget ) 




    def connectSignals(self): 
        self.combo_roll_category.currentIndexChanged.connect(self.loadCategories)
        self.combo_item_category.currentTextChanged.connect(self.loadItems)
        
        self.button_ok.clicked.connect(self.saveSettings)
        self.button_cancel.clicked.connect(self.cancelSave)
        
        
        self.button_add_category.clicked.connect(self.addToCategory)
        self.button_add_list.clicked.connect(self.addToItems)
        self.button_rem_category.clicked.connect(self.removeCategory)
        self.button_rem_list.clicked.connect(self.removeItem)

        self.chk_sequence.stateChanged.connect(self.toggleInSequence)
         
        self.list_category.itemChanged.connect(self.categoryAction) 
 

    def eventFilter(self, source, event):
        if (event.type() == QEvent.ContextMenu and source is self.list_item):
            menu = QMenu()
            menu.addAction('Edit Item')
            if menu.exec_(event.globalPos()):
                item = source.itemAt(event.pos())
                self.txt_list.setText(item.text())
                self.toEditRow = item 
            return True
        elif (event.type() == QEvent.ContextMenu and source is self.list_category):
            menu = QMenu()
            menu.addAction('Edit Category')
            if menu.exec_(event.globalPos()):
                item = source.itemAt(event.pos())
                self.txt_category.setText(item.text())
                self.toEditRow = item 
            return True
        return super(CategoryDialog, self).eventFilter(source, event)


    def loadCategories(self, index):
        self.category_slots = self.settings["category_slots"]

        if str(index + 1) in self.category_slots: 
            selected_slot =  self.category_slots[str(index+1)] 
            selected_keys =   list( selected_slot.keys() )

            self.list_category.clear()
            if(len(self.categories) > 0):
                for cat in  self.categories:   
                    item = QListWidgetItem(cat)

                    if cat in selected_keys:     
                        if selected_slot[cat] == 1:
                            item.setCheckState(Qt.Checked)
                        else:
                            item.setCheckState(Qt.Unchecked)
                    else:
                        item.setCheckState(Qt.Unchecked)

                    self.list_category.addItem(item)       

    def loadItems(self, text): 
        self.list_item.clear()
        
        if text and len(self.category_list[text]) > 0 : 
            for item in  self.category_list[text]:  
                QListWidgetItem(item, self.list_item)




    def categoryAction(self, category):
        i = str(self.combo_roll_category.currentIndex() + 1) 

        if category.checkState() == Qt.Unchecked:
            self.settings["category_slots"][i][category.text()] = 0
        else:
            self.settings["category_slots"][i][category.text()] = 1
        

    def addToCategory(self):
        if self.txt_category.text() not in self.categories:
            if self.toEditRow == None:  
                self.category_list[self.txt_category.text()] = []
                item = QListWidgetItem(self.txt_category.text())
                item.setCheckState(Qt.Unchecked)
                self.list_category.addItem(item)  
                self.categories = list( self.category_list.keys())  
            else:
                self.category_list[self.txt_category.text()] = self.category_list.pop(self.toEditRow.text())
                 
                for i in range(0,self.roll_limit):
                    if self.toEditRow.text() in  self.settings["category_slots"][str(i+1)] :
                        self.settings["category_slots"][str(i+1)][self.txt_category.text()] = self.settings["category_slots"][str(i+1)].pop(self.toEditRow.text())

                self.toEditRow.setText(self.txt_category.text()) 
                self.toEditRow = None
                self.categories = list( self.category_list.keys()) 
        
        self.txt_category.setText("")

    def addToItems(self): 
        selectedCategory =  self.category_list[self.combo_item_category.currentText()]
        
        if self.txt_list.text() not in selectedCategory:
            if self.toEditRow == None:
                selectedCategory.append(self.txt_list.text())
                QListWidgetItem(self.txt_list.text(), self.list_item)
            else:
                index = self.toEditRow.text() in selectedCategory 
                selectedCategory[index+1] = self.txt_list.text() 
                self.toEditRow.setText(self.txt_list.text()) 
                self.toEditRow = None
        self.txt_list.setText("")
     
    def removeCategory(self):
        category = self.list_category.item((self.list_category.currentRow()))
        if category:
            if category.text() in self.categories:
                self.category_list.pop(category.text())

                for i in range(0,self.roll_limit):
                    if category.text() in  self.settings["category_slots"][str(i+1)] :
                        self.settings["category_slots"][str(i+1)].pop(category.text())

                rem_cat = self.list_category.takeItem(self.list_category.currentRow())
                del rem_cat
                
                self.combo_item_category.removeItem(self.combo_item_category.findText(category.text()))
 
    def removeItem(self):
        selected_category =  self.category_list[self.combo_item_category.currentText()]
        item = self.list_item.item(self.list_item.currentRow())
        if item:
            if item.text() in selected_category:
                selected_category.remove(item.text())
                rem_itm = self.list_item.takeItem(self.list_item.currentRow())
                del rem_itm
 

    def toggleInSequence(self,state):
        if state == Qt.Unchecked:
            self.settings["slot_in_sequence"] = 0
        else:
            self.settings["slot_in_sequence"] = 1
        pass

    def cancelSave(self):
        self.loadCategoryList()
        self.loadSettings()
        self.done(0)

    def saveSettings(self):
        self.settings["roll_count"]  = int(self.dsb_roll_count.value())
        self.settings["timer_limit"] = int(self.dsb_minutes.value() * 60)

        self.settings["saturation_priority"] = self.color_priority_option[self.combo_sat.currentIndex()]
        self.settings["value_priority"]      = self.color_priority_option[self.combo_val.currentIndex()]

        self.settings["saturation_cutoff"]["low"]  = int(self.dsb_sat_low.value())
        self.settings["saturation_cutoff"]["mid"]  = int(self.dsb_sat_mid.value())
        self.settings["saturation_cutoff"]["high"]  = int(self.dsb_sat_high.value())
        self.settings["saturation_cutoff"]["lim"]  = int(self.dsb_sat_lim.value())
 
        self.settings["value_cutoff"]["low"] = int(self.dsb_val_low.value())
        self.settings["value_cutoff"]["mid"] = int(self.dsb_val_mid.value())
        self.settings["value_cutoff"]["high"] = int(self.dsb_val_high.value())
        self.settings["value_cutoff"]["lim"]  = int(self.dsb_val_lim.value())

        json_setting = json.dumps(self.settings, indent=4)
    
        with open(os.path.dirname(os.path.realpath(__file__)) + '/settings.json', "w") as outfile:
            outfile.write(json_setting)
        
        
        json_category = json.dumps(self.category_list, indent=4)
    
        with open(os.path.dirname(os.path.realpath(__file__)) + '/category.json', "w") as outfile:
            outfile.write(json_category)
        

        self.done(1)
        
        




       