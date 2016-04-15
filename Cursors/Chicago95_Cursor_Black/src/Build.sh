#!/bin/sh

if test ! -d cursors;
then mkdir cursors
else
rm -rf cursors
mkdir cursors
fi



########### Build cursors

xcursorgen AppStarting.conf             cursors/AppStarting
xcursorgen Arrow.conf			cursors/Arrow
xcursorgen ArrowRight.conf		cursors/ArrowRight
xcursorgen AngleNW.conf			cursors/AngleNW
xcursorgen AngleNE.conf			cursors/AngleNE
xcursorgen AngleNE.conf			cursors/AngleSW
xcursorgen AngleNW.conf			cursors/AngleSE
xcursorgen Copy.conf			cursors/Copy
xcursorgen Cross.conf			cursors/Cross
xcursorgen Crosshair.conf		cursors/Crosshair
xcursorgen Circle.conf			cursors/Circle
xcursorgen DND-ask.conf			cursors/DND-ask
xcursorgen DND-copy.conf		cursors/DND-copy
xcursorgen DND-link.conf		cursors/DND-link
xcursorgen Hand.conf			cursors/Hand

xcursorgen Handgrab.conf		cursors/Handgrab
xcursorgen Handsqueezed.conf		cursors/Handsqueezed

xcursorgen Handwriting.conf		cursors/Handwriting
xcursorgen Help.conf			cursors/Help
xcursorgen IBeam.conf			cursors/IBeam
xcursorgen Link.conf			cursors/Link
xcursorgen Move.conf			cursors/Move
xcursorgen NO.conf			cursors/NO
xcursorgen SizeAll.conf			cursors/SizeAll
xcursorgen AngleNE.conf			cursors/SizeNESW
xcursorgen BaseN.conf			cursors/SizeNS
xcursorgen AngleNW.conf			cursors/SizeNWSE
xcursorgen SizeWE.conf			cursors/SizeWE
xcursorgen UpArrow.conf			cursors/UpArrow
xcursorgen DownArrow.conf		cursors/DownArrow
xcursorgen LeftArrow.conf		cursors/LeftArrow
xcursorgen RightArrow.conf		cursors/RightArrow
xcursorgen BaseN.conf			cursors/BaseN
xcursorgen BaseN.conf			cursors/BaseS
xcursorgen HDoubleArrow.conf		cursors/HDoubleArrow
xcursorgen VDoubleArrow.conf		cursors/VDoubleArrow
xcursorgen Wait.conf			cursors/Wait
xcursorgen X.conf			cursors/X

xcursorgen ZoomIn.conf			cursors/ZoomIn
xcursorgen ZoomOut.conf			cursors/ZoomOut


cd cursors



########### Create copies and symlinks

#---------- AngleNW
cp AngleNW				ul_angle
cp AngleNW				dnd-none
cp AngleNW				dnd-move
rm -f AngleNW

#---------- AngleNE
cp AngleNE				ur_angle
rm -f AngleNE

#---------- AngleSW
cp AngleSW				ll_angle
rm -f AngleSW

#---------- AngleSE
cp AngleSE				lr_angle
rm -f AngleSE

#---------- AppStarting
cp AppStarting				left_ptr_watch
cp -s left_ptr_watch			08e8e1c95fe2fc01f976f1e063a24ccd
cp -s left_ptr_watch			3ecb610c1bf2410f44200f48c40d3599
rm -f AppStarting

#---------- Arrow
cp Arrow				arrow
cp Arrow				draft_large
cp Arrow				draft_small
cp Arrow				left_ptr
cp Arrow				right_ptr
cp Arrow				top_left_arrow
rm -f Arrow

#---------- ArrowRight
cp ArrowRight				right_ptr
rm -f ArrowRight

#---------- BaseN
cp BaseN				base_arrow_up
cp BaseN				based_arrow_up
rm -f BaseN

#---------- BaseS
cp BaseS				base_arrow_down
cp BaseS				based_arrow_down
rm -f BaseS

#---------- Cirlce
cp Circle 				circle
rm -f Circle

#---------- Copy
cp Copy					copy
cp -s copy				1081e37283d90000800003c07f3ef6bf
cp -s copy				6407b0e94181790501fd1e167b474872
cp -s copy				08ffe1cb5fe6fc01f906f1c063814ccf
rm -f Copy

#---------- Cross
cp Cross				cross
cp Cross				cross_reverse
cp Cross				tcross
rm -f Cross

