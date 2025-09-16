#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2024/10/17 13:03
# @Author  : 兵
# @email    : 1747193328@qq.com


from functools import partial

import numpy as np

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from pyqtgraph import GraphicsLayoutWidget, ScatterPlotItem, PlotItem, ViewBox, TextItem

from NepTrainKit import utils
from NepTrainKit.core.types import Brushes, Pens
from NepTrainKit.config import Config
from ..base.canvas import CanvasLayoutBase
from ...io import NepTrainResultData


class MyPlotItem(PlotItem):
    """
    自定义Item 实例化即可创建一个axes
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.disableAutoRange()

        self._scatter = ScatterPlotItem()
        self.addItem(self._scatter)

        self.text = TextItem(color=(231, 63, 50))

        self.addItem(self.text)

        self.current_point = ScatterPlotItem()
        self.current_point.setZValue(100)
        if "title" in kwargs:
            self.setTitle(kwargs["title"])

    def scatter(self, *args, **kargs):
        self._scatter.setData(*args, **kargs)

    def set_current_point(self, x, y):

        current_size = Config.getint("plot", "current_marker_size", 20) or 20
        self.current_point.setData(x, y, brush=Brushes.Current, pen=Pens.Current,
                                   symbol='star', size=current_size)
        if self.current_point not in self.items:
            self.addItem(self.current_point)

    def add_diagonal(self):

        self.addLine(angle=45, pos=(0.5, 0.5), pen=Pens.Line)

    def item_clicked(self, scatter_item, items, event):

        if items.any():
            item = items[0]

            self.structureIndexChanged.emit(item.data())

    @property
    def title(self):
        return self.titleLabel.text

    @title.setter
    def title(self, t):
        if t == self.title:
            return
        self.setTitle(t)
        if t != "descriptor":
            self.add_diagonal()

    @property
    def rmse_size(self):
        return self.text.textItem.font().pointSize()
    @rmse_size.setter
    def rmse_size(self,size):

        self.text.setFont(QFont("Arial",size))
class CombinedMeta(type(CanvasLayoutBase), type(GraphicsLayoutWidget)):
    pass


class PyqtgraphCanvas(CanvasLayoutBase, GraphicsLayoutWidget, metaclass=CombinedMeta):
    """
    pyqtgraph 绘图类
    """

    def __init__(self, *args, **kwargs):
        GraphicsLayoutWidget.__init__(self, *args, **kwargs)

        CanvasLayoutBase.__init__(self)
        self.nep_result_data = None

    def set_nep_result_data(self, dataset):
        self.nep_result_data: NepTrainResultData = dataset

    def clear_axes(self):
        self.clear()

        super().clear_axes()

    def init_axes(self, axes_num):
        self.clear_axes()

        for r in range(axes_num):
            plot = MyPlotItem(title="")
            self.addItem(plot)
            plot.getViewBox().mouseDoubleClickEvent = partial(self.view_on_double_clicked, plot=plot)
            plot.getViewBox().setMouseEnabled(False, False)
            self.axes_list.append(plot)

            plot._scatter.sigClicked.connect(self.item_clicked)

        self.set_view_layout()

    def view_on_double_clicked(self, event, plot):
        self.set_current_axes(plot)

    def set_view_layout(self):
        if len(self.axes_list) == 0:
            return
        if self.current_axes not in self.axes_list:
            self.set_current_axes(self.axes_list[0])
            return

        self.ci.clear()
        self.addItem(self.current_axes, row=0, col=0, colspan=4)
        self.current_axes.rmse_size = 12

        # 将其他子图放在第二行
        other_plots = [p for p in self.axes_list if p != self.current_axes]
        for i, other_plot in enumerate(other_plots):
            self.addItem(other_plot, row=1, col=i)
            other_plot.rmse_size = 6

        for col, factor in enumerate([3, 1]):
            self.ci.layout.setRowStretchFactor(col, factor)

    @utils.timeit
    def plot_nep_result(self):
        """
        画图函数 每次数据变动（删除、撤销等）均通过此函数重新绘图
        """
        self.nep_result_data.select_index.clear()

        for index, _dataset in enumerate(self.nep_result_data.datasets):
            plot = self.axes_list[index]
            plot.title = _dataset.title
            pg_size = Config.getint("widget", "pg_marker_size", 7) or 7
            plot.scatter(_dataset.x, _dataset.y, data=_dataset.structure_index,
                         brush=Brushes.get(_dataset.title.upper()), pen=Pens.get(_dataset.title.upper()),
                         symbol='o', size=pg_size,

                         )
            # 设置视图框更新模式
            self.auto_range(plot)
            if _dataset.group_array.num != 0:
                # 更新结构
                if self.structure_index not in _dataset.group_array.now_data:
                    self.structure_index = _dataset.group_array.now_data[0]
                    self.structureIndexChanged.emit(self.structure_index)

            else:
                plot.set_current_point([], [])

            if _dataset.title not in ["descriptor"]:
                #
                pos = self.convert_pos(plot, (0, 1))
                text = f"rmse: {_dataset.get_formart_rmse()}"
                plot.text.setText(text)
                plot.text.setPos(*pos)

    def plot_current_point(self, structure_index):
        """
        鼠标点击后 在所有子图上绘制五角星标记当前点
        """
        self.structure_index = structure_index

        for plot in self.axes_list:
            dataset = self.get_axes_dataset(plot)
            array_index = dataset.convert_index(structure_index)
            if dataset.is_visible(array_index) :

                data=dataset.all_data[array_index,: ]
                plot.set_current_point(data[:,dataset.x_cols].flatten(),
                                       data[:, dataset.y_cols].flatten(),
                                       )
            else:
                plot.set_current_point([], [])
    def item_clicked(self, scatter_item, items, event):

        if items.any():
            item = items[0]

            self.structureIndexChanged.emit(item.data())

    def select_point_from_polygon(self, polygon_xy, reverse):

        index = self.is_point_in_polygon(
            np.column_stack([self.current_axes._scatter.data["x"], self.current_axes._scatter.data["y"]]), polygon_xy)
        index = np.where(index)[0]
        select_index = self.current_axes._scatter.data[index]["data"].tolist()
        self.select_index(select_index, reverse)

    def select_point(self, pos, reverse):
        """
        鼠标单击选择结构
        """
        items = self.current_axes._scatter.pointsAt(pos)
        if len(items):
            item = items[0]
            index = item.index()
            structure_index = item.data()
            self.select_index(structure_index, reverse)
    @utils.timeit
    def update_scatter_color(self, structure_index, color=Brushes.Selected):
        """
        当结构点的状态发生变化的时候 通过该函数更改axes中散点的颜色
        """

        for i, plot in enumerate(self.axes_list):

            if not plot._scatter:
                continue
            structure_index_set = set(structure_index)
            index_list = [i for i, val in enumerate(plot._scatter.data["data"]) if val in structure_index_set]

            plot._scatter.data["brush"][index_list] = color
            plot._scatter.data['sourceRect'][index_list] = (0, 0, 0, 0)

            plot._scatter.updateSpots()

    def convert_pos(self, plot, pos):
        view_range = plot.viewRange()
        x_range = view_range[0]  # x轴范围 [xmin, xmax]
        y_range = view_range[1]  # y轴范围 [ymin, ymax]

        # 将百分比位置转换为坐标
        x_percent = pos[0]  # 50% 对应 x 轴中间
        y_percent = pos[1]  # 20% 对应 y 轴上的某个位置

        x_pos = x_range[0] + x_percent * (x_range[1] - x_range[0])  # 根据百分比计算实际位置
        y_pos = y_range[0] + y_percent * (y_range[1] - y_range[0])  # 根据百分比计算实际位置
        return x_pos, y_pos

    def auto_range(self, plot=None):

        if plot is None:
            plot = self.current_axes
        if plot:

            view = plot.getViewBox()

            x_range = [10000, -10000]
            y_range = [10000, -10000]
            for item in view.addedItems:
                if isinstance(item, ScatterPlotItem):

                    x = item.data["x"]
                    y = item.data["y"]

                    x = x[x > -10000]
                    y = y[y > -10000]
                    if x.size == 0:
                        x_range = [0, 1]
                        y_range = [0, 1]
                        continue
                    x_min = np.min(x)
                    x_max = np.max(x)
                    y_min = np.min(y)
                    y_max = np.max(y)
                    if x_min < x_range[0]:
                        x_range[0] = x_min
                    if x_max > x_range[1]:
                        x_range[1] = x_max
                    if y_min < y_range[0]:
                        y_range[0] = y_min
                    if y_max > y_range[1]:
                        y_range[1] = y_max
            if plot.title != "descriptor":

                real_range = (min(x_range[0], y_range[0]), max(x_range[1], y_range[1]))
                view.setRange(xRange=real_range, yRange=real_range)
            else:
                view.setRange(xRange=x_range, yRange=y_range)

    def pan(self, checked):

        if self.current_axes:
            self.current_axes.setMouseEnabled(checked, checked)
            self.current_axes.getViewBox().setMouseMode(ViewBox.PanMode)

    def pen(self, checked):
        if self.current_axes is None:
            return False

        if checked:
            self.draw_mode = True
            # 初始化鼠标状态和轨迹数据
            self.is_drawing = False
            self.x_data = []
            self.y_data = []

        else:
            self.draw_mode = False
            pass

    #
    def mousePressEvent(self, event):
        if not self.draw_mode:
            return super().mousePressEvent(event)

        if event.button() == Qt.MouseButton.LeftButton or event.button() == Qt.MouseButton.RightButton:
            self.is_drawing = True
            self.x_data.clear()  # 清空之前的轨迹数据
            self.y_data.clear()  # 清空之前的轨迹数据
            self.curve = self.current_axes.plot([], [], pen='r')

            self.curve.setData([], [])  # 清空绘制线条，避免对角线

    def mouseReleaseEvent(self, event):

        if not self.draw_mode:
            return super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton or event.button() == Qt.MouseButton.RightButton:
            self.is_drawing = False
            reverse = event.button() == Qt.MouseButton.RightButton
            self.current_axes.removeItem(self.curve)
            # 创建鼠标轨迹的多边形
            if len(self.x_data) > 2:

                self.select_point_from_polygon(np.column_stack((self.x_data, self.y_data)), reverse)
            else:
                # 右键的话  选中单个点
                pass
                pos = event.pos()
                mouse_point = self.current_axes.getViewBox().mapSceneToView(pos)

                x = mouse_point.x()
                self.select_point(mouse_point, reverse)
            return

    def mouseMoveEvent(self, event):
        if not self.draw_mode:
            return super().mouseMoveEvent(event)

        if self.is_drawing:
            pos = event.pos()
            if self.current_axes.sceneBoundingRect().contains(pos):
                # 将场景坐标转换为视图坐标
                mouse_point = self.current_axes.getViewBox().mapSceneToView(pos)
                x, y = mouse_point.x(), mouse_point.y()
                # 记录轨迹数据
                self.x_data.append(x)
                self.y_data.append(y)

                # 更新绘图
                self.curve.setData(self.x_data, self.y_data)
