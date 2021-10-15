# PicorderOS Wifi Module Proto
print("Loading Modulated EM Network Analysis")

from wifi import Cell, Scheme



class Wifi_Scan(object):

    def __init__(self):
        pass

    def update(self):
        ap_list = list(Cell.all('wlan0'))
        return ap_list

    def get_info(self,selection):
        ap_list = self.update()

        if selection <= (len(ap_list)-1):
            return (ap_list[selection].ssid, ap_list[selection].signal, ap_list[selection].quality, ap_list[selection].frequency, ap_list[selection].bitrates, ap_list[selection].encrypted, ap_list[selection].channel, ap_list[selection].address, ap_list[selection].mode)

    def get_ssid_list(self):

        title_list = []

        ap_list = self.get_list()
        for ap in ap_list:
            name = ap.ssid
            title_list.append(name)

        return title_list

    def get_list(self):
        return self.update()


class BT_Scan(object):

    def __init__(self):
        pass
