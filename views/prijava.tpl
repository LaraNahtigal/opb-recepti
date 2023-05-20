<!DOCTYPE html>
<html>
    <form action="{{url('prijava')}}" method="POST" style="width:60%">
    <div class="form-group">
      <label for="uporabnisko_ime">Uporabniško ime</label>
      <input type="input" class="form-control" name="uporabnisko_ime"  placeholder="Vnesi uporabniško ime">
    </div>
    <div class="form-group">
      <label for="geslo">Geslo</label>
      <input type="password" class="form-control" name="geslo" placeholder="Geslo">
    </div>
   
    <button type="submit" class="btn btn-primary">Prijava</button>
    </form>

    %if napaka:
        <p class="opozorilo">{{napaka}}</p>
    %end
</html>