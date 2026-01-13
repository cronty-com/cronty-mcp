# Warsaw AI Breakfast - Demo Script

**Temat:** Cronty MCP - powiadomienia push dla AI agentów
**Czas:** 4 minuty
**Format:** Demo + kod (bez slajdów)

---

## Struktura czasowa

| Sekcja                         | Czas | Kumulatywnie |
|--------------------------------|------|--------------|
| Intro (Dlaczego?)              | 0:30 | 0:30         |
| Demo 1: Obsidian (natychmiast) | 0:30 | 1:00         |
| Demo 2: Obsidian (za 4 min)    | 0:20 | 1:20         |
| Demo 3: Lovable                | 0:40 | 2:00         |
| Ewaluacja + Skill              | 1:20 | 3:20         |
| Wnioski + CTA                  | 0:40 | 4:00         |

---

## Scenariusz

### [0:00-0:30] INTRO - Dlaczego?

> "Używam Life Navigatora od Macieja Cieleckiego w Obsidian do organizacji dnia. Świetne narzędzie, ale brakowało mi jednej rzeczy - powiadomień push na telefon.
>
> AI agent może zaplanować mój dzień, ale nie może mi przypomnieć o spotkaniu za godzinę. Dlatego zbudowałem MCP, który to umożliwia."

**Akcja:** Masz otwarty Obsidian z Life Navigator

---

### [0:30-1:00] DEMO 1 - Obsidian: powiadomienie natychmiastowe

> "Pokażę jak to działa."

**Akcja w Obsidian:**
```
Wyślij mi powiadomienie push z wiadomością "Cześć Warsaw AI Breakfast!"
```

**Pokazać:** Telefon z powiadomieniem

> "Powiadomienie przyszło. Pod spodem NTFY i Upstash QStash."

---

### [1:00-1:20] DEMO 2 - Obsidian: powiadomienie za 4 minuty

> "Teraz ustawię powiadomienie za 4 minuty - zobaczymy czy przyjdzie pod koniec."

**Akcja w Obsidian:**
```
Zaplanuj powiadomienie za 4 minuty z wiadomością "Czas na pytania!"
```

---

### [1:20-2:00] DEMO 3 - Lovable

> "MCP działa nie tylko w Obsidian. Pokażę Lovable."

**Akcja:** Przełącz na Lovable, pokaż konfigurację MCP

> "Lovable to AI do budowania aplikacji webowych. Konfiguracja MCP - wystarczy URL i token."

**Akcja w Lovable:**
```
Wyślij powiadomienie push "Pozdrowienia z Lovable!"
```

**Pokazać:** Telefon z powiadomieniem

> "Ten sam MCP, inny klient. Raz budujesz, używasz wszędzie."

---

### [2:00-3:20] EWALUACJA + SKILL

> "Skąd wiem, że MCP działa dobrze? Zbudowałem system ewaluacji."

**Akcja:** Odpał ewaluację w terminalu

```bash
cd .claude/skills/fastmcp-builder/scripts
uv run python evaluation.py -t stdio -s ../../../../server.py ../../../evaluations/cronty-mcp.xml
```

> "7 zadań testowych. Claude dostaje pytanie, używa moich narzędzi, sprawdzam czy odpowiedź jest poprawna."

**Podczas gdy ewaluacja się odpala, pokaż plik XML:**

**Akcja:** Otwórz `evaluations/cronty-mcp.xml`

```xml
<task id="2">
  <question>Check the current date and time and send a test push notification
  with the message "Evaluation test scheduled at {current_time}"...</question>
  <expected>Yes</expected>
</task>
```

> "Kluczowe odkrycie - LLM potrzebował aktualnej godziny żeby ustawić reminder. Musiałem dodać ją do health toola. Bez ewaluacji bym tego nie zauważył."

**Pokaż wynik ewaluacji:** 100% accuracy

> "Ten system ewaluacji to skill dla Claude Code, który sam zbudowałem. Bazuje na oficjalnym MCP builder od Anthropic."

**Akcja:** Pokaż `.claude/skills/fastmcp-builder/SKILL.md`

> "Skill to instrukcja dla Claude jak budować MCP serwery. Zawiera wzorce, best practices i właśnie ten system ewaluacji."

---

### [3:20-4:00] WNIOSKI + CTA

> "Trzy rzeczy:
> 1. MCP daje AI agentom nowe możliwości - raz budujesz, używasz wszędzie
> 2. Ewaluacje pokazują czego LLM naprawdę potrzebuje
> 3. Skille w Claude Code to sposób na dzielenie się wiedzą"

**Akcja:** Scrolluj do QR code

> "Repo jest open source. QR kod - GitHub i LinkedIn. Zapraszam do rozmowy!"

**[Telefon dzwoni z powiadomieniem "Czas na pytania!"]**

> "Powiadomienie przyszło. Dziękuję!"

---

## Przygotowanie przed prezentacją

### Checklist

- [ ] Obsidian otwarty z Life Navigator
- [ ] Lovable otwarty z konfiguracją MCP
- [ ] Telefon widoczny / połączony z projektorem
- [ ] NTFY app zainstalowana i subskrybowana na topic
- [ ] Terminal gotowy w katalogu `.claude/skills/fastmcp-builder/scripts`
- [ ] VS Code z otwartymi plikami:
  - [ ] `evaluations/cronty-mcp.xml`
  - [ ] `.claude/skills/fastmcp-builder/SKILL.md`
- [ ] Ten dokument w podglądzie Markdown (scrolluj na koniec dla QR)
- [ ] Dry run: wyślij testowe powiadomienie 5 min przed

### Backup plan

Jeśli powiadomienie nie przyjdzie na żywo:
> "Czasami sieć zawodzi - ale wierzcie mi, działa! Sprawdźcie sami z repo."

Jeśli ewaluacja się zawiesza:
> Pokaż wcześniej zapisany output z ewaluacji

---

## Kluczowe komunikaty

1. **Problem:** AI agenty nie mogą działać w przyszłości
2. **Rozwiązanie:** MCP + QStash + NTFY = scheduled notifications
3. **Uniwersalność:** Raz budujesz MCP, używasz w Obsidian, Lovable, Claude Desktop
4. **Insight:** Ewaluacje pokazują czego LLM naprawdę potrzebuje
5. **Bonus:** Skille w Claude Code

---

## Notatki do dry-run

- Powiadomienie za 4 min = wyślij na 1:00, przyjdzie na ~5:00
- Miej backup screenshoty gdyby demo nie zadziałało
- Przećwicz przełączanie: Obsidian → Lovable → Terminal → VS Code
- Ewaluacja trwa ~30-40 sekund - wykorzystaj ten czas na pokazanie XML

---
---
---

<br><br><br><br><br><br><br><br><br><br>

# Dziękuję!

<br>

<img src="linkedn-maks-qrcode.png" width="300" alt="QR Code">

<br>

**Maksymilian Majer**<br>
LinkedIn: [linkedin.com/in/maksymilianmajer](https://www.linkedin.com/in/maksymilianmajer/)<br>
Repo: [github.com/cronty-com/cronty-mcp](https://github.com/cronty-com/cronty-mcp)<br>
Claude Hooks: [dub.sh/claude-ntfy](https://dub.sh/claude-ntfy)<br>
<br>
Pytania? Zapraszam do rozmowy przy kawie!
