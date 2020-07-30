"""
# Shantae Herrmann
# Professor Lim
# ATCM 3311.0U1
# Assignment 03
# 07/31/2020
# Description: This program will create a turntable tool for maya
"""

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.cmds as mc
import math
import sys
import mtoa.utils as mutils

from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QCheckBox

import mayautils


def maya_main_window():
    """Return the maya main window widget"""
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window), QtWidgets.QWidget)


class TurntableUI(QtWidgets.QDialog):
    """Smart Save UI Class"""

    def __init__(self):
        """Constructor"""
        # Passing the object SimpleUI as an argument to super()
        # makes this line python 2 and 3 compatible
        super(TurntableUI, self).__init__(parent=maya_main_window())
        self.scene = mayautils.SceneFile()
        self.setWindowTitle("Create Turntable")
        self.resize(500, 200)
        self.setWindowFlags(self.windowFlags() ^
                            QtCore.Qt.WindowContextHelpButtonHint)
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        """Create widgets for our UI"""
        self.title_lbl = QtWidgets.QLabel("Create Turntable")
        self.title_lbl.setStyleSheet("font: bold 20px")
        self.title_lbl = QtWidgets.QLabel("Create Turntable")
        self.title_lbl.setStyleSheet("font: bold 20px")

        self.wireframe = QtWidgets.QCheckBox("Wireframe")
        self.wireframe.setChecked(False)

        self.wireframeShaded = QtWidgets.QCheckBox("Wireframe on Shaded")
        self.wireframeShaded.setChecked(False)

        self.light = QtWidgets.QCheckBox("Create Lights")
        self.light.setChecked(False)

        self.length_lbl = QtWidgets.QLabel("Frames")
        self.length_le = QtWidgets.QLineEdit()
        self.length_le.setText(self.scene.length)

        self.undoTurntable_btn = QtWidgets.QPushButton("Undo Turntable")
        self.renderOptions_btn = QtWidgets.QPushButton("Render Options")

        self.generate_turntable_btn = QtWidgets.QPushButton("Generate Turntable")
        self.render_btn = QtWidgets.QPushButton("Render")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")

    def create_layout(self):
        """Lay out our widgets in the UI"""
        self.length_lay = QtWidgets.QHBoxLayout()
        self.length_lay.addWidget(self.length_lbl)
        self.length_lay.addWidget(self.length_le)

        self.bottom_btn_lay = QtWidgets.QHBoxLayout()
        self.bottom_btn_lay.addWidget(self.generate_turntable_btn)
        self.bottom_btn_lay.addWidget(self.render_btn)
        self.bottom_btn_lay.addWidget(self.cancel_btn)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.title_lbl)
        self.main_layout.addWidget(self.wireframe)
        self.main_layout.addWidget(self.wireframeShaded)
        self.main_layout.addWidget(self.light)
        self.main_layout.addLayout(self.length_lay)
        self.main_layout.addWidget(self.undoTurntable_btn)
        self.main_layout.addWidget(self.renderOptions_btn)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.bottom_btn_lay)
        self.setLayout(self.main_layout)

    def _populate_scenefile_properties(self):
        """Populates the SceneFile object's properties from the UI"""
        self.scene.length = self.length_le.text()

    def create_connections(self):
        """Connect our widgets signals to slots"""
        self.cancel_btn.clicked.connect(self.cancel)
        self.render_btn.clicked.connect(self.render)
        self.generate_turntable_btn.clicked.connect(self.generate_turntable)
        self.wireframe.stateChanged.connect(lambda: self.wire_check(self.wireframe))
        self.wireframeShaded.stateChanged.connect(lambda: self.wireShaded_check(self.wireframeShaded))
        self.light.stateChanged.connect(lambda: self.light_check(self.light))
        self.renderOptions_btn.clicked.connect(self.renderOptions)
        self.undoTurntable_btn.clicked.connect(self.undoTurntable)

    @QtCore.Slot()
    def generate_turntable(self):
        """Automatically creates 360 degree turntable with lights relative to object size"""
        # Creates object selection which selects current object in panel view
        objectSelection = cmds.ls(sl=True)
        bBox = cmds.exactWorldBoundingBox(objectSelection)

        objectDistance = cmds.shadingNode('distanceBetween', asUtility=True)
        locator1 = cmds.spaceLocator()
        locatorShape1 = cmds.listRelatives(locator1[0], shapes=True)

        locator2 = cmds.spaceLocator()
        locatorShape2 = cmds.listRelatives(locator2[0], shapes=True)

        #Creates ground cylinder for selected object.
        objectGround = cmds.polyCylinder(axis=[0, 1, 0], height=bBox[4] / 10.0, radius=bBox[3] * 2.5, subdivisionsX=30,
                                   subdivisionsZ=1, n='turntableGround')
        cmds.setAttr(objectGround[0] + '.translateY', bBox[1] - (bBox[4] / 10.0) / 2)
        cmds.parent(locator2[0], objectSelection[0])
        cmds.setAttr(locator1[0] + '.translateX', 0)
        cmds.setAttr(locator1[0] + '.translateY', 0)
        cmds.setAttr(locator1[0] + '.translateZ', 0)
        cmds.setAttr(locator2[0] + '.translateX', 0)
        cmds.setAttr(locator2[0] + '.translateY', 0)
        cmds.setAttr(locator2[0] + '.translateZ', 0)
        cmds.connectAttr(locatorShape1[0] + '.worldPosition', objectDistance + '.point1')
        cmds.connectAttr(locatorShape2[0] + '.worldPosition', objectDistance + '.point2')

        #Creates nurb circle for the turntable and adjusts position based on object selected.
        cameraCircle = cmds.circle(radius = bBox[3] * 9, sections = 50)
        cmds.setAttr(cameraCircle[0] + '.rotateX', 90)
        cmds.reverseCurve(cameraCircle[0])
        cmds.setAttr(cameraCircle[0] + '.translateY', bBox[1] - (bBox[4] / 10.0) / 2)
        cmds.select(cameraCircle, r=True)
        cmds.move(0, 5, 0)

        #Creates turntable camera and groups the camera, circle, and ground.
        cmds.camera(n='turntableCamera')
        cmds.group('nurbsCircle1', 'turntableCamera1', 'turntableGround', n='cameraSetup')

        # Creates a path animation based on the objects 'turntableCamera1' and 'cameraCircle'
        cmds.pathAnimation('turntableCamera1', cameraCircle[0], fractionMode=True, follow=True, followAxis='x', upAxis='y',
                           worldUpType='vector', worldUpVector=[0, 1, 0], inverseUp=False, inverseFront=False,
                           bank=False, startTimeU=1, endTimeU=120)
        cmds.delete('locator1', 'locator2')

    @QtCore.Slot()
    def cancel(self):
        """Quits the dialog"""
        self.close()

    @QtCore.Slot()
    def render(self):
        """Opens the arnold render view"""
        cmds.arnoldRenderView()

    @QtCore.Slot()
    def renderOptions(self):
        """Opens the render options menu"""
        cmds.RenderGlobalsWindow()

    @QtCore.Slot()
    def undoTurntable(self):
        """Deletes the current turntable"""
        cmds.delete('nurbsCircle1', 'turntableCamera1', 'cameraSetup', 'turntableGround')

    def wire_check(self, wireframe):
        """Makes objects in scene wireframe mode"""
        if wireframe.text() == "Wireframe":
            panel = mc.getPanel(withLabel='Persp View')
            def makeWireframe():
                if wireframe.isChecked() == True:
                    cmds.modelEditor(panel, edit=True, displayAppearance='wireframe')
                else:
                    cmds.modelEditor(panel, edit=True, displayAppearance='flatShaded')

            makeWireframe()

    def wireShaded_check(self, wireframeShaded):
        """Makes objects in scene wireframe on shaded mode"""
        if wireframeShaded.text() == "Wireframe on Shaded":
            panel = mc.getPanel(withLabel='Persp View')
            def makeWireframeShaded():
                if wireframeShaded.isChecked() == True:
                    currentState = mc.modelEditor(panel, q=True, wireframeOnShaded=True)
                    mc.modelEditor(panel, edit=True, wireframeOnShaded=not currentState)
                else:
                    currentState = mc.modelEditor(panel, q=True, wireframeOnShaded=False)
                    mc.modelEditor(panel, edit=True, wireframeOnShaded=not currentState)

            makeWireframeShaded()

    def light_check(self, light):
        """Creates skydome light in scene"""
        if light.text() == "Create Lights":
            if light.isChecked() == True:
                Skydome = cmds.shadingNode('aiSkyDomeLight', asLight=True)
                cmds.group(Skydome, name='light_GRP')
            else:
                cmds.delete('aiSkyDomeLight1', 'transform1', 'light_GRP')

    def getFrameLength(self):
        print(self.length_le.text())