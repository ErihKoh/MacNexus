"""Діаграма використання дискового простору директоріями."""

from pathlib import Path

from PySide6.QtCharts import (
    QBarCategoryAxis,
    QBarSet,
    QChart,
    QChartView,
    QHorizontalBarSeries,
    QValueAxis,
)
from PySide6.QtCore import QMargins, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QVBoxLayout, QWidget
from src.models.directory_entry import DirectoryEntry


class DirectoryUsageChart(QWidget):
    """Відображає десять найбільших директорій."""

    LIMIT = 10

    def __init__(self) -> None:
        super().__init__()

        self._chart = QChart()
        self._chart.setTitle("Top 10 найбільших директорій")
        self._chart.legend().hide()
        self._chart.setAnimationOptions(QChart.AnimationOption.NoAnimation)
        self._chart.setMargins(QMargins(12, 12, 12, 12))

        self._category_axis: QBarCategoryAxis | None = None
        self._value_axis: QValueAxis | None = None

        self._chart_view = QChartView(self._chart)
        self._chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._chart_view)

        self.setMinimumHeight(360)
        self._theme = "dark"
        self.apply_theme()

    def set_data(
        self,
        entries: list[DirectoryEntry],
        total_size: int,
        root: Path,
    ) -> None:
        """Оновлює діаграму за результатами сканування."""

        self._chart.removeAllSeries()

        for axis in self._chart.axes():
            self._chart.removeAxis(axis)

        self._category_axis = None
        self._value_axis = None

        candidates = [entry for entry in entries if entry.path != root and entry.size > 0]

        top_entries = sorted(
            candidates,
            key=lambda entry: entry.size,
            reverse=True,
        )[: self.LIMIT]

        if not top_entries:
            self._chart.setTitle("Немає даних для відображення")
            self.apply_theme()
            return

        bar_set = QBarSet("Розмір")
        categories = []

        for entry in top_entries:
            size_mib = entry.size / (1024 * 1024)
            bar_set.append(size_mib)

            try:
                relative_path = entry.path.relative_to(root)
            except ValueError:
                relative_path = entry.path

            categories.append(relative_path.as_posix())

        series = QHorizontalBarSeries()
        series.append(bar_set)
        series.setLabelsVisible(False)

        self._chart.addSeries(series)

        self._category_axis = QBarCategoryAxis()
        self._category_axis.append(categories)

        self._value_axis = QValueAxis()
        self._value_axis.setTitleText("Розмір (MiB)")
        self._value_axis.setLabelFormat("%.0f")

        self._chart.addAxis(
            self._category_axis,
            Qt.AlignmentFlag.AlignLeft,
        )
        self._chart.addAxis(
            self._value_axis,
            Qt.AlignmentFlag.AlignBottom,
        )

        series.attachAxis(self._category_axis)
        series.attachAxis(self._value_axis)

        self._chart.setTitle("Top 10 найбільших директорій")
        self.apply_theme()

    def set_theme(self, theme: str) -> None:
        """Встановлює кольори діаграми відповідно до теми застосунку."""

        self._theme = theme
        self.apply_theme()

    def apply_theme(self) -> None:
        """Застосовує кольори активної теми до всіх елементів діаграми."""

        themes = {
            "dark": {
                "background": "#20232a",
                "text": "#e4e7ed",
                "grid": "#343945",
                "bar": "#5b9cff",
            },
            "light": {
                "background": "#ffffff",
                "text": "#252a34",
                "grid": "#e1e5eb",
                "bar": "#3478d4",
            },
        }

        colors = themes[self._theme]

        background = QColor(colors["background"])
        text = QColor(colors["text"])
        grid = QColor(colors["grid"])
        bar_color = QColor(colors["bar"])

        self._chart.setBackgroundBrush(background)
        self._chart.setTitleBrush(text)
        self._chart.setPlotAreaBackgroundBrush(background)
        self._chart.setPlotAreaBackgroundVisible(True)

        self._chart_view.setBackgroundBrush(background)

        if self._category_axis is not None:
            self._category_axis.setLabelsBrush(text)
            self._category_axis.setTitleBrush(text)
            self._category_axis.setLinePen(QPen(grid))

        if self._value_axis is not None:
            self._value_axis.setLabelsBrush(text)
            self._value_axis.setTitleBrush(text)
            self._value_axis.setLinePen(QPen(grid))
            self._value_axis.setGridLinePen(QPen(grid))

        for series in self._chart.series():
            for bar_set in series.barSets():
                bar_set.setColor(bar_color)
