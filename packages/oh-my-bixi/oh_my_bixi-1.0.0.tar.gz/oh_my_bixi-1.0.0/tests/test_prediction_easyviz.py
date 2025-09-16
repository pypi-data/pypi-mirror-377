import unittest

import numpy as np

from bixi.prediction.easyviz import *


class TestSinglePanel(unittest.TestCase):
    def test_uniform_1x1(self):
        H, W = 128, 128
        p = Panel(
            ImageVItem(np.random.rand(H, W), 'gray')
        )
        fig = p.to_matplotlib_figure()
        fig.show()
        plt.close(fig)

    def test_uniform_1x2(self):
        H, W = 128, 128
        vitem = ImageVItem(np.random.rand(H, W), 'gray')
        p = Panel(
            vitem, vitem,
            ncols=2
        )
        fig = p.to_matplotlib_figure()
        fig.show()
        plt.close(fig)

    def test_uniform_2x2(self):
        H, W = 128, 128
        vitem = ImageVItem(np.random.rand(H, W), 'gray', title='Item')
        p = Panel(
            vitem, vitem, vitem, vitem,
            ncols=2, hspace=0.0, wspace=0.01,
        )
        fig = p.to_matplotlib_figure(left=0.25)
        fig.show()
        plt.close(fig)

    def test_nonuniform_2x3(self):
        H, W = 128, 128
        vitem_1x1 = ImageVItem(np.random.rand(H, W), 'gray', title='Span 1x1')
        vitem_2x1 = ImageVItem(np.random.rand(2 * H, W), 'viridis', span=(2, 1), title='Span 2x1')
        p = Panel(
            vitem_1x1, vitem_1x1, vitem_2x1,
            ncols=3
        )
        fig = p.to_matplotlib_figure()
        fig.show()
        plt.close(fig)

    def test_nonuniform_4x3(self):
        H, W = 128, 128
        vitem_1x1 = ImageVItem(np.random.rand(H, W), 'gray', title='Span 1x1')
        vitem_1x1_at01 = ImageVItem(np.random.rand(H, W), 'Blues', location=(0, 1), title='Span 1x1 at (0, 1)')
        vitem_2x1 = ImageVItem(np.random.rand(2 * H, W), 'viridis', span=(2, 1), title='Span 2x1')
        vitem_1x3 = ImageVItem(np.random.rand(H, 3 * W), 'jet', span=(1, 3), title='Span 1x3')
        p = Panel(
            vitem_1x1_at01, vitem_1x1, vitem_1x1, vitem_1x1, vitem_2x1, vitem_1x1, vitem_1x3,
            ncols=3
        )
        fig = p.to_matplotlib_figure()
        fig.show()
        plt.close(fig)


