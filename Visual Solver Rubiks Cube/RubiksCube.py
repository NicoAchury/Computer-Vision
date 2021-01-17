
##################################################
## VISUAL RUBIK'S CUBE SOLVER

# A Rubiks cube solver using Computer Vision and rubik_solver library in Python.
# Please see: https://pypi.org/project/rubik-solver/
# This solver uses the following notation for the Kociemba's Algorithm

#                ----------------
#                | 0  | 1  | 2  |
#                ----------------
#                | 3  | 4  | 5  |
#                ----------------
#                | 6  | 7  | 8  |
#                ----------------
# -------------------------------------------------------------
# | 9  | 10 | 11 | 18 | 19 | 20 | 27 | 28 | 29 | 36 | 37 | 38 |
# -------------------------------------------------------------
# | 12 | 13 | 14 | 21 | 22 | 23 | 30 | 31 | 32 | 39 | 40 | 41 |
# -------------------------------------------------------------
# | 15 | 16 | 17 | 24 | 25 | 26 | 33 | 34 | 35 | 42 | 43 | 44 |
# -------------------------------------------------------------
#                ----------------
#                | 45 | 46 | 47 |
#                ----------------
#                | 48 | 49 | 50 |
#                ----------------
#                | 51 | 52 | 53 |
#                ----------------
# Kociemba solver needs the following cubies at place:

# 4 (Upper center): YELLOW
# 13 (Left center): BLUE
# 22 (Front center): RED
# 31 (Right center): GREEN
# 40 (Back center): ORANGE
# 49 (Down center): WHITE


##################################################
## This program is free software; you can redistribute it and/or modify it
## under the terms of the GNU General Public Licence.
##################################################
## Author: Nicolas Achury
## Credits: [Nicolas Achury, Victor Cabezas]
## Version: 1
## Email: nicolas.beltran.18@alumni.ucl.ac.uk
##################################################



#//////////////////////////////////////////////////////////////////////////////////////////////////////////
# LIBRARIES
#//////////////////////////////////////////////////////////////////////////////////////////////////////////

import cv2
import numpy as np
from rubik_solver import utils
import time
import warnings
from tkinter import messagebox 
import tkinter
warnings.simplefilter(action='ignore', category=FutureWarning)


#//////////////////////////////////////////////////////////////////////////////////////////////////////////
# FUNCTIONS DEFINITIONS 
#//////////////////////////////////////////////////////////////////////////////////////////////////////////

#----------------------------------------------------------------------------------------------------------
# Nothing - Required to calibrate the color in Real-Time
#----------------------------------------------------------------------------------------------------------
def Nothing(x):
	pass

#----------------------------------------------------------------------------------------------------------
# DisaggregatedSolution - Disaggregates the Cubiks solution into a simplied form (e.g. R2 --> R R)
#----------------------------------------------------------------------------------------------------------

def DisaggregatedSolution(Solution):

	for i, ele in enumerate(Solution):
		if ele == 'R2':
			Solution[i] = 'R'
			Solution.insert(i,'R')
		elif ele == 'D2':
			Solution[i] = 'D'
			Solution.insert(i,'D')
		elif ele == 'U2':
			Solution[i] = 'U'
			Solution.insert(i,'U')	
		elif ele == 'L2':
			Solution[i] = 'L'
			Solution.insert(i,'L')
		elif ele == 'B2':
			Solution[i] = 'B'
			Solution.insert(i,'B')
		elif ele == 'F2':
			Solution[i] = 'F'
			Solution.insert(i,'F')

	return Solution

#----------------------------------------------------------------------------------------------------------
# CreateMatrix - Considering a list of colors and central points observed from CV2, this function  
#			   - shapes the data into a matrix form to be equal to the Cube's face itself.
#----------------------------------------------------------------------------------------------------------

def CreateMatrix(Points, Colors):

	Pointsc1 = Points[0:3]
	Pointsc2 = Points[3:6]
	Pointsc3 = Points[6:9]

	Colorsc1 = np.array(Colors[0:3])
	Colorsc2 = np.array(Colors[3:6])
	Colorsc3 = np.array(Colors[6:9])

	Outc1 = np.argsort(Pointsc1 ,axis=0)
	Outc2 = np.argsort(Pointsc2 ,axis=0)
	Outc3 = np.argsort(Pointsc3 ,axis=0)

	Colorsc1 = Colorsc1[Outc1[:,1]]
	Colorsc2 = Colorsc2[Outc2[:,1]]
	Colorsc3 = Colorsc3[Outc3[:,1]]

	Pointsc1 = Pointsc1[Outc1[:,1]]
	Pointsc2 = Pointsc2[Outc2[:,1]]
	Pointsc3 = Pointsc3[Outc3[:,1]]
	
	MatrixPoints = np.concatenate((Pointsc1, Pointsc2, Pointsc3),axis=1)
	MatrixPoints = MatrixPoints.reshape((3,3,2))
	MatrixColors = np.array([Colorsc1,Colorsc2,Colorsc3]).T

	return MatrixColors, MatrixPoints

#----------------------------------------------------------------------------------------------------------
# IdentifyPosCol - From the list of rectangles indentified, this function calculates the central point of 
#				 - each one and the associated color.
#----------------------------------------------------------------------------------------------------------

def IdentifyPosCol(Rect_l):


	Points = np.zeros((9,2))
	Colors = []
	for i,Rect in enumerate(Rect_l):
		M = cv2.moments(Rect)
		cX = int(M['m10']/M['m00'])
		cY = int(M['m01']/M['m00'])
		HSV_val = hsv[cY][cX]
		Points[i][0] = cX
		Points[i][1] = cY
		if (lower_blue<=HSV_val).all() and (HSV_val<=upper_blue).all():
			Colors.append('b')
		elif (lower_green<=HSV_val).all() and (HSV_val<=upper_green).all():
			Colors.append('g')
		elif (lower_yellow<=HSV_val).all() and (HSV_val<=upper_yellow).all():
			Colors.append('y')
		elif (lower_orange<=HSV_val).all() and (HSV_val<=upper_orange).all():
			Colors.append('o')
		elif (lower_red<=HSV_val).all() and (HSV_val<=upper_red).all():
			Colors.append('r')
		elif ((lower_white1<=HSV_val).all() and (HSV_val<=upper_white1).all()) or ((lower_white2<=HSV_val).all() and (HSV_val<=upper_white2).all()):
			Colors.append('w')
		else:
			Colors.append('Z')

	if 'Z' in Colors:
		print(f'Error en: {Colors}')
		Click = messagebox.showerror("Error","Color calibration is required")
		if Click == "ok":
			exit()

	Colors = np.array(Colors)

	if len(Colors) != 9:
		print(f'Error en: {Colors}')
		Click = messagebox.showerror("Error","Color calibration is required")
		if Click == "ok":
			exit()

	out = np.argsort(Points,axis=0)
	Colors = Colors[out[:,0]]
	Points = Points[out[:,0]]


	return Colors, Points

