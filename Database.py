# uvozimo psycopg2
from turtle import pos
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import os
from typing import List, TypeVar, Type
from model import *
import model
from pandas import DataFrame
from re import sub
import avtor as auth
from datetime import datetime
from dataclasses_json import dataclass_json

import dataclasses
# Ustvarimo generično TypeVar spremenljivko. Dovolimo le naše entitene, ki jih imamo tudi v bazi
# kot njene vrednosti. Ko dodamo novo entiteno, jo moramo dodati tudi v to spremenljivko.

DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

T = TypeVar(
    "T",
    Recepti,
    Postopki,
    Sestavine,
    SestavineReceptov,
    NutrientskeVrednosti,
    Uporabnik,
    Kategorije,
    Kulinarike,
    Oznake,
    Komentarji2
    )

class Repo:

    def __init__(self):
        self.conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)



##################################################### GENERIČNE METODE ##################################################### 

#-------------------------------------------------- prikazovanje podatkov --------------------------------------------------

    def dobi_vse_gen(self, typ: Type[T]) -> List[T]:
        """ 
        Generična metoda, ki za podan vhodni dataclass vrne seznam teh objektov iz baze.
        Predpostavljamo, da je tabeli ime natanko tako kot je ime posameznemu dataclassu.
        """
        # ustvarimo sql select stavek, kjer je ime tabele typ.__name__ oz. ime razreda
        tbl_name = typ.__name__
        sql_cmd = f'''SELECT * FROM {tbl_name};'''
        self.cur.execute(sql_cmd)
        return [typ.from_dict(d) for d in self.cur.fetchall()]


    def dobi_vse_gen_id(self, typ: Type[T], id: int, id_col = "id") -> T:
        """
        Generična metoda, ki vrne vse dataclass objekte pridobljen iz baze na podlagi njegovega idja.
        """
        tbl_name = typ.__name__
        sql_cmd = f'SELECT * FROM {tbl_name} WHERE {id_col} = %s';
        self.cur.execute(sql_cmd, (id,))    
        return [typ.from_dict(s) for s in self.cur.fetchall()]


    def dobi_gen_id(self, typ: Type[T], id: int, id_col = "id") -> T:
        """
        Generična metoda, ki vrne prvi dataclass objekt pridobljen iz baze na podlagi njegovega idja.
        """
        tbl_name = typ.__name__
        sql_cmd = f'SELECT * FROM {tbl_name} WHERE {id_col} = %s';
        self.cur.execute(sql_cmd, (id,))

        ## Zaradi zakomentirane kode nama ne izpiše prve vrstice, ki jo najde z ukazom fetchone()
        #d = self.cur.fetchone()
        #if d is None:
        #    raise Exception(f'Vrstica z id-jem {id} ne obstaja v {tbl_name}');
    
        return typ.from_dict(self.cur.fetchone())

    
    def dobi_gen_ime(self, typ: Type[T], izbrana_kategorija: str, ime_stolpca = "kategorija") -> T:
        """
        Generična metoda, ki vrne seznam id-jev pridobljen iz baze na podlagi imena izbrane kategorije/kulinarike/oznake.
        """
        tbl_name = typ.__name__
        sql_cmd = f'SELECT * FROM {tbl_name} WHERE {ime_stolpca} = %s';
        self.cur.execute(sql_cmd, (izbrana_kategorija,))

        #d = self.cur.fetchone()
        #if d is None:
        #    raise Exception(f'Vrstica z imenom {izbrana_kategorija} ne obstaja v {tbl_name}');
    
        return [typ.from_dict(s) for s in self.cur.fetchall()]
    

