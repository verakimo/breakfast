# Hyvä aamiainen

**English version below.**

## Suomeksi

### Sovelluksen kuvaus

Hyvä aamiainen on aamiaisreseptien jakamiseen tarkoitettu web-sovellus. Käyttäjät voivat luoda tunnuksen, lisätä omia reseptejä sekä selata ja etsiä muiden käyttäjien lisäämiä reseptejä. Reseptiin tallennetaan nimi, ainekset, valmistusohje, valmistusaika ja luokittelut.

Käyttäjä voi muokata ja poistaa omia reseptejään. Jokaisella käyttäjällä on käyttäjäsivu, jolla näytetään käyttäjän lisäämien reseptien määrä ja lista hänen lisäämistään resepteistä. Käyttäjä voi myös lisätä profiilikuvan.

Kirjautuneet käyttäjät voivat kirjoittaa resepteihin kommentteja ja antaa arvosanan asteikolla 1–5. Reseptin sivulla näytetään kommentit, arvosanojen määrä ja keskimääräinen arvosana.

Sovelluksen pääasiallinen tietokohde on aamiaisresepti. Toissijainen tietokohde on reseptiin liittyvä kommentti ja arvosana.

### Nykyiset ominaisuudet

- Tunnuksen luominen sekä sisään- ja uloskirjautuminen
- Kaikkien käyttäjien lisäämien reseptien selaaminen
- Aamiaisreseptien lisääminen
- Omien reseptien muokkaaminen ja poistaminen
- Reseptien etsiminen hakusanalla
- Hakutulosten suodattaminen aamiaistyypin perusteella
- Hakeminen reseptin nimestä, aineksista ja valmistusohjeesta
- Tietokantaan tallennettavat reseptiluokittelut:
  - aamiaisen tyyppi
  - aamiaisen ominaisuudet
  - ruokavaliot
- Käyttäjäsivut, joilla näytetään reseptien määrä ja reseptilista
- JPEG-profiilikuvan lisääminen, vaihtaminen ja poistaminen
- Reseptien kommentointi ja arvostelu
- Reseptin keskimääräinen arvosana ja kommenttien määrä
- Ruokavaliotunnisteet reseptilistoissa ja hakutuloksissa
- CSRF-suojaus sovelluksen tietoja muuttavissa lomakkeissa
- Sovellus mukautuu eri kokoisille näytöille, ja sen ulkoasu on toteutettu itse kirjoitetulla CSS:llä ilman valmista CSS-kehystä.

### Teknologiat

Sovellus on toteutettu seuraavilla teknologioilla:

- Python 3.10
- Flask
- SQLite
- HTML
- Oma CSS
- Suorat SQL-kyselyt
- Git ja GitHub

### Asennus

Seuraavat ohjeet on tarkoitettu Linux- ja macOS-ympäristöihin.

#### 1. Kloonaa repositorio

Kloonaa tämä repositorio ja siirry projektin juurihakemistoon.

#### 2. Luo ja aktivoi virtuaaliympäristö

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Asenna Flask

```bash
pip install flask
```

#### 4. Luo asetustiedosto

Luo projektin juurihakemistoon tiedosto `config.py` ja lisää siihen Flask-sovelluksen salainen avain:

```python
"""Private configuration for the Flask application."""

SECRET_KEY = "lisää tähän satunnainen salainen avain"
```

Voit luoda satunnaisen avaimen seuraavalla komennolla:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Kopioi komennon tulostama arvo lainausmerkkien sisään. Älä lisää tiedostoa `config.py` versionhallintaan.

#### 5. Luo ja alusta tietokanta

Luo uusi SQLite-tietokanta tiedoston `schema.sql` avulla ja lisää alkutiedot tiedostosta `init.sql`:

```bash
sqlite3 database.db < schema.sql
sqlite3 database.db < init.sql
```

Jos haluat luoda tietokannan kokonaan uudelleen, poista ensin vanha tietokanta:

```bash
rm -f database.db
sqlite3 database.db < schema.sql
sqlite3 database.db < init.sql
```

Komento `rm -f database.db` poistaa pysyvästi kaikki paikalliseen tietokantaan aiemmin tallennetut tiedot.

#### 6. Käynnistä sovellus

```bash
flask run
```

Avaa Flaskin ilmoittama osoite selaimessa. Oletusosoite on:

```text
http://127.0.0.1:5000
```

### Sovelluksen testaaminen

Sovelluksessa ei ole valmiita käyttäjätunnuksia. Luo testitunnukset rekisteröitymissivulla.

#### Testiskenaario 1: Rekisteröityminen ja kirjautuminen

1. Luo ensimmäinen käyttäjätunnus.
2. Kirjaudu ulos.
3. Luo toinen käyttäjätunnus.
4. Testaa sisäänkirjautuminen oikealla salasanalla.
5. Testaa sisäänkirjautuminen väärällä salasanalla.
6. Testaa tunnuksen luominen jo käytössä olevalla käyttäjänimellä.
7. Varmista, että uloskirjautuminen päättää kirjautuneen istunnon.