#----------------------------------------------------------------------------------------------------------
# StringFace - This function takes the a matrix of observed colors and shape it into a concatenated string  
#			 - required for the Kociemba's algorithm
#----------------------------------------------------------------------------------------------------------

def StringFace(Matrix):
	s=''
	for row in Matrix:
		for e in row:
			s = s+e
	return s

#----------------------------------------------------------------------------------------------------------
# MovementR - This function defines the R movement using CV. For reference please see:
#			- https://ruwix.com/the-rubiks-cube/notation/
#----------------------------------------------------------------------------------------------------------

def MovementR(TakeIniFlag,Rectangles,stable, f_c, Solution, inverse):

	global ColorPosIni
	global ColorPosEnd

	if TakeIniFlag == 1:
		Colors, Points = IdentifyPosCol(Rectangles)
		MatrixColors, MatrixPoints  = CreateMatrix(Points, Colors)
		ColorPosIni = np.array(MatrixColors[:,2])
		TakeIniFlag = 0
		
	if stable > 10:
		Colors, Points = IdentifyPosCol(Rectangles)
		MatrixColors, MatrixPoints  = CreateMatrix(Points, Colors)
		ColorPosEnd = np.array(MatrixColors[:,2])
		if inverse == 0:
			Ini = (int(MatrixPoints[2][2][0]),int(MatrixPoints[2][2][1]))
			End = (int(MatrixPoints[0][2][0]),int(MatrixPoints[0][2][1]))
		elif inverse == 1:
			Ini = (int(MatrixPoints[0][2][0]),int(MatrixPoints[0][2][1]))
			End = (int(MatrixPoints[2][2][0]),int(MatrixPoints[2][2][1]))
			
		if (ColorPosIni == ColorPosEnd).all():
			cv2.arrowedLine(f_c, Ini, End,(0,255,0),5)

	if stable == 40:
	 	if (ColorPosIni != ColorPosEnd).any():
	 		print('movement complete')
	 		Solution.pop(0)
	 		TakeIniFlag = 1

	return TakeIniFlag, Solution

#----------------------------------------------------------------------------------------------------------
# MovementD - This function defines the D movement using CV. For reference please see:
#			- https://ruwix.com/the-rubiks-cube/notation/
#----------------------------------------------------------------------------------------------------------

def MovementD(TakeIniFlag,Rectangles,stable, f_c, Solution, inverse):

	global ColorPosIni
	global ColorPosEnd

	if TakeIniFlag == 1:
		Colors, Points = IdentifyPosCol(Rectangles)
		MatrixColors, MatrixPoints  = CreateMatrix(Points, Colors)
		ColorPosIni = np.array(MatrixColors[2,:])
		TakeIniFlag = 0

	if stable > 10:
		Colors, Points = IdentifyPosCol(Rectangles)
		MatrixColors, MatrixPoints  = CreateMatrix(Points, Colors)
		ColorPosEnd = np.array(MatrixColors[2,:])

		if inverse == 0:
			Ini = (int(MatrixPoints[2][0][0]),int(MatrixPoints[2][0][1]))
			End = (int(MatrixPoints[2][2][0]),int(MatrixPoints[2][2][1]))
		elif inverse == 1:
			Ini = (int(MatrixPoints[2][2][0]),int(MatrixPoints[2][2][1]))
			End = (int(MatrixPoints[2][0][0]),int(MatrixPoints[2][0][1]))

		if (ColorPosIni == ColorPosEnd).all():
			cv2.arrowedLine(f_c, Ini, End,(0,255,0),5)

	if stable == 40:
	 	if (ColorPosIni != ColorPosEnd).any():
	 		print('movement complete')
	 		Solution.pop(0)
	 		TakeIniFlag = 1

	return TakeIniFlag, Solution

#----------------------------------------------------------------------------------------------------------
# MovementL - This function defines the L movement using CV. For reference please see:
#			- https://ruwix.com/the-rubiks-cube/notation/
#----------------------------------------------------------------------------------------------------------

def MovementL(TakeIniFlag,Rectangles,stable, f_c, Solution, inverse):

	global ColorPosIni
	global ColorPosEnd

	if TakeIniFlag == 1:
		Colors, Points = IdentifyPosCol(Rectangles)
		MatrixColors, MatrixPoints  = CreateMatrix(Points, Colors)
		ColorPosIni = np.array(MatrixColors[:,0])
		TakeIniFlag = 0

	if stable > 10:
		Colors, Points = IdentifyPosCol(Rectangles)
		MatrixColors, MatrixPoints  = CreateMatrix(Points, Colors)
		ColorPosEnd = np.array(MatrixColors[:,0])
		if inverse == 0:
			Ini = (int(MatrixPoints[0][0][0]),int(MatrixPoints[0][0][1]))
			End = (int(MatrixPoints[2][0][0]),int(MatrixPoints[2][0][1]))
		elif inverse == 1:
			Ini = (int(MatrixPoints[2][0][0]),int(MatrixPoints[2][0][1]))
			End = (int(MatrixPoints[0][0][0]),int(MatrixPoints[0][0][1]))

		if (ColorPosIni == ColorPosEnd).all():
			cv2.arrowedLine(f_c, Ini, End,(0,255,0),5)

	if stable == 40:
		if (ColorPosIni != ColorPosEnd).any():
			print('movement complete')
			Solution.pop(0)
			TakeIniFlag = 1

	return TakeIniFlag, Solution

