# 🎣 Katinuko žvejyba

Nuotykių žaidimas apie katinuką, kuris žvejoja ir kovoja su rykliais po vandeniu!

## 📖 Apie žaidimą

**Katinuko žvejyba** - tai 2D nuotykių žaidimas, kuriame valdai katinuką valtyje ir žvejojai žuvis. Žaidimas turi du lygius su skirtingais peizažais, povandeninį mini-žaidimą su rykliais, monetų rinkimo sistemą ir parduotuvę gyvybių pirkimui.

## 🎮 Valdymas

### Paviršiaus scena:
- **A / D** - plaukti kairėn/dešinėn valtyje
- **E** - pradėti žvejybą (prie žuvų telkinio)
- **ESC** - atidaryti meniu

### Povandeninė scena:
- **W / ↑** - plaukti aukštyn
- **A / D** - judėti kairėn/dešinėn
- **SPACE** - gaudyti žuvį
- **F** - paleisti burbulą (sulėtina ryklius)
- **ENTER** - grįžti į paviršių (tik sugavus visas žuvis)
- **ESC** - atidaryti meniu

## 🎯 Žaidimo tikslas

1. Rask žuvų telkinius paviršiuje (pažymėti žuvų ikona)
2. Spausk **E** prie telkinio, kad nusileistum po vandeniu
3. Sugauk **visas žuvis** povandeniniame žaidime
4. Venkis **ryklių** - jie atima gyvybes!
5. Rinki **monetas** po vandeniu
6. Užbaik **3 telkinius**, kad pereitum į kitą lygį
7. Pirkti gyvybes parduotuvėje už 3 monetas

## ⚡ Funkcijos

### Lygių sistema
- **Lygis 1**: Ežero peizažas
- **Lygis 2**: Naujas peizažas (background2.png)
- Pereini į kitą lygį, kai sugaudi 3 žuvų telkinius

### Povandeninis žaidimas
- **Žuvys**: Sugauk visas žuvis, kad galėtum grįžti į paviršių
- **Rykliai**: Du tipai - patruliai ir atakuojantys
- **Burbulai**: Sulėtina ryklius 2 sekundėms
- **Platformos**: Gali ant jų nusilesti
- **Monetos**: Rink monetas gyvybių pirkimui
- **Fizika**: Gravitacija, platformų kolizijos

### Žaidėjo sistema
- **Gyvybės**: Prasidedi su 5 gyvybėmis
- **Nesužeidžiamumas**: 1.5 sekundės po smūgio
- **Parduotuvė**: Pirkti gyvybę už 3 monetas (max 5)
- **Statistika**: Pagautų žuvų ir monetų skaičiavimas

## 📁 Projekto struktūra

```
PyGame/
├── game.py           # Pagrindinis žaidimo failas
├── constants.py      # Konstantos ir nustatymai
├── assets.py         # Išteklių užkrovimas
├── entities.py       # Žaidimo objektų klasės
├── underwater.py     # Povandeninio žaidimo logika
├── ui.py            # Vartotojo sąsaja
├── README.md        # Dokumentacija
├── images/          # Paveikslėliai
│   ├── ezeras.png
│   ├── background2.png
│   ├── valtis_anim.png
│   ├── varna_Sheet.png
│   ├── zuvys_sheet.png
│   ├── Zuvis_A.png
│   ├── blizge.png
│   ├── riklys_a.png
│   ├── riklys_b.png
│   ├── press_e_Sheet.png
│   ├── uzmesti_Sheet.png
│   ├── dugnas.png
│   ├── meniu.png
│   ├── platforma.png
│   ├── pinigas.png
│   ├── pinigas_ikona.png
│   ├── dead.png
│   ├── burbulai.png
│   └── hp/
│       ├── 1hp.png
│       ├── 2hp.png
│       ├── 3hp.png
│       ├── 4hp.png
│       └── 5hp.png
└── sounds/          # Garso failai
    ├── littlefishes.mp3
    ├── hurt.mp3
    ├── reelin.mp3
    └── coins.mp3
```

## 🚀 Įdiegimas

### Reikalavimai:
- Python 3.7+
- Pygame CE

