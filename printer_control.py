# from escpos.printer import Usb
import sys
import platform
from escpos.printer import Usb

""" Seiko Epson Corp. Receipt Printer M129 Definitions (EPSON TM-T88IV) """


def printer_print(code):
    p = Usb(int(get_printer_id()[0], 16),int(get_printer_id()[1], 16), 0)
    if p.paper_status() == 0:
        text = 'Discount Code:\n\t{}\n'.format(code)
        p.text(text)
        p.barcode('1234567898765', 'EAN13', 64, 2, '', '')
        p.cut()
    elif p.paper_status() == 1:
        print('Paper running out soon!')
        # TODO: inform the manager immediately about the paper issue
        pass
    else:
        # TODO: show warning on screen that the machine is temporarily not able to print out barcode for non-app user,
        #  app users can still scan the barcode on the screen to obtain the voucher code
        pass


def get_printer_id_windows():
    import win32com.client
    vendor_id = ''
    product_id = ''
    wmi = win32com.client.GetObject("winmgmts:")
    for usb in wmi.InstancesOf("Win32_USBHub"):
        if 'Printing' in usb.Description:
            ids = usb.DeviceID.split("\\")[1].split("&")
            vendor_id = '0x' + ids[0][-4:]
            product_id = '0x' + ids[1][-4:]
    return vendor_id, product_id


def get_printer_id_linux():
    import re
    import subprocess
    vendor_id = ''
    product_id = ''
    device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
    df = subprocess.check_output("lsusb")
    print(df)
    for i in df.decode().split("\n"):
        if i:
            info = device_re.match(i)
            if info:
                dinfo = info.groupdict()
                if 'Epson' in dinfo['tag'] or 'Printing' in dinfo['tag']:
                    vendor_id = '0x' + dinfo['id'].split(":")[0]
                    product_id = '0x' + dinfo['id'].split(":")[1]
                    break
    return vendor_id, product_id


def get_printer_id():
    if platform.platform()[0] == 'W':
        return get_printer_id_windows()
    elif platform.platform()[0] == 'L':
        return get_printer_id_linux()
    else:
        return '', ''


if __name__ == '__main__':
    for a in sys.argv[1:]:
        printer_print(a)