#----------------------------------------------------------------------------------------------------------
# MovementU - This function defines the U movement using CV. For reference please see:
#			- https://ruwix.com/the-rubiks-cube/notation/
#----------------------------------------------------------------------------------------------------------

def MovementU(TakeIniFlag,Rectangles,stable, f_c, Solution, inverse):

	global ColorPosIni
	global ColorPosEnd

	if TakeIniFlag == 1:
		Colors, Points = IdentifyPosCol(Rectangles)
		MatrixColors, MatrixPoints  = CreateMatrix(Points, Colors)
		ColorPosIni = np.array(MatrixColors[0,:])
		TakeIniFlag = 0

	if stable > 10:
		Colors, Points = IdentifyPosCol(Rectangles)
		MatrixColors, MatrixPoints  = CreateMatrix(Points, Colors)
		ColorPosEnd = np.array(MatrixColors[0,:])
		if inverse == 0:
			Ini = (int(MatrixPoints[0][2][0]),int(MatrixPoints[0][2][1]))
			End = (int(MatrixPoints[0][0][0]),int(MatrixPoints[0][0][1]))
		elif inverse == 1:
			Ini = (int(MatrixPoints[0][0][0]),int(MatrixPoints[0][0][1]))
			End = (int(MatrixPoints[0][2][0]),int(MatrixPoints[0][2][1]))
		if (ColorPosIni == ColorPosEnd).all():
			cv2.arrowedLine(f_c, Ini, End,(0,255,0),5)

	if stable == 40:
	 	if (ColorPosIni != ColorPosEnd).any():
	 		print('movement complete')
	 		Solution.pop(0)
	 		TakeIniFlag = 1

	return TakeIniFlag, Solution

#----------------------------------------------------------------------------------------------------------
# MovementF - This function defines the F movement using CV. For reference please see:
#			- https://ruwix.com/the-rubiks-cube/notation/
#----------------------------------------------------------------------------------------------------------

def MovementF(TakeIniFlag,Rectangles,stable, f_c, Solution, RotateFlag, StageFlag, inverse):

	global ColorPosIni
	global ColorPosEnd

	if TakeIniFlag == 1:
		Colors, Points = IdentifyPosCol(Rectangles)
		MatrixColors, MatrixPoints  = CreateMatrix(Points, Colors)
		#### Verificar puede rotar (si es simetrica)
		ColorPosIni = np.array(MatrixColors[:,:])
		ColorPosRotate = np.array(list(list(x)[::-1] for x in zip(*ColorPosIni)))
		TakeIniFlag = 0
		if (ColorPosIni!=ColorPosRotate).any():
			RotateFlag = 0
		else:
			RotateFlag = 1
	

	if RotateFlag==0:

		if stable > 10:
			Colors, Points = IdentifyPosCol(Rectangles)
			MatrixColors, MatrixPoints  = CreateMatrix(Points, Colors)
			ColorPosEnd = np.array(MatrixColors[:,:])

			if inverse == 0:

				Ini1 = (int(MatrixPoints[0][0][0]),int(MatrixPoints[0][0][1]))
				End1 = (int(MatrixPoints[0][2][0]),int(MatrixPoints[0][2][1]))
				Ini2 = (int(MatrixPoints[0][2][0]),int(MatrixPoints[0][2][1]))
				End2 = (int(MatrixPoints[2][2][0]),int(MatrixPoints[2][2][1]))
				Ini3 = (int(MatrixPoints[2][2][0]),int(MatrixPoints[2][2][1]))
				End3 = (int(MatrixPoints[2][0][0]),int(MatrixPoints[2][0][1]))
				Ini4 = (int(MatrixPoints[2][0][0]),int(MatrixPoints[2][0][1]))
				End4 = (int(MatrixPoints[0][0][0]),int(MatrixPoints[0][0][1]))		

			elif inverse == 1:

				Ini1 = (int(MatrixPoints[0][2][0]),int(MatrixPoints[0][2][1]))
				End1 = (int(MatrixPoints[0][0][0]),int(MatrixPoints[0][0][1]))
				Ini2 = (int(MatrixPoints[2][2][0]),int(MatrixPoints[2][2][1]))
				End2 = (int(MatrixPoints[0][2][0]),int(MatrixPoints[0][2][1]))
				Ini3 = (int(MatrixPoints[2][0][0]),int(MatrixPoints[2][0][1]))
				End3 = (int(MatrixPoints[2][2][0]),int(MatrixPoints[2][2][1]))
				Ini4 = (int(MatrixPoints[0][0][0]),int(MatrixPoints[0][0][1]))
				End4 = (int(MatrixPoints[2][0][0]),int(MatrixPoints[2][0][1]))
						
			
			if (ColorPosIni == ColorPosEnd).all():
				cv2.arrowedLine(f_c, Ini1, End1,(0,255,0),5)
				cv2.arrowedLine(f_c, Ini2, End2,(0,255,0),5)
				cv2.arrowedLine(f_c, Ini3, End3,(0,255,0),5)
				cv2.arrowedLine(f_c, Ini4, End4,(0,255,0),5)


		if stable == 40:
			if (ColorPosIni != ColorPosEnd).any():
				print('movement complete')
				Solution.pop(0)
				TakeIniFlag = 1
				RotateFlag = 999


	if RotateFlag==1:


		if (stable > 10) and (StageFlag == 0):
			Colors, Points = IdentifyPosCol(Rectangles)
			MatrixColors, MatrixPoints  = CreateMatrix(Points, Colors)
			ColorPosEnd = np.array(MatrixColors[:,:])

			Ini1 = (int(MatrixPoints[0][0][0]),int(MatrixPoints[0][0][1]))
			End1 = (int(MatrixPoints[0][2][0]),int(MatrixPoints[0][2][1]))
			Ini2 = (int(MatrixPoints[1][0][0]),int(MatrixPoints[1][0][1]))
			End2 = (int(MatrixPoints[1][2][0]),int(MatrixPoints[1][2][1]))
			Ini3 = (int(MatrixPoints[2][0][0]),int(MatrixPoints[2][0][1]))
			End3 = (int(MatrixPoints[2][2][0]),int(MatrixPoints[2][2][1]))

			if(ColorPosIni == ColorPosEnd).all():
				cv2.arrowedLine(f_c, Ini1, End1,(0,255,0),5)
				cv2.arrowedLine(f_c, Ini2, End2,(0,255,0),5)
				cv2.arrowedLine(f_c, Ini3, End3,(0,255,0),5)

		if (stable == 40) and (StageFlag == 0):

		 	if (ColorPosIni != ColorPosEnd).any():
		 		TakeIniFlag = 1
		 		StageFlag = StageFlag + 1

		#### Second stage

		if TakeIniFlag == 1:
			Colors, Points = IdentifyPosCol(Rectangles)
			MatrixColors, MatrixPoints  = CreateMatrix(Points, Colors)
			ColorPosIni = np.array(MatrixColors[:,2])
			TakeIniFlag = 0


		if (stable > 10) and (StageFlag == 1):
			Colors, Points = IdentifyPosCol(Rectangles)
			MatrixColors, MatrixPoints  = CreateMatrix(Points, Colors)
			ColorPosEnd = np.array(MatrixColors[:,2])

			if inverse == 0:
				Ini1 = (int(MatrixPoints[2][2][0]),int(MatrixPoints[2][2][1]))
				End1 = (int(MatrixPoints[0][2][0]),int(MatrixPoints[0][2][1]))
			elif inverse == 1:
				Ini1 = (int(MatrixPoints[0][2][0]),int(MatrixPoints[0][2][1]))
				End1 = (int(MatrixPoints[2][2][0]),int(MatrixPoints[2][2][1]))

			if(ColorPosIni == ColorPosEnd).all():
				cv2.arrowedLine(f_c, Ini1, End1,(0,255,0),5)

		if (stable == 40) and (StageFlag == 1):

		 	if (ColorPosIni != ColorPosEnd).any():
		 		TakeIniFlag = 1
		 		StageFlag = StageFlag + 1

		#### third stage

		if TakeIniFlag == 1:
			Colors, Points = IdentifyPosCol(Rectangles)
			MatrixColors, MatrixPoints  = CreateMatrix(Points, Colors)
			ColorPosIni = np.array(MatrixColors[:,:])
			TakeIniFlag = 0


		if (stable > 10) and (StageFlag == 2):
			Colors, Points = IdentifyPosCol(Rectangles)
			MatrixColors, MatrixPoints  = CreateMatrix(Points, Colors)
			ColorPosEnd = np.array(MatrixColors[:,:])

			Ini1 = (int(MatrixPoints[0][2][0]),int(MatrixPoints[0][2][1]))
			End1 = (int(MatrixPoints[0][0][0]),int(MatrixPoints[0][0][1]))
			Ini2 = (int(MatrixPoints[1][2][0]),int(MatrixPoints[1][2][1]))
			End2 = (int(MatrixPoints[1][0][0]),int(MatrixPoints[1][0][1]))
			Ini3 = (int(MatrixPoints[2][2][0]),int(MatrixPoints[2][2][1]))
			End3 = (int(MatrixPoints[2][0][0]),int(MatrixPoints[2][0][1]))			

			if(ColorPosIni == ColorPosEnd).all():
				cv2.arrowedLine(f_c, Ini1, End1,(0,255,0),5)
				cv2.arrowedLine(f_c, Ini2, End2,(0,255,0),5)
				cv2.arrowedLine(f_c, Ini3, End3,(0,255,0),5)

		if (stable == 40) and (StageFlag == 2):

		 	if (ColorPosIni != ColorPosEnd).any():
		 		TakeIniFlag = 1
		 		StageFlag = 0
		 		RotateFlag = 999
		 		Solution.pop(0)
		 		print('movement complete')
				

	return TakeIniFlag, Solution, RotateFlag, StageFlag