#-------------------------------------------------- razvrščanje podatkov --------------------------------------------------

    def dobi_razlicne_gen_po_abecedi(self, typ: Type[T], ime_stolpca) -> List[T]:
        """ 
        Generična metoda, ki za podan vhodni dataclass vrne seznam različnih objektov iz baze
        in jih uredi po abecednem vrstnem redu glede na 'ime_stolpca'.
        """
        tbl_name = typ.__name__
        sql_cmd = f'''SELECT DISTINCT {ime_stolpca} FROM {tbl_name} ORDER BY {ime_stolpca};'''
        self.cur.execute(sql_cmd)
        return [typ.from_dict(d) for d in self.cur.fetchall()]


    def gen_urejeno(self, typ: Type[T], ime_stolpca) -> List[T]:
        """
        Generična metoda, ki za podan vhodni dataclass vrne seznem teh objektov iz baze.
        Seznam nato uredi po naraščajočem vrstnem redu glede na 'ime_stolpca'
        """
        tbl_name = typ.__name__
        sql_cmd = f'''SELECT * FROM {tbl_name} ORDER BY {ime_stolpca};'''
        self.cur.execute(sql_cmd)
        return [typ.from_dict(d) for d in self.cur.fetchall()]
    

    def dobi_vse_gen_id_urejeno(self, typ: Type[T], ime_stolpca, id: int, id_col = "id") -> T:
        """
        Generična metoda, ki vrne dataclass objekt pridobljen iz baze na podlagi njegovega idja.
        Seznam nato uredi po naraščajočem vrstnem redu glede na 'ime_stolpca'
        """
        tbl_name = typ.__name__
        sql_cmd = f'SELECT * FROM {tbl_name} WHERE {id_col} = %s ORDER BY {ime_stolpca}';
        self.cur.execute(sql_cmd, (id,))    
        return [typ.from_dict(s) for s in self.cur.fetchall()]
    

#-------------------------------------------------- dodajanje podatkov --------------------------------------------------
    
    def dodaj_gen(self, typ: T, serial_col="id", auto_commit=True):
        """
        Generična metoda, ki v bazo doda entiteto/objekt. V kolikor imamo definiram serial
        stolpec, objektu to vrednost tudi nastavimo.
        """

        tbl_name = type(typ).__name__

        cols =[c.name for c in dataclasses.fields(typ) if c.name != serial_col]
        
        sql_cmd = f'''
        INSERT INTO {tbl_name} ({", ".join(cols)})
        VALUES
        ({self.cur.mogrify(",".join(['%s']*len(cols)), [getattr(typ, c) for c in cols]).decode('utf-8')})
        '''

        if serial_col != None:
            sql_cmd += f'RETURNING {serial_col}'

        self.cur.execute(sql_cmd)

        if serial_col != None:
            serial_val = self.cur.fetchone()[0]

            # Nastavimo vrednost serial stolpca
            setattr(typ, serial_col, serial_val)

        if auto_commit: self.conn.commit()


    def dodaj_gen_brez_serial(self, typ: T, auto_commit=True):
        """
        Generična metoda, ki v bazo doda entiteto/objekt. Deluje na tabelah brez serial stolpca.
        """
        tbl_name = type(typ).__name__
        cols =[c.name for c in dataclasses.fields(typ)]
        sql_cmd = f'''
        INSERT INTO {tbl_name} ({", ".join(cols)})
        VALUES
        ({self.cur.mogrify(",".join(['%s']*len(cols)), [getattr(typ, c) for c in cols]).decode('utf-8')})
        '''
        self.cur.execute(sql_cmd)

        if auto_commit: self.conn.commit()
  

#-------------------------------------------------- brisanje podatkov --------------------------------------------------

    def izbrisi_gen(self,  typ: Type[T], id: int, id_col = "id"):
        """
        Generična metoda, ki vrne dataclass objekt pridobljen iz baze na podlagi njegovega idja.
        """
        tbl_name = typ.__name__
        sql_cmd = f'Delete FROM {tbl_name} WHERE {id_col} = %s';
        self.cur.execute(sql_cmd, (id,))
        self.conn.commit()


    def izbrisi_dva_pogoja(self, typ: Type[T], ime: str, ime_stolpca_ime: str, id: int, ime_stolpca_id: str):
        """
        Iz baze izbriše dane kategorije/kulinarike/oznake pri določenem id-ju recepta.
        """
        tbl_name = typ.__name__
        sql_cmd = f'Delete FROM {tbl_name} WHERE {ime_stolpca_ime} = %s AND {ime_stolpca_id} = %s';
        self.cur.execute(sql_cmd, (ime, id,))
        self.conn.commit()