### Įdiegimo žingsniai:

1. **Įdiegti Pygame CE:**
```bash
pip install pygame-ce
```

2. **Parsisiųsti projektą:**
```bash
git clone <repository-url>
cd PyGame
```

3. **Paleisti žaidimą:**
```bash
python game.py
```

## 🛠️ Naudoti Python įrankiai ir bibliotekos

### Pagrindinė biblioteka:
- **Pygame CE (Community Edition)** - Žaidimų kūrimo biblioteka
  - `pygame.display` - Lango valdymas
  - `pygame.image` - Paveikslėlių užkrovimas
  - `pygame.Surface` - Grafikos atvaizdavimas
  - `pygame.Rect` - Kolizijų aptikimas
  - `pygame.mixer` - Garso sistema
  - `pygame.font` - Teksto atvaizdavimas
  - `pygame.time` - Laiko valdymas, FPS kontrolė
  - `pygame.event` - Įvykių (klaviatūros, pelės) valdymas

### Python standartinės bibliotekos:
- **os** - Failų ir katalogų kelių valdymas
- **random** - Atsitiktinių skaičių generavimas (žuvų, ryklių pozicijos)
- **math** - Matematinės funkcijos (atstumų skaičiavimas, trigonometrija)

### Programavimo principai:
- **Objektinis programavimas (OOP)** - Klasės (Player, Shark, Fish, Bubble)
- **Modulinis dizainas** - Kodas padalintas į atskirus failus
- **MVC šablonas** - Logika, duomenys ir vaizdavimas atskirti
- **Žaidimo ciklas** - 60 FPS su `clock.tick(60)`
- **Fizikos sistema** - Gravitacija, greičio valdymas, kolizijos
- **Būsenų valdymas** - Žaidimo būsenos (meniu, paviršius, po vandeniu)

### Naudojamos technologijos:
- **Sprite sheet animacijos** - Efektyvus animacijų valdymas
- **Camera scrolling** - Pasaulio sekimas kamera
- **Collision detection** - Rect kolizijos aptikimas
- **State machine** - Ryklių elgesio sistema (patrol/attack)
- **Resource management** - Safe loading su fallback

## 🎨 Ištekliai

Žaidimas naudoja šiuos išteklius:
- **Sprite sheets**: Animuoti paveikslėliai
- **Foninė muzika**: Rami muzika žvejybai
- **Garso efektai**: Smūgiai, žuvų gaudymas, monetų rinkimas
- **HP ikonos**: 5 skirtingos gyvybių būsenos

## 🔧 Konfigūracija

Visos konstantos yra `constants.py` faile:
- Ekrano dydis: 1280x720
- Žaidėjo greitis: 8
- Ryklių greičiai: 1.0 (patruliai), 2.4 (ataka)
- Telkinių skaičius lygiui: 3
- Gyvybės kaina: 3 monetos

## 📝 Klasės ir moduliai

### `entities.py`
- `Player` - Žaidėjas (valtis)
- `Varna` - Paukščiai ore
- `FishingSpot` - Žvejybos taškai
- `UnderwaterFish` - Povandenės žuvys
- `Shark` - Rykliai
- `Bubble` - Burbulai
- `Coin` - Monetos

### `underwater.py`
- `UnderwaterGame` - Povandeninio žaidimo valdymas

### `ui.py`
- `UI` - HUD, meniu, tekstai

### `assets.py`
- `load_assets()` - Užkrauna paveikslėlius
- `load_sounds()` - Užkrauna garsus

## 🐛 Žinomi trūkumai

- Nėra garso nustatymų
- Tik 2 lygiai

## 🔮 Būsimi planai

- [ ] Daugiau lygių
- [ ] Įvairesnės žuvys
- [ ] Pasiekimų sistema
- [ ] Taškų lentelė
- [ ] Papildomi ginklai (tinklai, žiebuvėliai)
- [ ] Boss kovos

## 📄 Licencija

Šis projektas yra sukurtas mokymosi tikslais.

## 👨‍💻 Autorius

Sukūrė: Tomas

---

**Sėkmės žvejojant! 🎣**