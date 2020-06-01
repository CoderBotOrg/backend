############################################################################
#    CoderBot, a didactical programmable robot.
#    Copyright (C) 2014, 2015 Roberto Previtera <info@coderbot.org>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
############################################################################
#    CoderBot, a didactical programmable robot.
#    Copyright (C) 2014, 2015 Roberto Previtera <info@coderbot.org>
#
#    MUSICAL EXTENTION for CoderBot
#    This extention is develop by:
#    Michele Carbonera - miki_992@hotmail.it - m.carbonera@campus.unimib.it - michele.carbonera@unimib.it
#    Antonino Tramontana - a.tramontana1@campus.unimib.it
#    Copyright (C) 2020 
############################################################################

import json
import os

class MusicPackage:
    name_IT = None
    name_EN = None
    category = None
    version = None
    date = None
    interfaces = None
    nameID = None

    def __init__(self,nameID,category,name_IT,name_EN,version,date):
        self.nameID = nameID
        self.category = category
        self.name_IT = name_IT
        self.name_EN = name_EN
        self.version = version
        self.date = date
        self.interfaces = list()

    def getNameID(self):
        return self.nameID
    def getCategory(self):
        return self.category
    def getNameIT(self):
        return self.name_IT
    def getNameEN(self):
        return self.name_EN
    def getVersion(self):
        return self.version
    def getDate(self):
        return self.date
    def getInterfaces(self):
        return self.interfaces

    def addInterface(self,musicPackageInterface):
        self.interfaces.append(musicPackageInterface)

class MusicPackageInterface:
    interfaceName = None
    available = None
    icon = None

    def __init__(self,interfaceName,available,icon):
        self.interfaceName = interfaceName
        self.available = available
        self.icon = icon

    def getInterfaceName(self):
        return self.interfaceName

    def getAvaiable(self):
        return self.available
    
    def getIcon(self):
        return self.icon

class MusicPackageManager:
    _instance = None
    packages = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = MusicPackageManager()
            print("make MusicPackageManager")
        return cls._instance

    def __init__(self):
        self.packages = dict()
        with open('./sounds/notes/music_package.json') as json_file:
            data = json.load(json_file)
            for p in data['packages']:
                
                package = data['packages'][p]
                mp = MusicPackage(p,package['category'],package['name_IT'],package['name_EN'],package['version'],package['date'])
                for i in package['interface']:
                    interfaceItem = package['interface'][i]
                    mpi = MusicPackageInterface(i,interfaceItem['available'],interfaceItem['icon'])
                    mp.addInterface(mpi)

                if p not in self.packages:
                    self.packages[p] = mp



   def deletePackage(self, packageName):
       print("rimozione pacchetto")
       if packageName in self.packages:
          del self.packages[packageName]        
          self.updatePackages()
       else:
          print("errore, il pacchetto " + packageName + " non è stato trovato")

       if os.path.exists('./sounds/notes/' + packageName):
          os.system('rm -rf ./sounds/notes/' + packageName)


    def isPackageAvailable(self,namePackage):
        if namePackage in self.packages:
            return True
        else:
            return False