#----------------------------------------------------------------------------------------------------------
# MovementF - This function defines the F movement using CV. For reference please see:
#			- https://ruwix.com/the-rubiks-cube/notation/
#----------------------------------------------------------------------------------------------------------

def MovementB(TakeIniFlag,Rectangles,stable, f_c, Solution, StageFlag, inverse):

	global ColorPosIni
	global ColorPosEnd

	if TakeIniFlag == 1:
		Colors, Points = IdentifyPosCol(Rectangles)
		MatrixColors, MatrixPoints  = CreateMatrix(Points, Colors)
		ColorPosIni = np.array(MatrixColors[:,:])
		TakeIniFlag = 0



	if (stable > 10) and (StageFlag == 0):
		Colors, Points = IdentifyPosCol(Rectangles)
		MatrixColors, MatrixPoints  = CreateMatrix(Points, Colors)
		ColorPosEnd = np.array(MatrixColors[:,:])

		Ini1 = (int(MatrixPoints[0][2][0]),int(MatrixPoints[0][2][1]))
		End1 = (int(MatrixPoints[0][0][0]),int(MatrixPoints[0][0][1]))
		Ini2 = (int(MatrixPoints[1][2][0]),int(MatrixPoints[1][2][1]))
		End2 = (int(MatrixPoints[1][0][0]),int(MatrixPoints[1][0][1]))
		Ini3 = (int(MatrixPoints[2][2][0]),int(MatrixPoints[2][2][1]))
		End3 = (int(MatrixPoints[2][0][0]),int(MatrixPoints[2][0][1]))
		
		if(ColorPosIni == ColorPosEnd).all():
			cv2.arrowedLine(f_c, Ini1, End1,(0,255,0),5)
			cv2.arrowedLine(f_c, Ini2, End2,(0,255,0),5)
			cv2.arrowedLine(f_c, Ini3, End3,(0,255,0),5)

	if (stable == 40) and (StageFlag == 0):

	 	if (ColorPosIni != ColorPosEnd).any():
	 		TakeIniFlag = 1
	 		StageFlag = StageFlag + 1

	
	#### Second stage

	if TakeIniFlag == 1:
		Colors, Points = IdentifyPosCol(Rectangles)
		MatrixColors, MatrixPoints  = CreateMatrix(Points, Colors)
		ColorPosIni = np.array(MatrixColors[:,2])
		TakeIniFlag = 0


	if (stable > 10) and (StageFlag == 1):
		Colors, Points = IdentifyPosCol(Rectangles)
		MatrixColors, MatrixPoints  = CreateMatrix(Points, Colors)
		ColorPosEnd = np.array(MatrixColors[:,2])

		if inverse == 0:
			Ini1 = (int(MatrixPoints[2][2][0]),int(MatrixPoints[2][2][1]))
			End1 = (int(MatrixPoints[0][2][0]),int(MatrixPoints[0][2][1]))
		elif inverse == 1:
			Ini1 = (int(MatrixPoints[0][2][0]),int(MatrixPoints[0][2][1]))
			End1 = (int(MatrixPoints[2][2][0]),int(MatrixPoints[2][2][1]))

		if(ColorPosIni == ColorPosEnd).all():
			cv2.arrowedLine(f_c, Ini1, End1,(0,255,0),5)


	if (stable == 40) and (StageFlag == 1):

	 	if (ColorPosIni != ColorPosEnd).any():
	 		TakeIniFlag = 1
	 		StageFlag = StageFlag + 1


	#### third stage

	if TakeIniFlag == 1:
		Colors, Points = IdentifyPosCol(Rectangles)
		MatrixColors, MatrixPoints  = CreateMatrix(Points, Colors)
		ColorPosIni = np.array(MatrixColors[:,:])
		TakeIniFlag = 0

	if (stable > 10) and (StageFlag == 2):
		Colors, Points = IdentifyPosCol(Rectangles)
		MatrixColors, MatrixPoints  = CreateMatrix(Points, Colors)
		ColorPosEnd = np.array(MatrixColors[:,:])

		Ini1 = (int(MatrixPoints[0][0][0]),int(MatrixPoints[0][0][1]))
		End1 = (int(MatrixPoints[0][2][0]),int(MatrixPoints[0][2][1]))
		Ini2 = (int(MatrixPoints[1][0][0]),int(MatrixPoints[1][0][1]))
		End2 = (int(MatrixPoints[1][2][0]),int(MatrixPoints[1][2][1]))
		Ini3 = (int(MatrixPoints[2][0][0]),int(MatrixPoints[2][0][1]))
		End3 = (int(MatrixPoints[2][2][0]),int(MatrixPoints[2][2][1]))

		if(ColorPosIni == ColorPosEnd).all():
			cv2.arrowedLine(f_c, Ini1, End1,(0,255,0),5)
			cv2.arrowedLine(f_c, Ini2, End2,(0,255,0),5)
			cv2.arrowedLine(f_c, Ini3, End3,(0,255,0),5)

	if (stable == 40) and (StageFlag == 2):

	 	if (ColorPosIni != ColorPosEnd).any():
	 		TakeIniFlag = 1
	 		StageFlag = 0
	 		RotateFlag = 999
	 		Solution.pop(0)
	 		print('movement complete')

	return TakeIniFlag, Solution, StageFlag



