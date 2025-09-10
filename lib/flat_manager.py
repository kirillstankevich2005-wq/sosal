from lib.service.kufar import get_new_flats as get_kufar_flats
from lib.service.onliner import get_new_flats as get_onliner_flats
from lib.service.domovita import get_new_flats as get_domovita_flats
from lib.service.realt import get_new_flats as get_realt_flats

def getNewFlats():
    flats = []
    kufar_flats = get_kufar_flats()
    onliner_flats = get_onliner_flats()
    domovita_flats = get_domovita_flats()
    realt_flats = get_realt_flats()

    if( len(kufar_flats) > 0):
        flats = flats + kufar_flats

    if( len(onliner_flats) > 0):
        flats = flats + onliner_flats

    if( len(domovita_flats) > 0):
        flats = flats + domovita_flats
        
    if( len(realt_flats) > 0):
        flats = flats + realt_flats
    
    return flats; 