#-------------------------------------------------- posodabljanje podatkov --------------------------------------------------

    def posodobi_gen(self, typ: T, id_col = "id", auto_commit=True):
        """
        Generična metoda, ki posodobi objekt v bazi. Predpostavljamo, da je ime pripadajoče tabele
        enako imenu objekta, ter da so atributi objekta direktno vezani na ime stolpcev v tabeli.
        """
        tbl_name = type(typ).__name__
        
        id = getattr(typ, id_col)
        # dobimo vse atribute objekta razen id stolpca
        fields = [c.name for c in dataclasses.fields(typ) if c.name != id_col]

        sql_cmd = f'UPDATE {tbl_name} SET \n ' + \
                    ", \n".join([f'{field} = %s' for field in fields]) +\
                    f'WHERE {id_col} = %s'
        
        # iz objekta naredimo slovar (deluje samo za dataclasses_json)
        d = typ.to_dict()

        # sestavimo seznam parametrov, ki jih potem vsatvimo v sql ukaz
        parameters = [d[field] for field in fields]
        parameters.append(id)

        # izvedemo sql
        self.cur.execute(sql_cmd, parameters)
        if auto_commit: self.conn.commit()


################################################ UVAŽANJE PODATKOV V BAZO ################################################ 

    def camel_case(self, s):
        """
        Pomožna funkcija, ki podan niz spremeni v camel case zapis.
        """
        s = sub(r"(_|-)+", " ", s).title().replace(" ", "")
        return ''.join(s)     

    def col_to_sql(self, col: str, col_type: str, use_camel_case=True, is_key=False):
        """
        Funkcija ustvari del sql stavka za create table na podlagi njegovega imena
        in (python) tipa. Dodatno ga lahko opremimo še z primary key omejitvijo
        ali s serial lastnostjo. Z dodatnimi parametri, bi lahko dodali še dodatne lastnosti.
        """

        # ali stolpce pretvorimo v camel case zapis?
        if use_camel_case:
            col = self.camel_case(col)
        
        if col_type == "int":
            return f'"{col}" BIGINT{" PRIMARY KEY" if  is_key else ""}'
        elif col_type == "int32":
            return f'"{col}" BIGINT{" PRIMARY KEY" if  is_key else ""}'
        elif col_type == "int64":
            return f'"{col}" BIGINT{" PRIMARY KEY" if  is_key else ""}'
        elif col_type == "float":
            return f'"{col}" FLOAT'
        elif col_type == "float32":
            return f'"{col}" FLOAT'
        elif col_type == "float64":
            return f'"{col}" FLOAT'
        else:
        # če ni ujemanj stolpec naredimo kar kot text
            return f'"{col}" TEXT{" PRIMARY KEY" if  is_key else ""}'
    
    def df_to_sql_create(self, df: DataFrame, name: str, add_serial=False, use_camel_case=True) -> str:
        """
        Funkcija ustvari in izvede sql stavek za create table na podlagi podanega pandas DataFrame-a. 
        df: DataFrame za katerega zgradimo sql stavek
        name: ime nastale tabele v bazi
        add_serial: opcijski parameter, ki nam pove ali želimo dodat serial primary key stolpec
        """

        # dobimo slovar stolpcev in njihovih tipov
        cols = dict(df.dtypes)

        cols_sql = ""

        # dodamo serial primary key
        if add_serial: cols_sql += 'Id SERIAL PRIMARY KEY,\n'
        
        # dodamo ostale stolpce
        # tukaj bi stolpce lahko še dodatno filtrirali, preimenovali, itd.
        cols_sql += ",\n".join([self.col_to_sql(col, str(typ), use_camel_case=use_camel_case) for col, typ in cols.items()])


        # zgradimo končen sql stavek
        sql = f'''CREATE TABLE IF NOT EXISTS {name}(
            {cols_sql}
        )'''

        self.cur.execute(sql)
        self.conn.commit()
        
    def df_to_sql_insert(self, df:DataFrame, name:str, use_camel_case=True):
        """
        Vnese DataFrame v postgresql bazo. Paziti je treba pri velikosti dataframa,
        saj je sql stavek omejen glede na dolžino. Če je dataframe prevelik, ga je potrebno naložit
        po delih (recimo po 100 vrstic naenkrat), ali pa uporabit bulk_insert.
        df: DataFrame, ki ga želimo prenesti v bazo
        name: Ime tabele kamor želimo shranit podatke
        use_camel_case: ali pretovrimo stolpce v camel case zapis
        """
        cols = list(df.columns)

        # po potrebi pretvorimo imena stolpcev
        if use_camel_case: cols = [self.camel_case(c) for c in cols]

        # ustvarimo sql stavek, ki vnese več vrstic naenkrat
        sql_cmd = f'''INSERT INTO {name} ({", ".join([f'"{c}"' for c in cols])})
            VALUES 
            {','.join(
                self.cur.mogrify(f'({",".join(["%s"]*len(cols))})', i).decode('utf-8')
                for i in df.itertuples(index=False)
                )}
        '''

        # izvedemo ukaz
        self.cur.execute(sql_cmd)
        self.conn.commit()