#//////////////////////////////////////////////////////////////////////////////////////////////////////////
# PARAMETERS INITIALIZATION 
#//////////////////////////////////////////////////////////////////////////////////////////////////////////


#----------------------------------------------------------------------------------------------------------
# Tkinter to manage error windows
#----------------------------------------------------------------------------------------------------------
root = tkinter.Tk()
root.withdraw()


#----------------------------------------------------------------------------------------------------------
# Video Capture using CV2
#----------------------------------------------------------------------------------------------------------

vid = cv2.VideoCapture(0)

#----------------------------------------------------------------------------------------------------------
# TrackBars required to calibrate the Cube's color. If color calibration is required, the following steps
# must be done:

# 1. uncomment lines 671 to 679 - This allows the code to create the window and the trackbars to calibrate
#    the HSV colors.

# 2. On the main, uncomment lines 727 to 732. This allows the code to retrive the values of the trackbars in
#    real time, so the colors can be calibrated.

# 3. On the main, the color ranges must be calibrated. For this uncomment the lines dependending of the color. 
#    E.g:
#    For the red color this lines must be uncommented:
#    lower_red = np.array([hMin,sMin,vMin])
#    upper_red = np.array([hMax,sMax,vMax])

# 4. On the main where the color masks are defined (lines 828-832), you must uncomment and change the following line according
#    the color you are calibrating. E.g. for red color:
#    mask = maskRed ----> you are only seing the red color

# 5. Change the values of HMin, HMax, SMin, SMax, VMin and VMax so you isolate the color on the Calibration
#    screen.
#----------------------------------------------------------------------------------------------------------

# cv2.namedWindow('Parameters', cv2.WINDOW_NORMAL)
# cv2.createTrackbar('HMin','Parameters',0,255, Nothing)
# cv2.createTrackbar('HMax','Parameters',0,255, Nothing)

# cv2.createTrackbar('SMin','Parameters',0,255, Nothing)
# cv2.createTrackbar('SMax','Parameters',0,255, Nothing)

# cv2.createTrackbar('VMin','Parameters',0,255,Nothing)
# cv2.createTrackbar('VMax','Parameters',0,255,Nothing)

#----------------------------------------------------------------------------------------------------------
# Variables and Flags definition
#----------------------------------------------------------------------------------------------------------

stable = 0
FrontFlag = 1
UpFlag = 1
DownFlag = 1
BackFlag = 1
RightFlag = 1
LeftFlag = 1
SolveFlag = 0
sUp=sLeft=sFront=sRight=sBack=sDown = ''
sKociemba = ''
sKociembaFlag = 1
calculate = 1
Solution = []
Points = []
Colors = []
PositionCubeFlag = 0
VisualSolveFlag = 0
t = 0
TakeIniFlag = 1
StageFlag = 0
RotateFlag = 999
VisualRed = 0
VisualBlue = 0
VisualWhite = 0
VisualYellow = 0
VisualOrange = 0
VisualGreen = 0
CubeSolved = 0



