from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
import pysnmp
import os
import threading
import time
from socket import *
from netaddr import *
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.hlapi import  getCmd


redes_global = []
# Definindo a Janela
app = QApplication(sys.argv)
janelaApp = QWidget()
janelaApp.setWindowTitle("BlackNight   UNIRN - BSI  Turma 2014")
janelaApp.setGeometry(200, 200, 820, 620)





# Entrada de Dados
inputIP = QLineEdit()
inputMask = QLineEdit()
inputIPAlvo = QLineEdit()



# Botoes
bntSRede = QPushButton("Calcular Redes")
bntAlvo = QPushButton("Alvo")
bntSRede.setFixedWidth(150)
bntAlvo.setFixedWidth(150)




# Saida de dados
txtDisplay = QTextEdit()
txtDisplay.setFixedHeight(600)
txtDisplay.setFixedWidth(800)
txtDisplay.setStyleSheet("QTextEdit {background-color:black;color:white}")






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
  vbox1.addWidget(inputIPAlvo)
  vbox1.addWidget(bntAlvo)
  vbox1.addStretch()

  # Saida
  vbox2.addWidget(QLabel("Saida do Processamento:"))


  vbox2.addWidget(txtDisplay)
  vbox2.addStretch()

  hbox.addLayout(vbox1)
  hbox.addLayout(vbox2)

  janelaApp.setLayout(hbox)
  janelaApp.show()


def check_online(host):
  resposta = os.system('ping -n 1 {}'.format(host))
  time.sleep(1)

  if resposta == 0:
    pingstatus = "<span style='color:#80ff00;font-weight:bold'>Ativo  ;)</span>"
    # txtDisplay.append("Host --> %s  %s " % (host, pingstatus))

  else:
    pingstatus = "<span style='color:#ff0000;font-weight:bold'>Inativo  :(</span>"
    # txtDisplay.append("Host --> %s  %s " % (host, pingstatus))


def escrever(redes):
  txtDisplay.clear()

  redes_global = redes

  TAMANHO = redes.size

  txtDisplay.append("<span style='color:#00FFFF;font-weight:bold'>Informações</span>")
  txtDisplay.append("<span style='color:red;font-weight:lighter'>===============</span>")
  txtDisplay.append(
    "<span style='color:yellow'>Mascara da Rede:</span><span style='color:white;font-weight:bold'> %s</span>" % redes.netmask)
  txtDisplay.append(
    "<span style='color:yellow'>Numero de Hosts:</span><span style='color:white;font-weight:bold'> %s</span>" % TAMANHO)
  txtDisplay.append(
    "<span style='color:yellow'>Faixa de IP:</span><span style='color:white;font-weight:bold'>  %s <span style='color:yellow'> até </span>   %s </span>" % (
      redes[1], redes[redes.__len__() - 2]))
  txtDisplay.append(
    "<span style='color:yellow'>Broadcast: </span><span style='color:white;font-weight:bold'>  %s " % redes[
      redes.__len__() - 1])

  txtDisplay.append("<span style='color:#00FFFF;font-weight:bold'>:: Maquinas Online ::</span>")
  txtDisplay.append("<span style='color:red;font-weight:lighter'>===============</span>")
  threads = []
  for ip in redes_global:
    t = threading.Thread(target=check_online, args=(ip,))
    threads.append(t)
    t.start()



def obterRedes():
  calcularRedes(inputIP.text(),inputMask.text())




def getDescHost():
  txtDisplay.clear()




  txtDisplay.append("<span style='color:#00FFFF;font-weight:bold'>Informação do Host</span>")

  alvoTexto = inputIPAlvo.text()
  alvo = alvoTexto[:15]
  cmdGen = cmdgen.CommandGenerator()

  errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
    cmdgen.CommunityData('public', mpModel=0),
    cmdgen.UdpTransportTarget((alvo, 161)),
    cmdgen.MibVariable('iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0'),
    cmdgen.MibVariable('SNMPv2-MIB', 'sysDescr', 0)
  )



  # Check for errors and print out results
  if errorIndication:
    txtDisplay.append(str(errorIndication))

  else:
    if errorStatus:

      txtDisplay.append('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1] or '?'))


    else:
      for nome, val in varBinds:
        txtDisplay.append('%s = %s' % (nome.prettyPrint(), val.prettyPrint()))





def calcularRedes(ipRede, maskRede):

    netaddr = ipRede[:15]  # endereço IP de rede
    netmask = maskRede.strip('/')[:15]  # máscara /24 ou 255.255.255.0

    redes = IPNetwork(netaddr + '/' + netmask)
    escrever(redes)



if __name__ == '__main__':

  startJanela()

  # Comandos
  bntSRede.clicked.connect(obterRedes)
  bntAlvo.clicked.connect(getDescHost)

  sys.exit(app.exec_())