################################################ SPECIFIČNE METODE ################################################ 
    
#---------------------------------------------- pridobivanje podatkov ---------------------------------------------- 

    def dobi_recept(self, ime_recepta: str) -> Recepti:
        """
        Metoda, ki nam vrne vrstico iz tabele 'recepti' vrne vrstico z imenom 'ime_recepta'
        """
        # Preverimo, če recept že obstaja
        self.cur.execute("""
            SELECT id, ime, st_porcij, cas_priprave, cas_kuhanja, id_uporabnika from recepti
            WHERE ime = %s
          """, (ime_recepta,))
        
        row = self.cur.fetchone()

        if row:
            id, ime, st_porcij, cas_priprave, cas_kuhanja, id_uporabnika = row
            return Recepti(id, ime, st_porcij, cas_priprave, cas_kuhanja, id_uporabnika)
        
        raise Exception("Recept z imenom " + ime_recepta + " ne obstaja")


    def dobi_nutrientske_vrednosti(self, id: int) -> NutrientskeVrednosti:
        """
        Metoda, ki nam vrne vrstico iz tabele 'nutrientskevrednosti' vrne vrstico z danim id-jem 
        """
        self.cur.execute("""
            SELECT * from nutrientskevrednosti
            WHERE id_recepta = %s
          """, (id,))
        
        row = self.cur.fetchone()

        if row:
            id_recepta, kalorije, proteini, ogljikovi_hidrati, mascobe = row
            return NutrientskeVrednosti(id_recepta, round(kalorije,2), round(ogljikovi_hidrati,2), round(mascobe,2), round(proteini,2))
        
        raise Exception("Recept ne obstaja")


