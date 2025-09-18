from PyQt5.QtWidgets import QMessageBox

from orangewidget.settings import Setting
from orangewidget import gui
from oasys.widgets import gui as oasysgui

from orangecontrib.xrt.widgets.gui.ow_optical_element import OWOpticalElement
from orangecontrib.xrt.util.xrt_data import XRTData

class OWScreen(OWOpticalElement):

    name = "Screen"
    description = "XRT: Screen"
    icon = "icons/screen.png"
    priority = 4

    oe_name = Setting("my_screen")
    center = Setting("[0,0,0]")

    def __init__(self):
        super().__init__(show_plot_box=True)

    def populate_tab_setting(self):
        oasysgui.lineEdit(self.tab_bas, self, "oe_name", "O.E. Name", labelWidth=150, valueType=str, orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "center", "center: ",
                          labelWidth=150,
                          valueType=str,
                          orientation="horizontal")

    def draw_specific_box(self):
        pass

    def check_data(self):
        pass

    def xrtcode_parameters(self):
        if " " in self.oe_name:
            QMessageBox.critical(self, "Error", "component names cannot have blanks: %s" % self.oe_name, QMessageBox.Ok)

        return {
            "class_name":"Screen",
            "use_for_plot": self.use_for_plot,
            "limits_for_plot": self.limits_for_plot,
            "name":self.oe_name,
            "center":self.center,
                }

    def get_xrt_code(self):
        return self.xrtcode_template().format_map(self.xrtcode_parameters())

    def xrtcode_template(self):
        return \
"""
from xrt.backends.raycing.screens import Screen
bl.{name} = Screen(
    bl,
    name="{name}",
    center={center},
    )
"""

    def send_data(self):
        try:
            self.check_data()
            if self.xrt_data is None:
                out_xrt_data = XRTData("", {})
            else:
                out_xrt_data = self.xrt_data.duplicate()

            out_xrt_data.append(self.get_xrt_code(), self.xrtcode_parameters())

            self.send("XRTData", out_xrt_data)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e.args[0]), QMessageBox.Ok)

            self.setStatusMessage("")
            self.progressBarFinished()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    a = QApplication(sys.argv)
    ow = OWScreen()
    ow.show()
    a.exec_()


