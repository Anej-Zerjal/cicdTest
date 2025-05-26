# Kronoterm Voice Actions

## Pregled

Ta dodatek omogoča glasovno upravljanje vaše Kronoterm črpalke preko Home Assistant. Uporablja **Whisper** za prepoznavanje govora in **Piper** za sintezo govora, kar omogoča interakcijo s sistemom Kronoterm preko naravnega jezika.

[Video demonstracija](https://youtu.be/jNl_yXXjG2U)

## Predpogoji

* Delujoča namestitev **Home Assistant OS** ali **Home Assistant Supervised**. Ta dodatek **ne deluje** z metodo namestitve "Home Assistant Container", ker nima sistema za upravljanje dodatkov (Supervisor).
* Nameščen in delujoč **Whisper Add-on**, povezan z vašim Home Assistantom. Namestitev iz trgovine z dodatki (`Settings` > `Add-ons` > `Add-on Store`).
* Nameščen in delujoč **Piper Add-on** (neobvezno, vendar priporočljivo), povezan z vašim Home Assistantom. Namestitev iz trgovine z dodatki (`Settings` > `Add-ons` > `Add-on Store`).
* Naložena koda iz tega repozitorija.

## Funkcionalnosti

* **Glasovno upravljanje**: Omogoča glasovno upravljanje vaših Kronoterm črpalk preko Home Assistant.
* **Podpora za slovenski jezik**: Integracija podpira slovenski jezik, kar omogoča naravno interakcijo.
* **100% lokalno**: Vse operacije se izvajajo lokalno, brez potrebe po zunanjih strežnikih ali internetni povezavi.
* **Povratna informacija**: Integracija omogoča povratno informacijo, kar pomeni, da lahko sistem odgovori na vaše ukaze in vprašanja.

![Primer pogovora](/assets/image4.png "Primer pogovora")

### Možni ukazi za posamezne funkcionalnosti

<details>
<summary><b>Klikni in poglej</b></summary>
<br>
<p><it>
Za želeno funkcijo lahko izgovorite pripadajoče ukaze, ki so navedeni spodaj.
</it>
</p>
<details>
<summary>Poizvedba stanja sistema</summary>
<ul>
    <li>"ali je sistem vklopljen"</li>
    <li>"ali je sistem izklopljen"</li>
    <li>"kakšno je stanje sistema"</li>
</ul>
</details>

<details>
<summary>Poizvedba načina delovanja</summary>
<ul>
    <li>"kakšna funkcija se izvaja"</li>
    <li>"kakšna funkcija delovanja se izvaja"</li>
</ul>
</details>

<details>
<summary>Poizvedba stanja rezervnega vira</summary>
<ul>
    <li>"ali je rezervni vir vklopljen"</li>
    <li>"ali je rezervni vir izklopljen"</li>
    <li>"kakšen je status rezervnega vira"</li>
</ul>
</details>

<details>
<summary>Poizvedba stanja alternativnega vira</summary>
<ul>
    <li>"ali je alternativni vir vklopljen"</li>
    <li>"ali je alternativni vir izklopljen"</li>
    <li>"kakšen je status alternativnega vira"</li>
</ul>
</details>

<details>
<summary>Poizvedba režima delovanja</summary>
<ul>
    <li>"kakšen je trenuten režim delovanja"</li>
    <li>"kakšen je režim delovanja"</li>
</ul>
</details>

<details>
<summary>Poizvedba programa delovanja</summary>
<ul>
    <li>"kakšen je trenuten program"</li>
    <li>"kakšen je program delovanja"</li>
</ul>
</details>

<details>
<summary>Poizvedba stanja segrevanja sanitarne vode</summary>
<ul>
    <li>"kakšen je status hitrega segrevanja sanitarne vode"</li>
    <li>"ali je hitro segrevanje sanitarne vode vklopljeno"</li>
    <li>"ali je hitro segrevanje sanitarne vode izklopljeno"</li>
</ul>
</details>

<details>
<summary>Poizvedba statusa načina odtaljevanja</summary>
<ul>
    <li>"kakšen je status odtaljevanja"</li>
    <li>"ali je odtaljevanje vklopljeno"</li>
    <li>"ali je odtaljevanje izklopljeno"</li>
    <li>"ali se odtaljevanje izvaja"</li>
</ul>
</details>

<details>
<summary>Vklop toplotne črpalke</summary>
<ul>
    <li>"vklopi sistem"</li>
    <li>"vklopi toplotno črpalko in ogrevalne kroge"</li>
</ul>
</details>


<details>
<summary>Izklop toplotne črpalke</summary>
<ul>
    <li>"izklopi sistem"</li>
    <li>"izklopi toplotno črpalko in ogrevalne kroge"</li>
</ul>
</details>

<details>
<summary>Nastavljanje normalnega režima</summary>
<ul>
    <li>"nastavi normalen režim"</li>
    <li>"nastavi režim na normalen način"</li>
    <li>"vklopi normalen režim"</li>
</ul>
</details>

<details>
<summary>Nastavljanje ECO režima</summary>
<ul>
    <li>"nastavi eco režim"</li>
    <li>"nastavi režim na eco način"</li>
    <li>"vklopi eco režim"</li>
</ul>
</details>

<details>
<summary>Nastavljanje COM režima</summary>
<ul>
    <li>"nastavi com režim"</li>
    <li>"nastavi režim na com način"</li>
    <li>"vklopi com režim"</li>
</ul>
</details>

<details>
<summary>Vklop hitrega segrevanja sanitarne vode</summary>
<ul>
    <li>"vklopi hitro segrevanje sanitarne vode"</li>
</ul>
</details>

<details>
<summary>Izklop hitrega segrevanja sanitarne vode</summary>
<ul>
    <li>"izklopi hitro segrevanje sanitarne vode": disable_dhw_quick_heating</li>
</ul>
</details>

<details>
<summary>Poizvedba obremenitve toplotne črpalke</summary>
<ul>
    <li>"kakšna je trenutna obremenitev toplotne črpalke"</li>
</ul>
</details>

<details>
<summary>Nastavljanje temperature sanitarne vode</summary>
<ul>
    <li>"nastavi želeno temperaturo sanitarne vode na [x] stopinj"</li>
    <li>"nastavi temperaturo sanitarne vode na [x] stopinj"</li>
    <li>"segrej sanitarno vodo na [x] stopinj"</li>
</ul>
</details>

<details>
<summary>Poizvedba želene temperature sanitarne vode</summary>
<ul>
    <li>"kakšna je trenutna želena temperatura sanitarne vode"</li>
</ul>
</details>

<details>
<summary>Izklop segrevanja sanitarne vode</summary>
<ul>
    <li>"izklopi segrevanje sanitarne vode"</li>
</ul>
</details>

<details>
<summary>Nastavljanje normalnega režima sanitarne vode</summary>
<ul>
    <li>"nastavi normalen režim sanitarne vode"</li>
    <li>"nastavi režim sanitarne vode na normalno"</li>
    <li>"vklopi normalen režim segrevanja sanitarne vode"</li>
</ul>
</details>

<details>
<summary>Nastavljanje režima sanitarne vode po runiku</summary>
<ul>
    <li>"nastavi režim sanitarne vode po urniku"</li>
    <li>"vklopi režim segrevanja sanitarne vode po urniku"</li>
</ul>
</details>

<details>
<summary>Poizvedba režima sanitarne vode po runiku</summary>
<ul>
    <li>"kakšen je trenuten način delovanja sanitarne vode po urniku"</li>
</ul>
</details>

<details>
<summary>Poizvedba akutalne temperature sanitarne vode</summary>
<ul>
    <li>"kakšna je temperatura sanitarne vode": get_dhw_temperature</li>
</ul>
</details>

<details>
<summary>Nastavljanje temperature prostora</summary>
<ul>
    <li>"nastavi temperaturo prostora [ena/dva/tri/štiri] na [x] stopinj"</li>
    <li>"nastavi želeno temperaturo prostora [prvega/drugega/tretjega/četrtega] kroga na [x] stopinj"</li>
</ul>
</details>

<details>
<summary>Poizvedba želene temperature prostora</summary>
<ul>
    <li>"kakšna je trenutna želena temperatura prostora [prvega/drugega/tretjega/četrtega] kroga"</li>
    <li>"kakšna je trenutna želena temperatura prostora [ena/dva/tri/štiri]"</li>
</ul>
</details>

<details>
<summary>Izklop ogrevalnega kroga</summary>
<ul>
    <li>"izklopi [prvi/drugi/tretji/četrti] ogrevalni krog"</li>
    <li>"izklopi ogrevalni krog [ena/dva/tri/štiri]"</li>
</ul>
</details>

<details>
<summary>Nastavitev delovanja ogrevalnega kroga na normalni režim</summary>
<ul>
    <li>"nastavi delovanje [prvega/drugega/tretjega/četrtega] ogrevalnega kroga na normalni režim"</li>
    <li>"nastavi delovanje ogrevalnega kroga [ena/dva/tri/štiri] na normalni režim"</li>
    <li>"vklopi normalni režim na ogrevalnem krogu [ena/dva/tri/štiri]"</li>
    <li>"vklopi normalni režim na [prvem/drugem/tretjem/četrtem] ogrevalnem krogu"</li>
</ul>
</details>

<details>
<summary>Nastavitev delovanja ogrevalnega kroga po urniku</summary>
<ul>
    <li>"nastavi delovanje [prvega/drugega/tretjega/četrtega] ogrevalnega kroga na delovanje po urniku"</li>
    <li>"nastavi delovanje ogrevalnega kroga [ena/dva/tri/štiri] na delovanje po urniku"</li>
    <li>"vklopi delovanje po urniku na ogrevalnem krogu [ena/dva/tri/štiri]"</li>
    <li>"vklopi delovanje po urniku na [prvem/drugem/tretjem/četrtem] ogrevalnem krogu"</li>
</ul>
</details>

<details>
<summary>Poizvedba stanja ogrevalnega kroga</summary>
<ul>
    <li>"kakšen je status delovanja [prvega/drugega/tretjega/četrtega] ogrevalnega kroga"</li>
    <li>"kakšen je status delovanja ogrevalnega kroga [ena/dva/tri/štiri]"</li>
</ul>
</details>

<details>
<summary>Poizvedba aktualne temperature ogrevalnega kroga</summary>
<ul>
    <li>"kakšna je temperatura ogrevalnega kroga [ena/dva/tri/štiri]"</li>
    <li>"kakšna je temperatura [prvega/drugega/tretjega/četrtega] ogrevalnega kroga"</li>
</ul>
</details>
</details>


## Ročna namestitev

Ta navodila opisujejo, kako namestiti Addon v vaš Home Assistant sistem.

### Namestitev dodatka

Za namestitev morate mapo `kronoterm_voice_actions/wyoming` skopirati v mapo `/config/custom_components/` znotraj vašega Home Assistant sistema. To najlažje storite preko SSH povezave.

#### 1. Namestitev SSH na Home Assistant

Ta metoda uporablja ukaz scp (Secure Copy) za prenos datotek preko SSH protokola.

Zato predlagamo Add-on `Advanced SSH & Web Terminal`. S pomočjo njihove dokumentacije si namestite SSH bodisi z geslom bodisi z kriptografskim ključem.

**NUJNO** morate nastaviti `sftp=true` in `username=root` v konfiguraciji tega Add-ona.

**Če imate omogočen standardni SSH dostop do sistema HAOS/Supervised:** Preskočite ta korak, vendar se prepričajte, da poznate uporabniško ime, geslo/ključ in IP naslov za povezavo.

#### 2. Kopiranje Add-ona v Home Assistant

Odprite terminal ali ukazno vrstico **na vašem računalniku** (kjer imate shranjeno mapo `kronoterm_voice_actions/wyoming`)

Kreiranje mape custom_components:

```bash
shh -m hmac-sha2-512-etm@openssh.com root@<HA_IP_NASLOV>
cd /config
cd /config
mkdir custom_components
```

Kopiranje integracije:

```bash
scp -o MACs=hmac-sha2-512-etm@openssh.com -r /pot/do/mape/kronoterm_voice_actions/wyoming root@<HA_IP_NASLOV>:/config/custom_components/
```

* *(Primer: `scp -o MACs=hmac-sha2-512-etm@openssh.com -r C:\Projekti\Projekt-16\custom_components\kronoterm_voice_actions/wyoming root@192.168.1.100:/config/custom_components/`)*

* *(Primer za Linux/macOS: `scp -o MACs=hmac-sha2-512-etm@openssh.com -r ~/Downloads/Projekt-16/custom_components/kronoterm_voice_actions/wyoming root@192.168.1.100:/config/custom_components/`)*

* *(Primer: `scp -o MACs=hmac-sha2-512-etm@openssh.com -r C:\Projekti\Projekt-16\custom_components\kronoterm_voice_actions/wyoming root@192.168.1.100:/config/custom_components/`)*

* *(Primer za Linux/macOS: `scp -o MACs=hmac-sha2-512-etm@openssh.com -r ~/Downloads/Projekt-16/custom_components/kronoterm_voice_actions/wyoming root@192.168.1.100:/config/custom_components/`)*

* Vpisati boste morali geslo za SSH (ali pa bo uporabljen vaš SSH ključ, če je tako nastavljeno).

* Parameter `-r` zagotovi, da se skopira celotna mapa z vsebino.

* Parameter `-o MACs=<hmac-sha2-512-etm@openssh.com>` poskrbi, da se povezava vzpostavi četudi pride do `Corrupted MAC` napake, kar se lahko zgodi.

* Kopiranje lahko, če se povežete na sistem s `ssh root@<HAOS_IP> -m hmac-sha2-512-etm@openssh.com`.

**Preverjanje (neobvezno):**
Lahko se povežete na Home Assistant preko SSH (`ssh vase_ssh_uporabnisko_ime@<HA_IP_NASLOV>`) in zaženete ukaz `ls /config/custom_components/`, da preverite, ali je mapa `kronoterm_voice_control` prisotna.

#### 3. Osvežitev Home Assistant

1. **Ponovno začenite Home Assistant**
   * Pojdite v `Settings` in v desnjem zgornjem kotu kliknite tri pikice. Nato izberite `Restart Home Assistant` in nato zopet isto.
2. **Osvežite Integracije:**
   * V vmesniku Home Assistant pojdite na `Settings` > `Devices & services`
   * Osvežite stran v brskalniku (npr. Ctrl+F5 v Windows/Linux, Cmd+Shift+R v macOS), da Home Assistant ponovno preveri lokalne dodatke.

---

## Namestitev preko HACS

1. **Dodajanje repository-a**
   V vmesniku Home Assistant odprite sistem HACS in pojdite na **Integrations**. Kliknite tri pike v zgornjem desnem kotu in izberite možnost **Custom Repositories**. Dodajte URL tega skladišča in kot kategorijo izberite **Integration**.

2. **Nastavi integracijo**
   Po dodajanju repozitorija poiščite "KronotermVoiceActions" v sistemu HACS v razdelku **Integrations**. Kliknite nanj in izberite **Install**.

3. **Zaženite Home Assistant**
   Ponovno zaženite Home Assistant, da prepozna novo integracijo.

4. **Dodajte integracijo**
   Pojdite na **Nastavitve > Naprave in storitve** v programu Home Assistant. Kliknite gumb "Add integration" in poiščite "KronotermVoiceActions". Sledite navodilom za konfiguracijo integracije.

## Konfiguracija

1. **Namestite pogovornega agenta:**

   * Pojdite v `Settings` > `Devices & services` in desno spodaj izberite `Add integration`. Poiščite `Kronoterm Wyoming`.. Kliknite nanj in izberite `Setup another instance of Kronoterm Wyoming` in končno izberite `Set up the custom Kronoterm conversation agent`.

2. **Namestite STT in TTS integracij:**

   * Vrnite se v `Devices & services`.
   * Vaša integracija **Kronoterm Wyoming - Whisper** ali pa **Piper** bi se moral pojaviti avtomatično.
   * Kliknite gumb **Add**.

3. **Začetek pogovora**

   * Pojdite v `Settings` > `Voice assistants` in kliknite `Add assistant`. Izberite ime in nastavite jezik na `Slovenian`. Nato za `Conversation Conversation Agent` izberite `Kronoterm Agent`. Za `Speech-to-text` izberite `faster-whisper`. V primeru da imate naložen **Piper** ga lahko izberete za `Text-to-speech`.

![Kronoterm Wyoming](/assets/image.png "Kronoterm Wyoming")
![Assistant setup1](/assets/image2.png "Assistant setup1")
![Assistant setup2](/assets/image3.png "Assistant setup2")
