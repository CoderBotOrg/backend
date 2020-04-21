#__import__("../musicPackages")
import json
import sys
sys.path.insert(0, './')
import musicPackages
class MusicPackage_test:
    
    def test_musicPackage(self):
        print("sample Music Package: ")
        print(" name_IT = name_it, name_EN = name_en , category = sample_category, version = sample_version, date = sample_date, interfaces = sample_interfaces, nameID = sample_id")
        
        mpkg = musicPackages.MusicPackage(name_IT = "name_it", name_EN = "name_en", category= "sample_category", version= "sample_version", date="sample_date", nameID="sample_id")
        print("name_IT : ", mpkg.getNameIT())
        print("name_EN : ", mpkg.getNameEN())
        print("nameID : ", mpkg.getNameID())
        print("version : ", mpkg.getVersion())
        print("date : ", mpkg.getDate())
        print("category : ", mpkg.getCategory())
        print("interfaces : ", mpkg.getInterfaces())
    
    def test_isPackageAvaible(self):
        pkg_manager = musicPackages.MusicPackageManager()
        for package_name in pkg_manager.packages:
            print("Test if " + package_name + " package is available")
            result = pkg_manager.isPackageAvailable(package_name)
            if(result):
                print(package_name + " package is available")
            else:
                print(package_name + " package is not available")

        print("Test if NONE package is available" )
        result = pkg_manager.isPackageAvailable("NONE")
        if(result):
            print("NONE package is available")
        else:
            print("NONE package is not available")

test = MusicPackage_test()
test.test_musicPackage()
test.test_isPackageAvaible()

