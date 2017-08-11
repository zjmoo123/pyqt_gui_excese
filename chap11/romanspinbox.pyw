from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import sys

def romanFromInt(integer):
    """
    Code taken from Raymond Hettinger's code in Victor Yang's "Decimal
    to Roman Numerals" recipe in the Python Cookbook.

    # >>> r = [romanFromInt(x) for x in range(1, 4000)]
    # >>> i = [intFromRoman(x) for x in r]
    # >>> i == [x for x in range(1, 4000)]
    True
    """
    coding = zip(
        [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1],
        ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V",
         "IV", "I"])
    if integer <= 0 or integer >= 4000 or int(integer) != integer:
        raise ValueError("expecting an integer between 1 and 3999")
    result = []
    for decimal, roman in coding:
        while integer >= decimal:
            result.append(roman)
            integer -= decimal
    return "".join(result)


def intFromRoman(roman):
    """
    Code taken from Paul Winkler's "Roman Numerals" recipe in the Python
    Cookbook.
    """
    roman = roman.upper()
    coding = (("M",  1000, 3), ("CM", 900, 1), ("D",  500, 1),
              ("CD", 400, 1), ("C",  100, 3), ("XC", 90, 1),
              ("L",  50, 1), ("XL", 40, 1), ("X",  10, 3),
              ("IX", 9, 1), ("V",  5, 1),  ("IV", 4, 1), ("I",  1, 3))
    integer, index = 0, 0
    for numeral, value, maxrepeat in coding:
        count = 0
        while roman[index: index +len(numeral)] == numeral:
            count += 1
            if count > maxrepeat:
                raise ValueError("not a valid roman number: {0}".format(
                        roman))
            integer += value
            index += len(numeral)
    if index != len(roman):
        raise ValueError("not a valid roman number: {0}".format(roman))
    return integer

class RomanSpinBox(QSpinBox):
    def __init__(self,parent=None):
        super(RomanSpinBox, self).__init__(parent)
        regex = QRegExp(r"^M?M?M?(?:CM|CD|D?C?C?C?)"
                        r"(?:XC|XL|L?X?X?X?)(?:IX|IV|V?I?I?I?)$")
        regex.setCaseSensitivity(Qt.CaseInsensitive)
        self.validator = QRegExpValidator(regex,self)
        self.setRange(1,3999)
        self.lineEdit().textEdited.connect(self.fixCase)

    def fixCase(self,text):
        self.lineEdit().setText(text.upper())

    def validate(self, p_str, p_int):
        return self.validator.validate(p_str,p_int)

    def valueFromText(self, p_str):
        return intFromRoman(p_str)

    def textFromValue(self, p_int):
        return romanFromInt(p_int)


def report(value):
    print("{0:4d} {1}".format(value, romanFromInt(value)))

app = QApplication(sys.argv)
spinbox = RomanSpinBox()
spinbox.show()
spinbox.setWindowTitle("Roman")
spinbox.valueChanged.connect(report)
app.exec_()