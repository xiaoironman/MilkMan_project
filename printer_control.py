# from escpos.printer import Usb

""" Seiko Epson Corp. Receipt Printer M129 Definitions (EPSON TM-T88IV) """
import base64
import datetime
import string
import random

import base64
from Crypto.Cipher import AES


class EncryptData:
    def __init__(self, key):
        self.key = key  #initialization key
        self.length = AES.block_size  #Initialize the block size
        self.aes = AES.new(self.key, AES.MODE_ECB)  #Initialize AES, an instance of ECB mode
        # Truncate function to remove padded characters
        self.unpad = lambda date: date[0:-ord(date[-1])]

    def pad(self, text):
        """
        Fill the function so that the bytecode length of the encrypted data is an integer multiple of block_size
        """
        count = len(text.encode('utf-8'))
        add = self.length - (count % self.length)
        entext = text + ('0' * add)
        return entext

    def encrypt(self, encrData): #encryption function
        res = self.aes.encrypt(self.pad(encrData).encode("utf-8"))
        msg = str(base64.b64encode(res), encoding="utf-8")
        return msg

    def decrypt(self, decrData): #decryption function
        res = base64.decodebytes(decrData.encode("utf8"))
        msg = self.aes.decrypt(res).decode("utf8")
        return self.unpad(msg)


def printer_print(code):
    from escpos.printer import Usb
    p = Usb(int(get_printer_id()[0], 16),int(get_printer_id()[1], 16), 0)
    if p.paper_status() == 2:
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
    import platform
    if platform.platform()[0] == 'W':
        return get_printer_id_windows()
    elif platform.platform()[0] == 'L':
        return get_printer_id_linux()
    else:
        return '', ''


def read_weight_log(input: str):
    with open(input) as input_f:
        data = input_f.readline().split('"')
    output = dict()
    data_time = data[1::2]
    data_weight = data[2::2]
    time, weight, unit = [], [], []
    format = '%Y-%m-%d %I:%M:%S %p'
    for i, t in enumerate(data_time):
        time.append(datetime.datetime.strptime(t, format))
        weight.append(float(bytearray.fromhex(data_weight[i][9:-10]).decode()))
        unit.append(bytearray.fromhex(data_weight[i][-10:-6]).decode())

    return time, weight, unit


def gen_code(string_length):
    """Generate a random string with the combination of lowercase and uppercase letters """
    letters = string.ascii_letters + string.digits
    return 'M' + ''.join(random.choice(letters) for i in range(string_length - 2)) + 'K'


def encrypt(code: str):
    pass


def gen_qr(input: str, num_code: int):
    import qrcode
    img = qrcode.make(input)
    qr_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S_") + str(num_code) + '.png'
    img.save(qr_name)
    return qr_name


def json_format(text_list: list) -> str:
    text = ''
    for i in text_list:
        text += i + ';'
    return '{{\n\t\"recycle_codes\": [\n\t\"{}\"\n\t]\n}}'.format(text)


def gen_qr_main(key: str, num_of_code: int, code_length: int = 15):
    res = []
    key = key.encode('utf-8')
    eg = EncryptData(key)
    for i in range(num_of_code):
        res.append(eg.encrypt(gen_code(code_length)))
    qr_name = gen_qr(json_format(res), num_of_code)
    return qr_name


if __name__ == '__main__':

    qr_name = gen_qr_main('ASDFasdmseriq234', 3)
    print(qr_name, ' has been generated!')
