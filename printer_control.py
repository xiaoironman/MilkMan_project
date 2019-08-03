from escpos.printer import Usb

""" Seiko Epson Corp. Receipt Printer M129 Definitions (EPSON TM-T88IV) """
p = Usb(0x04b8,0x0E15,0)
p.text("Hello World\n")
p.barcode('1324354657687','EAN13',64,2,'','')
p.cut()