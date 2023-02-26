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
import logging
import copy

class MusicPackage:

    def __init__(self, nameID, category, name_IT, name_EN, version, date):
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

    def addInterface(self, musicPackageInterface):
        self.interfaces.append(musicPackageInterface)

class MusicPackageInterface:

    def __init__(self,interfaceName,available,icon):
        self.interfaceName = interfaceName
        self.available = available
        self.icon = icon

    def getInterfaceName(self):
        return self.interfaceName

    def getAvailable(self):
        return self.available

    def getIcon(self):
        return self.icon

class MusicPackageManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = MusicPackageManager()
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

    def listPackages(self):
        packages_serializable = dict()
        for name, package in self.packages.items():
            package_copy = copy.deepcopy(package)
            packages_serializable[name] = package_copy.__dict__
            packages_serializable[name]['interfaces'] = []
            for i in package.interfaces:
                packages_serializable[name]['interfaces'].append(i.__dict__)
        return packages_serializable

    def updatePackages(self):
        newdict = { 'packages': {} }
        for element in self.packages:
            nameID = self.packages[element].getNameID()
            newdict['packages'][nameID] = {  }
            newdict['packages'][nameID]['category']= self.packages[element].getCategory()
            newdict['packages'][nameID]['name_IT']= self.packages[element].getNameIT()
            newdict['packages'][nameID]['name_EN']= self.packages[element].getNameEN()
            newdict['packages'][nameID]['version']= self.packages[element].getVersion()
            newdict['packages'][nameID]['date']= self.packages[element].getDate()
            newdict['packages'][nameID]['interface']= {'base':{}, 'intermediate':{}, 'advanced': {}}
            newdict['packages'][nameID]['interface']['base']['available'] = self.packages[element].getInterfaces()[0].getAvailable()
            newdict['packages'][nameID]['interface']['base']['icon'] = self.packages[element].getInterfaces()[0].getIcon()
            newdict['packages'][nameID]['interface']['intermediate']['available'] = self.packages[element].getInterfaces()[1].getAvailable()
            newdict['packages'][nameID]['interface']['intermediate']['icon'] = self.packages[element].getInterfaces()[1].getIcon() 
            newdict['packages'][nameID]['interface']['advanced']['available'] = self.packages[element].getInterfaces()[2].getAvailable()
            newdict['packages'][nameID]['interface']['advanced']['icon'] = self.packages[element].getInterfaces()[2].getIcon()

        #json_packages = json.dumps(newdict)
        with open('sounds/notes/music_package.json', 'w', encoding='utf-8') as json_file:
            json.dump(newdict, json_file, ensure_ascii=False, indent=4)


    def deletePackage(self, packageName):
        logging.info("packageName: " + packageName)
        if packageName in self.packages:
            del self.packages[packageName]        
            self.updatePackages()
        else:
            logging.error("errore, il pacchetto " + packageName + " non è stato trovato")
            return 2

        if os.path.exists('./sounds/notes/' + packageName):
            os.system('rm -rf ./sounds/notes/' + packageName)
            return 1


    def verifyVersion(self, packageName, version):
        logging.info("verifica pacchetto")
        #newversionList = version.split('.')
        if packageName not in self.packages:
            return True
            
        newVersionList = [int(x) for x in version.split('.')]
        #for i in ragen(0,len(newversionList) -1):
            #newversionList[i] = int(newLversionList[i])

        oldVersion = self.packages[packageName].getVersion()
        oldVersionList = [int(x) for x in oldVersion.split('.')]    

        for i in range(0,len(newVersionList) -1):
            if(newVersionList[i] > oldVersionList[i] ):
                return True
            elif(newVersionList[i] < oldVersionList[i] ):
                return False

        return False

    def addPackage(self, filename):
        pkgnames = filename.split('_')
        version = pkgnames[1].replace('.zip', '')
        logging.info("Music Package version: " + version)
        pkgname = pkgnames[0]
        pkgpath = './sounds/notes/' + pkgname
        if not self.verifyVersion(pkgname, version):
            if (version == self.packages[pkgname].getVersion()):
                logging.error("errore, il pacchetto " + pkgname + " ha versione identica a quello attualmente installato")
                return 3
            else:
                logging.info("errore, il pacchetto " + pkgname + " ha versione precendente a quello attualmente installato")
                return 2
        else:

            os.system('unzip -o ' + '/tmp/' + filename + " -d /tmp")

            os.system('mkdir ' + pkgpath)
            os.system('mv /tmp/' + pkgname + "/" + 'audio.wav ' + pkgpath + '/')

            with open('/tmp/' + pkgname + '/' + pkgname + '.json') as json_file:
                logging.info("adding " + pkgname + " package")
                data = json.load(json_file)
                for p in data['packages']:
                    package = data['packages'][p]
                    mp = MusicPackage(p,package['category'],package['name_IT'],package['name_EN'],package['version'],package['date'])
                    for i in package['interface']:
                        interfaceItem = package['interface'][i]
                        mpi = MusicPackageInterface(i,interfaceItem['available'],interfaceItem['icon'])
                        mp.addInterface(mpi)

                    self.packages[p] = mp

            self.updatePackages()

            os.system('rm -rf /tmp/' + pkgname)
            return 1


    def isPackageAvailable(self,namePackage):
        if namePackage in self.packages:
            return True
        else:
            return False
