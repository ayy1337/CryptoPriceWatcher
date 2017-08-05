#!/usr/bin/python3

'''     Crypto Price Watcher
        Version: 1.0.01
        Author: ayy1337
        Licence: GNU GPL v3.0
'''


from PyQt5 import QtGui, QtCore, QtWidgets
Qt = QtCore.Qt
import sys, os, sys, shelve, time, threading, random, operator, copy, datetime, os, collections, grabtrex, grabpolo
from operator import attrgetter, itemgetter
import trexapi, poloapi
from random import randint

notificationsavailable = 1
try:
    from win10toast import ToastNotifier
    toaster = ToastNotifier()
except:
    try:
        from gi.repository import Notify
    except:
        notificationsavailable = 0
soundavailable = 1
try:
    from playsound import playsound
except:
    soundavailable = 0

class alertmodelitem():
    def __init__(self, data, idnum, alert, background = None):
        self.data = data
        self.id = idnum
        self.alert = alert
        self.background = background
        self.disabled = 0


class myTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None, gainloss=0, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.datatable = None
        self.headers = []
        self.gainloss = gainloss
        self.selectedticker = ''
        self.defaultsort = 1

    def update(self, dataIn):
        self.datatable = dataIn
    def rowCount(self, parent=QtCore.QModelIndex()):
        try:
            return len(self.datatable)
        except:
            return 0
    def columnCount(self, parent=QtCore.QModelIndex()):
        try:
            return len(self.datatable[0])
        except:
            return 0
    def data(self, index, role = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            try:
                i = index.row()
                j = index.column()
                try:
                    return self.datatable[i][j].data
                except:
                    pass
                return self.datatable[i][j]
            except:
                return Qt.QVariant()
        elif role == Qt.TextAlignmentRole:
            return (QtCore.Qt.AlignCenter)
        elif role == Qt.BackgroundRole:
            try:
                i = index.row()
                j = index.column()
                item = self.datatable[i][j]
                try:
                    return item.background
                except:
                    pass
                try:
                    if self.selectedticker == self.datatable[index.row()][0]:
                        if item[-1] == "%":
                            value = float(item[:-1])
                            if (value < -4) & (j in [1,3]):
                                brush = QtGui.QBrush(QtGui.QColor(245,219,255))
                                brush.setStyle(QtCore.Qt.SolidPattern)
                                return brush
                            elif (value > 4) & (j in [1,3]):
                                brush = QtGui.QBrush(QtGui.QColor(171,255,235))
                                brush.setStyle(QtCore.Qt.SolidPattern)
                                return brush

                        brush = QtGui.QBrush(QtGui.QColor(170,219,255))
                        brush.setStyle(QtCore.Qt.SolidPattern)
                        return brush
                    if item[-1] == "%":
                        value = float(item[:-1])
                        if j in [1,3]:
                            if (value <= -4):
                                brush = QtGui.QBrush(QtGui.QColor(255, 149, 149))
                            elif (value >= 4):
                                brush = QtGui.QBrush(QtGui.QColor(172, 255, 188))
                            if j == 3:

                                if (value > 0) & (value < 4):
                                    brush = QtGui.QBrush(QtGui.QColor(208,255,218))
                                elif (value <0) & (value > -4):
                                    brush = QtGui.QBrush(QtGui.QColor(255,208,211))
                    brush.setStyle(QtCore.Qt.SolidPattern)
                    return brush
                except:
                    pass
            except:
                return QtCore.QVariant()
            return QtCore.QVariant()
            

        return QtCore.QVariant()

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled
    def setheaders(self, headers):
        self.headers = headers

    def headerData(self, section, orientation, role= QtCore.Qt.DisplayRole):
        if (role != QtCore.Qt.DisplayRole):
            return QtCore.QVariant()
        if orientation != QtCore.Qt.Horizontal:
            return QtCore.QVariant()
        else:
            if section < len(self.headers):
                return self.headers[section]
            else:
                return QtCore.QVariant()
    def setData(self, row, value, role = QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            if row < len(self.datatable):
                self.datatable[row] = value
                indextl = self.index(row, 0) #top left
                indexbr = self.index(row, self.columnCount()-1) #bottom right
                self.dataChanged.emit(indextl, indexbr, [])#.emit(index,index, [])
                return True
        return False
    def index(self, row, column, parent=QtCore.QModelIndex()):
        try:
            data = self.datatable[row][column]
            return self.createIndex(row, column, data)
        except:
            return QtCore.QModelIndex()

    def insertRows(self, row, count, parent=QtCore.QModelIndex()):
        assert 0 <= row <= self.rowCount()
        assert count > 0

        self.beginInsertRows(parent, row, row + count - 1)
        new_row = [None] * self.columnCount()
        for row in range(row, row+count):
            self.datatable.insert(row,list(new_row))
        self.endInsertRows()

    def appendRow(self, data, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, self.rowCount(), self.rowCount())
        self.datatable.append(data)
        self.endInsertRows()

    def removeRows(self, row, count, parent = QtCore.QModelIndex()):
        assert 0 <= row <= self.rowCount()
        assert count > 0
        self.beginRemoveRows(parent, row, row+count-1)
        for row in range(row, row+count):
            del self.datatable[-1]
        self.endRemoveRows()
    
    def removeRow(self, row, parent=QtCore.QModelIndex()):
        try:
            self.beginRemoveRows(parent, row, row)
            del self.datatable[row]
            self.endRemoveRows()
        except:
            pass

    def sort(self, Ncol, order = 0):
        if self.defaultsort == 1:
            return
        self.layoutAboutToBeChanged.emit()
        if Ncol in (1, 3, 4):
            try:
                self.datatable = sorted(self.datatable, key = lambda item: float(item[Ncol][:-1]), reverse=order)
            except:
                pass
        elif Ncol == 2:
            try:
                self.datatable = sorted(self.datatable, key = lambda item: float(item[Ncol]), reverse=order)
            except:
                pass
        else:
            try:
                self.datatable = sorted(self.datatable, key = lambda item: (item[Ncol]), reverse=order)
            except:
                pass
        self.layoutChanged.emit()
    def rowchanged(self, rowindex):
        indextl = self.index(rowindex, 0) #top left
        indexbr = self.index(rowindex, self.columnCount()-1) #bottom right
        self.dataChanged.emit(indextl, indexbr, [])
    def firstrowempty(self):
        return self.datatable[0][0] == " "
    def cellchanged(self, row, col):
        index = self.index(row, col)
        self.dataChanged.emit(index, index, [])


######### Threads ##########

class polothread (threading.Thread):
    def __init__(self, threadID, name, app):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.app = app
        self.kill = 0
        self.paused = True  # start out paused
        self.state = threading.Condition()

    def run(self):
        self.resume()
        oldtime = int(time.time())
        while self.kill == 0:
            with self.state:
                if self.paused:
                    self.state.wait() # block until notified

            try:
                time1 = int(time.time())
                if (time1 - oldtime) > 2:
                    oldtime = time1
                    self.app.poloticks = self.app.poloupdater.update()
                time.sleep(.7)
            except:
                pass
        return
    def resume(self):
        with self.state:
            self.paused = False
            self.state.notify()  # unblock self if waiting

    def pause(self):
        with self.state:
            self.paused = True  # make self block and wait

class trexthread (threading.Thread):
    def __init__(self, threadID, name, app):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.app = app
        self.kill = 0
        self.paused = True  # start out paused
        self.state = threading.Condition()
    def run(self):
        self.resume()
        oldtime = int(time.time())
        while self.kill == 0:
            with self.state:
                if self.paused:
                    self.state.wait() # block until notified
            try:
                time1 = int(time.time())
                if (time1 - oldtime) > 2:
                    oldtime = time1
                    self.app.trexticks = self.app.trexupdater.update()
                time.sleep(.7)
            except:
                pass
        return
    def resume(self):
        with self.state:
            self.paused = False
            self.state.notify()  # unblock self if waiting

    def pause(self):
        with self.state:
            self.paused = True  # make self block and wait

######### new alert dialog  ##########

class Ui_addAlertDialog(object):
    def setupUi(self, addAlertDialog):
        addAlertDialog.setObjectName("addAlertDialog")
        addAlertDialog.resize(393, 272)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(addAlertDialog.sizePolicy().hasHeightForWidth())
        addAlertDialog.setSizePolicy(sizePolicy)
        self.buttonBox = QtWidgets.QDialogButtonBox(addAlertDialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.widget = QtWidgets.QWidget(addAlertDialog)
        self.widget.setGeometry(QtCore.QRect(10, 10, 371, 221))
        self.widget.setObjectName("widget")
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.cond2CB = QtWidgets.QComboBox(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cond2CB.sizePolicy().hasHeightForWidth())
        self.cond2CB.setSizePolicy(sizePolicy)
        self.cond2CB.setObjectName("cond2CB")
        self.gridLayout.addWidget(self.cond2CB, 2, 2, 1, 1)
        self.prclabel = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.prclabel.setFont(font)
        self.prclabel.setObjectName("prclabel")
        self.gridLayout.addWidget(self.prclabel, 3, 0, 1, 1)
        self.dnCB = QtWidgets.QCheckBox(self.widget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.dnCB.setFont(font)
        self.dnCB.setChecked(True)
        self.dnCB.setObjectName("dnCB")
        self.gridLayout.addWidget(self.dnCB, 4, 0, 1, 3)
        self.coinLE = QtWidgets.QLineEdit(self.widget)
        self.coinLE.setObjectName("coinLE")
        self.gridLayout.addWidget(self.coinLE, 0, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.cond1CB = QtWidgets.QComboBox(self.widget)
        self.cond1CB.setObjectName("cond1CB")
        self.gridLayout.addWidget(self.cond1CB, 2, 1, 1, 1)
        self.prcLE = QtWidgets.QLineEdit(self.widget)
        self.prcLE.setObjectName("prcLE")
        self.gridLayout.addWidget(self.prcLE, 3, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.exCB = QtWidgets.QComboBox(self.widget)
        self.exCB.setObjectName("exCB")
        self.gridLayout.addWidget(self.exCB, 1, 1, 1, 1)

        self.retranslateUi(addAlertDialog)
        self.buttonBox.accepted.connect(addAlertDialog.accept)
        self.buttonBox.rejected.connect(addAlertDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(addAlertDialog)
        addAlertDialog.setTabOrder(self.coinLE, self.exCB)
        addAlertDialog.setTabOrder(self.exCB, self.cond1CB)
        addAlertDialog.setTabOrder(self.cond1CB, self.cond2CB)
        addAlertDialog.setTabOrder(self.cond2CB, self.prcLE)
        addAlertDialog.setTabOrder(self.prcLE, self.dnCB)
        addAlertDialog.setTabOrder(self.dnCB, self.buttonBox)

    def retranslateUi(self, addAlertDialog):
        _translate = QtCore.QCoreApplication.translate
        addAlertDialog.setWindowTitle(_translate("addAlertDialog", "Add Alert"))
        self.label_2.setText(_translate("addAlertDialog", "Condition:"))
        self.prclabel.setText(_translate("addAlertDialog", "Price:"))
        self.dnCB.setText(_translate("addAlertDialog", "Desktop Notification"))
        self.label.setText(_translate("addAlertDialog", "Coin:"))
        self.label_3.setText(_translate("addAlertDialog", "Exchange:"))

class addAlertDialog(QtWidgets.QDialog):
    def __init__(self, parent, currexchange):
        super(addAlertDialog,self).__init__()
        self.ui = Ui_addAlertDialog()
        self.ui.setupUi(self)
        self.main = parent
        self.coinLE = self.ui.coinLE
        self.exCB = self.ui.exCB
        self.cond1CB = self.ui.cond1CB
        self.cond2CB = self.ui.cond2CB
        self.prcLE = self.ui.prcLE
        self.prclabel = self.ui.prclabel
        self.dnCB = self.ui.dnCB

        self.exCB.addItem("Poloniex")
        self.exCB.addItem("Bittrex")
        if currexchange == 1:
            self.exCB.setCurrentIndex(1)
        self.cond1CB.addItem("Price")
        #self.cond1CB.addItem("Change")
        self.cond2CB.addItem("Over")
        self.cond2CB.addItem("Under")

        #self.cond1CB.currentIndexChanged.connect(self.cond1Changed)
        self.coinLE.editingFinished.connect(self.coinlostfocus)
        self.exCB.currentIndexChanged.connect(self.exchangechanged)

        self.coinLE.setFocus()

    def cond1Changed(self, index):
        if index == 0:
            self.cond2CB.setItemText(0, "Over")
            self.cond2CB.setItemText(1, "Under")
            txt = self.coinLE.text()
            self.updateprice(txt, self.exCB.currentIndex())
        elif index == 1:
            self.cond2CB.setItemText(0, "5m")
            self.cond2CB.setItemText(1, "30m")
            self.prcLE.setText("")

    def coinlostfocus(self):
        coin = self.coinLE.text()
        # try:
        if self.cond1CB.currentIndex() == 0:
            self.updateprice(coin, self.exCB.currentIndex())
        # except:
        #     pass
    def exchangechanged(self, index):
        coin = self.coinLE.text()
        if len(coin) > 0:
            if self.cond1CB.currentIndex() == 0:
                self.updateprice(coin, index)

    def updateprice(self, coin, exchange):
        try:
            price = self.main.getprice(coin, exchange)
            self.prcLE.setText("{:.8f}".format(price))
        except:
            pass


##################################################
###########   Main App GUI class   ###############
##################################################
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1137, 866)
        MainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.widget_3 = QtWidgets.QWidget(self.centralwidget)
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.widget_3)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.widget_4 = QtWidgets.QWidget(self.widget_3)
        self.widget_4.setObjectName("widget_4")
        self.gridLayout = QtWidgets.QGridLayout(self.widget_4)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 4)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.widget_4)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAutoFillBackground(False)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(self.widget_4)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.horizontalLayout_2.setContentsMargins(-1, -1, -1, 5)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.gainView = QtWidgets.QTableView(self.widget_4)
        self.gainView.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(4)
        sizePolicy.setHeightForWidth(self.gainView.sizePolicy().hasHeightForWidth())
        self.gainView.setSizePolicy(sizePolicy)
        self.gainView.setMinimumSize(QtCore.QSize(350, 0))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.gainView.setFont(font)
        self.gainView.setAutoFillBackground(True)
        self.gainView.setAlternatingRowColors(False)
        self.gainView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.gainView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.gainView.setSortingEnabled(True)
        self.gainView.setObjectName("gainView")
        self.gainView.horizontalHeader().setVisible(True)
        self.gainView.horizontalHeader().setDefaultSectionSize(15)
        self.gainView.horizontalHeader().setMinimumSectionSize(10)
        self.gainView.horizontalHeader().setStretchLastSection(True)
        self.gainView.verticalHeader().setVisible(False)
        self.gainView.verticalHeader().setDefaultSectionSize(15)
        self.gainView.verticalHeader().setHighlightSections(False)
        self.gainView.verticalHeader().setMinimumSectionSize(15)
        self.gainView.verticalHeader().setSortIndicatorShown(False)
        self.horizontalLayout_2.addWidget(self.gainView)
        self.lossView = QtWidgets.QTableView(self.widget_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(4)
        sizePolicy.setHeightForWidth(self.lossView.sizePolicy().hasHeightForWidth())
        self.lossView.setSizePolicy(sizePolicy)
        self.lossView.setMinimumSize(QtCore.QSize(350, 0))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.lossView.setFont(font)
        self.lossView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.lossView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.lossView.setTextElideMode(QtCore.Qt.ElideLeft)
        self.lossView.setSortingEnabled(True)
        self.lossView.setObjectName("lossView")
        self.lossView.horizontalHeader().setVisible(True)
        self.lossView.horizontalHeader().setCascadingSectionResizes(False)
        self.lossView.horizontalHeader().setDefaultSectionSize(15)
        self.lossView.horizontalHeader().setMinimumSectionSize(10)
        self.lossView.horizontalHeader().setStretchLastSection(True)
        self.lossView.verticalHeader().setVisible(False)
        self.lossView.verticalHeader().setDefaultSectionSize(15)
        self.lossView.verticalHeader().setMinimumSectionSize(15)
        self.lossView.verticalHeader().setSortIndicatorShown(True)
        self.horizontalLayout_2.addWidget(self.lossView)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.exchangelabel = QtWidgets.QLabel(self.widget_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.exchangelabel.sizePolicy().hasHeightForWidth())
        self.exchangelabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.exchangelabel.setFont(font)
        self.exchangelabel.setIndent(50)
        self.exchangelabel.setObjectName("exchangelabel")
        self.horizontalLayout_3.addWidget(self.exchangelabel)
        self.mktavglabel = QtWidgets.QLabel(self.widget_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mktavglabel.sizePolicy().hasHeightForWidth())
        self.mktavglabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.mktavglabel.setFont(font)
        self.mktavglabel.setAlignment(QtCore.Qt.AlignCenter)
        self.mktavglabel.setObjectName("mktavglabel")
        self.horizontalLayout_3.addWidget(self.mktavglabel)
        self.sortButton = QtWidgets.QPushButton(self.widget_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sortButton.sizePolicy().hasHeightForWidth())
        self.sortButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.sortButton.setFont(font)
        self.sortButton.setObjectName("sortButton")
        self.horizontalLayout_3.addWidget(self.sortButton)
        self.sidepaneButton = QtWidgets.QPushButton(self.widget_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sidepaneButton.sizePolicy().hasHeightForWidth())
        self.sidepaneButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.sidepaneButton.setFont(font)
        self.sidepaneButton.setCheckable(True)
        self.sidepaneButton.setObjectName("sidepaneButton")
        self.horizontalLayout_3.addWidget(self.sidepaneButton)
        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(1, 1)
        self.horizontalLayout_3.setStretch(2, 1)
        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)
        self.btcpricelabel = QtWidgets.QLabel(self.widget_4)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.btcpricelabel.setFont(font)
        self.btcpricelabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.btcpricelabel.setObjectName("btcpricelabel")
        self.gridLayout.addWidget(self.btcpricelabel, 2, 0, 1, 1)
        self.horizontalLayout_5.addWidget(self.widget_4)
        self.widget_2 = QtWidgets.QWidget(self.widget_3)
        self.widget_2.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_2.sizePolicy().hasHeightForWidth())
        self.widget_2.setSizePolicy(sizePolicy)
        self.widget_2.setMinimumSize(QtCore.QSize(380, 0))
        self.widget_2.setObjectName("widget_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.widget_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.sidepaneWidget = QtWidgets.QTabWidget(self.widget_2)
        self.sidepaneWidget.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sidepaneWidget.sizePolicy().hasHeightForWidth())
        self.sidepaneWidget.setSizePolicy(sizePolicy)
        self.sidepaneWidget.setMinimumSize(QtCore.QSize(370, 0))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.sidepaneWidget.setFont(font)
        self.sidepaneWidget.setObjectName("sidepaneWidget")
        self.favouritesTab = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.favouritesTab.sizePolicy().hasHeightForWidth())
        self.favouritesTab.setSizePolicy(sizePolicy)
        self.favouritesTab.setObjectName("favouritesTab")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.favouritesTab)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.widget = QtWidgets.QWidget(self.favouritesTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName("widget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.widget)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.newfavLE = QtWidgets.QLineEdit(self.widget)
        self.newfavLE.setObjectName("newfavLE")
        self.gridLayout_3.addWidget(self.newfavLE, 1, 1, 1, 1)
        self.favexchCombo = QtWidgets.QComboBox(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.favexchCombo.sizePolicy().hasHeightForWidth())
        self.favexchCombo.setSizePolicy(sizePolicy)
        self.favexchCombo.setMinimumSize(QtCore.QSize(100, 0))
        self.favexchCombo.setObjectName("favexchCombo")
        self.gridLayout_3.addWidget(self.favexchCombo, 1, 0, 1, 1)
        self.favouritesView = QtWidgets.QTableView(self.widget)
        self.favouritesView.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.favouritesView.setFont(font)
        self.favouritesView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.favouritesView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.favouritesView.setSortingEnabled(True)
        self.favouritesView.setObjectName("favouritesView")
        self.favouritesView.horizontalHeader().setDefaultSectionSize(35)
        self.favouritesView.horizontalHeader().setMinimumSectionSize(30)
        self.favouritesView.horizontalHeader().setStretchLastSection(True)
        self.favouritesView.verticalHeader().setVisible(False)
        self.favouritesView.verticalHeader().setDefaultSectionSize(20)
        self.favouritesView.verticalHeader().setMinimumSectionSize(15)
        self.gridLayout_3.addWidget(self.favouritesView, 0, 0, 1, 2)
        self.gridLayout_5.addWidget(self.widget, 0, 0, 1, 1)
        self.sidepaneWidget.addTab(self.favouritesTab, "")
        self.alertsTab = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.alertsTab.sizePolicy().hasHeightForWidth())
        self.alertsTab.setSizePolicy(sizePolicy)
        self.alertsTab.setObjectName("alertsTab")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.alertsTab)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.widget_5 = QtWidgets.QWidget(self.alertsTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_5.sizePolicy().hasHeightForWidth())
        self.widget_5.setSizePolicy(sizePolicy)
        self.widget_5.setObjectName("widget_5")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.widget_5)
        self.gridLayout_4.setObjectName("gridLayout_4")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem, 3, 1, 1, 1)
        self.addAlertBtn = QtWidgets.QPushButton(self.widget_5)
        self.addAlertBtn.setMinimumSize(QtCore.QSize(50, 0))
        self.addAlertBtn.setMaximumSize(QtCore.QSize(50, 16777215))
        self.addAlertBtn.setObjectName("addAlertBtn")
        self.gridLayout_4.addWidget(self.addAlertBtn, 3, 2, 1, 1)
        self.alertsView = QtWidgets.QTableView(self.widget_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.alertsView.sizePolicy().hasHeightForWidth())
        self.alertsView.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.alertsView.setFont(font)
        self.alertsView.setSortingEnabled(True)
        self.alertsView.setObjectName("alertsView")
        self.alertsView.horizontalHeader().setDefaultSectionSize(50)
        self.alertsView.horizontalHeader().setMinimumSectionSize(25)
        self.alertsView.horizontalHeader().setStretchLastSection(True)
        self.alertsView.verticalHeader().setVisible(False)
        self.alertsView.verticalHeader().setDefaultSectionSize(20)
        self.alertsView.verticalHeader().setMinimumSectionSize(15)
        self.gridLayout_4.addWidget(self.alertsView, 0, 0, 1, 3)
        self.alertsLog = QtWidgets.QTextEdit(self.widget_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.alertsLog.sizePolicy().hasHeightForWidth())
        self.alertsLog.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.alertsLog.setFont(font)
        self.alertsLog.setReadOnly(True)
        self.alertsLog.setObjectName("alertsLog")
        self.gridLayout_4.addWidget(self.alertsLog, 2, 0, 1, 3)
        self.label_3 = QtWidgets.QLabel(self.widget_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout_4.addWidget(self.label_3, 1, 0, 1, 3)
        self.gridLayout_6.addWidget(self.widget_5, 0, 0, 1, 1)
        self.sidepaneWidget.addTab(self.alertsTab, "")
        self.gridLayout_2.addWidget(self.sidepaneWidget, 0, 0, 1, 1)
        self.horizontalLayout_5.addWidget(self.widget_2)
        self.horizontalLayout_4.addWidget(self.widget_3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1137, 29))
        self.menubar.setObjectName("menubar")
        self.menuMenu = QtWidgets.QMenu(self.menubar)
        self.menuMenu.setObjectName("menuMenu")
        self.menuExchange = QtWidgets.QMenu(self.menuMenu)
        self.menuExchange.setObjectName("menuExchange")
        MainWindow.setMenuBar(self.menubar)
        self.actionPoloniex = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.actionPoloniex.setFont(font)
        self.actionPoloniex.setObjectName("actionPoloniex")
        self.actionBittrex = QtWidgets.QAction(MainWindow)
        self.actionBittrex.setObjectName("actionBittrex")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.menuExchange.addAction(self.actionPoloniex)
        self.menuExchange.addAction(self.actionBittrex)
        self.menuMenu.addAction(self.menuExchange.menuAction())
        self.menuMenu.addAction(self.actionExit)
        self.menubar.addAction(self.menuMenu.menuAction())

        self.retranslateUi(MainWindow)
        self.sidepaneWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Crypto Price Watcher"))
        self.label.setText(_translate("MainWindow", "Gainers"))
        self.label_2.setText(_translate("MainWindow", "Losers"))
        self.exchangelabel.setText(_translate("MainWindow", "Current Exchange: Poloniex"))
        self.mktavglabel.setText(_translate("MainWindow", "Market avg: 0% / 0% / 0%"))
        self.sortButton.setText(_translate("MainWindow", "Default Sort"))
        self.sidepaneButton.setText(_translate("MainWindow", "<"))
        self.btcpricelabel.setText(_translate("MainWindow", "BTC Price:"))
        self.sidepaneWidget.setTabText(self.sidepaneWidget.indexOf(self.favouritesTab), _translate("MainWindow", "Favourites"))
        self.addAlertBtn.setText(_translate("MainWindow", "+"))
        self.label_3.setText(_translate("MainWindow", "Log:"))
        self.sidepaneWidget.setTabText(self.sidepaneWidget.indexOf(self.alertsTab), _translate("MainWindow", "Alerts"))
        self.menuMenu.setTitle(_translate("MainWindow", "Menu"))
        self.menuExchange.setTitle(_translate("MainWindow", "Exchange"))
        self.actionPoloniex.setText(_translate("MainWindow", "Poloniex"))
        self.actionBittrex.setText(_translate("MainWindow", "Bittrex"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))

