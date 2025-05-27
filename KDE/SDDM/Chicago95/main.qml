/***************************************************************************
* Chicago95 sddm theme
* 
* Copyright (c) Grassmunk
* 
* TODO: 
* - Add doted lines to selected items
* 
* Based on QTStep SDDM theme by:
* Copyright (c) 2015 Pier Luigi Fiorini <pierluigi.fiorini@gmail.com>
* Copyright (c) 2013 Abdurrahman AVCI <abdurrahmanavci@gmail.com>
*
* Permission is hereby granted, free of charge, to any person
* obtaining a copy of this software and associated documentation
* files (the "Software"), to deal in the Software without restriction,
* including without limitation the rights to use, copy, modify, merge,
* publish, distribute, sublicense, and/or sell copies of the Software,
* and to permit persons to whom the Software is furnished to do so,
* subject to the following conditions:
*
* The above copyright notice and this permission notice shall be included
* in all copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
* OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
* THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
* OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
* ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
* OR OTHER DEALINGS IN THE SOFTWARE.
*
***************************************************************************/

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls 2.15 as QQC2
// import QtQuick.Controls.Basic
import QtQuick.Layouts 1.15
import SddmComponents 2.0

Rectangle {
    id: container
    width: 1024
    height: 768
    
    color: "#55aaaa"
	
    // Use this to control all font sizes (also affects icons and overall size of the greeter)
	property double scalingFactor: 1

    LayoutMirroring.enabled: Qt.locale().textDirection == Qt.RightToLeft
    LayoutMirroring.childrenInherit: true

    // property int sessionIndex: session.index

    TextConstants { id: textConstants }

    Connections {
        target: sddm
        function onLoginSucceeded() {
        }

        function onLoginFailed() {
			message.text = textConstants.loginFailed;
			passwd_entry.text = "";
        }
    }

    Background {
        anchors.fill: parent
        source: config.background
        fillMode: Image.PreserveAspectCrop
        onStatusChanged: {
            if (status == Image.Error && source != config.defaultBackground) {
                source = config.defaultBackground
            }
        }

        MouseArea {
            anchors.fill: parent
            onClicked: {
                // listView.focus = true;
            }
        }
    }

    Rectangle {
    // Main Rectangle fills the whole screen
		anchors.fill: parent
		color: "transparent"
		// visible: primaryScreen
            Rectangle {
                // Here we make another rectangle which is the logon 'window'
                height: 144
                width: 461
                id: "greeter"
                anchors.centerIn: parent
			
			BorderImage {
				anchors.fill: parent
				border.left: 3
				border.right: 4
				border.top: 3
				border.bottom: 4
				smooth: false
				source: "greeter.svg"
			}
			GridLayout {
                // This is the top blue bar with a working Exit button
                columns: 1
                rows: 2
                anchors.fill: parent
                Rectangle {
                    Layout.row: 0
					id: header
					color: "#0000aa"
					Layout.leftMargin: 3
					Layout.rightMargin: 5
					Layout.topMargin: 3
					Layout.bottomMargin: 3
					Layout.alignment: Qt.AlignTop
					Layout.fillWidth: true
					Layout.preferredHeight: 18
					GridLayout {
                        id: titleBar
                        columns: 3
                        anchors.fill: parent
                        columnSpacing: 0
                        Layout.alignment: Qt.AlignTop
                        Text { 
                            Layout.fillWidth: true
                            Layout.column: 0
                            Layout.topMargin: -1
                            Layout.leftMargin: 2
                            id: welcome_text
                            color: "#ffffff"
                            font.bold: true
                            text: "Welcome to Windows"
                            font.family: "Helvetica"
                            font.pixelSize: 11
                        }
                        Image {
                            Layout.column: 1
                            Layout.preferredWidth: 16
                            Layout.rightMargin: 2
                            Layout.alignment: Qt.AlignRight
                            fillMode: Image.PreserveAspectFit
                            source: "help.svg"
                        }
                        
                        ToolButton {
                            Layout.rightMargin: 2
                            id: shutdown_button
                            enabled: sddm.canPowerOff
                            Layout.preferredWidth: 16
                            Layout.minimumWidth: 16
                            Layout.preferredHeight: 14


                            background: BorderImage {
                                border.left: 1
                                border.right: 2
                                border.top: 1
                                border.bottom: 2
                                smooth: false
                                source: shutdown_button.pressed ? "close-pressed.svg"
                                        : shutdown_button.hovered ? "close-hover.svg"
                                        : shutdown_button.focus ? "close-hover.svg"
                                        : "close.svg"
                            }

                            onClicked: sddm.powerOff()
                        }
                      
                    }
					
				}
                GridLayout {
                    // anchors.fill: parent
                    columns: 3
                    rows: 1
                    Layout.row: 1
					Layout.alignment: Qt.AlignTop
                    Image {
						Layout.alignment: Qt.AlignTop
                        Layout.topMargin: -2
                        Layout.leftMargin: 24
                        Layout.column: 0
                        Layout.row: 0
                        source: "start.png"
                    
                    }
                    ColumnLayout {
                        Layout.column: 1
                        Layout.row: 0
                        Layout.alignment: Qt.AlignTop
                        Text { 
                            Layout.row: 0
                            Layout.column: 0
                            Layout.leftMargin: 16
                            Layout.topMargin: -2
                            id: message_text
                            color: "#000000"
                            text: "Type a user name and password to log on to Windows."
                            font.family: "Helvetica"
                            font.pixelSize: 11
                        }
                        GridLayout {
                            Layout.topMargin: 0
                            Layout.leftMargin: 16
                            Layout.rightMargin: 57
                            Layout.alignment: Qt.AlignTop
                            columns: 2
                            
                            Label {
                                Layout.alignment: Qt.AlignLeft
								Layout.topMargin: 12
                                Layout.preferredWidth: 67
                                Layout.minimumWidth: 67
                                text: "User name:"
                                font.family: "Helvetica"
                                font.pixelSize: 11
                                color: "#000000"
                            }
                            
                            TextField {
                                id: username
                                text: userModel.lastUser
                                Layout.alignment: Qt.AlignLeft
                                Layout.fillWidth: true
                                Layout.topMargin: 17
                                Layout.preferredHeight: font.pixelSize + 12
                                font.family: "Helvetica"
                                font.pixelSize: 11
                                color: "#000000"

                                background: BorderImage {
                                    border.left: 2
                                    border.right: 2
                                    border.top: 2
                                    border.bottom: 2
                                    smooth: false
                                    source: username.focus ? "entry-focused.svg"
                                                        : "entry.svg"
                                }
                            }

                            Label {
                                Layout.alignment: Qt.AlignLeft
                                Layout.topMargin: -1
                                text: "Password:"
                                font.family: "Helvetica"
                                font.pixelSize: 11
                                color: "#000000"
                            }
                            
                            TextField {
                                id: password
                                echoMode: TextInput.Password
                                Layout.fillWidth: true
                                Layout.topMargin: 2
                                Layout.preferredHeight: font.pixelSize + 13
                                font.family: "Helvetica"
                                font.pixelSize: 11
                                color: "#000000"
                                background: BorderImage {
                                    border.left: 2
                                    border.right: 2
                                    border.top: 2
                                    border.bottom: 2
                                    smooth: false
                                    source: password.focus ? "entry-focused.svg"
                                                        : "entry.svg"
                                }
                            }
                                Keys.onPressed: event => {
                                    if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                                        sddm.login(username.text, password.text, sessionbutton.currentIndex);
                                        event.accepted = true;
                                    }
                                }
                            
                        }
                        
                    }
                    ColumnLayout {
                        Layout.alignment: Qt.AlignTop
                        Layout.topMargin: -2
                        Layout.leftMargin: 10
                        Layout.rightMargin: 15
                        Layout.column: 2
                        Layout.row: 0
                        ToolButton {
                            id: ok_button
                            enabled: username.text !== "" && password.text !== "" ? true : false
                            Layout.preferredWidth: 74
                            Layout.minimumWidth: 74
                            Layout.preferredHeight: 23
                            background: BorderImage {
                                border.left: 2
                                border.right: 2
                                border.top: 2
                                border.bottom: 2
                                smooth: false
                                source: ok_button.pressed ? "button-pressed.svg"
                                    : ok_button.hovered ? "button-hover.svg"
                                    : ok_button.focus ? "button-hover.svg"
                                    : "button.svg"
                            }
                            ColumnLayout {
                                id: ok_button_content
                                anchors.centerIn: parent
                                spacing: 4
                                Text {
                                color: "#000000"
                                text: "OK"
                                font.family: "Helvetica"
                                font.pixelSize: 11
                                opacity: ok_button.enabled ? 1 : 0.5
                                }
                            }
                         Keys.onReturnPressed: clicked()
                         onClicked: username.text !== "" && password.text !== "" ? sddm.login(username.text, password.text, sessionbutton.currentIndex) : sddm.loginFailed()
       
                        
                        }
                        ToolButton {
                            id: shutdown_button_2
                            enabled: sddm.canPowerOff
                            Layout.preferredWidth: 74
                            Layout.minimumWidth: 74
                            Layout.preferredHeight: 23
                            Layout.topMargin: 2


                            background: BorderImage {
                                border.left: 2
                                border.right: 2
                                border.top: 2
                                border.bottom: 2
                                smooth: false
                                source: shutdown_button_2.pressed ? "button-pressed.svg"
                                    : shutdown_button_2.hovered ? "button-hover.svg"
                                    : shutdown_button_2.focus ? "button-hover.svg"
                                    : "button.svg"
                            }
                            ColumnLayout {
                                id: shutdown_button_content_2
                                anchors.centerIn: parent
                                spacing: 4
                                Text {
                                    color: "#000000"
                                    text: "Cancel"
                                    font.family: "Helvetica"
                                    opacity: shutdown_button.enabled ? 1 : 0.5
                                    font.pixelSize: 11
                                }
                            }
                            onClicked: sddm.powerOff()
                        }
                        ToolButton {
						id: sessionbutton
                        Layout.topMargin: 9
                        Layout.preferredWidth: 74
                        Layout.minimumWidth: 74
                        Layout.preferredHeight: 23
						property int currentIndex: -1
						onClicked: {
                            sessionmenu.open()
                            }

                        RowLayout {
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 0
                            Label {
                                Layout.fillWidth: true
                                Layout.leftMargin: 7

                                text: instantiator.objectAt(sessionbutton.currentIndex).text || ""
                                Layout.preferredWidth:50
                                elide: Label.ElideRight

                                font.family: "Helvetica"
                                font.pixelSize: 11
                                color: "#000000"
                            }
                            Image {
                                fillMode: Image.PreserveAspectFit
                                source: "combo-indicator.svg"
                                Layout.rightMargin: 1
                            }
                        }
                        background: BorderImage {
                            border.left: 2
                            border.right: 2
                            border.top: 2
                            border.bottom: 2
                            smooth: false
                            source: sessionbutton.pressed ? "button-pressed.svg"
                                    : sessionbutton.hovered ? "button-hover.svg"
                                    : sessionbutton.focus ? "button-hover.svg"
                                    : "button.svg"
                        }

						
						Component.onCompleted: {
							currentIndex = sessionModel.lastIndex
							if (username.text === "")
								username.focus = true
							else
								password.focus = true
						}
						
						QQC2.Menu {
							id: sessionmenu
                            implicitWidth: 120 // Adjust menu width here
                            // x: sessionbutton.width
                            y: sessionbutton.height // + 5
							Instantiator {
								id: instantiator
								model: sessionModel
								onObjectAdded: function(index, object) {sessionmenu.insertItem(index, object)}
								onObjectRemoved: function(index, object) {sessionmenu.removeItem(object)}
								delegate: QQC2.MenuItem {
                                    id: control
									text: model.name
                                    background: Rectangle {
                                        // anchors.fill: parent
                                        color: control.highlighted ?  "#000080" : "transparent"
                                        }
                                    // color: "#000000"
                                    font.family: "Helvetica"
                                    font.pixelSize: 11
									onTriggered: {
										sessionbutton.currentIndex = model.index
									}
								}
							}

                            background: BorderImage {
                                    border.left: 2
                                    border.right: 2
                                    border.top: 2
                                    border.bottom: 2
                                    smooth: false
                                    source: "button.svg"
                            }

						}
					    }
                        
                    } 
                }
                
            }
			
            }
        
        
        
    }
}