class TestDoublePanels(unittest.TestCase):
    def test_horizontal_panels(self):
        H, W = 8, 8
        p = Panel(
            Panel(
                ImageVItem(np.random.rand(H, W), 'gray'),
                ImageVItem(np.random.rand(H, W), 'gray'),
                ImageVItem(np.random.rand(H, W), 'gray'),
                ncols=2, title="Panel 1: 2x2"
            ),
            Panel(
                ImageVItem(np.random.rand(H, W), 'gray'),
                ImageVItem(np.random.rand(H, W), 'gray'),
                ImageVItem(np.random.rand(H, W), 'gray'),
                ncols=1, title="Panel 2: 3x1"
            ),
            ncols=3, title="Root Panel"
        )
        fig = p.to_matplotlib_figure()
        fig.show()
        plt.close(fig)

    def test_vertical_panels(self):
        H, W = 8, 8
        p = Panel(
            Panel(
                ImageVItem(np.random.rand(H, W), 'gray'),
                ImageVItem(np.random.rand(H, W), 'gray'),
                ImageVItem(np.random.rand(H, W), 'gray'),
                ncols=2, title="Panel 1: 2x2"
            ),
            Panel(
                ImageVItem(np.random.rand(H, W), 'gray'),
                ImageVItem(np.random.rand(H, W), 'gray'),
                ImageVItem(np.random.rand(H, W), 'gray'),
                ncols=1, title="Panel 2: 3x1"
            ),
            ncols=2, title="Root Panel"
        )
        fig = p.to_matplotlib_figure()
        fig.show()
        plt.close(fig)

    def test_nonuniform_vertical_panels(self):
        H, W = 8, 8
        p = Panel(
            Panel(
                ImageVItem(np.random.rand(H, W), 'gray'),
                ImageVItem(np.random.rand(H, W), 'gray'),
                ImageVItem(np.random.rand(H, W), 'gray'),
                ncols=2, title="Panel 1: 2x2", span=(1, 1)
            ),
            Panel(
                ImageVItem(np.random.rand(H, W), 'gray'),
                ImageVItem(np.random.rand(H, W), 'gray'),
                ImageVItem(np.random.rand(H, W), 'gray'),
                ncols=1, title="Panel 2: 3x1", span=(2, 2)
            ),
            ncols=2, title="Root Panel"
        )
        fig = p.to_matplotlib_figure()
        fig.show()
        plt.close(fig)

    def test_nested_panels(self):
        H, W = 8, 8
        p = Panel(
            Panel(
                Panel(
                    ImageVItem(np.random.rand(H, W), 'gray'),
                    ImageVItem(np.random.rand(H, W), 'gray'),
                    ImageVItem(np.random.rand(H, W), 'gray'),
                    ncols=2, title="Panel Inside: 2x2", span=(1, 1)
                ), title="Panel Outside: 1x1"
            ), title="Root Panel"
        )
        fig = p.to_matplotlib_figure(inch_per_unit=5)
        fig.show()
        plt.close(fig)


class TestComplexHierarchy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        H, W = 16, 16
        cls.p1 = Panel(
            ImageVItem(np.random.rand(H, W), 'gray'),
            ImageVItem(np.random.rand(H, W), 'gray'),
            ImageVItem(np.random.rand(H, W), 'gray'),
            ImageVItem(np.random.rand(H, W), 'gray', title='subplot A.4'),
            ncols=2, title="Panel A) 2x2 Grid, 1x1 Span", span=(1, 1)
        )

        xs = np.linspace(-1, 1, 100)
        ys_sin = np.sin(xs)
        ys_cos = np.cos(xs)
        cls.p2 = Panel(
            LambdaVItem(lambda ax: ax.plot(xs, ys_sin), title="Sine", location=(1, 0)),
            LambdaVItem(lambda ax: ax.plot(xs, ys_cos), title="Cosine", location=(0, 0)),
            ncols=1, title="Panel B) 2x1 Grid, 1x1 Span", span=(1, 1)
        )

        cls.p3 = Panel(
            ImageOverlayVItem(
                np.random.rand(H, W), np.random.rand(H, W), alpha=0.5, title="Heatmap"
            ), title="Panel C) 1x1 Grid, 1x1 Span", span=(1, 1)
        )

    def test_left2x2_middle2x1_right_1x1(self):
        p = Panel(
            self.p1, self.p2, self.p3,
            ncols=3, title="Root Panel"
        )

        fig = p.to_matplotlib_figure(inch_per_unit=5)
        fig.show()
        plt.close(fig)

    def test_hstack(self):
        p = Panel.hstack(
            self.p1, self.p2, self.p3,
            title="Root hstacked Panel"
        )

        fig = p.to_matplotlib_figure(inch_per_unit=5)
        fig.show()
        plt.close(fig)

    def test_vstack(self):
        p = Panel.vstack(
            self.p1, self.p2, self.p3,
            title="Root vstacked Panel"
        )

        fig = p.to_matplotlib_figure(inch_per_unit=5)
        fig.show()
        plt.close(fig)
