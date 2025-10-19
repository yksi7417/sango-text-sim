
# Sango Characters Strategy — Traits & Loyalty (EN/中文)

Adds **officer traits** and **loyalty** to the bilingual Characters & Assignments MVP.

## Traits (examples)
- **Brave 勇猛**: +8% attacking power when stationed in the attacking city
- **Strict 嚴整**: +10% effectiveness on `train`
- **Benevolent 仁德**: +10% effectiveness on `farm`
- **Charismatic 魅力**: +10% effectiveness on `recruit`
- **Scholar 學士**: +10% effectiveness on `research`
- **Engineer 工師**: +10% defender multiplier (when stationed in defending city), +10% `fortify`
- **Merchant 商賈**: +10% effectiveness on `trade`

## Loyalty
- Officers start around **60–90** loyalty.
- Each successful assignment: **+1** loyalty; if **energy <= 10** after work: **-2** (overworked).
- Battle participation: attack/defend officers in the city gain **+2** on win, **-1** on loss.
- If a **player officer** drops below **35 loyalty**, there's a **10% monthly** chance to **defect** to an adjacent enemy city.
- Use `reward/賞賜` to raise loyalty (costs gold).

## New command
- `reward OFFICER with N` (English)  
- `賞賜 OFFICER 以 N`（中文）

## Run
```
python -m venv .venv
# activate
pip install -r requirements.txt
python game.py
```

Try:
```
武將
指派 關羽 至 農業 於 Chengdu
賞賜 關羽 以 200
狀態 Chengdu
結束
```
