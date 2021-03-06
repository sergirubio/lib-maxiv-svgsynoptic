from threading import Lock

from PyQt4 import QtCore


class JSInterface(QtCore.QObject):

    """
    Interface between python and a webview's javascript.

    All methods decorated with "pyqtSlot" on this class can be called
    from the JS side.
    """

    subscription = QtCore.pyqtSignal(str)
    rightclicked = QtCore.pyqtSignal(str, str)
    leftclicked = QtCore.pyqtSignal(str, str)
    hovered = QtCore.pyqtSignal(str, str)
    plugin_command = QtCore.pyqtSignal(str, str, str)
    tooltip = QtCore.pyqtSignal(str)
    evaljs = QtCore.pyqtSignal(str)
    lock = Lock()

    def __init__(self, frame, parent=None):
        self.frame = frame
        super(JSInterface, self).__init__(parent)
        self.evaljs.connect(self._evaluate_js)

    def evaluate(self, js):
        # This is probably totally unneccesary
        self.evaljs.emit(js)

    def _evaluate_js(self, js):
        with self.lock:
            self.frame.evaluateJavaScript(js)

    @QtCore.pyqtSlot(str, str)
    def left_click(self, section, models):
        self.leftclicked.emit(section, models)

    @QtCore.pyqtSlot(str, str)
    def right_click(self, section, models):
        self.rightclicked.emit(section, models)

    @QtCore.pyqtSlot(str, str)
    def hover(self, section, models):
        print "hover", section, models
        self.hovered.emit(section, models)

    @QtCore.pyqtSlot(str)
    def update_tooltip(self, model):
        self.tooltip.emit(model)

    @QtCore.pyqtSlot(str)
    def subscribe(self, devices):
        "Update the list of attributes to pay attention to"
        self.subscription.emit(devices)

    @QtCore.pyqtSlot(str)
    def subscribe_tooltip(self, models):
        self.tooltip.emit(models)

    @QtCore.pyqtSlot()
    def setup(self):
        pass

    @QtCore.pyqtSlot(str, str, str)
    def run_plugin_command(self, plugin, cmd, args):
        print "run_plugin_command", plugin, cmd, args
        # Note: since we're using signals to loosely connect with the widget
        # it's not possible to get a return value. But we probably don't
        # want that anyway since it might block..?
        self.plugin_command.emit(plugin, cmd, args)

    @QtCore.pyqtSlot(str)
    def load_svg(self, svg_file):
        "Load an SVG file into the synoptic"
        # Note: ideally the webview would be able to load the SVG
        # directly, but due to the fact that we want to be able to
        # load js and css assets from the svgsynoptic library path,
        # the basepath is set to there. That means that things in our
        # own directory aren't accessible :(
        with open(svg_file) as f:
            data = f.read()
            self.evaljs.emit(r"loadSVGString(%r);" % data)
