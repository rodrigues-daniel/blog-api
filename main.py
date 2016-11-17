# encoding: utf-8
# encoding: iso-8859-1
# encoding: win-1252

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
import pysnmp
import os
import threading
import subprocess
import time
import socket
from netaddr import *
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.hlapi import getCmd

app = QApplication(sys.argv)


#tread que lista as maquinas da rede é chamado por self.thread na linha 294
class RedesThread(QThread):
  def __init__(self, redes , parent=app):

    self.lista_de_redes = redes # passa a lista de ips

    QThread.__init__(self, parent)



    self.signal = SIGNAL("status")
    self.start()

  def run(self): 

    for host_ip in self.lista_de_redes:

      try:        

        resposta = ()

        if os.name == 'nt':  # ser for uma maquina windows (sistema nt) este trecho será executado

          resposta = subprocess.getstatusoutput('ping -n 1 %s' % host_ip)


        else:   # ser for uma maquina sistema posix  linux,mac etc..  este trecho será executado

          resposta = subprocess.getstatusoutput('ping -c 1 %s' % host_ip)

        texto = resposta[1]  # retirando resposta da  tupla  no index 1
        ltexto = texto.lower() # todo texto transformado em letras minusculas para facilitar no codigo
        
        # Resposta para Destino inacessivel
        posi_inacessivel = ltexto.find('inacess') 

        
        # Resposta para tempo esgotado
        posi_tempo_esgotado = ltexto.find('esgotado')  
        inacessivel = ltexto[posi_inacessivel:posi_inacessivel + 7]

        tempo_esgotado = ltexto[posi_tempo_esgotado:posi_tempo_esgotado + 8]
        
        
        # testa se  host inacessivel ou tempo esgotado
        if (inacessivel == 'inacess' or tempo_esgotado == 'esgotado'):

          # enviara comando para linha 300 a ser processado na linha 309 
          self.emit(self.signal, 'INATIVO', host_ip, "0")

        else:
          s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          porta = 22
          estado_porta = ""
          try:

            s.connect((host_ip, porta))
            estado_porta = 'Porta {} Aberta'.format(porta)
          except:
            estado_porta = 'Porta {} Fechada'.format(porta)

          s.close()
          self.emit(self.signal, 'ATIVO', host_ip, estado_porta)



      except subprocess.CalledProcessError:

        self.emit(self.signal, "Erro de Procssamento")

class JanelaMae(QMainWindow):
  count = 0

  def __init__(self, parent=None):
    super(JanelaMae, self).__init__(parent)
    self.mdi = QMdiArea()
    self.setCentralWidget(self.mdi)
    bar = self.menuBar()

    subWindBlackNight = QMdiSubWindow()
    subWindBlackNight.setWidget(BlackNight())
    self.mdi.addSubWindow(subWindBlackNight)

    arquivo = bar.addMenu("Arquivo")
    arquivo.addAction("Novo")
    arquivo.addAction("Cascata")
    arquivo.addAction("Encaixado")
    arquivo.triggered[QAction].connect(self.windowaction)
    self.setWindowTitle("MDI demo")
    subWindBlackNight.show()

  def windowaction(self, q):
    print("disparou")


    if q.text() == "Novo":
      JanelaMae.count = JanelaMae.count + 1
      sub = QMdiSubWindow()

      sub.setWidget(QTextEdit())
      sub.setWindowTitle("Sub Janela" + str(JanelaMae.count))
      self.mdi.addSubWindow(sub)
      sub.show()

    if q.text() == "Cascata":
      self.mdi.cascadeSubWindows()

    if q.text() == "Encaixado":
      self.mdi.tileSubWindows()