#//////////////////////////////////////////////////////////////////////////////////////////////////////////
# MAIN 
#//////////////////////////////////////////////////////////////////////////////////////////////////////////


while True:

	#--------------------------------------------------------------
	# Getting the H,S and V values for color calibration
	#--------------------------------------------------------------

	# hMin = cv2.getTrackbarPos('HMin','Parameters')
	# hMax = cv2.getTrackbarPos('HMax','Parameters')
	# sMin = cv2.getTrackbarPos('SMin','Parameters')
	# sMax = cv2.getTrackbarPos('SMax','Parameters')
	# vMin = cv2.getTrackbarPos('VMin','Parameters')
	# vMax = cv2.getTrackbarPos('VMax','Parameters')


	#--------------------------------------------------------------
	# Color Ranges - Each user has their own color calibration.
	# 			   - this must be done according to light conditions
	#--------------------------------------------------------------

	#BLUE - Tuned
	# lower_blue = np.array([hMin,sMin,vMin])
	# upper_blue = np.array([hMax,sMax,vMax])
	lower_blue = np.array([93,137,114])
	upper_blue = np.array([118,255,255])
	#GREEN - Tuned
	# lower_green = np.array([hMin,sMin,vMin])
	# upper_green = np.array([hMax,sMax,vMax])
	lower_green = np.array([52,90,105])
	upper_green = np.array([87,255,255])
	#YELLOW - Tuned
	# lower_yellow = np.array([hMin,sMin,vMin])
	# upper_yellow = np.array([hMax,sMax,vMax])
	lower_yellow = np.array([28,46,126])
	upper_yellow = np.array([65,255,255])
	#ORANGE - Tuned
	# lower_orange = np.array([hMin,sMin,vMin])
	# upper_orange = np.array([hMax,sMax,vMax])
	lower_orange = np.array([0,0,228])
	upper_orange = np.array([28,255,255])
	#WHITE - Tuned
	# lower_white2 = np.array([hMin,sMin,vMin])
	# upper_white2 = np.array([hMax,sMax,vMax])
	lower_white1 = np.array([0,0,172])
	upper_white1 = np.array([0,21,255])
	lower_white2 = np.array([71,0,132])
	upper_white2 = np.array([109,170,255])
	#RED - Tuned
	# lower_red = np.array([hMin,sMin,vMin])
	# upper_red = np.array([hMax,sMax,vMax])
	lower_red = np.array([146,60,126])
	upper_red = np.array([178,255,255])


	#--------------------------------------------------------------
	# Read the frame from the camera
	#--------------------------------------------------------------

	ret, frame = vid.read()

	#--------------------------------------------------------------
	# Crop the frame as not all the information read by the camera
	# is useful.
	#--------------------------------------------------------------

	f_c= frame[100:350, 150:500]
	
	#--------------------------------------------------------------
	# Convert BGR to HSV for color isolation
	#--------------------------------------------------------------

	hsv = cv2.cvtColor(f_c,cv2.COLOR_BGR2HSV)

	#--------------------------------------------------------------
	# Defining the masks according to the cube's colors
	#--------------------------------------------------------------

	#BLUE
	maskBlue = cv2.inRange(hsv, lower_blue, upper_blue)

	#GREEN
	maskGreen = cv2.inRange(hsv,lower_green,upper_green)
	
	#YELLOW
	maskYellow = cv2.inRange(hsv,lower_yellow,upper_yellow)
	
	#ORANGE
	maskOrange = cv2.inRange(hsv,lower_orange,upper_orange)
	
	#WHITE
	maskWhite1 = cv2.inRange(hsv,lower_white1,upper_white1)
	maskWhite2 = cv2.inRange(hsv,lower_white2,upper_white2)
	maskWhite = maskWhite1+maskWhite2
	
	#RED	
	maskRed = cv2.inRange(hsv,lower_red,upper_red)

	#--------------------------------------------------------------
	# Defining the final mask as a combination of the individual colors
	#--------------------------------------------------------------

	mask = maskBlue+maskGreen+maskYellow+maskOrange+maskWhite+maskRed

	#--------------------------------------------------------------
	# For color calibration, please uncomment the mask associated 
	# with the color you are tuning.
	#--------------------------------------------------------------

	# mask = maskRed
	# mask = maskWhite	
	# mask = maskOrange
	# mask = maskGreen
	# mask = maskYellow
	# mask = maskBlue

	#--------------------------------------------------------------
	# Apply filter to smoothe the image 
	#--------------------------------------------------------------

	mask = cv2.bilateralFilter(mask,1,50,120)	

	#--------------------------------------------------------------
	# Find the contours in the image, this includes the rectangles
	# of the Rubiks cube.
	#--------------------------------------------------------------

	contours = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[0]

	#--------------------------------------------------------------
	# Contours filtering. Only contours with an area between
	# 1117 and 2441 (this was tunned) and 4 edges are useful.
	#--------------------------------------------------------------

	Rectangles=[]

	for i in contours: 
		if (cv2.contourArea(i)>1117) and (cv2.contourArea(i)<2441):
	 		epsilon = 0.11*cv2.arcLength(i, True)
	 		approx = cv2.approxPolyDP(i, epsilon,True)

	 		if len(approx)==4:
	 			cv2.drawContours(f_c, [approx], -1,(255,0,255),2)
	 			Rectangles.append(approx)

	#--------------------------------------------------------------
	# If 9 rectangles are boing identified, it means the identification
	# is stable
	#--------------------------------------------------------------

	if len(Rectangles)!=9:
		stable=0
	elif len(Rectangles)==9:
		stable = stable+1		

	#--------------------------------------------------------------
	# If the rectangle's identification is stable over a 25 cycle
	# read the colors and positions of each face. This identification
	# is repeated until all the flags are 0 which means all the faces
	# were identified
	#--------------------------------------------------------------	
	

	if ((stable == 25) and (FrontFlag or DownFlag or RightFlag or LeftFlag or BackFlag or UpFlag)):

		Colors, Points = IdentifyPosCol(Rectangles)
		MatrixColors, MatrixPoints  = CreateMatrix(Points, Colors)

		# Red color
		if (MatrixColors[1][1] =='r') and (FrontFlag==1):
			sFront = StringFace(MatrixColors)
			FrontFlag = 0
			VisualRed = 1

		# White color
		elif (MatrixColors[1][1] =='w') and (DownFlag==1):
			sDown = StringFace(MatrixColors)
			DownFlag = 0
			VisualWhite = 1

		# Green color
		elif (MatrixColors[1][1] =='g') and (RightFlag==1):
			sRight = StringFace(MatrixColors)
			RightFlag = 0
			VisualGreen = 1

		# Blue color
		elif (MatrixColors[1][1] =='b') and (LeftFlag==1):
			sLeft = StringFace(MatrixColors)
			LeftFlag = 0
			VisualBlue = 1

		# Orange color
		elif (MatrixColors[1][1] =='o') and (BackFlag==1):
			sBack = StringFace(MatrixColors)
			BackFlag = 0
			VisualOrange = 1

		# Yellow color
		elif (MatrixColors[1][1] =='y') and (UpFlag==1):
			sUp = StringFace(MatrixColors)
			UpFlag = 0
			VisualYellow = 1


	#--------------------------------------------------------------
	# Show the visual alert once a face has being identified.
	#--------------------------------------------------------------	

	# Red
	if VisualRed == 1:
		t =  t+1
		if t < 50:
			cv2.putText(frame,'RED READY!', (180, 210),cv2.FONT_HERSHEY_SIMPLEX, 1.5,(0, 0, 255),3,cv2.LINE_AA)
		else:
			cv2.putText(frame,'', (180, 210),cv2.FONT_HERSHEY_SIMPLEX, 1.5,(0, 0, 255),3,cv2.LINE_AA)
			VisualRed = 0
			SolveFlag = 1
			t = 0

	# Blue
	if VisualBlue == 1:
		t =  t+1
		if t < 50:
			cv2.putText(frame,'BLUE READY!', (170, 210),cv2.FONT_HERSHEY_SIMPLEX, 1.5,(255, 0, 0),3,cv2.LINE_AA)
		else:
			cv2.putText(frame,'', (170, 210),cv2.FONT_HERSHEY_SIMPLEX, 1.5,(255, 0, 0),3,cv2.LINE_AA)
			VisualBlue = 0
			SolveFlag = 1
			t = 0

	# Green
	if VisualGreen == 1:
		t =  t+1
		if t < 50:
			cv2.putText(frame,'GREEN READY!', (150, 210),cv2.FONT_HERSHEY_SIMPLEX, 1.5,(0, 255, 0),3,cv2.LINE_AA)
		else:
			cv2.putText(frame,'', (150, 210),cv2.FONT_HERSHEY_SIMPLEX, 1.5,(0, 255, 0),3,cv2.LINE_AA)
			VisualGreen = 0
			SolveFlag = 1
			t = 0

	# Yellow
	if VisualYellow == 1:
		t =  t+1
		if t < 50:
			cv2.putText(frame,'YELLOW READY!', (140, 210),cv2.FONT_HERSHEY_SIMPLEX, 1.5,(0, 255, 255),3,cv2.LINE_AA)
		else:
			cv2.putText(frame,'', (140, 210),cv2.FONT_HERSHEY_SIMPLEX, 1.5,(0, 255, 255),3,cv2.LINE_AA)
			VisualYellow = 0
			SolveFlag = 1
			t = 0

	# Orange
	if VisualOrange == 1:
		t =  t+1
		if t < 50:
			cv2.putText(frame,'ORANGE READY!', (140, 210),cv2.FONT_HERSHEY_SIMPLEX, 1.5,(0, 165, 255),3,cv2.LINE_AA)
		else:
			cv2.putText(frame,'', (140, 210),cv2.FONT_HERSHEY_SIMPLEX, 1.5,(0, 165, 255),3,cv2.LINE_AA)
			VisualOrange = 0
			SolveFlag = 1
			t = 0

	# White
	if VisualWhite == 1:
		t =  t+1
		if t < 50:
			cv2.putText(frame,'WHITE READY!', (165, 210),cv2.FONT_HERSHEY_SIMPLEX, 1.5,(255, 255, 255),3,cv2.LINE_AA)
		else:
			cv2.putText(frame,'', (165, 210),cv2.FONT_HERSHEY_SIMPLEX, 1.5,(255, 255, 255),3,cv2.LINE_AA)
			VisualWhite = 0
			SolveFlag = 1
			t = 0


	#--------------------------------------------------------------
	# Calculate the cube's current configuration in a string sKociemba
	# Please see: https://pypi.org/project/rubik-solver/
	#--------------------------------------------------------------	

	if (sKociembaFlag == 1) and (len(sUp+sLeft+sFront+sRight+sBack+sDown)==54):
		sKociemba = sUp+sLeft+sFront+sRight+sBack+sDown
		sKociembaFlag = 0

	#--------------------------------------------------------------
	# Solve cube using Kociemba algorithm
	# Please see: https://pypi.org/project/rubik-solver/
	# Solution storaged in variable with the same name
	#--------------------------------------------------------------	

	if ((SolveFlag == 1) and (len(sKociemba)==54)):

		try:
			Solution = utils.solve(sKociemba, 'Kociemba')
			Solution = DisaggregatedSolution(Solution)
			SolveFlag = 0
			calculate = 0
		except:
			Click = messagebox.showerror("Error","In the way the faces were shown, it is impossible to find a solution according to the Kociemba's Algorithm. Please bear in mind the algorithm requires a specific order.")
			if Click == "ok":
				exit()


	#--------------------------------------------------------------
	# Position the cube facing the red centre towards the camera
	# and the the yellow centre upward
	#--------------------------------------------------------------	

	if (calculate==0) and (PositionCubeFlag == 0):
		cv2.putText(frame,'POSITION THE RED CENTRE TOWARDS THE CAMERA AND', (25, 50),cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0, 0, 255),2,cv2.LINE_AA)
		cv2.putText(frame,'VERIFY THE YELLOW CENTRE IS FACING UPWARD', (65, 80),cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0, 0, 255),2,cv2.LINE_AA)

	if (calculate==0) and (stable == 20):
		Colors, Points = IdentifyPosCol(Rectangles)
		MatrixColors, MatrixPoints  = CreateMatrix(Points, Colors)

		if (MatrixColors[1][1]=='r'):
			PositionCubeFlag = 1

	if (calculate==0) and (PositionCubeFlag == 1) and (VisualSolveFlag == 0):
		t =  t+1
		if t < 100:
			cv2.putText(frame,'READY?', (220, 220),cv2.FONT_HERSHEY_SIMPLEX, 2,(0, 0, 255),4,cv2.LINE_AA)
		else:
			cv2.putText(frame,'', (220, 220),cv2.FONT_HERSHEY_SIMPLEX, 2,(0, 0, 255),4,cv2.LINE_AA)
			VisualSolveFlag = 1
			t = 0



