import sys
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QAction, QTableWidget, QFileDialog, QTableWidgetItem, QLabel
from PyQt5.QtGui import QIcon

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from XRDutils import ContainerXRD, PhaseMap, opt_from_theta, PhaseList
from numpy import newaxis, ones, arange, asarray, sqrt, linspace

import yaml

def set_opt(n, m, init_opt):
    nn = n + 3
    opt = ones(nn * m,dtype='float32')

    opt[0::nn] = init_opt[0]
    opt[1::nn] = init_opt[1]
    opt[2::nn] = init_opt[2]

    return opt

def set_opt_(n, m, init_opt):
    nn = 3
    opt = ones(nn * m,dtype='float32')

    opt[0::nn] = init_opt[0]
    opt[1::nn] = init_opt[1]
    opt[2::nn] = init_opt[2]

    return opt

def mesh_opt():

    theta_min, theta_max, betas = linspace(10,25,50), linspace(35,55,50), linspace(30,60,40)

    opt = []
    for t0 in theta_min:
        for tm in theta_max:
            for b in betas:
                opt += [opt_from_theta(t0,tm,b)]

    return asarray(opt)

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=300):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)

        super(MplCanvas, self).__init__(self.fig)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        openAction = QAction(QIcon('open.png'), '&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open document')
        openAction.triggered.connect(self.openCall)

        saveAction = QAction(QIcon('save.png'), '&Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save calibration')
        saveAction.triggered.connect(self.saveCall)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)

        self.file_label = QLabel()
        self.d1_label = QLabel()
        self.d2_label = QLabel()

        self.d1_label.setText('MYTHEN1')
        self.d2_label.setText('MYTHEN2')

        self.sc = MplCanvas(self, width=5, height=4, dpi=100)

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar(self.sc, self)

        self.tableWidget_opt_left = QTableWidget()
        self.tableWidget_opt_right = QTableWidget()

        self.tableWidget_opt_left.setRowCount(1)
        self.tableWidget_opt_right.setRowCount(1)

        self.tableWidget_opt_left.setColumnCount(3)
        self.tableWidget_opt_right.setColumnCount(3)

        self.tableWidget_opt_left.setFixedHeight(100)
        self.tableWidget_opt_right.setFixedHeight(100)

        self.tableWidget_opt_left.setMinimumHeight(100)
        self.tableWidget_opt_right.setMinimumHeight(100)


        self.tableWidget_opt_left.setHorizontalHeaderLabels(['a','s','beta'])
        self.tableWidget_opt_right.setHorizontalHeaderLabels(['a','s','beta'])
        self.tableWidget_opt_left.verticalHeader().setVisible(False)
        self.tableWidget_opt_right.verticalHeader().setVisible(False)

        self.tableWidget_theta_left = QTableWidget()
        self.tableWidget_theta_right = QTableWidget()


        self.tableWidget_theta_left.setRowCount(1)
        self.tableWidget_theta_right.setRowCount(1)

        self.tableWidget_theta_left.setColumnCount(3)
        self.tableWidget_theta_right.setColumnCount(3)

        self.tableWidget_theta_left.setFixedHeight(100)
        self.tableWidget_theta_right.setFixedHeight(100)

        self.tableWidget_theta_left.setHorizontalHeaderLabels(['theta_min','theta_max','range'])
        self.tableWidget_theta_right.setHorizontalHeaderLabels(['theta_min','theta_max','range'])
        self.tableWidget_theta_left.verticalHeader().setVisible(False)
        self.tableWidget_theta_right.verticalHeader().setVisible(False)


        self.tableWidget_left = QTableWidget()
        self.tableWidget_right = QTableWidget()

        self.tableWidget_left.setRowCount(0)
        self.tableWidget_right.setRowCount(0)

        self.tableWidget_left.setColumnCount(0)
        self.tableWidget_right.setColumnCount(0)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.file_label)
        layout.addWidget(self.sc)

        label_layout = QtWidgets.QHBoxLayout()
        opt_layout = QtWidgets.QHBoxLayout()
        theta_layout = QtWidgets.QHBoxLayout()
        sigma_layout = QtWidgets.QHBoxLayout()

        label_layout.addWidget(self.d1_label)
        label_layout.addWidget(self.d2_label)

        opt_layout.addWidget(self.tableWidget_opt_left)
        opt_layout.addWidget(self.tableWidget_opt_right)

        theta_layout.addWidget(self.tableWidget_theta_left)
        theta_layout.addWidget(self.tableWidget_theta_right)

        sigma_layout.addWidget(self.tableWidget_left)
        sigma_layout.addWidget(self.tableWidget_right)

        layout.addLayout(label_layout)
        layout.addLayout(opt_layout)
        layout.addLayout(theta_layout)
        layout.addLayout(sigma_layout)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.show()

    def saveCall(self):
        if hasattr(self,'filename'):
            print(self.filename)
            dict_file = [{'beta' : round(float(self.pm.beta[0][0]), 4)},
                         {'calibration' : 
                             {'theta_min' : round(float(self.pm.min_theta[0][0]), 4), 'theta_max' : round(float(self.pm.max_theta[0][0]), 4)}}] 

            with open(self.filename[:self.filename.rfind('/') + 1] + 'calibration.yaml', 'w') as file:
                calibration = yaml.dump(dict_file, file)

    def openCall(self):
        """
        Open spectrum
        """
        self.filename = QFileDialog.getOpenFileName(self, 'Open file','',"Data File (*.dat)")[0]
        print(self.filename)

        self.file_label.setText(self.filename)

        self.container = ContainerXRD('config.yaml')

        self.container.read_database()

        self.container.data.data = self.container.data.__read_single_dat__(self.filename)[newaxis,newaxis,:]
        self.container.data.n_channels = [1280]
        self.container.data.opt = [[0,-2000,43]]

        self.container.opt = self.container.data.opt

        self.container.remove_background()

        alumina = PhaseList([self.container.database['Aluminium oxide'][0]])
        #alumina = PhaseList([self.container.database['SRM1976a'][0]])

        opt = mesh_opt()

        self.container.data.data = self.container.data.data.repeat(len(opt),axis=0)
        self.container.data.background = self.container.data.background.repeat(len(opt),axis=0)
        self.container.data.no_background = self.container.data.no_background.repeat(len(opt),axis=0)
        self.container.data.normalized = self.container.data.normalized.repeat(len(opt),axis=0)

        self.pm = PhaseMap(self.container,alumina)

        self.pm.detectors[0].opt = set_opt(self.pm.detectors[0].n,self.pm.detectors[0].n_pixels,opt.T)
        self.pm.detectors[0]._opt = set_opt_(self.pm.detectors[0].n,self.pm.detectors[0].n_pixels,opt.T)

        #print(self.pm.detectors[0].opt.shape)
        #print(self.pm.detectors[0].opt)
        #print(self.pm.detectors[0].opt.reshape(self.pm.detectors[0].n+3,-1))
        #print(self.pm.detectors[0].opt.reshape(self.pm.detectors[0].n+3,-1).shape)

        self.pm.mp_synthetic_spectra()
        self.pm.mp_cosine_similarity()


        #print(self.pm.cosine_similarity[0].max(),self.pm.cosine_similarity[0].argmax())
        idx = self.pm.cosine_similarity[0].argmax()

        #print(self.pm.detectors[0].opt.shape)
        #print(idx)

        """
        Second pass
        """
        mm = self.pm.detectors[0].n + 3
        #opt = self.pm._opt[0][idx]
        opt = self.pm.detectors[0].opt[idx*mm:idx*mm+3]

        print('opt:',opt)

        self.container = ContainerXRD('config.yaml')

        self.container.data.data = self.container.data.__read_single_dat__(self.filename)[newaxis,newaxis,:]
        self.container.data.n_channels = [1280]
        self.container.data.opt = [[0,-2000,43]]
        self.container.opt = self.container.data.opt

        self.container.remove_background()

        self.pm = PhaseMap(self.container,alumina)
        #self.pm.opt[0][0] = opt
        #self.pm.detectors[0].opt[0][0] = opt
        #self.pm._opt[0][0] = opt

        self.pm.detectors[0].opt[0] = opt[0]
        self.pm.detectors[0].opt[1] = opt[1]
        self.pm.detectors[0].opt[2] = opt[2]

        print('det:',self.pm.detectors[0].opt)
        #self.pm._opt[0][0] = opt

        self.pm.set_n_iter(128)
        self.pm.a_s_n_beta_gamma()

        self.pm.mp_gamma_sigma()

        self.pm.mp_synthetic_spectra()
        self.pm.mp_cosine_similarity()

        self.sc.axes.cla()

        print('theta.shape:',self.pm.detectors[0].theta[0])

        rescale = 1e3

        print(self.pm.detectors[0].opt[0])

        for detector in self.pm.detectors:
            #self.sc.axes.plot(detector.theta[0,0],detector.data[0][0] * rescale, lw=0.66, color='gray')
            #self.sc.axes.plot(detector.theta[0,0],detector.z[0][0] * rescale ,lw=0.66, color='steelblue')

            self.sc.axes.plot(detector.theta[0],detector.data[0] * rescale, lw=0.66, color='gray')
            self.sc.axes.plot(detector.theta[0],detector.z[0] * rescale ,lw=0.66, color='steelblue')

            self.sc.axes.vlines(detector.mu,0,detector.intensity * rescale,'k',ls='-',lw=1.5)

        phase = self.pm.phase.get_theta(theta_min=10,theta_max=70)
        self.sc.axes.vlines(phase.theta,0,phase.intensity,'r',ls='--',lw=1)

        self.sc.axes.set_xlim(10,50)

        self.sc.axes.set_xlabel(r'$2 \theta$')
        self.sc.axes.set_ylabel('Normalized Intensity (a.u)')

        self.sc.axes.draw(self.sc.fig.canvas.renderer)

        #self.tableWidget_opt_left.setItem(0,0,QTableWidgetItem("%.2f"%self.pm.detectors[0]._a[0]))
        #self.tableWidget_opt_left.setItem(0,1,QTableWidgetItem("%.2f"%self.pm.detectors[0]._s[0]))
        #self.tableWidget_opt_left.setItem(0,2,QTableWidgetItem("%.2f"%self.pm.detectors[0]._beta[0]))

        self.tableWidget_opt_left.setItem(0,0,QTableWidgetItem("%.2f"%self.pm.detectors[0].opt[0]))
        self.tableWidget_opt_left.setItem(0,1,QTableWidgetItem("%.2f"%self.pm.detectors[0].opt[1]))
        self.tableWidget_opt_left.setItem(0,2,QTableWidgetItem("%.2f"%self.pm.detectors[0].opt[2]))

        self.tableWidget_theta_left.setItem(0,0,QTableWidgetItem("%.2f"%self.pm.detectors[0].min_theta[0]))
        self.tableWidget_theta_left.setItem(0,1,QTableWidgetItem("%.2f"%self.pm.detectors[0].max_theta[0]))
        self.tableWidget_theta_left.setItem(0,2,QTableWidgetItem("%.2f"%(self.pm.detectors[0].max_theta[0] - self.pm.detectors[0].min_theta[0])))

        self.tableWidget_left.setRowCount(self.pm.detectors[0].n)

        self.tableWidget_left.setColumnCount(4)
        self.tableWidget_right.setColumnCount(4)

        self.tableWidget_left.setHorizontalHeaderLabels(['theta','intensity','sigma','FWHM'])
        self.tableWidget_right.setHorizontalHeaderLabels(['theta','intensity','sigma','FWHM'])

        def w(x):
            _a = 5.0;
            return (sqrt((_a * x)**2 + 1) / _a + x);

        for i in range(self.pm.detectors[0].n):
            self.tableWidget_left.setItem(i,0,QTableWidgetItem("%.2f"%self.pm.detectors[0].mu[i]))
            self.tableWidget_left.setItem(i,1,QTableWidgetItem("%.2f"%(self.pm.detectors[0].intensity[i] * 1e3)))
            self.tableWidget_left.setItem(i,2,QTableWidgetItem("%.2f"%sqrt(self.pm.detectors[0].sigma2.reshape(-1,self.pm.detectors[0].n)[0][i])))
            self.tableWidget_left.setItem(i,3,QTableWidgetItem("%.2f"%(2.355 * sqrt(self.pm.detectors[0].sigma2.reshape(-1,self.pm.detectors[0].n)[0][i]))))
            #self.tableWidget_left.setItem(i,4,QTableWidgetItem("%.2f"%w(self.pm.detectors[0].opt.reshape(-1,self.pm.detectors[0].n+3)[0][i+3])))
            #self.tableWidget_left.setItem(i,4,QTableWidgetItem("%.2f"%(self.pm.detectors[0].gamma[i])))
        print((self.pm.detectors[0].opt.reshape(-1,self.pm.detectors[0].n+3)).shape)
        print(self.pm.detectors[0].opt.reshape(-1,self.pm.detectors[0].n+3))

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()
