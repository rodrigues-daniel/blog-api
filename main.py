from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
from pysnmp import *
from socket import *
from netaddr import *



# Definindo a Janela
app = QApplication(sys.argv)
janelaApp = QWidget()
janelaApp.setWindowTitle("BlackNight   UNIRN - BSI  Turma 2014")
janelaApp.setGeometry(200, 200, 820, 620)





# Entrada de Dados
inputIP = QLineEdit()
inputMask = QLineEdit()


# Botoes
bntSRede = QPushButton("Calcular Redes")
bntSRede.setFixedWidth(150)


# Saida de dados
txtDisplay = QTextEdit()
txtDisplay.setFixedHeight(600)
txtDisplay.setFixedWidth(800)
txtDisplay.setStyleSheet("QTextEdit {background-color:black;color:white}")








def escrever(redes):



    TAMANHO = redes.size

    txtDisplay.append("<span style='color:#00FFFF;font-weight:bold'>Informações</span>")
    txtDisplay.append("<span style='color:red;font-weight:lighter'>===============</span>")
    txtDisplay.append("<span style='color:yellow'>Numero de Redes:</span><span style='color:white;font-weight:bold'> %s</span>" % TAMANHO)


    proximo_char = 0x00


    for rede in redes:

      txtDisplay.append("95")










def startJanela():
  # Formatando e  Organizando layout

  hbox = QHBoxLayout()
  vbox1 = QVBoxLayout()
  vbox2 = QVBoxLayout()

  vbox1.addWidget(QLabel("Infome o IP de Rede:"))
  vbox1.addWidget(inputIP)
  vbox1.addWidget(QLabel("Mascara de Rede:"))
  vbox1.addWidget(inputMask)
  vbox1.addWidget(bntSRede)
  vbox1.addStretch()

  # Saida
  vbox2.addWidget(QLabel("Saida do Processamento:"))


  vbox2.addWidget(txtDisplay)
  vbox2.addStretch()

  hbox.addLayout(vbox1)
  hbox.addLayout(vbox2)

  janelaApp.setLayout(hbox)


  janelaApp.show()
  sys.exit(app.exec_())


def obterRedes():
  calcularRedes(inputIP.text(),inputMask.text())



# Comandos
bntSRede.clicked.connect(obterRedes)




def calcularRedes(ipRede, maskRede):

    netaddr = ipRede[:15]  # endereço IP de rede
    netmask = maskRede.strip('/')[:15]  # máscara /24 ou 255.255.255.0

    redes = IPNetwork(netaddr + '/' + netmask)

    escrever(redes)



if __name__ == '__main__':
  startJanela()
