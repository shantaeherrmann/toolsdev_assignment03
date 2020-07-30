"""
# Shantae Herrmann
# Professor Lim
# ATCM 3311.0U1
# Assignment 03
# 07/31/2020
# Description: This program will create a turntable tool for maya
"""

import pymel.core as pmc

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import math
import sys

from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance

class SceneFile(object):
    """Class used to to represent a DCC software scene file

    The class will be a convenient object that we can use to manipulate our
    scene files. Examples features include the ability to predefine our naming
    conventions and automatically increment our versions.
    """

    def __init__(self, length='120'):
        self.length = QLineEdit(self)

    def create_turntable(self):
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

    def render_frame(self):
        '''Opens Arnold render view'''
        cmds.arnoldRenderView()