#### Testiskenaario 2: Reseptien lisääminen ja tarkastelu

1. Kirjaudu sisään ensimmäisenä käyttäjänä.
2. Lisää resepti, jolla on nimi, ainekset, valmistusohje, valmistusaika ja luokittelut.
3. Lisää toinen resepti eri luokitteluilla.
4. Varmista, että molemmat reseptit näkyvät etusivulla.
5. Avaa reseptit ja varmista, että kaikki annetut tiedot ja luokittelut näkyvät oikein.
6. Varmista, että aineksissa ja valmistusohjeissa olevat rivinvaihdot säilyvät.

#### Testiskenaario 3: Muokkaaminen, poistaminen ja käyttöoikeudet

1. Muokkaa yhtä reseptiä sen omistajana.
2. Varmista, että muutetut tiedot näkyvät reseptin sivulla.
3. Kirjaudu sisään toisena käyttäjänä.
4. Varmista, ettei ensimmäisen käyttäjän resepteille näytetä muokkaus- tai poistotoimintoja.
5. Kirjaudu uudelleen sisään ensimmäisenä käyttäjänä ja poista yksi resepteistä.
6. Varmista, että poistaminen vaatii erillisen vahvistuksen.
7. Varmista, että poistettu resepti katoaa reseptilistoista.

Kun resepti poistetaan, sovellus palauttaa käyttäjän sivulle, jolta resepti avattiin: etusivulle, käyttäjäsivulle tai samoihin hakutuloksiin.

#### Testiskenaario 4: Haku

1. Lisää reseptejä, joiden nimet, ainekset ja aamiaistyypit eroavat selvästi toisistaan.
2. Hae reseptiä sen nimessä olevalla sanalla.
3. Hae reseptiä aineksissa olevalla sanalla.
4. Hae reseptiä valmistusohjeessa olevalla sanalla.
5. Suodata reseptejä aamiaistyypin perusteella.
6. Yhdistä hakusana ja aamiaistyyppi samaan hakuun.
7. Tee haku, joka ei tuota tuloksia, ja varmista, että sovellus näyttää siitä ilmoituksen.

#### Testiskenaario 5: Käyttäjäsivut ja profiilikuvat

1. Avaa reseptin lisänneen käyttäjän käyttäjäsivu.
2. Varmista, että sivulla näkyvät oikea reseptien määrä ja reseptilista.
3. Avaa kirjautuneen käyttäjän oma käyttäjäsivu.
4. Lisää alle 100 kilotavun kokoinen JPEG-profiilikuva.
5. Vaihda profiilikuva toiseen JPEG-kuvaan.
6. Poista profiilikuva.
7. Yritä lisätä muu kuin JPEG-tiedosto tai yli 100 kilotavun tiedosto ja varmista, että sovellus hylkää sen.

#### Testiskenaario 6: Kommentit ja arvosanat

1. Kirjaudu sisään toisena käyttäjänä.
2. Avaa ensimmäisen käyttäjän lisäämä resepti.
3. Anna reseptille arvosana 1–5 ja kirjoita kommentti.
4. Varmista, että kommentti, arvosana, arvosanojen määrä ja keskimääräinen arvosana päivittyvät.
5. Lisää kommentti, jossa on useita rivejä, ja varmista, että rivinvaihdot näkyvät.
6. Lisää esimerkiksi teksti `<script>alert("test")</script>` ja varmista, että se näkyy tekstinä eikä suoritettavana HTML-koodina.

#### Testiskenaario 7: Validointi ja navigointi

1. Yritä lähettää pakollisia lomakkeita puuttuvilla tiedoilla.
2. Yritä syöttää kenttiin sallittua pidempiä arvoja.
3. Varmista, että validointipalaute näkyy oikealla sivulla.
4. Varmista, että aiemmin syötetyt kelvolliset arvot säilyvät lomakkeessa validointivirheen jälkeen.
5. Testaa sovellusta kapealla selainikkunalla.
6. Varmista, että navigointi, lomakkeet, reseptitiedot ja käyttäjätilipaneeli pysyvät käyttökelpoisina.

---

## English

### Application description

Hyvä aamiainen is a web application for sharing breakfast recipes. Users can create an account, add their own recipes, and browse and search recipes added by other users. A recipe contains a title, ingredients, preparation instructions, preparation time, and classifications.

Users can edit and delete only their own recipes. Each user has a profile page showing the number of recipes they have added and a list of those recipes. Users can also upload a profile picture.

Logged-in users can write comments and rate recipes from 1 to 5. A recipe page shows its comments, number of ratings, and average rating.

The primary data object is a breakfast recipe. The secondary data object is a comment and rating connected to a recipe.

