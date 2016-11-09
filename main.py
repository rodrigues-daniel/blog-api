from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
import pysnmp
import os
import threading
import subprocess
import time
from socket import *
from netaddr import *
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.hlapi import getCmd

app = QApplication(sys.argv)

class RedesThread(QThread):

  def __init__(self, parent=app):


      QThread.__init__(self, parent)

      self.signal =  SIGNAL("ops")




  def run(self):
    # time.sleep(2)
    print("in thread")
    self.emit(self.signal, "hi from HELL thread!")





class MainGui(QWidget):


  def __init__(self,pai = None):
      QWidget.__init__(self,pai)



      self.STATUS_ATIVO = False
      self.HOST_IP = None
      self.STATUS_FORMATO_ATIVO = " <span style='color:#80ff00;font-weight:bold'>Ativo  ;)</span>"
      self.STATUS_FORMATO_INATIVO = " <span style='color:#ff0000;font-weight:bold'>Inativo  :(</span>"





      redes_global = []
      # Definindo a Janela


      self.setWindowTitle("BlackNight   UNIRN - BSI  Turma 2014")
      self.setGeometry(200, 200, 820, 620)

      # Entrada de Dados
      self.inputIP = QLineEdit()
      self.inputMask = QLineEdit()
      self.inputIPAlvo = QLineEdit()

      # Botoes
      self.bntSRede = QPushButton("Calcular Rede")
      self.connect(self.bntSRede,SIGNAL("clicked()"),self.obterRedes)

      self.bntAlvo = QPushButton("Alvo")
      self.connect(self.bntAlvo,SIGNAL("clicked()"), self.appinit)






      self.bntSRede.setFixedWidth(150)
      self.bntAlvo.setFixedWidth(150)

      # Saida de dados
      self.txtDisplay = QTextEdit()
      self.txtDisplay.setFixedHeight(600)
      self.txtDisplay.setFixedWidth(800)
      self.txtDisplay.setStyleSheet("QTextEdit {background-color:black;color:white}")

      # Formatando e  Organizando layout

      hbox = QHBoxLayout()
      vbox1 = QVBoxLayout()
      vbox2 = QVBoxLayout()

      vbox1.addWidget(QLabel("Infome o IP de Rede:"))
      vbox1.addWidget(self.inputIP)
      vbox1.addWidget(QLabel("Mascara de Rede:"))
      vbox1.addWidget(self.inputMask)

      vbox1.addWidget(self.bntSRede)
      vbox1.addWidget(self.inputIPAlvo)
      vbox1.addWidget(self.bntAlvo)
      vbox1.addStretch()

      # Saida
      vbox2.addWidget(QLabel("Saida do Processamento:"))

      vbox2.addWidget(self.txtDisplay)
      vbox2.addStretch()

      hbox.addLayout(vbox1)
      hbox.addLayout(vbox2)

      self.setLayout(hbox)




  def appinit(self):
    self.thread = RedesThread()
    self.connect(self.thread, self.thread.signal, self.teste2)
    self.thread.start()



  def teste(self):
    print("inasdfasdfsfs")



  def teste2(self,texto):
    print("inasdfasdfsfs testes novamente")
    print(texto)






  def escrever(self,redes):
    self.txtDisplay.clear()

    TAMANHO = redes.size

    self.txtDisplay.append("<span style='color:#00FFFF;font-weight:bold'>Informações</span>")
    self.txtDisplay.append("<span style='color:red;font-weight:lighter'>===============</span>")
    self.txtDisplay.append(
      "<span style='color:yellow'>Mascara da Rede:</span><span style='color:white;font-weight:bold'> %s</span>" % redes.netmask)
    self.txtDisplay.append(
      "<span style='color:yellow'>Numero de Hosts:</span><span style='color:white;font-weight:bold'> %s</span>" % TAMANHO)
    self.txtDisplay.append(
      "<span style='color:yellow'>Faixa de IP:</span><span style='color:white;font-weight:bold'>  %s <span style='color:yellow'> até </span>   %s </span>" % (
        redes[1], redes[redes.__len__() - 2]))
    self.txtDisplay.append(
      "<span style='color:yellow'>Broadcast: </span><span style='color:white;font-weight:bold'>  %s " % redes[
        redes.__len__() - 1])

    self.txtDisplay.append("<span style='color:#00FFFF;font-weight:bold'>:: Maquinas Online ::</span>")
    self.txtDisplay.append(
      "<span style='color:red;font-weight:lighter'>=========================================================================</span>")


  def check_online(self,redes):
    for host_ip in redes:

      try:

        # resposta = subprocess.check_call(['ping', '-n', '1', '{}'.format(host_ip)], stderr=subprocess.DEVNULL,stdout=subprocess.DEVNULL)
        # universal_newlines = True

        resposta = ()

        if os.name == 'nt':

          resposta = subprocess.getstatusoutput('ping -n 1 %s' % host_ip)

        else:

          resposta = subprocess.getstatusoutput('ping -c 1 %s' % host_ip)

        texto = resposta[1]  # retirando resposta de uma tupla
        ltexto = texto.lower()
        posi_inacessivel = ltexto.find("inacess")  # Resposta para Destino inacessivel
        posi_tempo_esgotado = ltexto.find("esgotado")  # Resposta para Destino inacessivel
        inacessivel = ltexto[posi_inacessivel:posi_inacessivel + 7]
        tempo_esgotado = ltexto[posi_tempo_esgotado:posi_tempo_esgotado + 8]

        if inacessivel != 'inacess':

          if tempo_esgotado == 'esgotado':
            self.txtDisplay.append("Host Inativo --> %s  %s " % (host_ip, self.STATUS_FORMATO_INATIVO))
          else:
            self.txtDisplay.append("Host --> %s  %s " % (host_ip, self.STATUS_FORMATO_ATIVO))


      except subprocess.CalledProcessError:
        self.txtDisplay.append("Erro de Procssamento")


  def getDescHost(self):
    self.txtDisplay.clear()

    self.txtDisplay.append("<span style='color:#00FFFF;font-weight:bold'>Informação do Host</span>")

    alvoTexto = self.inputIPAlvo.text()
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
      self.txtDisplay.append(str(errorIndication))

    else:
      if errorStatus:

        self.txtDisplay.append('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1] or '?'))


      else:
        for nome, val in varBinds:
          self.txtDisplay.append('%s = %s' % (nome.prettyPrint(), val.prettyPrint()))


  def calcularRedes(self,ipRede = "127.0.0.1", maskRede = "30"):
    netaddr = ipRede[:15]  # endereço IP de rede
    netmask = maskRede.strip('/')[:15]  # máscara /24 ou 255.255.255.0

    redes = IPNetwork(netaddr + '/' + netmask)
    self.escrever(redes)
    self.check_online(redes)


  def obterRedes(self):
    self.calcularRedes(self.inputIP.text(), self.inputMask.text())







if __name__ == '__main__':



  win = MainGui()

  win.show()



  # Comandos
  """
   bntSRede.clicked.connect(obterRedes)
   bntAlvo.clicked.connect(getDescHost)"""
  sys.exit(app.exec_())
