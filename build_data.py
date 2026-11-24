#!/usr/bin/env python3
"""Build the DashElectrify dataset.

Sources
-------
1. Pledge signatories: the Presidency signatory sheet as captured by the
   three-hourly refresh on LXC 104 (src/pledge_source.html, refreshed
   2026-11-20 06:02 TRT). Parsed, never retyped.
2. World Bank WDI, live API, no key. Latest available year per series.

Output: data/dashboard.json
"""
import json
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(ROOT, "data", "raw")
os.makedirs(RAW, exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) dashElectrify/1.0"}
WB_NAMES = {}  # official English names straight from the API payload
WB_SHORT = {"Micronesia, Fed. Sts.": "Micronesia"}


def get_json(url, cache_name, tries=4):
    path = os.path.join(RAW, cache_name)
    if os.path.exists(path) and os.path.getsize(path) > 200:
        return json.load(open(path))
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read().decode("utf-8"))
            json.dump(data, open(path, "w"))
            return data
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 + 2 * i)
    raise RuntimeError(f"fetch failed {url}: {last}")


# ---------------------------------------------------------------- pledge list
SHEET_ID = "15477d2O1xoP0Sx4_8whJbSFd2R1VkOs6qB6Z1pJVg9Q"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=0"


def parse_pledge():
    """Status per country, straight from the live tracker export."""
    import csv, io
    path = os.path.join(RAW, "pledge.csv")
    if not os.path.exists(path) or os.path.getsize(path) < 1000:
        req = urllib.request.Request(SHEET_URL, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r:
            open(path, "wb").write(r.read())
    rows = list(csv.reader(io.StringIO(open(path, encoding="utf-8").read())))
    body = [r for r in rows[3:] if r and r[0].strip()]
    status = {}
    for r in body:
        name = r[0].strip()
        st = (r[2].strip() if len(r) > 2 else "")
        low = st.lower()
        if name.lower() == "european union":
            continue
        if low == "yes":
            status[name] = "national"
        elif low.startswith("yes - eu"):
            status[name] = "eu"
        elif low == "likely":
            status[name] = "likely"
        elif low == "considering":
            status[name] = "considering"
        else:
            status[name] = "none"
    return status


# ------------------------------------------------------------- name to ISO-3
ISO_FIX = {
    "congo": "COG", "democratic republic of the congo": "COD",
    "lao people's democratic republic": "LAO", "lao pdr": "LAO",
    "micronesia": "FSM", "federated states of micronesia": "FSM",
    "republic of korea": "KOR", "korea, rep.": "KOR", "korea, republic of": "KOR",
    "turkiye": "TUR", "türkiye": "TUR", "cote d'ivoire": "CIV", "côte d'ivoire": "CIV",
    "eswatini": "SWZ", "swaziland": "SWZ", "north macedonia": "MKD",
    "russian federation": "RUS", "russia": "RUS", "united states": "USA",
    "united kingdom": "GBR", "iran, islamic rep.": "IRN", "iran": "IRN",
    "viet nam": "VNM", "vietnam": "VNM", "syrian arab republic": "SYR",
    "egypt, arab rep.": "EGY", "egypt": "EGY", "yemen, rep.": "YEM",
    "gambia, the": "GMB", "bahamas, the": "BHS", "brunei darussalam": "BRN",
    "cabo verde": "CPV", "cape verde": "CPV", "timor-leste": "TLS",
    "hong kong sar, china": "HKG", "macao sar, china": "MAC",
    "west bank and gaza": "PSE", "kyrgyz republic": "KGZ", "slovak republic": "SVK",
    "st. lucia": "LCA", "st. vincent and the grenadines": "VCT",
    "st. kitts and nevis": "KNA", "sao tome and principe": "STP",
    "são tomé and príncipe": "STP", "antigua and barbuda": "ATG",
    "trinidad and tobago": "TTO", "united arab emirates": "ARE",
    "czechia": "CZE", "czech republic": "CZE", "netherlands": "NLD",
    "bolivia": "BOL", "venezuela, rb": "VEN", "venezuela": "VEN",
}

# ISO resolution built from the Natural Earth file in data/, so no dependency
# and no aggregate rows: only real countries can appear on the map.
_GEO = json.load(open(os.path.join(ROOT, "data", "countries.geo.json")))
_GEO_NAMES = {}
for _f in _GEO["features"]:
    _p = _f["properties"]
    _iso = (_p.get("iso") or "").upper()
    if not _iso or _iso == "-99":
        continue
    if _p.get("name"):
        _GEO_NAMES[_p["name"].strip().lower()] = _iso
_GEO_ISOS = {(f["properties"].get("iso") or "").upper() for f in _GEO["features"]}

ALIAS = {
    # every name as the Presidency sheet spells it, mapped explicitly so no
    # fuzzy matcher can silently drop a signatory
    "albania": "ALB", "andorra": "AND", "antigua and barbuda": "ATG",
    "armenia": "ARM", "australia": "AUS", "bangladesh": "BGD",
    "burkina faso": "BFA", "cambodia": "KHM", "canada": "CAN", "chile": "CHL",
    "colombia": "COL", "congo": "COG", "costa rica": "CRI", "djibouti": "DJI",
    "dominica": "DMA", "ecuador": "ECU", "eswatini": "SWZ", "ethiopia": "ETH",
    "fiji": "FJI", "ghana": "GHA", "guatemala": "GTM", "guinea": "GIN",
    "iceland": "ISL", "israel": "ISR", "jamaica": "JAM", "japan": "JPN",
    "kenya": "KEN", "lao people's democratic republic": "LAO", "lao pdr": "LAO",
    "lithuania": "LTU", "maldives": "MDV", "micronesia": "FSM", "monaco": "MCO",
    "mongolia": "MNG", "mozambique": "MOZ", "new zealand": "NZL",
    "nicaragua": "NIC", "niger": "NER", "norway": "NOR", "pakistan": "PAK",
    "palau": "PLW", "panama": "PAN", "papua new guinea": "PNG",
    "philippines": "PHL", "portugal": "PRT", "republic of korea": "KOR",
    "seychelles": "SYC", "singapore": "SGP", "solomon islands": "SLB",
    "somalia": "SOM", "st. kitts and nevis": "KNA", "switzerland": "CHE",
    "togo": "TGO", "tonga": "TON", "turkiye": "TUR", "uganda": "UGA",
    "united arab emirates": "ARE", "united kingdom": "GBR", "uruguay": "URY",
    "zambia": "ZMB", "zimbabwe": "ZWE",
    # general aliases the World Bank download may need elsewhere
    "turkey": "TUR", "czechia": "CZE", "czech republic": "CZE",
    "netherlands": "NLD", "cote d'ivoire": "CIV", "viet nam": "VNM",
    "russian federation": "RUS", "united states": "USA", "iran": "IRN",
    "egypt": "EGY", "syria": "SYR", "yemen": "YEM", "gambia": "GMB",
    "cape verde": "CPV", "timor-leste": "TLS", "sao tome and principe": "STP",
    "bolivia": "BOL", "venezuela": "VEN", "tanzania": "TZA", "moldova": "MDA",
    "kosovo": "XKX",
}

# countries too small for the 1:110m geometry, drawn as dots at their capital
DOTS = {
    "AND": [1.53, 42.51], "DMA": [-61.39, 15.30], "MDV": [73.51, 4.18],
    "MCO": [7.42, 43.74], "PLW": [134.58, 7.50], "SYC": [55.45, -4.62],
    "SGP": [103.82, 1.35], "SLB": [159.96, -9.43], "TON": [-175.20, -21.14],
    "KNA": [-62.72, 17.30], "ATG": [-61.85, 17.12],
}

def to_iso(name):
    key = name.strip().lower().replace("’", "'")
    if key in ALIAS:
        return ALIAS[key]
    return _GEO_NAMES.get(key)


# ------------------------------------------------------------------- WB pull
IND = {
    "pop": "SP.POP.TOTL",
    "gdp": "NY.GDP.MKTP.CD",
    "gdp_pc": "NY.GDP.PCAP.CD",
    "access": "EG.ELC.ACCS.ZS",
    "access_rural": "EG.ELC.ACCS.RU.ZS",
    "access_urban": "EG.ELC.ACCS.UR.ZS",
    "renew_fec": "EG.FEC.RNEW.ZS",
    "renew_elec": "EG.ELC.RNEW.ZS",
    "elec_pc": "EG.USE.ELEC.KH.PC",
    "access_gap_years": "EG.ELC.ACCS.ZS",
}


def wb(indicator, start=2010, end=2024):
    url = (f"https://api.worldbank.org/v2/country/all/indicator/{indicator}"
           f"?format=json&per_page=20000&date={start}:{end}")
    data = get_json(url, f"{indicator}_{start}_{end}.json")
    if not isinstance(data, list) or len(data) < 2 or data[1] is None:
        return {}, {}
    latest, series = {}, {}
    for row in data[1]:
        iso = row.get("countryiso3code")
        val = row.get("value")
        if iso and row.get("country", {}).get("value"):
            WB_NAMES[iso] = row["country"]["value"]
        yr = int(row.get("date"))
        if not iso or val is None:
            continue
        if iso not in latest or yr > latest[iso][0]:
            latest[iso] = (yr, float(val))
        series.setdefault(iso, {})[yr] = float(val)
    return latest, series


def norm(s):
    import unicodedata, re as _re
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return _re.sub(r"[^a-z ]", "", s).replace("the ", "").strip()


# Countries present in the geography file with no World Bank name of their own.
FALLBACK_NAMES = {
    "COK": "Cook Islands",
    "NIU": "Niue",
    "VAT": "Vatican City",
    "TWN": "Taiwan",
    "XKX": "Kosovo",
}

def name_index():
    geo = json.load(open(os.path.join(ROOT, "data", "countries.geo.json")))
    idx = {}
    for f in geo["features"]:
        pr = f["properties"]
        iso = (pr.get("iso") or "").upper()
        nm = pr.get("name") or pr.get("name_en")
        if iso and nm:
            idx[norm(nm)] = iso
    idx.update({
        "turkiye": "TUR", "republic of korea": "KOR", "micronesia": "FSM",
        "st kitts and nevis": "KNA", "congo": "COG", "lao peoples democratic republic": "LAO",
        "cote divoire": "CIV", "eswatini": "SWZ", "united arab emirates": "ARE",
        "bolivia": "BOL", "venezuela": "VEN", "iran": "IRN", "syria": "SYR",
        "moldova": "MDA", "tanzania": "TZA", "vietnam": "VNM", "brunei": "BRN",
        "cape verde": "CPV", "sao tome and principe": "STP", "timor leste": "TLS",
        "palestine": "PSE", "gambia": "GMB", "bahamas": "BHS", "kyrgyzstan": "KGZ",
        "slovakia": "SVK", "czech republic": "CZE", "north macedonia": "MKD",
        "democratic republic of the congo": "COD", "tanzania united republic of": "TZA",
        "united states of america": "USA", "russian federation": "RUS",
        "republic of moldova": "MDA", "hong kong": "HKG",
        "cook islands": "COK", "nauru": "NRU", "niue": "NIU", "vatican": "VAT",
        "state of palestine": "PSE", "democratic republic of the congo": "COD",
        "democratic peoples republic of korea": "PRK", "republic of the congo": "COG",
    })
    return idx


# ------------------------------------------------------- 2030 national targets
def read_xlsx_rows(path, sheet=3):
    """Minimal xlsx reader: zip + inline/shared strings, no openpyxl."""
    import zipfile, html
    z = zipfile.ZipFile(path)
    ss = []
    if "xl/sharedStrings.xml" in z.namelist():
        sst = z.read("xl/sharedStrings.xml").decode("utf-8", "ignore")
        ss = [html.unescape("".join(re.findall(r"<t[^>]*>([^<]*)</t>", si)))
              for si in re.findall(r"<si>(.*?)</si>", sst, re.S)]
    x = z.read(f"xl/worksheets/sheet{sheet}.xml").decode("utf-8", "ignore")
    rows = []
    for r in re.findall(r"<row[^>]*>(.*?)</row>", x, re.S):
        cells = {}
        for m in re.finditer(r'<c r="([A-Z]+)(\d+)"([^>]*)>(.*?)</c>', r, re.S):
            col, _, attrs, inner = m.groups()
            v = re.search(r"<v>([^<]*)</v>", inner)
            isv = re.search(r"<is>.*?<t[^>]*>([^<]*)</t>", inner, re.S)
            if isv:
                cells[col] = html.unescape(isv.group(1))
            elif v:
                val = v.group(1)
                if 't="s"' in attrs and ss:
                    try:
                        val = ss[int(val)]
                    except Exception:
                        pass
                cells[col] = val
        if cells:
            rows.append(cells)
    return rows


def ember_targets():
    path = os.path.join(RAW, "ember_targets.xlsx")
    if not os.path.exists(path):
        return {}
    rows = read_xlsx_rows(path, 3)
    if not rows:
        return {}
    hdr = rows[0]
    want = {v: k for k, v in hdr.items()}
    out = {}
    for r in rows[1:]:
        iso = (r.get(want.get("country_code", "A"), "") or "").strip().upper()
        if len(iso) != 3:
            continue
        def num(key):
            col = want.get(key)
            if not col:
                return None
            try:
                return float(r.get(col))
            except (TypeError, ValueError):
                return None
        gw = num("res_capacity_target")
        share = num("res_share_target")
        yr = num("target_year")
        if gw is None and share is None:
            continue
        out[iso] = {"res_target_gw": gw, "res_target_share": share,
                    "target_year": int(yr) if yr else 2030}
    return out



# ------------------------------------------------- country tab extra layers
def owid_mix(path):
    """Per-country yearly electricity mix shares (Ember via Our World in Data)."""
    import csv as _csv
    if not os.path.exists(path):
        return {}
    rows = list(_csv.DictReader(open(path, newline="", encoding="utf-8")))
    cols = [c for c in rows[0].keys() if c not in ("entity", "code", "year")]
    out = {}
    for r in rows:
        iso = (r.get("code") or "").strip()
        if len(iso) != 3:
            continue
        try:
            y = int(r["year"])
        except (TypeError, ValueError):
            continue
        rec = out.setdefault(iso, {"years": [], "fossil": [], "renew": [], "nuclear": []})
        rec["years"].append(y)
        for key, col in zip(("fossil", "renew", "nuclear"),
                            ("fossil_share_of_electricity__pct",
                             "renewable_share_of_electricity__pct",
                             "nuclear_share_of_electricity__pct")):
            try:
                rec[key].append(round(float(r.get(col)), 2))
            except (TypeError, ValueError):
                rec[key].append(None)
    for iso, rec in out.items():
        order = sorted(range(len(rec["years"])), key=lambda i: rec["years"][i])
        for k in ("years", "fossil", "renew", "nuclear"):
            rec[k] = [rec[k][i] for i in order]
    return out


def dashdist_grid(path):
    """Grid loss share and network density from the DashDist build."""
    if not os.path.exists(path):
        return {}
    d = json.load(open(path))
    out = {}
    for r in d.get("rows", []):
        iso = (r.get("iso") or "").upper()
        if len(iso) != 3:
            continue
        out[iso] = {"losses": r.get("losses"), "kwh_pc": r.get("kwh_pc"),
                    "net_km": r.get("net_km"), "km_per_1000_people": r.get("km_per_1000_people"),
                    "km_per_1000km2": r.get("km_per_1000km2"),
                    "year_losses": r.get("year_losses")}
    return out


def plans_register(path):
    if not os.path.exists(path):
        return []
    d = json.load(open(path))
    return d.get("entries", [])


def main():
    sheet = parse_pledge()

    data = {}
    for key, code in IND.items():
        if key == "access_gap_years":
            continue
        latest, series = wb(code)
        print(f"  {key:12s} {code:18s} countries={len(latest)}")
        for iso, (yr, val) in latest.items():
            if iso not in _GEO_ISOS:
                continue
            data.setdefault(iso, {})[key] = val
            data[iso][key + "_year"] = yr
        if key == "access":
            data["__access_series__"] = {k: v for k, v in series.items() if k in _GEO_ISOS}

    access_series = data.pop("__access_series__", {})
    idx = name_index()
    idx.update({norm(v): k for k, v in WB_NAMES.items()})
    status, unmapped = {}, []
    for name, st in sheet.items():
        iso = idx.get(norm(name))
        if not iso:
            unmapped.append(name)
            continue
        if st == "none":
            status.setdefault(iso, {"status": "none", "source": ""})
            continue
        status[iso] = {"status": st, "source": st}
    print(f"pledge rows {len(sheet)}, mapped {len(status)}, unmapped {len(unmapped)} {unmapped[:10]}")
    print("  national", sum(1 for v in status.values() if v["status"] == "national"),
          "eu", sum(1 for v in status.values() if v["status"] == "eu"),
          "likely", sum(1 for v in status.values() if v["status"] == "likely"),
          "considering", sum(1 for v in status.values() if v["status"] == "considering"))

    countries = {}
    for iso, vals in data.items():
        if iso.startswith("__"):
            continue
        st = status.get(iso, {"status": "none", "source": ""})
        pv = st.get("status", "none")
        countries[iso] = {**vals,
                          "pledge": "signed" if pv in ("national", "eu") else pv,
                          "pledge_date": "",
                          "pledge_source": pv if pv in ("national", "eu") else "",
                          "pledge_individual_eu": False}

    # attach names from countries.geo.json for anything the WB missed
    geo = json.load(open(os.path.join(ROOT, "data", "countries.geo.json")))
    names = {}
    for f in geo["features"]:
        p = f["properties"]
        names[(p.get("iso") or "").upper()] = p.get("name")

    for iso, meta in status.items():
        if iso not in countries:
            pv = meta["status"]
            countries[iso] = {"pledge": "signed" if pv in ("national", "eu") else pv,
                              "pledge_date": "",
                              "pledge_source": pv if pv in ("national", "eu") else ""}
    for iso, meta in status.items():
        if iso in countries and iso in DOTS:
            countries[iso]["dot"] = DOTS[iso]
    targets = ember_targets()
    hit = 0
    for iso, t in targets.items():
        if iso in countries:
            countries[iso].update(t)
            hit += 1
    print(f"2030 targets: {len(targets)} parsed, {hit} matched to countries")

    for iso in countries:
        countries[iso]["name"] = (names.get(iso) or WB_SHORT.get(WB_NAMES.get(iso, ""), WB_NAMES.get(iso))
                                or FALLBACK_NAMES.get(iso) or iso)

    mix = owid_mix(os.path.join(RAW, "owid_elec_mix.csv"))
    grid = dashdist_grid("/home/simon/projects/dashdist/data/dashboard.json")
    plans = plans_register("/home/simon/projects/electrification-tracker/src/data.json")
    mix_hit = grid_hit = 0
    for iso in list(countries):
        if iso in mix:
            m = mix[iso]
            countries[iso]["mix"] = {"year": m["years"][-1], "fossil": m["fossil"][-1],
                                     "renew": m["renew"][-1], "nuclear": m["nuclear"][-1]}
            mix_hit += 1
        if iso in grid:
            countries[iso].update(grid[iso])
            grid_hit += 1
    plan_idx = name_index()
    plan_idx.update({norm(v): k for k, v in WB_NAMES.items()})
    PLAN_ALIASES = {norm(k): v for k, v in {
        "Korea, Republic of": "KOR", "Republic of Korea": "KOR", "South Korea": "KOR",
        "Turkiye": "TUR", "Türkiye": "TUR", "Cote d'Ivoire": "CIV",
        "Russian Federation": "RUS", "Iran (Islamic Republic of)": "IRN", "Viet Nam": "VNM",
        "United States of America": "USA", "United Republic of Tanzania": "TZA",
        "Netherlands (Kingdom of the)": "NLD", "Democratic Republic of the Congo": "COD",
    }.items()}
    for e in plans:
        iso2 = plan_idx.get(norm(e.get("country") or "")) or PLAN_ALIASES.get(norm(e.get("country") or ""))
        if iso2 and iso2 in countries:
            e["iso"] = iso2
            e["country_display"] = countries[iso2].get("name")
            e["pledge"] = countries[iso2].get("pledge")
            e["pledge_source"] = countries[iso2].get("pledge_source")
        else:
            e["country_display"] = e.get("country")
            e["pledge"] = None
    by_name = {}
    for e in plans:
        by_name.setdefault((e.get("country") or "").strip().lower(), []).append(e)
    for iso, v in countries.items():
        hit = by_name.get((v.get("name") or "").strip().lower())
        if hit:
            v["plans"] = hit
    print(f"mix {mix_hit} countries, grid {grid_hit} countries, plans {len(plans)} entries")

    signed_isos = [i for i, v in countries.items() if v["pledge"] == "signed"]
    agg = {
        "signatories": sum(1 for i, v in countries.items()
                           if v["pledge"] == "signed" and v.get("pledge_source") == "national"),
        "eu_covered": sum(1 for v in countries.values()
                          if v["pledge"] == "signed" and v.get("pledge_source") == "eu"),
        "individual_eu": sum(1 for v in countries.values()
                             if v["pledge"] == "signed" and v.get("pledge_source") == "national"
                             and v.get("pledge_individual_eu")),
        "total_signed": sum(1 for v in countries.values() if v["pledge"] == "signed"),
        "eu_members": sum(1 for i, v in countries.items()
                          if v["pledge"] == "signed" and v.get("pledge_source") == "eu"),
        "likely": sum(1 for v in countries.values() if v["pledge"] == "likely"),
        "considering": sum(1 for v in countries.values() if v["pledge"] == "considering"),
        "pop_signed": sum(v.get("pop") or 0 for i, v in countries.items() if i in signed_isos),
        "pop_world": sum(v.get("pop") or 0 for v in countries.values()),
        "gdp_signed": sum(v.get("gdp") or 0 for i, v in countries.items() if i in signed_isos),
        "gdp_world": sum(v.get("gdp") or 0 for v in countries.values()),
        "year_max": max((v.get("pop_year") or 0) for v in countries.values()),
    }
    agg["share_pop"] = agg["pop_signed"] / agg["pop_world"] if agg["pop_world"] else None
    agg["share_gdp"] = agg["gdp_signed"] / agg["gdp_world"] if agg["gdp_world"] else None
    # access-weighted: population without electricity in signatory countries
    def without(v):
        if v.get("pop") is None or v.get("access") is None:
            return 0.0
        return v["pop"] * (1 - v["access"] / 100.0)
    agg["unserved_signed"] = sum(without(v) for i, v in countries.items() if i in signed_isos)
    agg["unserved_world"] = sum(without(v) for v in countries.values())

    out = {"meta": {
        "title": "DashElectrify",
        "subtitle": "The 35-by-35 electrification pledge, country by country",
        "pledge_as_of": "2026-11-23",
        "wdi_last_updated": "2026-11-11",
        "sources": [
            "COP31 Presidency pledge registry, status as of 2026-11-23",
            "World Bank World Development Indicators, API, last updated 2026-11-11",
        ],
    }, "agg": agg, "countries": countries, "access_series": access_series,
       "mix_series": {iso: mix[iso] for iso in mix if iso in countries}, "plans": plans}
    json.dump(out, open(os.path.join(ROOT, "data", "dashboard.json"), "w"), separators=(",", ":"))
    print("aggregates:", json.dumps(agg, indent=1)[:400])
    print("countries:", len(countries), "signed:", len(signed_isos))


if __name__ == "__main__":
    main()
