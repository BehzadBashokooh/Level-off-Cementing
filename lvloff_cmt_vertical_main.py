from lvloff_cmt_vertical import Ui_Form
import pandas as pd
import numpy as np
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5.QtWebEngineWidgets import *
import plotly.express as px
import plotly.offline as pyo
import plotly.graph_objs as go


class AppWindow(qtw.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Modify the casing and openhole ID size with this variable (bigger L => bigger ID)
        self.L = 50

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.browser = QWebEngineView(self)
        self.browser.resize(670, 900)
        self.browser.setParent(self.ui.chart)

        self.ui.calc_btn.clicked.connect(self.calculate)
        self.ui.example_btn.clicked.connect(self.example)
        self.ui.init_btn.clicked.connect(self.init_btn)
        self.ui.fin_btn.clicked.connect(self.final_btn)

    def example(self):
        # Fills the input data lineedits with example data
        self.ui.total_md.setText(str(2300))
        self.ui.shoe_md.setText(str(1900))
        self.ui.loss_zone_md.setText(str(2200))
        self.ui.rtts_md.setText(str(1400))
        self.ui.csg_cap.setText(str(0.078))
        self.ui.oh_cap.setText(str(0.07))
        self.ui.dp_cap.setText(str(0.01718))
        self.ui.mw.setText(str(65))
        self.ui.cmt_weight.setText(str(100))
        self.ui.final_cmt_col.setText(str(100))
        self.ui.loss_zone_press.setText(str(2650))

    def calculate(self):
        # Read the input data and conduct the level-off calculations

        # Read input data
        self.total_md = float(self.ui.total_md.text())
        self.shoe_md = float(self.ui.shoe_md.text())
        self.loss_zone_md = float(self.ui.loss_zone_md.text())
        self.rtts_md = float(self.ui.rtts_md.text())
        self.csg_cap = float(self.ui.csg_cap.text())
        self.oh_cap = float(self.ui.oh_cap.text())
        self.dp_cap = float(self.ui.dp_cap.text())
        self.mw = float(self.ui.mw.text())
        self.cmt_weight = float(self.ui.cmt_weight.text())
        self.final_cmt_col = float(self.ui.final_cmt_col.text())
        self.loss_zone_press = float(self.ui.loss_zone_press.text())

        # Start of calculations
        self.final_cmt_col_press = 0.052*self.cmt_weight/7.481*self.final_cmt_col*3.281

        self.mud_drop_dp = self.loss_zone_md - self.final_cmt_col - ((self.loss_zone_press -
                                                                      self.final_cmt_col_press)/(0.052*self.mw/7.481*3.281))

        self.mud_drop_vol = self.mud_drop_dp*3.281*self.dp_cap
        self.cmt_lost_vol = self.mud_drop_vol
        self.total_dp_vol = (self.rtts_md)*3.281*self.dp_cap
        self.rtts_to_shoe_vol = (
            self.shoe_md - self.rtts_md)*3.281*self.csg_cap

        self.oh_vol = (self.loss_zone_md - self.shoe_md)*3.281*self.oh_cap

        if self.final_cmt_col < self.loss_zone_md - self.shoe_md:
            self.final_cmt_vol = self.final_cmt_col*3.281*self.oh_cap
            self.disp_mud_vol = self.total_dp_vol + self.rtts_to_shoe_vol + \
                (self.oh_vol - self.final_cmt_vol - self.cmt_lost_vol)
            if self.mud_drop_vol < self.oh_vol - self.final_cmt_vol:
                self.cmt_lvldrop = (self.cmt_lost_vol/self.oh_cap)/3.281
            else:
                cmt_lvldrop_1 = self.loss_zone_md - self.shoe_md - self.final_cmt_col
                cmt_lvldrop_1_vol = self.oh_vol - self.final_cmt_vol
                cmt_lvldrop_2_vol = self.mud_drop_vol - cmt_lvldrop_1_vol
                cmt_lvldrop_2 = (cmt_lvldrop_2_vol/self.csg_cap)/3.281
                self.cmt_lvldrop = cmt_lvldrop_1 + cmt_lvldrop_2
        else:
            self.final_cmt_vol = self.oh_vol + \
                (self.final_cmt_col - (self.loss_zone_md - self.shoe_md)) * \
                3.281*self.csg_cap
            self.cmt_lvldrop = (self.cmt_lost_vol/self.csg_cap)/3.281

        self.initial_cmt_col = self.final_cmt_col + self.cmt_lvldrop
        self.total_cmt_vol = self.final_cmt_vol + self.cmt_lost_vol
        self.disp_mud_vol = self.total_dp_vol + \
            self.rtts_to_shoe_vol + self.oh_vol - self.total_cmt_vol
        self.init_toc_rtts = self.loss_zone_md - self.rtts_md - self.initial_cmt_col
        self.loss_zone_press_diff = 0.052*self.initial_cmt_col*3.281*self.cmt_weight/7.481 + \
            0.052*(self.loss_zone_md - self.initial_cmt_col) * \
            3.281*self.mw/7.481 - self.loss_zone_press
        self.init_toc_md = self.loss_zone_md - self.initial_cmt_col
        self.final_toc_md = self.loss_zone_md - self.final_cmt_col
        # End of calculations

        self.populate_output()
        self.well_schematic()
        self.fluids_init()
        self.show_fig('initial')
        self.ui.init_btn.setEnabled(True)
        self.ui.fin_btn.setEnabled(True)

    def populate_output(self):
        # Populate the output linedits
        self.ui.cmt_col_disp.setText('{:.2f}'.format(self.initial_cmt_col))
        self.ui.total_cmt_vol.setText('{:.2f}'.format(self.total_cmt_vol))
        self.ui.disp_mud_vol.setText('{:.2f}'.format(self.disp_mud_vol))
        self.ui.cmt_lost_vol.setText('{:.2f}'.format(self.cmt_lost_vol))
        self.ui.mud_lvldrop_dp.setText('{:.2f}'.format(self.mud_drop_dp))
        self.ui.cmt_lvldrop.setText('{:.2f}'.format(self.cmt_lvldrop))
        self.ui.init_toc_rtts.setText('{:.2f}'.format(self.init_toc_rtts))
        self.ui.loss_zone_press_diff.setText(
            '{:.2f}'.format(self.loss_zone_press_diff))

    def well_schematic(self):
        # Makes the well schematic (casing, open hole, drill pipe and RTTS packer)
        L = self.L
        rtts_md = self.rtts_md
        shoe_md = self.shoe_md
        total_md = self.total_md
        loss_zone_md = self.loss_zone_md

        # Plotly chart
        # Drillpipe
        dp = go.Scatter(x=[-L, -L, L, L], y=[rtts_md, 0, 0, rtts_md], line=dict(
            color='black'), mode="lines", fill="toself", fillcolor='rgb(160, 162, 163)')

        # Casing
        csg = go.Scatter(x=[-4*L, -4*L, 4*L, 4*L], y=[shoe_md, 0, 0, shoe_md], line=dict(
            color='black'), mode="lines", fill="toself", fillcolor='rgb(113, 121, 126)')

        # Casing shoe
        csgr_tri = go.Scatter(x=[4.4*L], y=[shoe_md], line=dict(color='black'),
                              mode="markers", marker_symbol='triangle-sw', marker_size=15)  # right
        csgl_tri = go.Scatter(x=[-4.4*L], y=[shoe_md], line=dict(color='black'),
                              mode="markers", marker_symbol='triangle-se', marker_size=15)  # left

        # Open hole
        size = int((total_md - shoe_md)//10)

        ohx1 = 3.9*L*np.ones(size) + L/4*np.random.rand(size)  # left & right
        ohy1 = np.linspace(shoe_md, total_md, size)

        ohx2 = np.linspace(-3.9*L, 3.9*L, 30)  # bottom
        ohy2 = total_md*np.ones(30) + L/4*np.random.rand(30)

        ohx = np.concatenate((-ohx1, ohx2, np.flip(ohx1)),
                             axis=None)  # combine the lines
        ohy = np.concatenate((ohy1, ohy2, np.flip(ohy1)), axis=None)
        self.ohdf = pd.DataFrame({'x': ohx, 'y': ohy})

        ohb = go.Scatter(x=ohx, y=ohy, line=dict(color='black'),
                         mode="lines", fill="toself")  # bottom

        # RTTS packer
        rtts_r = go.Scatter(x=[L, 4*L, 4*L, L, L], y=[rtts_md, rtts_md, rtts_md-L, rtts_md-L, rtts_md], line=dict(color='black'),
                            mode="lines+text", fill="toself", fillcolor='rgb(50,50,50)')
        rtts_l = go.Scatter(x=[-L, -4*L, -4*L, -L, -L], y=[rtts_md, rtts_md, rtts_md-L, rtts_md-L, rtts_md], line=dict(color='black'),
                            mode="lines", fill="toself", fillcolor='rgb(50,50,50)')

        # Loss zone
        x = np.linspace(3.9*L, 6.9*L, 15)
        y = loss_zone_md*np.ones(15) + L/4*np.random.rand(15)
        lzr = go.Scatter(x=x, y=y, line=dict(color='black'), mode="lines")
        lzl = go.Scatter(x=-x, y=y, line=dict(color='black'), mode="lines")

        self.well_schematic_data = [csg, dp, ohb, rtts_r, rtts_l, lzr, lzl]
        self.csg_shoe_icons = [csgr_tri, csgl_tri]

    def fluids_init(self):

        L = self.L
        ohdf = self.ohdf
        rtts_md = self.rtts_md
        shoe_md = self.shoe_md
        loss_zone_md = self.loss_zone_md
        init_toc_md = self.init_toc_md

        # Fluids initial condition
        if init_toc_md >= shoe_md:

            cmtdf = ohdf.copy()[(ohdf['y'] >= init_toc_md) &
                                (ohdf['y'] <= loss_zone_md)]
            muddf = ohdf.copy()[(ohdf['y'] <= init_toc_md)]
            muddf.loc[-2] = [-4*L, rtts_md]
            muddf.loc[-1] = [-4*L, shoe_md]
            muddf.index = muddf.index+1
            muddf = muddf.sort_index()
            muddf = muddf.append({'x': 4*L, 'y': shoe_md}, ignore_index=True)
            muddf = muddf.append({'x': 4*L, 'y': rtts_md}, ignore_index=True)
            cmt = go.Scatter(x=cmtdf['x'], y=cmtdf['y'], line=dict(
                color='rgba(0,0,0,0)'), mode="lines", fill="toself", fillcolor='rgb(202, 204, 206)')
            mud = go.Scatter(x=muddf['x'], y=muddf['y'], line=dict(
                color='rgba(0,0,0,0)'), mode="lines", fill="toself", fillcolor='#FFD700')
            dp_mud = go.Scatter(x=[-L, -L, L, L], y=[rtts_md, 0, 0, rtts_md], line=dict(
                color='black'), mode="lines", fill="toself", fillcolor='#FFD700')

        else:
            cmtdf = ohdf[(ohdf['y'] <= loss_zone_md)]

            cmtdf.loc[-1] = [-4*L, init_toc_md]
            cmtdf.index = cmtdf.index+1
            cmtdf = cmtdf.sort_index()
            cmtdf = cmtdf.append(
                {'x': 4*L, 'y': init_toc_md}, ignore_index=True)
            cmt = go.Scatter(x=cmtdf['x'], y=cmtdf['y'], line=dict(
                color='rgba(0,0,0,0)'), mode="lines", fill="toself", fillcolor='rgb(202, 204, 206)')
            mud = go.Scatter(x=[-4*L, -4*L, 4*L, 4*L], y=[init_toc_md, rtts_md, rtts_md, init_toc_md],
                             line=dict(color='rgba(0,0,0,0)'), mode="lines", fill="toself", fillcolor='#FFD700')
            dp_mud = go.Scatter(x=[-L, -L, L, L], y=[rtts_md, 0, 0, rtts_md], line=dict(
                color='black'), mode="lines", fill="toself", fillcolor='#FFD700')

        self.fluids_init_data = [cmt, mud, dp_mud]

    def fluids_final(self):

        L = self.L
        ohdf = self.ohdf
        mud_drop_dp = self.mud_drop_dp
        rtts_md = self.rtts_md
        shoe_md = self.shoe_md
        loss_zone_md = self.loss_zone_md
        final_toc_md = self.final_toc_md

        # Fluids final condition
        if final_toc_md >= shoe_md:

            cmtdf = ohdf.copy()[(ohdf['y'] >= final_toc_md) &
                                (ohdf['y'] <= loss_zone_md)]
            muddf = ohdf.copy()[(ohdf['y'] <= final_toc_md)]
            muddf.loc[-2] = [-4*L, rtts_md]
            muddf.loc[-1] = [-4*L, shoe_md]
            muddf.index = muddf.index+1
            muddf = muddf.sort_index()
            muddf = muddf.append({'x': 4*L, 'y': shoe_md}, ignore_index=True)
            muddf = muddf.append({'x': 4*L, 'y': rtts_md}, ignore_index=True)
            cmt = go.Scatter(x=cmtdf['x'], y=cmtdf['y'], line=dict(
                color='rgba(0,0,0,0)'), mode="lines", fill="toself", fillcolor='rgb(202, 204, 206)')
            mud = go.Scatter(x=muddf['x'], y=muddf['y'], line=dict(
                color='rgba(0,0,0,0)'), mode="lines", fill="toself", fillcolor='#FFD700')
            dp_mud = go.Scatter(x=[-L, -L, L, L], y=[rtts_md, mud_drop_dp, mud_drop_dp, rtts_md],
                                line=dict(color='black'), mode="lines", fill="toself", fillcolor='#FFD700')

        else:
            cmtdf = ohdf[(ohdf['y'] <= loss_zone_md)]

            cmtdf.loc[-1] = [-4*L, final_toc_md]
            cmtdf.index = cmtdf.index+1
            cmtdf = cmtdf.sort_index()
            cmtdf = cmtdf.append(
                {'x': 4*L, 'y': final_toc_md}, ignore_index=True)
            cmt = go.Scatter(x=cmtdf['x'], y=cmtdf['y'], line=dict(
                color='rgba(0,0,0,0)'), mode="lines", fill="toself", fillcolor='rgb(202, 204, 206)')
            mud = go.Scatter(x=[-4*L, -4*L, 4*L, 4*L], y=[final_toc_md, rtts_md, rtts_md, final_toc_md],
                             line=dict(color='rgba(0,0,0,0)'), mode="lines", fill="toself", fillcolor='#FFD700')
            dp_mud = go.Scatter(x=[-L, -L, L, L], y=[rtts_md, 0, 0, rtts_md], line=dict(
                color='black'), mode="lines", fill="toself", fillcolor='#FFD700')

        self.fluids_final_data = [cmt, mud, dp_mud]

    def show_fig(self, chart_type):
        # Aggregates the data for plotly figure and displays the results
        L = self.L
        mud_drop_dp = self.mud_drop_dp
        rtts_md = self.rtts_md
        shoe_md = self.shoe_md
        total_md = self.total_md
        loss_zone_md = self.loss_zone_md
        init_toc_md = self.init_toc_md
        final_toc_md = self.final_toc_md

        if chart_type == 'initial':
            self.fig_data = self.well_schematic_data + \
                self.fluids_init_data + self.csg_shoe_icons
        elif chart_type == 'final':
            self.fig_data = self.well_schematic_data + \
                self.fluids_final_data + self.csg_shoe_icons

        fig = go.Figure(data=self.fig_data)
        fig.update_yaxes(autorange="reversed", scaleanchor="x",
                         scaleratio=1, showgrid=False, fixedrange=True, zerolinecolor='black')
        fig.update_xaxes(showgrid=False, visible=False, fixedrange=True)
        fig.update_layout(
            showlegend=False,
            autosize=False,
            width=430,
            height=600,
            paper_bgcolor='rgb(240, 230, 140,1)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=0,
            ))

        # Annotations
        ax = 45
        ay = -20
        # RTTS Depth
        fig.add_annotation(x=4*L, y=rtts_md, text=str(rtts_md) + ' m', showarrow=True,
                           font=dict(size=16), ax=ax, ay=ay)
        # Initial TOC
        if chart_type == 'initial':
            fig.add_annotation(x=4*L, y=init_toc_md, text='Initial TOC: {:.2f} m'.format(init_toc_md), showarrow=True,
                               font=dict(size=16), ax=2*ax, ay=ay)
        elif chart_type == 'final':
            fig.add_annotation(x=4*L, y=final_toc_md, text='Final TOC: {:.2f} m'.format(final_toc_md), showarrow=True,
                               font=dict(size=16), ax=2*ax, ay=ay)
            fig.add_annotation(x=4*L, y=mud_drop_dp, text='Final TOM: {:.2f} m'.format(mud_drop_dp), showarrow=True,
                               font=dict(size=16), ax=2*ax, ay=ay)
        self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))

    def init_btn(self):

        self.show_fig('initial')

    def final_btn(self):

        self.fluids_final()
        self.show_fig('final')


if __name__ == '__main__':
    app = qtw.QApplication([])

    widget = AppWindow()
    widget.show()

    app.exec()