#---------- Crosshair
cp Crosshair				crosshair
rm -f Crosshair

#---------- DND-ask
cp DND-ask				dnd-ask
rm -f DND-ask

#---------- DND-copy
cp DND-copy				dnd-copy
rm -f DND-copy

#---------- DND-link
cp DND-link				dnd-link
rm -f DND-link

#---------- Handpointer
cp Hand					hand
cp Hand					hand1
cp Hand					hand2
cp -s hand2				e29285e634086352946a0e7090d73106
rm -f Hand

#---------- Handgrab
cp Handgrab				HandGrab
cp -s HandGrab				9d800788f1b08800ae810202380a0822
cp -s HandGrab				5aca4d189052212118709018842178c0
rm -f Handgrab

#---------- Handsqueezed
cp Handsqueezed				HandSqueezed
cp -s HandSqueezed			208530c400c041818281048008011002
rm -f Handsqueezed


#---------- Handwriting
cp Handwriting				pencil
rm -f Handwriting

#---------- Help
cp Help					question_arrow
cp -s question_arrow			d9ce0ab605698f320427677b458ad60b
cp -s question_arrow			5c6cd98b3f3ebcb1f9c7f1c204630408
rm -f Help

#---------- IBeam
cp IBeam				xterm
cp IBeam				ibeam
rm -f IBeam

#---------- Link
cp Link					link
cp -s link				3085a0e285430894940527032f8b26df
cp -s link				640fb0e74195791501fd1ed57b41487f
cp -s link				0876e1c15ff2fc01f906f1c363074c0f
rm -f Link

#---------- NO
cp NO 					crossed_circle
cp NO					dnd-none
cp -s crossed_circle			03b6e0fcb3499374a867c041f52298f0
rm -f NO

#---------- Move
cp Move					move	
cp Move					plus			
cp -s move				4498f0e0c1937ffe01fd06f973665830
cp -s move				9081237383d90e509aa00f00170e968f
rm -f Move

#---------- SizeAll
cp SizeAll				fleur
rm -f SizeAll

#---------- SizeNESW
cp SizeNESW				bottom_left_corner
cp SizeNESW				fd_double_arrow
cp SizeNESW				top_right_corner
cp -s fd_double_arrow			fcf1c3c7cd4491d801f1e1c78f100000
rm -f SizeNESW

#---------- SizeNS
cp SizeNS				bottom_side
cp SizeNS				double_arrow
cp SizeNS				top_side
cp -s double_arrow			00008160000006810000408080010102
rm -f SizeNS

#---------- SizeNWSE
cp SizeNWSE				bd_double_arrow
cp SizeNWSE				bottom_right_corner
cp SizeNWSE				top_left_corner
cp -s bd_double_arrow			c7088f0f3e6c8088236ef8e1e3e70000
rm -f SizeNWSE

#---------- SizeWE
cp SizeWE				left_side
cp SizeWE				right_side
cp -s right_side			028006030e0e7ebffc7f7070c0600140
rm -f SizeWE

#---------- UpArrow
cp UpArrow				center_ptr
cp UpArrow				sb_up_arrow
rm -f UpArrow

#---------- DownArrow
cp DownArrow				sb_down_arrow
rm -f DownArrow

#---------- LeftArrow
cp LeftArrow				sb_left_arrow
rm -f LeftArrow

#---------- RightArrow
cp RightArrow				sb_right_arrow
rm -f RightArrow

#---------- HDoubleArrow
cp HDoubleArrow				h_double_arrow
cp HDoubleArrow				sb_h_double_arrow
cp -s sb_h_double_arrow			14fef782d02440884392942c11205230
	
rm -f HdoubleArrow

#---------- VDoubleArrow
cp VDoubleArrow				v_double_arrow
cp VDoubleArrow				sb_v_double_arrow
cp -s sb_v_double_arrow			2870a09082c103050810ffdffffe0204

rm -f VdoubleArrow

#---------- Wait
cp Wait					watch
rm -f Wait

#---------- X
cp X 					X_cursor
cp X                                    X-cursor
rm -f X

#---------- ZoomIn
cp ZoomIn				zoomIn
cp -s zoomIn 				f41c0e382c94c0958e07017e42b00462
rm -f ZoomIn
#---------- ZoomOut
cp ZoomOut				zoomOut
cp -s zoomOut 				f41c0e382c97c0938e07017e42800402
rm -f ZoomOut



########### Done!
echo "Done!"
