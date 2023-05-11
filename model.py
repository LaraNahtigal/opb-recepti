from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass

class Recept:
    id: int = field(default=0)
    ime: str = field(default='')
    st_porcij: int = field(default=0)
    cas_priprave: int = field(default=0)
    cas_kuhanja: int = field(default=0) 

@dataclass

class ReceptPosSes:
    id_recepta: int = field(default=0)
    ime: str = field(default='')
    st_porcij: int = field(default=0)
    cas_priprave: int = field(default=0)
    cas_kuhanja: int = field(default=0) 
    postopek: str = field(default='')
    sestavine: str = field(default='')

@dataclass_json
@dataclass

class Postopek:
    id_recepta: int = field(default=0)
    st_koraka: int = field(default=0)
    postopek: str = field(default="")

@dataclass_json
@dataclass

class SestavineReceptov:
    id_recepta: int = field(default=0)
    kolicina: str = field(default='')
    enota: str = field(default='')
    sestavina: list = field(default='')

@dataclass_json
@dataclass

class Sestavine:
    id: int = field(default=0)
    ime: str = field(default="")
    mascobe : int = field(default=0)
    ogljikovi_hidrati : int = field(default=0)
    kalorije : int = field(default=0)
    proteini : int = field(default=0)

@dataclass

class NutrienstkaVrednost:
    id_recepta: int = field(default=0)
    mascobe : int = field(default=0)
    ogljikovi_hidrati : int = field(default=0)
    kalorije : int = field(default=0)
    proteini : int = field(default=0)

@dataclass_json
@dataclass

class Uporabnik:
    id: int = field(default=0)
    ime: str = field(default="")

@dataclass_json
@dataclass

class Komentarji:
    id: int = field(default=0)
    avtor: str = field(default="")
    vsebina: str = field(default="")
    #datum

@dataclass_json
@dataclass

class Kategorija:
    id_recepta: int = field(default=0)
    kategorija: str = field(default="")

@dataclass_json
@dataclass
class Kulinarika:
    id_recepta: int = field(default=0)
    kulinarika: str = field(default="")

@dataclass_json
@dataclass
class Oznaka:
    id_recepta: int = field(default=0)
    oznaka: str = field(default="")