from bs4 import BeautifulSoup
import json
import requests
import time
import random

#peticion get 
def consulta(url,string):
    resp=requests.get(url)
    datos=list()
    if(resp.status_code==200):
        api = json.loads(resp.text)
        if(string!=""):
            return api[string]
        else:
            return api
    return datos

#creo tabla
def cargarTipoP(valor):
    tipom=list()
    datos=valor
    for d in datos['double_damage_to']:
        tipom.append([d['name'],2])
    for d in datos['half_damage_to']:
        tipom.append([d['name'],0.5])
    for d in datos['no_damage_to']:
        tipom.append([d['name'],0])
    return tipom

#peticion get a api-pokemon    
def consultaApi(name):
    resp=requests.get('https://pokeapi.co/api/v2/pokemon/'+name)
    datos_pokemon=list()
    if(resp.status_code==200):
        api = json.loads(resp.text)

        #numero del pokemon
        datos_pokemon.append(api['id'])

        #nombre
        datos_pokemon.append([api['species']['name'],api['species']['url']])

        #stat del pokemon
        datos_pokemon.append(list())
        for stats in api['stats']:
            datos_pokemon[2].append([stats['base_stat'],stats['stat']['name']])

        #typo del pokemon
        datos_pokemon.append(list())
        for tipos in api['types']:
            aux=consulta(tipos['type']['url'],"damage_relations")
            datos_pokemon[3].append([tipos['type']['name'],cargarTipoP(aux)])

        #movimientos del pokemon
        datos_pokemon.append(list())
        for move in api['moves']:
            datos_pokemon[4].append([move['move']['name'],move['move']['url']])

        #otras formas
        datos_pokemon.append(list())
        auxC=consulta(datos_pokemon[1][1],"varieties")
        for c in auxC:
            if(c['is_default']!=True):
                datos_pokemon[5].append(c['pokemon']['name'])
                

    return datos_pokemon

#peticion get a wiki-genero   
def consultaWiki(name):
    page=requests.get('https://www.wikidex.net/wiki/'+name)
    valor=list()
    if(page.status_code==200):
        soup=BeautifulSoup(page.text,'html.parser')
        soup=soup.find_all(title='Probabilidad de encontrar a un Pokémon de cada sexo')
        cadena=str(soup)
        if(len(cadena)>143):
            i=0
            while i<len(cadena):
                if(cadena[i]=="%"):
                    aux=1
                    cadena1=""
                    while (cadena[i-aux]!=" "):
                         cadena1+=cadena[i-aux]
                         aux+=1;
                    cadena1=cadena1[::-1]
                    valor.append(cadena1)
                i+=1
        else:
            cadena=cadena.split("<td>")
            cadena=cadena[1].split("\n")
            valor.append(cadena)
    return valor

class Pokemon:
    def __init__(self,nombre):
         pokemon=list()
         pokemon=consultaApi(nombre)
         pokemon.append(consultaWiki(nombre))
         if(len(pokemon)>3):
             self.numero=pokemon[0]
             self.nombre=pokemon[1]
             self.stat_base=self.cargarStat(pokemon[2])
             self.typo=pokemon[3]
             self.lis_mov=pokemon[4]
             self.lis_mov.sort(key=lambda x:x[0])
             self.otrasFormas=pokemon[5]
             self.genero=pokemon[6]
             self.power=0
             self.mov=0
             self.error=0
         else:
             self.nombre=""
             self.numero=""
             self.stat_base=""
             self.typo=""
             self.lis_mov=""
             self.genero=""
             self.otrasFormas=""
             self.error=1
             self.power=0
             self.mov=0
             
    def cargarStat(self,stat):
        i=0
        VI=31
        EV=250
        level=100
        new_Stat=list()
        aux=0
        for s in stat:
            if(i==0):
                aux=((((s[0]+VI)*2+(pow(EV,(1/2))/4))*level/100))+level+5
                new_Stat.append([s[0],aux,s[1]])
            else:
                aux=((((s[0]+VI)*2+(pow(EV,(1/2))/4))*level/100))+5
                new_Stat.append([s[0],aux,s[1]])
            i+=1
        return new_Stat
    
    def retornarStat(self,nombre):
        for s in self.stat_base:
            if(s[2]==nombre):
                return s
            
    def retornarAtak(self,nombre):
         for s in self.lis_mov:
             if(s[0]==nombre):
                 return s
                
    def numeroPokemon(self):
            print("Pokémon número  "+str(self.numero))
            
    def nombrePokemon(self):
            print("Nombre del Pokémon:  "+(self.nombre[0].capitalize()))
            
    def tiposDelPokemon(self):
        print("Sus tipos son:")
        for tipo in self.typo:
            print(" - "+tipo[0].capitalize())
            
    def estadisticasBaseDelPokemon(self):
        print("Estadísticas base del Pokémon:")
        for stat in self.stat_base:
            if(stat[0]=="hp"):
                print(" - "+"HP"+" = "+str(stat[0]))
            else:
                print(" - "+stat[2].capitalize()+" = "+str(stat[0]))

    def otras_Formas(self):
        print("Otras formas del Pokémon:")
        for aux in self.otrasFormas:
            print(aux)
            
    def retornarGenero(self):
       if(len(self.genero)==1):
           print("Género:"+"\n"+self.genero[0][0])
       elif(self.error!=1):
           if(self.genero[0]=='0' or self.genero[1]=='0'):
               print('Género único:')
               if(self.genero[0]=='0'):
                   print(" - Hembra")
               elif(self.genero[1]=='0'):
                   print(" - Macho")
           else:
               print('Género:')
               print(" - Hembra:"+self.genero[0])
               print(" - Macho:"+self.genero[1])
       else:
          print("sin datos")

    def movimientosPokemon(self):
        i=0
        print("Movimientos que puede aprender el pokémon:")
        for mov in self.lis_mov:
            print(str(i)+" - "+(mov[0].capitalize()))
            i+=1
            
    def cargarAtaque(self,valor):
        if(valor<0):
            print("valor incorrecto")
            self.power=1
            return self.power
        if(len(self.lis_mov)-1>=valor):
            aux=consulta(self.lis_mov[valor][1],"")
            self.power= 1 if (aux['power']==None) else aux['power']
            if(self.power>1):
                self.mov=valor #numero del ataque
                self.tipoMov=[aux['type']['name'],consulta(aux['type']['url'],"damage_relations")]
                self.cargarTipoM()
        else:
            self.power=1
        return self.power
    
    def cargarTipoM(self):
        tipom=list()
        tipom.append(self.tipoMov[0])
        datos=self.tipoMov[1]
        tipom.append(list())
        for d in datos['double_damage_to']:
            tipom[1].append([d['name'],2])
        for d in datos['half_damage_to']:
            tipom[1].append([d['name'],0.5])
        for d in datos['no_damage_to']:
            tipom[1].append([d['name'],0])
        self.tipoMov=tipom
        
        
    def mostrarStat(self):
        print(" El hp  al nivel 100 de "+self.nombre[0]+" es "+str(self.stat_base[0][1]))
        print(" El atk  al nivel 100 de "+self.nombre[0]+" es "+str(self.stat_base[1][1]))
        print(" El def  al nivel 100 de "+self.nombre[0]+" es "+str(self.stat_base[2][1]))
        print(" El spa  al nivel 100 de "+self.nombre[0]+" es "+str(self.stat_base[3][1]))
        print(" El spd  al nivel 100 de "+self.nombre[0]+" es "+str(self.stat_base[4][1]))
        print(" El spe  al nivel 100 de "+self.nombre[0]+" es "+str(self.stat_base[5][1]))

    def generarSTAB(self):
        if(self.tipoMov[0]==self.typo[0][0]):
            return 1.2
        return 1
    
    def generarType(self,tipoP):
        for d in self.typo[0][1]:
            if(d[0]==tipoP):
                return d[1]
        return 1
        
    def mostraMoviemientoS(self):
        if(self.power>1):
            aux=self.lis_mov[self.mov][0]
            print("Seleccione un ataque a ejecutar: "+str(self.mov))
            print("El ataque selecionado es: "+(aux.capitalize()))
            print("Poder de ataque es: "+str(self.power))

    def buscarStat(self,nombre):
        for stat in self.stat_base:
            if(nombre==stat[2]):
                return stat[1]
        return 0
            
    def __repr__(self):
        return str(self.__dict__)
    
