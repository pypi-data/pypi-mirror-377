#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/18 22:12
# @Author  : 兵
# @email    : 1747193328@qq.com

from PySide6.QtCore import Signal, QSize
from PySide6.QtGui import QAction, QIcon, QActionGroup
from qfluentwidgets import CommandBar, Action,CommandBarView


class KitToolBarBase(CommandBarView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent
        self._actions = {}
        self.setIconSize(QSize(24, 24))
        self.setSpaing(2)
        self.init_actions()

    def addButton(self, name,icon,callback,checkable=False):
        action = Action(QIcon(icon),name,self)
        if checkable:
            action.setCheckable(True)
            action.toggled.connect(callback)
        else:
            action.triggered.connect(callback)
        self._actions[name] = action
        self.addAction(action)
        action.setToolTip(name)
        return action

    def init_actions(self):
        pass
class NepDisplayGraphicsToolBar(KitToolBarBase):
    panSignal=Signal(bool)
    resetSignal=Signal()
    findMaxSignal=Signal()
    sparseSignal=Signal()
    penSignal=Signal(bool)
    undoSignal=Signal()
    discoverySignal=Signal()
    deleteSignal=Signal()
    editInfoSignal=Signal()
    revokeSignal=Signal()
    exportSignal=Signal()
    shiftEnergySignal=Signal()
    inverseSignal=Signal()
    selectIndexSignal=Signal()
    rangeSignal=Signal()
    dftd3Signal=Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.action_group:QActionGroup

    def init_actions(self):
        self.addButton("Reset View",QIcon(":/images/src/images/init.svg"),self.resetSignal)
        pan_action=self.addButton("Pan View",
                                   QIcon(":/images/src/images/pan.svg"),
                                   self.pan,
                                   True
                                   )
        self.addButton("Select by Index",
                       QIcon(":/images/src/images/index.svg"),
                       self.selectIndexSignal)
        self.addButton("Select by Range",
                       QIcon(":/images/src/images/data_range.svg"),
                       self.rangeSignal)
        find_max_action = self.addButton("Find Max Error Point",
                                        QIcon(":/images/src/images/find_max.svg"),
                                        self.findMaxSignal)
        sparse_action=self.addButton("Sparse samples",
                                    QIcon(":/images/src/images/sparse.svg"),
                                    self.sparseSignal)




        pen_action=self.addButton("Mouse Selection",
                                   QIcon(":/images/src/images/pen.svg"),
                                   self.pen,
                                   True
                                   )
        self.action_group = QActionGroup(self)
        self.action_group.setExclusive(True)  # 设置为互斥组
        self.action_group.addAction(pan_action)
        self.action_group.addAction(pen_action)
        self.action_group.setExclusionPolicy(QActionGroup.ExclusionPolicy.ExclusiveOptional)
        discovery_action = self.addButton("Finding non-physical structures",
                                        QIcon(":/images/src/images/discovery.svg"),
                                        self.discoverySignal)
        inverse_action = self.addButton("Inverse Selection",
                                     QIcon(":/images/src/images/inverse.svg"),
                                     self.inverseSignal)
        revoke_action = self.addButton("Undo",
                                     QIcon(":/images/src/images/revoke.svg"),
                                     self.revokeSignal)

        delete_action = self.addButton("Delete Selected Items",
                                     QIcon(":/images/src/images/delete.svg"),
                                     self.deleteSignal)


        self.addSeparator()
        self.addButton("Edit Info",
                       QIcon(":/images/src/images/edit_info.svg"),
                       self.editInfoSignal)
        export_action = self.addButton("Export structure descriptor",
                                     QIcon(":/images/src/images/export.svg"),
                                     self.exportSignal)
        self.addSeparator()
        self.addButton("Energy Baseline Shift",
                       QIcon(":/images/src/images/alignment.svg"),
                       self.shiftEnergySignal)
        self.addButton("DFT D3",
                       QIcon(":/images/src/images/dft_d3.png"),
                       self.dftd3Signal)
    def reset(self):
        if self.action_group.checkedAction():
            self.action_group.checkedAction().setChecked(False)

    def pan(self, checked):
        """切换平移模式"""
        if checked:
            self.panSignal.emit(True)
        else:
            self.panSignal.emit(False)

    def pen(self, checked):
        if checked:
            self.penSignal.emit(True)
        else:
            self.penSignal.emit(False)




class StructureToolBar(KitToolBarBase):
    pass
    showBondSignal=Signal(bool)
    orthoViewSignal=Signal(bool)
    autoViewSignal=Signal(bool)
    exportSignal=Signal()
    arrowSignal=Signal()
    def init_actions(self):
        view_action = self.addButton( "Ortho View",
                                          QIcon(":/images/src/images/view_change.svg"),
                                          self.view_changed,
                                    True)
        auto_action = self.addButton( "Automatic View",
                                          QIcon(":/images/src/images/auto_distance.svg"),
                                          self.auto_view_changed,
                                    True)
        show_bond_action = self.addButton( "Show Bonds",
                                          QIcon(":/images/src/images/show_bond.svg"),
                                          self.show_bond,
                                         True)

        self.addButton("Show Arrows",
                       QIcon(":/images/src/images/xyz.svg"),
                       self.arrowSignal)

        export_action = self.addButton("Export current structure",
                                     QIcon(":/images/src/images/export1.svg"),
                                     self.exportSignal)

    def view_changed(self,checked):
        if checked:
            self.orthoViewSignal.emit(True)
        else:
            self.orthoViewSignal.emit(False)
    def auto_view_changed(self,checked):
        if checked:
            self.autoViewSignal.emit(True)
        else:
            self.autoViewSignal.emit(False)
    def show_bond(self,checked):

        if checked:
            self._actions["Show Bonds"].setIcon(QIcon(":/images/src/images/hide_bond.svg"))
            self.showBondSignal.emit(True)
        else:
            self._actions["Show Bonds"].setIcon(QIcon(":/images/src/images/show_bond.svg"))
            self.showBondSignal.emit(False)