#---------------------------------------------- dodajanje podatkov ---------------------------------------------- 
    
    def dodaj_recept(self, recept: Recepti) -> Recepti:
        """ 
        Metoda v tabelo 'recepti' doda novo objekt 
        """
        # Preverimo, če recept že obstaja
        self.cur.execute("""
            SELECT id, ime, st_porcij, cas_priprave, cas_kuhanja, id_uporabnika from recepti
            WHERE ime = %s
          """, (recept.ime,))
        
        row = self.cur.fetchone()
        if row:
            recept.id = row[0]
            return recept
        
        # Sedaj dodamo recept
        self.cur.execute("""
            INSERT INTO recepti (ime, st_porcij, cas_priprave, cas_kuhanja, id_uporabnika)
              VALUES (%s, %s, %s, %s, %s) RETURNING id; """, (recept.ime, recept.st_porcij, recept.cas_priprave, recept.cas_kuhanja, recept.id_uporabnika,))
        recept.id = self.cur.fetchone()[0]
        self.conn.commit()
        return recept


    def dodaj_komentar(self, komentar: Komentarji2) -> Komentarji2:
        """ 
        Metoda v tabelo 'komentarji' doda novo objekt. Metoda je od generične različna v tem, 
        da ima default vrednost timestamp
        """
        self.cur.execute("""
            INSERT INTO komentarji2 (id_uporabnika, id_recepta, vsebina)
              VALUES (%s, %s, %s) RETURNING id; """, (komentar.id_uporabnika, komentar.id_recepta, komentar.vsebina, ))

        komentar.id = self.cur.fetchone()[0]
        self.conn.commit()
        return komentar
    

    def slovar_komentarja(self, komentar: Komentarji2):
        """
        Pomožna metoda, ki ustvari slovar danega komentarja
        """
        self.cur.execute("""
            SELECT id, uporabnisko_ime FROM uporabnik
            WHERE id = %s;
            """, ([komentar.id_uporabnika]))

        row = self.cur.fetchone()
        if row:
            slovar = {
                'ime_uporabnika' : row[1],
                'datum_objave' : komentar.datum_objave,
                'vsebina' : komentar.vsebina
            }
        return slovar


    def dodaj_postopek(self, postopek : Postopki) -> Postopki:

        # ta pogoj mora preveriti ce obstaja postopek z dolocenim id in številko koraka, 
        # saj bo vec korakov shranjenih pod isti id recepta
        self.cur.execute("""
            SELECT id_recepta, st_koraka, postopek FROM postopki
            WHERE id_recepta = %s AND st_koraka = %s
             """, (postopek.id_recepta, postopek.st_koraka))
        
        row = self.cur.fetchone()
        
        if row:
            postopek.id_recepta = row[0]
            return postopek

        self.cur.execute("""
            INSERT INTO postopki (id_recepta, st_koraka, postopek)
              VALUES (%s, %s, %s) """, (postopek.id_recepta, postopek.st_koraka, postopek.postopek,))
        self.conn.commit()


    def dodaj_sestavino(self, sestavina : SestavineReceptov) -> SestavineReceptov:

        # ta pogoj mora preveriti ce obstaja sestavina z dolocenim id in imenom, 
        # saj bo vec sestavin shranjenih pod isti id recepta
        self.cur.execute("""
            SELECT id_recepta, sestavina from SestavineReceptov
            WHERE id_recepta = %s AND sestavina = %s
          """, (sestavina.id_recepta, sestavina.sestavina,))
        
        row = self.cur.fetchone()
        
        if row:
            sestavina.id_recepta = row[0]
            return sestavina

        self.cur.execute("""
            INSERT INTO SestavineReceptov (id_recepta, kolicina, enota, sestavina)
              VALUES (%s, %s, %s, %s) """, (sestavina.id_recepta, sestavina.kolicina, sestavina.enota, sestavina.sestavina))
        self.conn.commit()


    def uporabnik(self, uporabnik : Uporabnik) -> Uporabnik:
        """
        Doda novega uporabnika v database.
        """
        # Preverimo, če uporabnik že obstaja
        self.cur.execute("""
            SELECT id, uporabnisko_ime, geslo, zadnji_login from uporabnik
            WHERE uporabnisko_ime = %s
          """, (uporabnik.uporabnisko_ime,))
        
        row = self.cur.fetchone()
        if row:
            uporabnik.id = row[0]
            return uporabnik

        # Sedaj dodamo uporabnika
        self.cur.execute("""
            INSERT INTO uporabnik (uporabnisko_ime, geslo, zadnji_login)
            VALUES (%s, %s, %s) RETURNING id; """, (uporabnik.uporabnisko_ime, uporabnik.geslo, uporabnik.zadnji_login))
        uporabnik.id = self.cur.fetchone()[0]
        self.conn.commit()
        return uporabnik

#---------------------------------------------- brisanje receptov ---------------------------------------------- 

    def brisi_recept(self, recept : Recepti) -> List[Recepti]:
        # Preverimo, če recept obstaja. Če obstaja, izbrišemo vrstice z id-jem
        # recepta, ki ga želimo zbrisati v vseh tabelah.
        # Pred tem moramo izbrisati vse reference na tabelo recepti.
        tabele = [model.SestavineReceptov, model.Oznake, model.NutrientskeVrednosti,
                  model.Kategorije, model.Kulinarike, model.Postopki, model.Komentarji2]
        
        for t in tabele:
            self.izbrisi_gen(t, recept.id, id_col = "id_recepta")
        
        self.izbrisi_gen(model.Recepti, recept.id, "id")


#---------------------------------------------- iskanje podatkov ---------------------------------------------- 

    def najdi_sestavino(self, id, ime):
        """
        Iz database poišče sestavino z imenom 'ime' v receptu z danim id-jem
        """
        self.cur.execute("""
            SELECT * from SestavineReceptov
            WHERE id_recepta = %s AND sestavina = %s
          """, (id, ime,))
        
        row = self.cur.fetchone()
        
        if row:
            sestavina = row
            return SestavineReceptov(
                id_recepta=sestavina[0],
                kolicina=sestavina[1],
                enota=sestavina[2],
                sestavina=sestavina[3]
            )


