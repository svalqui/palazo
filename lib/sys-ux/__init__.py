import configparser as confp
import sys


class ConfFile():
    def __init__(self, conf_file=''):
        self.conf_received = conf_file
        self.conf_current = ''

    def read(self):
        self.conf_current = confp.ConfigParser()
        self.conf_current.read(self.conf_received)

    def show(self):
        self.read()
        for stanza in self.conf_current.sections():
            print('Stanza: ', stanza)
            for entry in self.conf_current.items(stanza):
                print('  Entry :', entry)

if __name__ == '__main__':
    ConfFile.show(sys.argv[1])
