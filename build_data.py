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
def parse_pledge():
    html = open(os.path.join(ROOT, "src", "pledge_source.html"), encoding="utf-8").read()
    tables = re.findall(r"<table>(.*?)</table>", html, re.S)

    def rows(tbl):
        out = []
        for tr in re.findall(r"<tr>(.*?)</tr>", tbl, re.S):
            cells = [
                re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", c)).strip()
                for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)
            ]
            if cells:
                out.append(cells)
        return out

    signed, watch = [], []
    for i, t in enumerate(tables):
        r = rows(t)
        if not r:
            continue
        head = [c.lower() for c in r[0]]
        body = r[1:] if "country" in " ".join(head) else r
        for row in body:
            if not row or not row[0]:
                continue
            if i == 0:
                signed.append({"name": row[0], "region": row[1] if len(row) > 1 else "",
                               "date": row[2] if len(row) > 2 else ""})
            else:
                watch.append({"name": row[0], "note": " ".join(row[1:])[:120]})

    # the sheet counts the EU once for the bloc; 24 member states ride with it
    eu_members = [
        "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czechia", "Denmark",
        "Estonia", "Finland", "France", "Germany", "Greece", "Hungary", "Ireland",
        "Italy", "Latvia", "Lithuania", "Luxembourg", "Malta", "Netherlands",
        "Poland", "Portugal", "Romania", "Slovakia", "Slovenia", "Spain", "Sweden",
    ]
    individual_eu = [r[0] for r in rows(tables[1])[1:]] if len(tables) > 1 else []
    return signed, watch, eu_members, individual_eu


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
        yr = int(row.get("date"))
        if not iso or val is None:
            continue
        if iso not in latest or yr > latest[iso][0]:
            latest[iso] = (yr, float(val))
        series.setdefault(iso, {})[yr] = float(val)
    return latest, series


def main():
    signed, watch, eu_members, individual_eu = parse_pledge()
    print(f"pledge: {len(signed)} national rows, {len(watch)} watch rows")

    status = {}
    for e in signed:
        iso = to_iso(e["name"])
        if not iso:
            print("  unmapped signatory:", e["name"])
            continue
        status[iso] = {"status": "signed", "date": e["date"], "region": e["region"],
                       "source": "national",
                       "individual_eu": e["name"].strip().lower() in {n.lower() for n in individual_eu}}
    for name in eu_members:
        iso = to_iso(name)
        if iso and iso not in status:
            status[iso] = {"status": "signed", "date": "EU bloc", "region": "Europe",
                           "source": "eu"}
    for e in watch:
        iso = to_iso(e["name"])
        if iso and iso not in status:
            note = (e.get("note") or "").lower()
            st = "likely" if "likely" in note else ("considering" if "consider" in note else "considering")
            status[iso] = {"status": st, "date": "", "region": "", "source": "watch"}

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
    countries = {}
    for iso, vals in data.items():
        if iso.startswith("__"):
            continue
        st = status.get(iso, {"status": "none"})
        countries[iso] = {**vals, "pledge": st.get("status", "none"),
                          "pledge_date": st.get("date", ""),
                          "pledge_source": st.get("source", ""),
                          "pledge_individual_eu": bool(st.get("individual_eu"))}

    # attach names from countries.geo.json for anything the WB missed
    geo = json.load(open(os.path.join(ROOT, "data", "countries.geo.json")))
    names = {}
    for f in geo["features"]:
        p = f["properties"]
        names[(p.get("iso") or "").upper()] = p.get("name")

    for iso, meta in status.items():
        if iso not in countries:
            countries[iso] = {"pledge": meta["status"], "pledge_date": meta.get("date", ""),
                              "pledge_source": meta.get("source", "")}
    for iso, meta in status.items():
        if iso in countries and iso in DOTS:
            countries[iso]["dot"] = DOTS[iso]
    for iso in countries:
        countries[iso]["name"] = names.get(iso, iso)

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
        "pledge_as_of": "2026-11-20",
        "wdi_last_updated": "2026-11-11",
        "sources": [
            "COP31 Presidency signatory sheet, as captured 2026-11-20 06:02 TRT",
            "World Bank World Development Indicators, API, last updated 2026-11-11",
        ],
    }, "agg": agg, "countries": countries, "access_series": access_series}
    json.dump(out, open(os.path.join(ROOT, "data", "dashboard.json"), "w"), separators=(",", ":"))
    print("aggregates:", json.dumps(agg, indent=1)[:400])
    print("countries:", len(countries), "signed:", len(signed_isos))


if __name__ == "__main__":
    main()