#---------------------------------------------- urejanje podatkov ----------------------------------------------  
    
    def uredi_postopek(self, postopek: Postopki):
        self.cur.execute("""
            UPDATE postopki
            SET postopek = %s
            WHERE id_recepta = %s AND st_koraka = %s;
          """, (postopek.postopek, postopek.id_recepta, postopek.st_koraka))
        self.conn.commit()


    def pristej_nutriente(self, nutrienti : NutrientskeVrednosti, sestavina : SestavineReceptov) -> NutrientskeVrednosti:
        s = (self.dobi_gen_ime(model.Sestavine, sestavina.sestavina, "ime"))[0]
        kolicina = float(sestavina.kolicina)
        enota = sestavina.enota

        if enota == "g" or enota == "ml":
            kolicina *= 0.01
        if enota == "cup":
            kolicina *= 1.28
        if enota == "ounce":
            kolicina *= 0.28
        if enota == "pound":
            kolicina *= 4.54
        if enota == "tbsp":
            kolicina *= 0.15
        if enota == "tsp":
            kolicina *= 0.03
        if enota == "bunch":
            kolicina *= 2
        if enota == "scoop":
            kolicina *= 0.3

        id_recepta = nutrienti.id_recepta
        kalorije = float(kolicina * s.kalorije + nutrienti.kalorije)
        proteini = float(kolicina * s.proteini + nutrienti.proteini)
        mascobe = float(kolicina * s.mascobe + nutrienti.mascobe)
        ogljikovi_hidrati = float(kolicina * s.ogljikovi_hidrati + nutrienti.ogljikovi_hidrati)

        sql_cmd = f'''UPDATE nutrientskevrednosti 
                      SET kalorije = %s, proteini = %s, ogljikovi_hidrati = %s, mascobe = %s
                      WHERE id_recepta = %s''';
        self.cur.execute(sql_cmd, (kalorije, proteini, ogljikovi_hidrati, mascobe, id_recepta))
        self.conn.commit()


    def odstej_nutriente(self, nutrienti : NutrientskeVrednosti, sestavina : SestavineReceptov) -> NutrientskeVrednosti:
        """
        Ko izbrišemo sestavino, odštejemo tudi nutrientske vrednosti.
        """
        try: 
            s = (self.dobi_gen_ime(model.Sestavine, sestavina.sestavina, "ime"))[0]
            kolicina = float(sestavina.kolicina)
            enota = sestavina.enota

            if enota == "g" or enota == "ml":
                kolicina *= 0.01
            if enota == "cup":
                kolicina *= 1.28
            if enota == "ounce":
                kolicina *= 0.28
            if enota == "pound":
                kolicina *= 4.54
            if enota == "tbsp":
                kolicina *= 0.15
            if enota == "tsp":
                kolicina *= 0.03
            if enota == "bunch":
                kolicina *= 2
            if enota == "scoop":
                kolicina *= 0.3

            id_recepta = nutrienti.id_recepta
            kalorije = float(- kolicina * s.kalorije + nutrienti.kalorije)
            proteini = float(- kolicina * s.proteini + nutrienti.proteini)
            mascobe = float(- kolicina * s.mascobe + nutrienti.mascobe)
            ogljikovi_hidrati = float(- kolicina * s.ogljikovi_hidrati + nutrienti.ogljikovi_hidrati)

            sql_cmd = f'''UPDATE nutrientskevrednosti 
                          SET kalorije = %s, proteini = %s, ogljikovi_hidrati = %s, mascobe = %s
                          WHERE id_recepta = %s''';
            self.cur.execute(sql_cmd, (kalorije, proteini, ogljikovi_hidrati, mascobe, id_recepta))
            self.conn.commit()
        except:
            id_recepta = nutrienti.id_recepta
            kalorije = float(nutrienti.kalorije)
            proteini = float(nutrienti.proteini)
            mascobe = float(nutrienti.mascobe)
            ogljikovi_hidrati = float(nutrienti.ogljikovi_hidrati)

            sql_cmd = f'''UPDATE nutrientskevrednosti 
                          SET kalorije = %s, proteini = %s, ogljikovi_hidrati = %s, mascobe = %s
                          WHERE id_recepta = %s''';
            self.cur.execute(sql_cmd, (kalorije, proteini, ogljikovi_hidrati, mascobe, id_recepta))
            self.conn.commit()
