# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction contributors <https://github.com/easyscience/diffraction>
# SPDX-License-Identifier: BSD-3-Clause

import asciichartpy

from easydiffraction.plotting.plotters.plotter_base import DEFAULT_HEIGHT
from easydiffraction.plotting.plotters.plotter_base import SERIES_CONFIG
from easydiffraction.plotting.plotters.plotter_base import PlotterBase
from easydiffraction.utils.formatting import paragraph

DEFAULT_COLORS = {
    'meas': asciichartpy.blue,
    'calc': asciichartpy.red,
    'resid': asciichartpy.green,
}


class AsciiPlotter(PlotterBase):
    def _get_legend_item(self, label):
        color_start = DEFAULT_COLORS[label]
        color_end = asciichartpy.reset
        line = '────'
        name = SERIES_CONFIG[label]['name']
        item = f'{color_start}{line}{color_end} {name}'
        return item

    def plot(
        self,
        x,
        y_series,
        labels,
        axes_labels,
        title,
        height=None,
    ):
        # Intentionally unused; kept for a consistent plotting API
        del axes_labels
        title = paragraph(title)
        legend = '\n'.join([self._get_legend_item(label) for label in labels])

        if height is None:
            height = DEFAULT_HEIGHT
        colors = [DEFAULT_COLORS[label] for label in labels]
        config = {'height': height, 'colors': colors}
        y_series = [y.tolist() for y in y_series]

        chart = asciichartpy.plot(y_series, config)

        print(f'{title}')
        print(f'Displaying data for selected x-range from {x[0]} to {x[-1]} ({len(x)} points)')
        print(f'Legend:\n{legend}')
        print(chart)