##################################################
###############   Main App Class   ###############
##################################################

class App(QtWidgets.QMainWindow):
    def __init__(self, app):
        super(App, self).__init__()
        self.appy = app
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.cw = self.ui.centralwidget
        self.poloaction = self.ui.actionPoloniex
        self.trexaction = self.ui.actionBittrex
        self.unbold = self.trexaction.font()
        self.bold = QtGui.QFont(self.unbold)
        self.bold.setWeight(75)
        self.trexaction.triggered.connect(self.trexactionclicked)
        self.poloaction.triggered.connect(self.poloactionclicked)
        self.ui.actionExit.triggered.connect(self.exithandler)
        self.exchangelabel = self.ui.exchangelabel
        self.ui.sortButton.clicked.connect(self.defaultsortclicked)
        self.mktavglabel = self.ui.mktavglabel
        self.sidepanebutton = self.ui.sidepaneButton
        self.sidepanebutton.toggled.connect(self.sidepanetoggled)
        self.addalertbtn = self.ui.addAlertBtn
        self.addalertbtn.clicked.connect(self.addalertclicked)
        self.sidewidgetholder = self.ui.widget_2
        self.sidepane = self.ui.sidepaneWidget
        self.sidepane.currentChanged.connect(self.tabchanged)
        self.alertslog = self.ui.alertsLog
        self.btcpricelabel = self.ui.btcpricelabel
        w = self.width()
        w2 = self.sidewidgetholder.width()
        self.sidewidgetholder.hide()
        self.resize(750,self.height())
        self.w4 = self.ui.widget_4
        self.w3 = self.ui.widget_3
        cwd = os.getcwd()
        if os.name in ['posix','linux']:
            self.databasepath = cwd + "/db"
            self.soundpath = cwd + "/Res//alertsound.wav"
            self.os = 'linux'
        else:
            self.databasepath = cwd + "\\db"
            self.soundpath = cwd + "\\Res\\alertsound.wav"
            self.os = 'windows'
        try:
            d = shelve.open(self.databasepath)
            try:
                self.favourites = d['favourites']
            except:
                self.favourites = []

            d.close()
        except:
            self.favourites = []
            self.alerts = []
           


        self.initstuff()
        self.setupgainview()
        self.setuplossview()
        self.setupfavouritestab()
        self.setupalertstab()
        #self.setupfavcombo()

    def initstuff(self):
        self.updateRunning = 0
        self.poloticks = self.trexticks = [[],[]]
        self.poloupdater = grabpolo.updater()
        self.trexupdater = grabtrex.updater()
        self.exchanges = [self.poloupdater,self.trexupdater]
        self.currentexchange = 0
        self.polothread = polothread(1, "poloUpdateThread", self)
        self.trexthread = trexthread(2, "trexUpdateThread", self)
        self.polothread.start()
        self.trexthread.start()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.callback)
        self.timer.start(1000)
        self.notifytimer = QtCore.QTimer()
        self.notifytimer.timeout.connect(self.alertsnotify)
        self.notifytimer.start(60000)



    def setupgainview(self):
        self.gainview = self.ui.gainView
        self.gainmodel = myTableModel(self, 1)
        self.gainmodel.setheaders(['Coin', '5m', 'Price', '30m', '24h', 'Vol'])
        self.gainmodel.update([(" ", " ", " ", " ", ' ', " ")])
        self.gainview.setModel(self.gainmodel)
        header = self.gainview.horizontalHeader()
        for i in range(5):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)
        header.setDefaultAlignment(QtCore.Qt.AlignCenter)
        header.sectionClicked.connect(self.gainheaderclicked)
        self.gainview.doubleClicked.connect(self.gainlossclicked)

    def gainheaderclicked(self, index):
        self.gainmodel.defaultsort = 0

    def setuplossview(self):
        self.lossview = self.ui.lossView
        self.lossmodel = myTableModel(self, 1)
        self.lossmodel.setheaders(['Coin', '5m', 'Price', '30m', '24h', 'Vol'])
        self.lossmodel.update([(" ", " ", " ", " ", ' ', " ")])
        self.lossview.setModel(self.lossmodel)
        header = self.lossview.horizontalHeader()
        for i in range(5):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)
        header.setDefaultAlignment(QtCore.Qt.AlignCenter)
        header.sectionClicked.connect(self.lossheaderclicked)
        self.lossview.doubleClicked.connect(self.gainlossclicked)

    def lossheaderclicked(self, index):
        self.lossmodel.defaultsort = 0

    def gainlossclicked(self, index):
        i = index.row()
        coinname = index.model().datatable[i][0]
        if len(coinname) > 1:
            if self.currentexchange == 0:
                ticker = "BTC_" + coinname
            else:
                ticker = "BTC-" + coinname
            self.addfav(ticker)


    def setupfavouritestab(self):
        self.favexchCombo = self.ui.favexchCombo
        self.favexchCombo.addItem("Poloniex")
        self.favexchCombo.addItem("Bittrex")
        nfle = self.newfavLE = self.ui.newfavLE
        nfle.returnPressed.connect(self.addfav)
        self.favView = self.ui.favouritesView
        self.favModel = myTableModel(self,1)
        self.favModel.setheaders(['Coin', '5m', 'Price', '30m', '24h', 'Vol'])
        self.favModel.update([(" ", " ", " ", " ", ' ', " ")])
        self.favView.setModel(self.favModel)
        header = self.favView.horizontalHeader()
        for i in range(5):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)
        header.setDefaultAlignment(QtCore.Qt.AlignCenter)
        header.sectionClicked.connect(self.favheaderclicked)
        self.favView.doubleClicked.connect(self.favViewClicked)

    def favheaderclicked(self, index):
        self.favModel.defaultsort = 0

    def favViewClicked(self, index):
        i = index.row()
        coinname = index.model().datatable[i][0].split('(')
        if len(coinname) > 1:
            if coinname[1][0] == 'p':
                coinname = "BTC_" + coinname[0]
            else:
                coinname = "BTC-" + coinname[0]
            self.favourites.remove(coinname)
            self.savefavs()

    def savefavs(self):
        try:
            d = shelve.open(self.databasepath)
            d['favourites'] = self.favourites
            d.close()
        except:
            pass


    def setupalertstab(self):
        self.alertsView = self.ui.alertsView
        self.alertsModel = myTableModel(self, 0)
        self.alertsModel.setheaders(['Alerts'])
        self.alertsModel.update([' '])
        self.alertsView.setModel(self.alertsModel)
        header = self.alertsView.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setDefaultAlignment(QtCore.Qt.AlignCenter)
        self.alertsView.horizontalHeader().setStyleSheet("font: 10pt bold")
        self.alertsModel.removeRow(0)
        self.alertsView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.alertsView.customContextMenuRequested.connect(self.alertsViewClicked)
        self.alertsView.doubleClicked.connect(self.alertsViewDblClicked)
        self.highlightbrush = QtGui.QBrush(QtGui.QColor(255,203,119))
        self.highlightbrush.setStyle(QtCore.Qt.SolidPattern)
        self.disabledbrush = QtGui.QBrush(QtGui.QColor(170,170,170))
        self.disabledbrush.setStyle(QtCore.Qt.SolidPattern)
        try:
            d = shelve.open(self.databasepath)
            self.alerts = d['alerts']
            d.close()
            for item in self.alerts:
                string = self.alertstring(item)
                modelitem = alertmodelitem(string, item['id'], item)
                self.alertsModel.appendRow([modelitem])
        except:
            self.alerts = []
        self.alertids = []
        self.triggeredsincelastview = []
        self.dnalerts = []
        for item in self.alerts:
            self.alertids.append(item['id'])
    
    def alertsViewClicked(self, point):
        row = self.alertsView.rowAt(point.y())
        mdi = self.alertsModel.datatable[row][0]
        rowid = mdi.id
        if mdi.disabled:
            mdi.disabled = 0
            mdi.background = None
            mdi.alert['disabled'] = 0

        else:
            mdi.disabled = 1
            mdi.background = self.disabledbrush
            mdi.alert['disabled'] = 1
        self.alertsModel.cellchanged(row,0)

    def alertsViewDblClicked(self, index):
        if QtWidgets.QApplication.mouseButtons() & QtCore.Qt.RightButton:
            print('rclick received')
            return
        try:
            i = index.row()
            alertid = index.model().datatable[i][0].id
            for item in self.alerts:
                if item['id'] == alertid:
                    self.alerts.remove(item)
                    self.dnalerts.remove(item)
                    self.triggeredsincelastview.remove(item)
            self.alertids.remove(alertid)
            self.savealerts()
            self.alertsModel.removeRow(i)            
        except:
            pass
        

    def savealerts(self):
        try:
            d = shelve.open(self.databasepath)
            d['alerts'] = self.alerts
            d.close()
        except:
            pass


    def addalertclicked(self):
        try:
            exchnge = self.currentexchange
            dg = addAlertDialog(self, exchnge)
            dg.coinLE.setFocus()
            result = dg.exec_()
            coin = dg.coinLE.text()
            exchange = dg.exCB.currentIndex()
            cond1 = dg.cond1CB.currentIndex()
            cond2 = dg.cond2CB.currentIndex()
            price = dg.prcLE.text()
            notification = dg.dnCB.isChecked()
            if exchange == 0:
                coin = "BTC_" + coin.upper()
            else:
                coin = "BTC-" + coin.upper()
            if coin in self.exchanges[exchange].coins:
                try:
                    price = float(price)
                except:
                    print("couldn't float the price")
                    return
                success = False
                while not success:
                    num = randint(1,999999)
                    success = 1 if (num not in self.alertids) else False
                alert = {'coin': coin, 'exchange': exchange, 'cond1': cond1, 'cond2': cond2, 'price': price, 'notify': notification, 'id': num, 'disabled': 0}
                self.alerts.append(alert)
                self.alertids.append(num)
                string = self.alertstring(alert)
                modelitem = alertmodelitem(string, alert['id'], alert)
                self.alertsModel.appendRow([modelitem])
                self.savealerts()
        except:
            pass

    def alertstring(self, alert):
        try:
            a = alert
            coinname = a['coin']
            exch = a['exchange']
            cond1 = a['cond1']
            cond2 = a['cond2']
            price = a['price']
            if exch == 0:
                coinname = coinname.split('_')[1] + '(p)'
            elif exch == 1:
                coinname = coinname.split('-')[1] + "(b)"
            if cond1 == 0:
                if cond2 == 0:
                    b = "over"
                elif cond2 == 1:
                    b = "under"
                string = "{} {} {:.8f}".format(coinname, b, price)
            elif cond1 == 1:
                if cond2 == 0:
                    b = "5 minutes"
                elif cond2 == 1:
                    b = "30 minutes"
                string = "{} {:0f} in {}".format(coinname, price, b)
            return string
        except:
            pass






    def callback(self):
        try:
            a = QtCore.QTimer(self)
            a.singleShot(10, self.updateview)
            a.singleShot(20, self.updatemktavglabel)
            a.singleShot(30, self.updatefavourites)
            a.singleShot(40, self.checkalerts)
            a.singleShot(50, self.updatebtcprice)
        except:
            pass

    def updateview(self):
        try:
            if self.currentexchange == 0:
                gain,loss = self.poloticks
            elif self.currentexchange == 1:
                gain,loss = self.trexticks
        except:
            return
        for (a,b) in [(self.gainmodel, gain),(self.lossmodel, loss)]:
            model = a
            data = b
            i = 0
            rowstoadd = []
            if len(data) == 0:

                rows = model.rowCount()
                if rows > 1:
                    model.removeRows(1,rows-1)
                model.setData(0, (" ", " ", " ", " ", ' ', " "))
                continue
            for b in data:
                l = "{},{:>5.1f}%,{:.8f},{:>5.1f}%,{:>5d}%,{:>1}".format(b[0], b[1], float(b[2]), float(b[4]), int(b[5]), b[6])
                l = l.split(',')
                if i < len(model.datatable):
                    model.setData(i, l)
                else:
                    rowstoadd.append(l)
                i += 1
            modelrowcount = model.rowCount()
            if len(rowstoadd) > 0:
                model.insertRows(model.rowCount(), len(rowstoadd))
                for n in range(modelrowcount, modelrowcount + len(rowstoadd)):
                    model.setData(n, rowstoadd[n-modelrowcount])
            else:
                diff = len(model.datatable) - i
                if diff > 0:
                    model.removeRows((len(model.datatable)-diff), diff)
        h = self.gainview.horizontalHeader()
        self.gainmodel.sort(h.sortIndicatorSection(),h.sortIndicatorOrder())
        h = self.lossview.horizontalHeader()
        self.lossmodel.sort(h.sortIndicatorSection(),h.sortIndicatorOrder())

    def updatemktavglabel(self):
        try:
            lbl = self.mktavglabel
            if self.currentexchange == 0:
                coins = self.poloupdater.coins
                seperator = '_'
            else:
                coins = self.trexupdater.coins
                seperator = '-'
            t1 = t2 = t3 = n1 = n2 = n3 = 0
            for item in coins:
                try:
                    splt = item.split(seperator)
                    if splt[0] != "BTC":
                        continue
                    co = coins[item]
                    pricenow = co.minutes[-1].close
                    lenmins = len(co.minutes)
                    fm = co.minutes[-1*min(6,lenmins)].close
                    tm = co.minutes[-1*min(30,lenmins)].close
                    fmc = (pricenow/fm) -1
                    tmc = (pricenow/tm) -1
                    dc = co.minutes[-1].change
                    if (fmc >= -.9) and (fmc <= 7):
                        t1 += fmc; n1 += 1
                    if (tmc >= -.9) and (tmc <= 7):
                        t2 += tmc; n2+=1
                    if (dc >= -.9) and (dc <= 7):
                        t3 += dc; n3 += 1
                except:
                    pass
            a1 = (t1/n1)*100
            a2 = (t2/n2)*100
            a3 = (t3/n3)*100
            lbl.setText("Market avg: {:.2f}% / {:.2f}% / {:.2f}%".format(a1,a2,a3))
        except:
            return

    def updatefavourites(self):
        try:
            favs = self.favourites
            tcoins = self.trexupdater.coins
            pcoins = self.poloupdater.coins
            out = []
            for item in favs:
                if '_' in item:
                    out.append(self.poloupdater.getfav(item))
                else:
                    out.append(self.trexupdater.getfav(item))
            #for (a,b) in [(self.gainmodel, gain),(self.lossmodel, loss)]:
            model = a = self.favModel
            data = b = out
            i = 0
            rowstoadd = []
            if len(data) == 0:

                rows = model.rowCount()
                if rows > 1:
                    model.removeRows(1,rows-1)
                model.setData(0, (" ", " ", " ", " ", ' ', " "))
                return
            for b in data:
                l = "{},{:>5.1f}%,{:.8f},{:>5.1f}%,{:>5d}%,{:>1}".format(b[0], b[1], float(b[2]), float(b[3]), int(b[4]), b[5])
                l = l.split(',')
                if i < len(model.datatable):
                    model.setData(i, l)
                else:
                    rowstoadd.append(l)
                i += 1
            modelrowcount = model.rowCount()
            if len(rowstoadd) > 0:
                model.insertRows(model.rowCount(), len(rowstoadd))
                for n in range(modelrowcount, modelrowcount + len(rowstoadd)):
                    model.setData(n, rowstoadd[n-modelrowcount])
            else:
                diff = len(model.datatable) - i
                if diff > 0:
                    model.removeRows((len(model.datatable)-diff), diff)
            h = self.favView.horizontalHeader()
            self.favModel.sort(h.sortIndicatorSection(),h.sortIndicatorOrder())
        except:
            pass

    def checkalerts(self):
        try:
            for a in self.alerts:
                coin = a['coin']
                exch = a['exchange']
                cond1 = a['cond1']
                cond2 = a['cond2']
                price = a['price']
                notify = a['notify']
                alertid = a['id']
                disabled = a['disabled']
                if disabled == 1:
                    continue
                trig = 0
                if cond1 == 0:
                    if cond2 == 0:
                        trig = 1 if self.exchanges[exch].getlast(coin) >= price else trig
                    elif cond2 == 1:
                        trig = 1 if self.exchanges[exch].getlast(coin) <= price else trig

                if trig:
                    if a not in self.triggeredsincelastview:
                        self.triggeredsincelastview.append(a)
                        self.alertslog.append("Alert: {} was triggered at {}".format(self.alertstring(a), time.strftime("%H:%M", time.localtime())))
                    if notify and (a not in self.dnalerts):
                        self.dnalerts.append(a)
                    row = self.alerts.index(a)
                    self.alertsModel.datatable[row][0].background = self.highlightbrush
                    self.alertsModel.cellchanged(row,0)
        except:
            pass


    def alertsnotify(self):
        try:
            if (self.sidepane.currentIndex() == 0) or (not self.isActiveWindow()):
                pass
            else:
                return
            num = len(self.triggeredsincelastview)
            num1 = len(self.dnalerts)
            if num1 > 0:
                if notificationsavailable:
                    out = []
                    for item in self.dnalerts[:5]:
                        out.append(self.alertstring(item) + "\n")
                    if num1 > 5:
                        out.append("..and {} more...".format(num1-5))
                    txt = "".join(out)[:-1]
                    if self.os == "linux":
                        n = Notify.Notification.new("Alert!", txt)
                        n.set_timeout(10000)
                        n.show()
                    elif self.os == "windows":
                        toaster.show_toast("Alert!", txt, duration=10)
            if num > 0:
                if soundavailable:
                    playsound(self.soundpath)
        except:
            pass

    def updatebtcprice(self):
        try:
            seperator = '_' if self.currentexchange == 0 else '-'
            btcprice = self.exchanges[self.currentexchange].getlast("USDT" + seperator + "BTC")
            self.btcpricelabel.setText("BTC Price: {:.2f} USDT".format(btcprice))
            return
        except:
            pass






    def sidepanetoggled(self, checked):
        try:
            if checked:
                self.oldwidth = self.width()
                self.sidewidgetholder.show()
                self.sidepanebutton.setText(">")

            else:
                height = self.height()
                self.sidewidgetholder.hide()
                self.appy.sendPostedEvents()
                a = QtCore.QEventLoop()
                a.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
                self.appy.processEvents()
                self.resize(self.oldwidth,height)
                self.sidepanebutton.setText("<")
        except:
            pass

    def tabchanged(self, index):
        try:
            if index == 0:
                if len(self.triggeredsincelastview) > 0:
                    self.alertslog.append("---------------")
                self.dnalerts = []
                self.triggeredsincelastview = []
                for item in self.alertsModel.datatable:
                    bg = item[0].background
                    if bg == self.highlightbrush:
                        item[0].background = None
        except:
            pass
            
        
    def defaultsortclicked(self):
        self.gainmodel.defaultsort = 1
        self.lossmodel.defaultsort = 1
        self.favModel.defaultsort = 1


    def trexactionclicked(self):
        self.currentexchange = 1
        self.trexaction.setFont(self.bold)
        self.poloaction.setFont(self.unbold)
        self.updateview()
        self.exchangelabel.setText("Current Exchange: Bittrex")
        self.favexchCombo.setCurrentIndex(1)


    def poloactionclicked(self):
        self.currentexchange = 0
        self.trexaction.setFont(self.unbold)
        self.poloaction.setFont(self.bold)
        self.updateview()
        self.exchangelabel.setText("Current Exchange: Poloniex")
        self.favexchCombo.setCurrentIndex(0)

    def addfav(self, ticker = None):
        try:
            if ticker == None:
                coinname = self.newfavLE.text().upper()
                cb = self.favexchCombo
                print(cb.currentText(), cb.currentIndex())
                if self.favexchCombo.currentIndex() == 0:
                    ticker = "BTC_" + coinname
                    coins = self.poloupdater.coins
                else:
                    ticker = "BTC-"+ coinname
                    coins = self.trexupdater.coins
                if (ticker in coins) and (ticker not in self.favourites):
                    self.favourites.append(ticker)
                    self.newfavLE.setText("")
            else:
                if ticker not in self.favourites:
                    self.favourites.append(ticker)
            d = shelve.open(self.databasepath)
            d['favourites'] = self.favourites
            d.close()
            return
        except:
            pass

    def getprice(self, coin, exchange):
        try:
            if exchange == 0:
                coin = "BTC_" + coin.upper()
                price = self.poloupdater.coins[coin].minutes[-1].close
            else:
                coin = "BTC-" + coin.upper()
                price = self.trexupdater.coins[coin].minutes[-1].close
            return price
        except:
            pass

    def exithandler(self):
        self.polothread.kill = 1
        self.trexthread.kill = 1
        QtWidgets.QApplication.quit()

def main():
    app = QtWidgets.QApplication(sys.argv)
    form = App(app)
    form.show()
    app.aboutToQuit.connect(form.exithandler)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