class BlackNight(QWidget):
  def __init__(self, pai=None):
    QWidget.__init__(self, pai)

    self.STATUS_FORMATO_ATIVO = "     &#160; &#160; &#160;<span style='color:#ff0000;font-weight:bold'>&#174;</span><span style='color:#80ff00;font-weight:bold;'> ATIVO </span>"
    self.STATUS_FORMATO_INATIVO = "     &#160; &#160; &#160;<span style='color:#ff0000;font-weight:bold'>&#8224;</span><span style='color:#ff0000;font-weight:bold;'> INATIVO </span>"

    redes_global = []
    # Definindo a Janela


    self.setWindowTitle("BlackNight   UNIRN - BSI  Turma 2014")
    self.setGeometry(200, 200, 820, 620)
    self.setFixedWidth(820)

    # Entrada de Dados
    self.inputIP = QLineEdit()
    self.inputMask = QLineEdit()
    self.inputIPAlvo = QLineEdit()

    self.le = QLabel("Hello")

    # Comandos
    self.bntSRede = QPushButton("Calcular Rede")
    self.connect(self.bntSRede, SIGNAL("clicked()"), self.obterRedes)

    self.bntAlvo = QPushButton("Obter Info")
    self.connect(self.bntAlvo, SIGNAL("clicked()"),self.getDescHost)

    self.bntConect = QPushButton("Conectar no Alvo")
    self.connect(self.bntConect, SIGNAL("clicked()"), self.conectarAoHost)

    self.bntArq = QPushButton("Arquivo de Senhas")
    self.connect(self.bntArq, SIGNAL("clicked()"), self.lerSenhas)

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
    vbox1.addWidget(self.bntArq)
    vbox1.addWidget(self.bntConect)
    vbox1.addStretch()

    # Saida
    vbox2.addWidget(QLabel("Saida do Processamento:"))

    vbox2.addWidget(self.txtDisplay)
    vbox2.addStretch()

    hbox.addLayout(vbox1)
    hbox.addLayout(vbox2)

    self.setLayout(hbox)

  def conectarAoHost(self):

    alvoTexto = self.inputIPAlvo.text()
    alvo = alvoTexto[:15]

    ssh = subprocess.Popen(["ssh", "%s" % alvo,"uname -a"],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    resposta = ssh.stdout.readlines()
    if resposta == []:
      erro = ssh.stderr.readlines()
      self.txtDisplay.setText(str(erro))
    else:
      self.txtDisplay.setText(str(resposta))





  def lerSenhas(self):
    arquivo = QFileDialog.getOpenFileName(self, 'Arquivo de Senhas', os.path.dirname(os.path.abspath(__file__)),
                                        "Arquivos de Texto (*.txt)")

    self.senhas = []

    with open(arquivo, 'r') as linhas:
      for line in linhas:
        self.senhas.append(line)
      linhas.close()

  def escrever(self, redes):
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

        self.txtDisplay.append(
          '%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1] or '?'))


      else:
        for nome, val in varBinds:
          self.txtDisplay.append('%s = %s' % (nome.prettyPrint(), val.prettyPrint()))

  def calcularRedes(self, ipRede="127.0.0.1", maskRede="30"):
    netaddr = ipRede[:15]  # endereço IP de rede
    netmask = maskRede.strip('/')[:15]  # máscara /24 ou 255.255.255.0

    redes = IPNetwork(netaddr + '/' + netmask)

    self.escrever(redes)

    self.thread = RedesThread(redes)
    self.connect(self.thread, self.thread.signal, self.check_online)
    self.thread.start()


  def obterRedes(self):
    self.calcularRedes(self.inputIP.text(), self.inputMask.text())


  #chamado na linha 300  pela thread
  def check_online(self, status, ip, estado_porta):

    if status == 'INATIVO':
      self.txtDisplay.append("HOST %s %s" % (ip, self.STATUS_FORMATO_INATIVO,))
    else:
      self.txtDisplay.append(
        "HOST %s  %s   &#160; &#160; &#160; <span style='color:#ffffff;font-weight:bold'> %s </span>" % (
          ip, self.STATUS_FORMATO_ATIVO, estado_porta))




def main():

    ex = JanelaMae()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