#//////////////////////////////////////////////////////////////////////////////////////////////////////////
# VISUAL MOVEMENTS 
#//////////////////////////////////////////////////////////////////////////////////////////////////////////


#----------------------------------------------------------------------------------------------------------
# R - MOVEMENT
#----------------------------------------------------------------------------------------------------------

	if (VisualSolveFlag==1) and (len(Solution)>0):
		if (Solution[0] == "R"):
			TakeIniFlag, Solution = MovementR(TakeIniFlag,Rectangles,stable, f_c, Solution, 0)
		elif (Solution[0] == "R'"):
			TakeIniFlag, Solution = MovementR(TakeIniFlag,Rectangles,stable, f_c, Solution, 1)		
		if len(Solution)==0:
			CubeSolved = 1
			print('Cube Solved')

#----------------------------------------------------------------------------------------------------------
# D - MOVEMENT
#----------------------------------------------------------------------------------------------------------

	if (VisualSolveFlag==1) and (len(Solution)>0):
		if (Solution[0] == "D"):
			TakeIniFlag, Solution = MovementD(TakeIniFlag,Rectangles,stable, f_c, Solution, 0)
		elif (Solution[0] == "D'"):
			TakeIniFlag, Solution = MovementD(TakeIniFlag,Rectangles,stable, f_c, Solution, 1)
		if len(Solution)==0:
			CubeSolved = 1
			print('Cube Solved')

