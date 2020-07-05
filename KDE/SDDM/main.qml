/***************************************************************************
* Chicago95 sddm theme
*
* Copyright (c) Grassmunk
*
* TODO:
* - Make the 'X' have a 'pressed' version
* - Add doted lines to selected items
*
* Based on QTStep SDDM theme by:
* Copyright (c) 2015 Pier Luigi Fiorini <pierluigi.fiorini@gmail.com>
* Copyright (c) 2013 Abdurrahman AVCI <abdurrahmanavci@gmail.com
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

import QtQuick 2.2
import QtQuick.Controls 1.4
import QtQuick.Controls 1.4 as QQC
import QtQuick.Controls.Styles 1.4
import QtQuick.Layouts 1.3
import SddmComponents 2.0

Rectangle {
    id: container
    width: 1024
    height: 768

    color: "#008080"

// 	Use this to control all font sizes (also affects icons and overall size of the greeter)
	property double scalingFactor: 1

    LayoutMirroring.enabled: Qt.locale().textDirection == Qt.RightToLeft
    LayoutMirroring.childrenInherit: true

    property int sessionIndex: session.index

    TextConstants { id: textConstants }

    Connections {
        target: sddm
        onLoginSucceeded: {
        }

        onLoginFailed: {
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
                listView.focus = true;
            }
        }
    }

	Rectangle {
	// Main Rectangle fills the whole screen
	anchors.fill: parent
	color: "transparent"
	//visible: primaryScreen
	Rectangle {
		// Here we make another rectangle which is the logon 'window'
		height: 175
		width: 640
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
					color: "#000080"
					Layout.leftMargin: 3
					Layout.rightMargin: 3
					Layout.topMargin: 3
					Layout.bottomMargin: 3
					Layout.alignment: Qt.AlignTop
					Layout.fillWidth: true
					Layout.preferredHeight: 19
					GridLayout {
                        id: titleBar
                        columns: 3
                        anchors.fill: parent
                        columnSpacing: 0
                        Layout.alignment: Qt.AlignVCenter
                        Text {
                            Layout.fillWidth: true
                            Layout.column: 0
                            Layout.leftMargin: 5
                            id: welcome_text
                            color: "#ffffff"
                            font.bold: true
                            text: "Enter Network Password"
                            font.family: "Sans"
                            font.pixelSize: 12
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
						style: ButtonStyle {
							background: BorderImage {
								border.left: 1
								border.right: 2
								border.top: 1
								border.bottom: 2
								smooth: false
								source: control.pressed ? "button-pressed.svg"
								      : control.hovered ? "button-hover.svg"
								      : control.focus ? "button-hover.svg"
								      : "button.svg"
							}
						}
						ColumnLayout {
							id: shutdown_button_content
							anchors.centerIn: parent
							spacing: 4
							Image {
								Layout.alignment: Qt.AlignCenter
								sourceSize.width: 16
								sourceSize.height: 14
								source: "close.svg"
							}
						}
						onClicked: sddm.powerOff()
					}

                    }

				}
                GridLayout {
                    anchors.fill: parent
                    columns: 3
                    rows: 1
                    Layout.row: 1
                    Image {
                        Layout.topMargin: 30
                        Layout.leftMargin: 20
                        Layout.column: 0
                        Layout.row: 0
                        source: "start.png"

                    }
                    ColumnLayout {
                        Layout.column: 1
                        Layout.row: 0
                        Text {
                            Layout.row: 0
                            Layout.column: 0
                            Layout.leftMargin: 15
                            Layout.topMargin: 40
                            id: message_text
                            color: "#000000"
                            text: "Enter your network password for Microsoft Networking."
                            font.family: "Sans"
                            font.pixelSize: 12
                        }
                        GridLayout {
                            Layout.topMargin: 15
                            Layout.leftMargin: 15
                            columns: 2

                            Label {
                                Layout.alignment: Qt.AlignRight
                                text: textConstants.userName
                                font.family: "Sans"
                                font.pixelSize: 12
                                color: "#000000"
                            }

                            TextField {
                                id: username
                                text: userModel.lastUser
                                Layout.fillWidth: true
                                Layout.preferredHeight: font.pixelSize + 15
                                font.family: "Sans"
                                font.pixelSize: 12
                                textColor: "#000000"
                                style: TextFieldStyle {
                                    background: BorderImage {
                                        border.left: 2
                                        border.right: 2
                                        border.top: 2
                                        border.bottom: 2
                                        smooth: false
                                        source: control.focus ? "entry-focused.svg"
                                                            : "entry.svg"
                                    }
                                }
                            }
                            Label {
                                Layout.alignment: Qt.AlignRight
                                text: textConstants.password
                                font.family: "Sans"
                                font.pixelSize: 12
                                color: "#000000"
                            }

                            TextField {
                                id: password
                                echoMode: TextInput.Password
                                Layout.fillWidth: true
                                Layout.preferredHeight: font.pixelSize + 15
                                font.family: "Sans"
                                font.pixelSize: 12
                                textColor: "#000000"
                                style: TextFieldStyle {
                                    background: BorderImage {
                                        border.left: 2
                                        border.right: 2
                                        border.top: 2
                                        border.bottom: 2
                                        smooth: false
                                        source: control.focus ? "entry-focused.svg"
                                                            : "entry.svg"
                                    }
                                }
                            }
                                Keys.onPressed: {
                                    if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                                        sddm.login(username.text, password.text, sessionbutton.currentIndex);
                                        event.accepted = true;
                                    }
                                }

                        }

                    }
                    ColumnLayout {
                        Layout.topMargin: 30
                        Layout.leftMargin: 10
                        Layout.rightMargin: 10
                        Layout.column: 2
                        Layout.row: 0
                        ToolButton {
                            id: ok_button
                            enabled: username.text !== "" && password.text !== "" ? true : false
                            Layout.preferredWidth: 80
                            Layout.minimumWidth: 80
                            Layout.preferredHeight: 30
                            style: ButtonStyle {
                                background: BorderImage {
                                    border.left: 2
                                    border.right: 2
                                    border.top: 2
                                    border.bottom: 2
                                    smooth: false
                                    source: control.pressed ? "button-pressed.svg"
                                        : control.hovered ? "button-hover.svg"
                                        : control.focus ? "button-hover.svg"
                                        : "button.svg"
                                }
                            }
                            ColumnLayout {
                                id: ok_button_content
                                anchors.centerIn: parent
                                spacing: 4
                                Text {
                                color: "#000000"
                                text: "OK"
                                font.family: "Sans"
                                font.pixelSize: 12
                                opacity: ok_button.enabled ? 1 : 0.5
                                }
                        }
                         Keys.onReturnPressed: clicked()
                         onClicked: username.text !== "" && password.text !== "" ? sddm.login(username.text, password.text, sessionbutton.currentIndex) : sddm.loginFailed()


                        }
                        ToolButton {
                            id: shutdown_button_2
                            enabled: sddm.canPowerOff
                            Layout.preferredWidth: 80
                            Layout.minimumWidth: 80
                            Layout.preferredHeight: 30
                            style: ButtonStyle {
                                background: BorderImage {
                                    border.left: 2
                                    border.right: 2
                                    border.top: 2
                                    border.bottom: 2
                                    smooth: false
                                    source: control.pressed ? "button-pressed.svg"
                                        : control.hovered ? "button-hover.svg"
                                        : control.focus ? "button-hover.svg"
                                        : "button.svg"
                                }
                            }
                            ColumnLayout {
                                id: shutdown_button_content_2
                                anchors.centerIn: parent
                                spacing: 4
                                Text {
                                    color: "#000000"
                                    text: "Cancel"
                                    font.family: "Sans"
                                    opacity: shutdown_button.enabled ? 1 : 0.5
                                    font.pixelSize: 12
                                }
                            }
                            onClicked: sddm.powerOff()
                        }
                        ToolButton {
						id: sessionbutton
                        Layout.preferredWidth: 80
                        Layout.minimumWidth: 80
                        Layout.preferredHeight: 30
						property int currentIndex: -1

						style: ButtonStyle {
							padding.right: 1
							label: RowLayout {
								Label {
									Layout.fillWidth: true
									text: instantiator.objectAt(sessionbutton.currentIndex).text || ""
									font.family: "Liberation Sans"
									font.pixelSize: 12
									color: "#000000"
								}
								Image {
									fillMode: Image.PreserveAspectFit
									source: "combo-indicator.svg"
								}
							}
							background: BorderImage {
								border.left: 2
								border.right: 2
								border.top: 2
								border.bottom: 2
								smooth: false
								source: control.pressed ? "button-pressed.svg"
								      : control.hovered ? "button-hover.svg"
								      : control.focus ? "button-hover.svg"
								      : "button.svg"
							}
						}

						Component.onCompleted: {
							currentIndex = sessionModel.lastIndex
						}

						menu: QQC.Menu {
							id: sessionmenu
							Instantiator {
								id: instantiator
								model: sessionModel
								onObjectAdded: sessionmenu.insertItem(index, object)
								onObjectRemoved: sessionmenu.removeItem(object)
								delegate: QQC.MenuItem {
									text: model.name
									onTriggered: {
										sessionbutton.currentIndex = model.index
									}
								}
							}
						}
					}

                } }

            }

            }



    }
}
