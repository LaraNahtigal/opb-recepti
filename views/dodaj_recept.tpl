% rebase('osnova.tpl')

<table class="navigacija">
    <tr>
        <th class="nav-stolpec-1">
            <form action="{{url('moji_recepti')}}" method="GET">
                <button class="gumb-moji-recepti" type="submit">Moji recepti</button>
            </form>
        </th>
        <th class="nav-stolpec-1">
            <form action="{{url('vsi_recepti_prijava')}}" method="GET">
                <button class="gumb-moji-recepti" type="submit">Vsi recepti</button>
            </form>
        </th>
        <th class="nav-stolpec-1"></th>
        <th class="nav-stolpec-mid">
            <div class="dropdown">
                Kategorije
                <div class="dropdown-content">
                    % for kategorija in kategorije:
                        <a href="{{url('doloceni_recepti_kat', kategorija=kategorija)}}">{{kategorija}}</a><br>
                    % end
                </div>
            </div>
        </th>
        <th class="nav-stolpec-mid">
            <div class="dropdown">
                Kulinarike
                <div class="dropdown-content">
                    % for kulinarika in kulinarike:
                        <a href="{{url('doloceni_recepti_kul', kulinarika=kulinarika)}}">{{kulinarika}}</a><br>
                    % end
                </div>
            </div>
        </th>
        <th class="nav-stolpec-mid">
            <div class="dropdown">
                Oznake
                <div class="dropdown-content" style="height: 500px;">
                    % for oznaka in oznake:
                        <a href="{{url('doloceni_recepti_oz', oznaka=oznaka)}}">{{oznaka}}</a><br>
                    % end
                </div>
            </div>
        </th>
        <th class="nav-stolpec-1"></th>
        <th class="nav-stolpec-1"></th>
        <th class="nav-stolpec-1">
            <div class="dropdown" style="text-align: center;">
                ° ° °
                <div class="dropdown-content">
                    <div class="button">
                        <a class="button" href="{{url('prijava_get')}}" method="GET">Prijava</a><br>
                    </div>
                    <div class="button">
                        <a class="button" href="{{url('odjava')}}" method="GET">Odjava</a><br>
                    </div>
                </div>
            </div>
        </th>
    </tr>
</table>

<div class='recept'>
    <h1>DODAJ RECEPT</h1>
    <div class="dodaj_tabela">
        <form action="{{url('dodaj_recept_post')}}" method="POST">
            <table style="width:40%;"> 
                <tr> <th>Ime recepta:</th> <td><input type="text" name="ime"></td></tr>
                <tr> <th>Število porcij:</th> <td><input type="number" name="st_porcij"><td></tr>
                <tr> <th>Čas kuhanja:</th> <td><input type="number" name="cas_kuhanja"><td></tr>
                <tr> <th>Čas priprave:</th> <td><input type="number" name="cas_priprave"><td></tr>
            </table>
        <button class="gumb gumb-recept" type="submit" >Dodaj</button>
        </form>
    </div>
</div>




    