#----------------------------------------------------------------------------------------------------------
# L - MOVEMENT
#----------------------------------------------------------------------------------------------------------

	if (VisualSolveFlag==1) and (len(Solution)>0):
		if (Solution[0] == "L"):
			TakeIniFlag, Solution = MovementL(TakeIniFlag,Rectangles,stable, f_c, Solution, 0)
		elif (Solution[0] == "L'"):
			TakeIniFlag, Solution = MovementL(TakeIniFlag,Rectangles,stable, f_c, Solution, 1)
		if len(Solution)==0:
			CubeSolved = 1
			print('Cube Solved')

#----------------------------------------------------------------------------------------------------------
# U - MOVEMENT
#----------------------------------------------------------------------------------------------------------

	if (VisualSolveFlag==1) and (len(Solution)>0):
		if (Solution[0] == "U"):
			TakeIniFlag, Solution = MovementU(TakeIniFlag,Rectangles,stable, f_c, Solution, 0)
		elif (Solution[0] == "U'"):
			TakeIniFlag, Solution = MovementU(TakeIniFlag,Rectangles,stable, f_c, Solution, 1)
		if len(Solution)==0:
			CubeSolved = 1
			print('Cube Solved')

#----------------------------------------------------------------------------------------------------------
# F - MOVEMENT
#----------------------------------------------------------------------------------------------------------

	if (VisualSolveFlag==1) and (len(Solution)>0):
		if (Solution[0] == "F"):
			TakeIniFlag, Solution, RotateFlag, StageFlag = MovementF(TakeIniFlag,Rectangles,stable, f_c, Solution, RotateFlag, StageFlag, 0)
		elif (Solution[0] == "F'"):
			TakeIniFlag, Solution, RotateFlag, StageFlag = MovementF(TakeIniFlag,Rectangles,stable, f_c, Solution, RotateFlag, StageFlag, 1)
		if len(Solution)==0:
			CubeSolved = 1
			print('Cube Solved')

#----------------------------------------------------------------------------------------------------------
# B - MOVEMENT
#----------------------------------------------------------------------------------------------------------

	if (VisualSolveFlag==1) and (len(Solution)>0):
		if (Solution[0] == "B"):
			TakeIniFlag, Solution, StageFlag = MovementB(TakeIniFlag,Rectangles,stable, f_c, Solution, StageFlag, 0)
		elif (Solution[0] == "B'"):
			TakeIniFlag, Solution, StageFlag = MovementB(TakeIniFlag,Rectangles,stable, f_c, Solution, StageFlag, 1)
		if len(Solution)==0:
			CubeSolved = 1
			print('Cube Solved')


#//////////////////////////////////////////////////////////////////////////////////////////////////////////
# CUBE SOLVED
#//////////////////////////////////////////////////////////////////////////////////////////////////////////

#----------------------------------------------------------------------------------------------------------
# Once the cube is solved, show the visual alert.
#----------------------------------------------------------------------------------------------------------

	if CubeSolved == 1:
		t =  t+1
		if t < 200:
			cv2.putText(frame,'CUBE SOLVED!', (165, 210),cv2.FONT_HERSHEY_SIMPLEX, 1.5,(255, 0, 255),3,cv2.LINE_AA)
		else:
			cv2.putText(frame,'', (165, 210),cv2.FONT_HERSHEY_SIMPLEX, 1.5,(255, 255, 255),3,cv2.LINE_AA)
			VisualWhite = 0
			t = 0
			exit()



#//////////////////////////////////////////////////////////////////////////////////////////////////////////
# Show image accoring to CV2
#//////////////////////////////////////////////////////////////////////////////////////////////////////////

	res = cv2.bitwise_and(f_c,f_c,mask=mask)
	cv2.imshow('RUBIK SOLVER', frame)
	cv2.imshow('Calibration',res)
	if cv2.waitKey(1) & 0xFF == ord('q'): 
		break

vid.release()
cv2.destroyAllWindows()