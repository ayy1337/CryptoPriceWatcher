#!/usr/bin/python3

'''     Crypto Price Watcher
        Version: 1.0
        Author: ayy1337
        Licence: GNU GPL v3.0
'''


from PyQt5 import QtGui, QtCore, QtWidgets
Qt = QtCore.Qt
import sys, os, sys, shelve, time, threading, random, operator, copy, datetime, collections, grabtrex, grabpolo
from operator import attrgetter, itemgetter
import trexapi, poloapi

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1211, 866)
        MainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 4)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAutoFillBackground(False)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
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
        self.gainView = QtWidgets.QTableView(self.centralwidget)
        self.gainView.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(4)
        sizePolicy.setHeightForWidth(self.gainView.sizePolicy().hasHeightForWidth())
        self.gainView.setSizePolicy(sizePolicy)
        self.gainView.setMinimumSize(QtCore.QSize(380, 0))
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
        self.lossView = QtWidgets.QTableView(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(4)
        sizePolicy.setHeightForWidth(self.lossView.sizePolicy().hasHeightForWidth())
        self.lossView.setSizePolicy(sizePolicy)
        self.lossView.setMinimumSize(QtCore.QSize(380, 0))
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
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.exchangelabel = QtWidgets.QLabel(self.centralwidget)
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
        self.sortButton = QtWidgets.QPushButton(self.centralwidget)
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
        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(1, 1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1211, 23))
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
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Crypto Price Watcher"))
        self.label.setText(_translate("MainWindow", "Gainers"))
        self.label_2.setText(_translate("MainWindow", "Losers"))
        self.exchangelabel.setText(_translate("MainWindow", "Current Exchange: Poloniex"))
        self.sortButton.setText(_translate("MainWindow", "Default Sort"))
        self.menuMenu.setTitle(_translate("MainWindow", "Menu"))
        self.menuExchange.setTitle(_translate("MainWindow", "Exchange"))
        self.actionPoloniex.setText(_translate("MainWindow", "Poloniex"))
        self.actionBittrex.setText(_translate("MainWindow", "Bittrex"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))

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
    def removeRows(self, row, count, parent = QtCore.QModelIndex()):
        assert 0 <= row <= self.rowCount()
        assert count > 0
        self.beginRemoveRows(parent, row, row+count-1)
        for row in range(row, row+count):
            del self.datatable[-1]
        self.endRemoveRows()
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
                if (time1 - oldtime) > 1:
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
                if (time1 - oldtime) > 1:
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


class App(QtWidgets.QMainWindow):
    def __init__(self):
        super(App, self).__init__()
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

        self.initstuff()
        self.setupgainview()
        self.setuplossview()

    def initstuff(self):
        self.updateRunning = 0
        self.poloticks = self.trexticks = [[],[]]
        self.poloupdater = grabpolo.updater()
        self.trexupdater = grabtrex.updater()
        self.currentexchange = 0
        self.polothread = polothread(1, "poloUpdateThread", self)
        self.trexthread = trexthread(2, "trexUpdateThread", self)
        self.polothread.start()
        self.trexthread.start()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.callback)
        self.timer.start(2000)

    def setupgainview(self):
        self.gainview = self.ui.gainView
        self.gainmodel = myTableModel(self, 1)
        self.gainmodel.setheaders(['Ticker', '5m', 'Price', '30m', '24h', 'Vol'])
        self.gainmodel.update([(" ", " ", " ", " ", ' ', " ")])
        self.gainview.setModel(self.gainmodel)
        header = self.gainview.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)
        header.setDefaultAlignment(QtCore.Qt.AlignCenter)
        header.sectionClicked.connect(self.gainheaderclicked)

    def gainheaderclicked(self, index):
        self.gainmodel.defaultsort = 0



    def setuplossview(self):
        self.lossview = self.ui.lossView
        self.lossmodel = myTableModel(self, 1)
        self.lossmodel.setheaders(['Ticker', '5m', 'Price', '30m', '24h', 'Volume'])
        self.lossmodel.update([(" ", " ", " ", " ", ' ', " ")])
        self.lossview.setModel(self.lossmodel)
        header = self.lossview.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)
        header.setDefaultAlignment(QtCore.Qt.AlignCenter)
        header.sectionClicked.connect(self.lossheaderclicked)

    def lossheaderclicked(self, index):
        self.lossmodel.defaultsort = 0

    def defaultsortclicked(self):
        self.gainmodel.defaultsort = 1
        self.lossmodel.defaultsort = 1


    def trexactionclicked(self):
        self.currentexchange = 1
        self.trexaction.setFont(self.bold)
        self.poloaction.setFont(self.unbold)
        self.updateview()
        self.exchangelabel.setText("Current Exchange: Bittrex")


    def poloactionclicked(self):
        self.currentexchange = 0
        self.trexaction.setFont(self.unbold)
        self.poloaction.setFont(self.bold)
        self.updateview()
        self.exchangelabel.setText("Current Exchange: Poloniex")


    def callback(self):
        try:
            a = QtCore.QTimer(self)
            a.singleShot(10, self.updateview)
        except:
            pass


    def updateview(self):
        if self.currentexchange == 0:
            gain,loss = self.poloticks
        elif self.currentexchange == 1:
            gain,loss = self.trexticks
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

    def exithandler(self):
        self.polothread.kill = 1
        self.trexthread.kill = 1
        QtWidgets.QApplication.quit()

def main():
    app = QtWidgets.QApplication(sys.argv)
    form = App()
    form.show()
    app.aboutToQuit.connect(form.exithandler)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