def calcularDamage(pokemon1,pokemon2):
    level=100
    power=pokemon1.power 
    A = pokemon1.buscarStat('special-attack')
    D = pokemon2.buscarStat('special-defense')
    rand=random.randint(85, 100)/100
    STAB=pokemon1.generarSTAB()
    typee=pokemon1.generarType(pokemon2.typo[0][0])
    damage=((((2*level/5)+2)*power*(A/D)/50)+2)*typee*STAB*rand*1
    return damage

print("Bienvenido al simulador")
#cargar pokemon 1
nombre = input("Ingrese el nombre del primer Pokémon:")
poke1=Pokemon(nombre)
while(poke1.error==1):
    print("Nombre incorrecto ingrese otro nombre")
    nombre = input("Ingrese el nombre del primer Pokémon:")
    poke1=Pokemon(nombre)
poke1.numeroPokemon()
poke1.nombrePokemon()
poke1.tiposDelPokemon()
poke1.estadisticasBaseDelPokemon()
poke1.retornarGenero()
poke1.otras_Formas()
poke1.movimientosPokemon()
ban=0
while True:
   try:
     aux=int(input("Ingrese movimiento: "))
   except ValueError:
      print("Escribe un numero, no una letra.")
      ban=1
   finally:
       if(ban==0):
          break
       else:
          ban=0;
while (poke1.cargarAtaque(aux)==1):
    print("Movimientos tipo valido ingrese otro ")
    aux=int(input("Ingrese movimiento: "))
poke1.mostraMoviemientoS()
poke1.mostrarStat()

#cargar pokemon 2
nombre = input("Ingrese el nombre del primer Pokémon:")
poke2=Pokemon(nombre)
while(poke2.error==1):
    print("Nombre incorrecto ingrese otro nombre")
    nombre = input("Ingrese el nombre del primer Pokémon:")
    poke2=Pokemon(nombre)
poke2.numeroPokemon()
poke2.nombrePokemon()
poke2.tiposDelPokemon()
poke2.estadisticasBaseDelPokemon()
poke2.retornarGenero()
poke2.otras_Formas()
poke2.movimientosPokemon()
while True:
   try:
     aux=int(input("Ingrese movimiento: "))
   except ValueError:
      print("Escribe un numero, no una letra.")
      ban=1
   finally:
       if(ban==0):
          break
       else:
          ban=0;
while (poke2.cargarAtaque(aux)==1):
    print("Movimientos tipo valido ingrese otro ")
    aux=int(input("Ingrese movimiento: "))
poke2.mostraMoviemientoS()
poke2.mostrarStat()

#pelea
damage=calcularDamage(poke1,poke2)
print("El daño realizó "+(poke1.nombre[0].capitalize())+" a "+(poke2.nombre[0].capitalize())+" fue de:"+str(damage))
hp2=poke2.buscarStat('hp')-damage
print((poke2.nombre[0].capitalize())+" quedó con un HP de: "+str(hp2))
