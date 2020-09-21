import math
import os
import re

class asa():
    def __init__(self, B, cordas, offsets, alfa_stol = 13.5):

        self.envs = B
        self.B = (B[-1]*2)

        self.cordas = cordas

        total = 0
        for i in range(0,len(B)):
            if (i == 0):
                total += ((cordas[i] + cordas[i+1])*B[i])/2
            else:
                total+= ((cordas[i] + cordas[i+1])*(B[i]-B[i-1]))/2

        self.S = (total*2)

        self.AR = self.B**2/self.S
 
        self.afil = cordas[-1]/cordas[0]

        self.mac = ( cordas[0]*(2/3)* ((1+self.afil+self.afil**2)/(1+self.afil)))

        self.alfa_stol = alfa_stol

        # Constantes
        self.g = 9.81
        self.rho = 1.225
        self.mi = 0.025
        self.pista_total = 60

    def file_and_commands(self):
        o  = open("asa.avl", "w")
        o.write(" Asa\n" +
        "0.0                                 | Mach\n" +
        "0     0     0.0                     | iYsym  iZsym  Zsym\n"+
        "%f     %f     %f   | Sref   Cref   Bref\n" %(self.S, self.mac, self.B)+
        "0.00000     0.00000     0.00000   | Xref   Yref   Zref\n"+
        "0.00                               | CDp  (optional)\n"+
        "SURFACE                      | (keyword)\n"+
        "Main Wing\n"+
        "11        1.0\n"+
        "INDEX                        | (keyword)\n"+
        "1814                         | Lsurf\n"+
        "YDUPLICATE\n"+
        "0.0\n"+
        "SCALE\n"+
        "1.0  1.0  1.0\n"+
        "TRANSLATE\n"+
        "0.0  0.0  0.0\n"+
        "ANGLE\n"+
        "0.000                         | dAinc\n"+
        "SECTION                                              |  (keyword)\n"+
        "0.0000    0.0000    0.0000    %f   0.000    8    3   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]\n" %(cordas[0])+
        "AFIL 0.0 1.0\n"+
        "airfoil.dat\n"+
        "SECTION                                                     |  (keyword)\n" +
        "%f    %f    0.0000    %f   0.000    8    3   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]\n" %(offsets[0], envs[0], cordas[1])+
        "AFIL 0.0 1.0\n"+
        "airfoil.dat\n"+
        "SECTION                                                     |  (keyword)\n" +
        "%f   %f    0.0000    %f   0.000   13    1   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]\n" %(offsets[1], envs[1], cordas[2])+
        "AFIL 0.0 1.0\n"+
        "airfoil.dat \n" +
        "SECTION                                                     |  (keyword)\n" +
        "%f    %f    0.0000    %f   0.000   13    1   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]\n" %(offsets[2], envs[2], cordas[3])+
        "AFIL 0.0 1.0\n"+
        "airfoil.dat \n")
        o.close()

        commands  = open("comandos.txt" , "w")
        commands.write(" load asa\n"  +
        "oper\n" +
        "a\n" +
        "a %f\n" %(self.alfa_stol) +
        "x\n" +
        "ft\n" +
        "resultado.txt\n"  +
        "quit\n")
        commands.close()

    def coeficientes(self):

        self.file_and_commands()

        run_avl_command = 'avl.exe<' + 'comandos.txt'
        os.system(run_avl_command)
        results = (open("resultado.txt")).readlines()
        coefficients = []
        for line in results:
            matches = re.findall(r"\d\.\d\d\d\d\d", line)
            for value in matches:
                coefficients.append(float(value))
        
        CD = coefficients[-6]
        CL = coefficients[-7]

        self.CD = CD
        self.CL = CL

        # Limpar Arquivos
        dirList = os.listdir()
        arquivo = ""
        for file in dirList:
            if (file == "asa.avl") or (file == "resultado.txt") or  (file == "comandos.txt"):
                arquivo = file
                os.remove(arquivo)
            
    def lift (self, V, rho = 1.225 ):
        return (self.rho*V**(2)*0.5*self.CL*self.S)
    
    def drag (self, V, rho = 1.225 ):
        return (self.rho*V**(2)*0.5*self.CD*self.S)

    def mtow (self, rho = 1.225, T=38.125):
        for k in range (0, 270):
            W= (k/(9)) * self.g
            V = math.sqrt((2*W)/(self.rho*self.S*self.CL)) * 1.2 * 0.7
            D = self.rho*V**(2)*0.5*self.CD*self.S
            L = self.rho*V**(2)*0.5*self.CL*self.S
            Slo = round((1.44*(W)**(2))/(self.g*self.rho*self.S*self.CL*(T-(D+self.mi*(W-L)))), 2)
            if Slo > self.pista_total:
                break    

        return W


# Usando como exemplo uma asa com 3 seções
cordas = [0.37,0.355,0.2,0.05]
envs = [0.35,1.85,2.1]
offsets = [0.019207, 0.046857, 0.430388]

# Criando o objeto
asa1 = asa(envs,cordas, offsets)

# Obtendo valores
asa1.coeficientes()

lift = asa1.lift(12)

drag = asa1.drag(12)

mtow = asa1.mtow()


print (mtow)