### Current features

- Account creation, login, and logout
- Browsing recipes added by all users
- Adding breakfast recipes
- Editing and deleting one's own recipes
- Searching recipes by keyword
- Filtering search results by breakfast type
- Searching recipe titles, ingredients, and preparation instructions
- Recipe classifications stored in the database:
  - breakfast type
  - breakfast features
  - diets
- User profile pages with recipe counts and recipe lists
- JPEG profile picture upload, replacement, and deletion
- Comments and ratings for recipes
- Average rating and comment count on recipe pages
- Diet labels in recipe lists and search results
- CSRF protection for forms that change application data
- The application adapts to different screen sizes, and its appearance is implemented with custom CSS without a CSS framework.

### Technology

The application is implemented with:

- Python 3.10
- Flask
- SQLite
- HTML
- Custom CSS
- Direct SQL queries
- Git and GitHub

### Installation

The following instructions are intended for Linux and macOS.

#### 1. Clone the repository

Clone this repository and move to its root directory.

#### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Flask

```bash
pip install flask
```

#### 4. Create the configuration file

Create a file named `config.py` in the project root and add a secret key for the Flask application:

```python
"""Private configuration for the Flask application."""

SECRET_KEY = "add a random secret key here"
```

You can generate a random key with the following command:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copy the generated value inside the quotation marks. Do not add `config.py` to version control.

#### 5. Create the database

Create a new SQLite database from `schema.sql` and add the initial data from `init.sql`:

```bash
sqlite3 database.db < schema.sql
sqlite3 database.db < init.sql
```

To recreate the database from the beginning, delete the old database first:

```bash
rm -f database.db
sqlite3 database.db < schema.sql
sqlite3 database.db < init.sql
```

The command `rm -f database.db` permanently removes all data previously stored in the local database.

#### 6. Start the application

```bash
flask run
```

Open the address shown by Flask in a web browser. The default address is:

```text
http://127.0.0.1:5000
```

### How to test the application

The application does not include predefined user accounts. Create test accounts through the registration page.

#### Test scenario 1: Registration and authentication

1. Create the first user account.
2. Log out.
3. Create the second user account.
4. Test logging in with a correct password.
5. Test logging in with an incorrect password.
6. Test creating an account with an already used username.
7. Confirm that logging out ends the authenticated session.

#### Test scenario 2: Adding and viewing recipes

1. Log in as the first user.
2. Add a recipe with a title, ingredients, preparation instructions, preparation time, and classifications.
3. Add another recipe with different classifications.
4. Confirm that both recipes appear on the home page.
5. Open each recipe and verify that all entered information and classifications are displayed.
6. Confirm that line breaks in ingredients and preparation instructions are preserved.

#### Test scenario 3: Editing, deleting, and access rights

1. While logged in as the recipe owner, edit one recipe.
2. Confirm that the changed information is visible on the recipe page.
3. Log in as the second user.
4. Confirm that edit and delete actions are not available for the first user's recipes.
5. Log back in as the first user and delete one of the recipes.
6. Confirm that deletion requires a separate confirmation.
7. Confirm that the deleted recipe disappears from the recipe lists.

When a recipe is deleted, the application returns to the page from which the recipe was opened: the home page, a user profile, or the current search results.

#### Test scenario 4: Search

1. Add recipes with clearly different titles, ingredients, and breakfast types.
2. Search using a word from a recipe title.
3. Search using a word from the ingredients.
4. Search using a word from the preparation instructions.
5. Filter recipes by breakfast type.
6. Combine a keyword with a breakfast type.
7. Search for a value that produces no results and confirm that an empty-state message is shown.

#### Test scenario 5: User profiles and profile pictures

1. Open a recipe author's profile page.
2. Confirm that the profile shows the correct recipe count and recipe list.
3. Open the logged-in user's own profile.
4. Upload a JPEG profile picture smaller than 100 KB.
5. Replace the profile picture with another JPEG file.
6. Delete the profile picture.
7. Try uploading a non-JPEG file or a file larger than 100 KB and confirm that it is rejected.

#### Test scenario 6: Comments and ratings

1. Log in as the second user.
2. Open a recipe created by the first user.
3. Add a rating from 1 to 5 and a comment.
4. Confirm that the comment, rating, rating count, and average rating are updated.
5. Add comments containing multiple lines and confirm that the line breaks remain visible.
6. Add text such as `<script>alert("test")</script>` and confirm that it is displayed as text rather than executed as HTML.

#### Test scenario 7: Validation and navigation

1. Try submitting required forms with missing values.
2. Try entering values longer than the stated limits.
3. Confirm that validation feedback appears on the relevant page.
4. Confirm that previously entered valid values remain in the form after a validation error.
5. Test the application at a narrow browser width.
6. Confirm that navigation, forms, recipe information, and the account panel remain usable.
