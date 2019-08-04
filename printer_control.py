from escpos.printer import Usb
import sys


""" Seiko Epson Corp. Receipt Printer M129 Definitions (EPSON TM-T88IV) """


def printer_print(code):
    p = Usb(0x04b8, 0x0E15, 0)
    text = 'Discount Code:\n\t{}\n'.format(code)
    p.text(text)
    p.barcode('1234567898765', 'EAN13', 64, 2, '', '')
    p.cut()


if __name__ == '__main__':
    print(sys.argv)
    for a in sys.argv[1:]:
        printer_print(a)
