#!/usr/bin/env python3
"""Download the free-licence Wikimedia Commons photos for the Everton chart into ./photos,
with photographer and licence credits in ./photos/credits.json. Safe to re-run: existing files are kept."""
import html, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request

UA = "EvertonChart/1.0 (https://engoyd.github.io/everton/; https://github.com/EngoyD/everton)"
API = "https://en.wikipedia.org/w/api.php"
PEOPLE = [
    ("gary-lineker", "Prime_Minister_Keir_Starmer_hosts_St_George's_Day_Reception_(54470857860)_(cropped).jpg"),
    ("peter-reid", "Peter_Reid_Sunderland_1998small.jpg"),
    ("john-heitinga", "GAE_-_Ajax_-_52788475730_(John_Heitinga).jpg"),
    ("james-mcfadden", "JamesMcFadden_2009_pre-season_cropped.jpg"),
    ("louis-saha", "Louis_Saha_-_53821556907_(cropped).jpg"),
    ("duncan-ferguson", "Duncan_Ferguson,_November_2019.jpg"),
    ("dixie-dean", "Dixie_Dean_(1931).jpg"),
    ("neville-southall", "NevilleSouthall.jpg"),
    ("alan-ball", "Alan_Ball_(cropped).jpg"),
    ("nick-barmby", "Nick_Barmby_23-07-11_1.png"),
    ("phil-neville", "Phil_Neville_2019.jpg"),
    ("andy-gray", "Andy_Gray_2004-10-23.jpg"),
    ("david-unsworth", "David_Unsworth_2017.png"),
    ("john-collins", "John_Collins_Hibs_(cropped).jpg"),
    ("michael-ball", "Michael_Ball_Leicester.png"),
    ("david-weir", "David_Weir_2014.jpg"),
    ("andy-johnson", "Andy_johnson_fulham.jpg"),
    ("pat-jennings", "Pat_Jennings_(2018).jpg"),
    ("anders-limpar", "Anders_Limpar*.jpg"),
    ("gary-speed", "Gary_Speed_2011.jpg"),
    ("bobby-collins", "Bobby_Collins_1959.jpg"),
    ("lucas-neill", "Lucas_Neill.jpg"),
    ("andrei-kanchelskis", "Kanchelskis_Andrei.jpg"),
    ("bruce-rioch", "Bruce_Rioch.jpg"),
    ("aiden-mcgeady", "AidenMcGeadyIreland.png"),
    ("martin-keown", "Martin_Keown_2015.jpg"),
    ("norman-whiteside", "Norman_whiteside_head_crop.jpg"),
    ("jesper-blomqvist", "Jesper_Blomqvist.jpg"),
    ("richard-dunne", "FIFA_WC-qualification_2014_-_Austria_vs_Ireland_2013-09-10_-_Richard_Dunne_01.jpg"),
    ("niclas-alexandersson", "Niclas_Alexandersson_2006.jpg"),
    ("brian-labone", "Brian_Labone_México_70.png"),
    ("keith-newton", "Keith_Newton_México_70.png"),
    ("graeme-sharp", "Graeme_Sharp_2018.jpg"),
    ("leighton-baines", "Baines_Leighton_126176_(cropped).jpg"),
    ("lee-carsley", "Lee_Carsley.png"),
    ("dick-roose", "Roose.jpg"),
    ("kevin-kilbane", "Kevin_Kilbane_(13938890939).jpg"),
    ("lars-jacobsen", "Lars_Jacobsen_20120609.jpg"),
    ("joseph-yobo", "JosephYobo'13_(cropped).JPG"),
    ("daniel-amokachi", "Daniel_Amokachi.jpg"),
    ("leon-osman", "Leon_Osman_Bohemians_V_Everton_(44_of_51).jpg"),
    ("don-hutchison", "Hutchison,_Don.jpg"),
    ("pat-nevin", "Pat_Nevin_2017.jpg"),
    ("darron-gibson", "Darron_Gibson_2012_Sopot.jpg"),
    ("joleon-lescott", "Joleon_Lescott_8696_(15441498930).jpg"),
    ("kevin-mirallas", "Kevin_Mirallas.jpg"),
    ("jack-sharp", "1193388_Jack_Sharp.jpg"),
    ("harry-makepeace", "Everton_fa_cup_1906_(Makepeace).jpg"),
    ("phil-jagielka", "Phil_Jagielka_2015-07-18_1.jpg"),
    ("jacky-robertson", "RobertsonJT.jpg"),
    ("edgar-chadwick", "Player_chadwick.jpg"),
    ("pat-van-den-hauwe", "PAT_VAN_DEN_HAUWE_2018.jpg"),
    ("maarten-stekelenburg", "GAE_-_Ajax_-_52788476880_(Maarten_Stekelenburg).jpg"),
    ("gerry-peyton", "Gerry_Peyton_(cropped).jpg"),
    ("marc-hottiger", "Marc_Hottiger.JPG"),
    ("ashley-williams", "AUT_vs._WAL_2016-10-06_(128).jpg"),
    ("ben-howard-baker", "Benjamin_Howard_Baker_1920.jpg"),
    ("bill-lacey", "Bill_Lacey_(1914).png"),
    ("marouane-fellaini", "Marouane_Fellaini_2018.jpg"),
    ("frank-jefferis", "Frank_Jefferis.jpg"),
    ("jan-mucha", "JanMucha2010.jpg"),
    ("james-mccarthy", "1_james_mccarthy_everton_2015_(cropped).jpg"),
    ("diniyar-bilyaletdinov", "Spar-Rub15_(7).jpg"),
    ("billy-scott", "Everton_fa_cup_1906_(Scott).jpg"),
    ("nikica-jelavic", "Nikica_Jelavić_with_West_Ham_United_in_2015.jpg"),
    ("jimmy-dunn", "Wembley_wizards_duke_york_(Dunn).jpg"),
    ("jimmy-oneill", "JimmyONeill.jpg"),
    ("sandy-young", "Everton_fa_cup_1906_(Young).jpg"),
    ("jimmy-settle", "Everton_fa_cup_1906_(Settle).jpg"),
    ("jack-rodwell", "Jack_Rodwell_2013_(3x4_cropped).jpg"),
    ("bob-howarth", "Preston_north_end_art_(Howarth).jpg"),
    ("bert-freeman", "Bert_Freeman.jpg"),
    ("gylfi-sigur-sson", "ISL-HRV_(21)_(cropped).jpg"),
    ("fred-geary", "Fred_Geary.jpg"),
    ("phil-griffiths", "Phil_Griffiths.jpg"),
    ("james-rodriguez", "Argentina_-_Colombia_2022_(28)_(cropped_2).jpg"),
    ("cuco-martina", "Cuco_Martina_-_Audi-quattro-Cup_(2015).jpg"),
    ("joshua-king", "Chelsea_0_Bournemouth_1_(cropped).jpg"),
    ("lucas-digne", "Lucas_Digne_France_v_Norway_26_June_26-043.jpg"),
    ("cenk-tosun", "Cenk_Tosun_in_2023.jpg"),
    ("muhamed-besic", "Muhamed_Besic_2014-05-03.jpg"),
    ("allan", "Allan_Marques_Loureiro_in_Everton_(cropped).jpg"),
    ("idan-tal", "Idan_Tal.jpg"),
    ("idrissa-gueye", "Idrissa_Gueye_(cropped).jpg"),
    ("enner-valencia", "Enner_Valencia_Cote_D'Ivoire_v_Ecuador_14_June_2026-95.jpg"),
    ("christian-atsu", "Christian_Atsu_20150331_Mali_vs_Ghana_039_(cropped).jpg"),
    ("kurt-zouma", "Kurt_Zouma_West_Ham.jpg"),
    ("charlie-parry", "Parry_180395.jpg"),
    ("michael-keane", "Michael_Keane_2017.jpg"),
    ("davy-klaassen", "GAE_-_Ajax_-_52788472780_(Davy_Klaassen).jpg"),
    ("ramiro-funes-mori", "SM-Villareal_(3).jpg"),
    ("oumar-niasse", "Loko_skndrb_10.jpg"),
    ("john-stones", "John_Stones_England_v_Ghana_23_June_2026-038.jpg"),
    ("conor-coady", "Conor_Coady_30082025_(1).jpg"),
    ("abdoulaye-doucoure", "Stade_rennais_-_Le_Havre_AC_20150708_40.JPG"),
    ("jordan-pickford", "Jordan_Pickford_England_v_Ghana_23_June_2026-316_(cropped).jpg"),
    ("demarai-gray", "Demarai_Gray_August_2014.png"),
    ("nikola-vlasic", "Nikola_Vlasic_Croatia_v_Portugal_2_July_2026-189.jpg"),
    ("dominic-calvert-lewin", "Dominic_Calvert-Lewin_13092025_(5).jpg"),
    ("ben-godfrey", "Ben_Godfrey_2019-05-06_1.jpg"),
    ("alex-iwobi", "Issa_Diop,_Alex_Iwobi_and_Antonee_Robinson_04032026_(1)_(cropped).jpg"),
    ("henry-onyekuru", "Henry_Onyekuru,_2018.jpg"),
    ("moise-kean", "FC_Zenit_Saint_Petersburg_vs._Juventus,_20_October_2021_64_-_Moise_Kean_(cropped).jpg"),
    ("antonee-robinson", "Antonee_Robinson_Australia_v_USA_19_June_2026-24_(cropped).jpg"),
    ("orel-mangala", "Orel_mangala.jpg"),
    ("james-garner", "James_Garner_2025.jpg"),
    ("mark-travers", "Mark_Travers_29122024_(2).jpg"),
    ("jesper-lindstr-m", "2022128173607_2022-05-08_Fussball_Eintracht_Frankfurt_vs_Borussia_Mönchengladbach_-_Sven_-_1D_X_MK_II_-_0635_-_AK8I7370_(Jesper_Lindstrøm_cropped).jpg"),
    ("beto", "Fulham_v_Everton_10052025_(7)_(Beto).jpg"),
    ("jarrad-branthwaite", "Celebration!_(54493257432)_(Jarrad_Branthwaite).jpg"),
    ("nathan-patterson", "Nathan_Patterson_Scotland_v_Bolivia_6_June_2026-58.jpg"),
    ("armando-broja", "Armando_Broja_29112025_(2).jpg"),
    ("amadou-onana", "Amadou_Onana_USMNT_v_Belgium_Mar_28_2026-96_(cropped).jpg"),
    ("iliman-ndiaye", "Iliman_Ndiaye_France_v_Senegal_16_June_2026-243.jpg"),
    ("jake-obrien", "Jake_O'Brien_in_2024.png"),
    ("bryan-oviedo", "Bryan_Oviedo_20160116.jpg"),
    ("wayne-rooney", "Wayne_Rooney_(50121495731)_(cropped).jpg"),
    ("tim-howard", "Tim_Howard_2023.jpg"),
    ("tommy-lawton", "Tommy_Lawton_(ca.1951).jpg"),
    ("yakubu-ayegbeni", "Yakubu_in_2013_(cropped).jpg"),
    ("tomasz-radzinski", "Tomasz_Radzinski_2004.jpg"),
    ("thomas-myhre", "Thomas_Myhre_04.jpg"),
    ("tim-cahill", "Tim_Cahill_(53557484101).jpg"),
    ("robert-warzycha", "Robert_Warzycha_Crew.jpg"),
    ("tony-cottee", "Tony_Cottee_at_Tony_Carr's_testimonial.jpg"),
    ("simon-davies", "Simon_Davies_Wales_October_2006.jpg"),
    ("tommy-wright", "Tommy_wright_figurita.jpg"),
    ("steven-pienaar", "Steven_Pienaar_2015.jpg"),
    ("tobias-linderoth", "Tobias_Linderoth_2006.jpg"),
    ("steven-naismith", "Steven_Naismith_(cropped).jpg"),
    ("victor-anichebe", "Victor_Anichebe_Bohemians_V_Everton_(5_of_51).jpg"),
    ("stuart-mccall", "Stuart_mccall.jpg"),
    ("slaven-bilic", "Slaven_Bilić.jpg"),
    ("segundo-castillo", "Segundo_Castillo.png"),
    ("terry-phelan", "Terry_Phelan_SUFC.png"),
    ("val-harris", "Ireland_1914_(Harris).png"),
    ("walter-abbott", "Walter_Abbott.jpg"),
    ("william-balmer", "Everton_fa_cup_1906_(Balmer).jpg"),
    ("wally-boyes", "Phillips_card_boyes.jpg"),
    ("yannick-bolasie", "Yannick_Bolasie2.jpg"),
    ("salomon-rondon", "Salomón_Rondón_2021.jpg"),
    ("teddy-hughes", "Edward_\"Ted\"_Hughes_(cropped).jpg"),
    ("romelu-lukaku", "Romelu_Lukaku_Belgium_v_USA_6_July_2026-038.jpg"),
    ("seamus-coleman", "Nair_Tiknizyan,_Seamus_Coleman,_Festy_Ebosele_YantsImages_-_Asatur_Yesayants_668_(cropped).jpg"),
    ("shane-duffy", "Shane_Duffy_2018.jpg"),
    ("smart-arridge", "Smart-Arridge.jpg"),
    ("ross-barkley", "Ross_Barkley_in_2019.jpg"),
    ("robin-olsen", "SWE-SWI_(8)_(cropped).jpg"),
    ("richarlison", "Richarlison_é_homenageado_na_ALES_(10.July.2019)_08_(cropped).jpg"),
    ("yerry-mina", "Yerry_Mina,_Colombia_NT_presidential_send-off,_Jun_2026.jpg"),
    ("vitaliy-mykolenko", "Виталий_Миколенко_—_1182449_(cropped).jpg"),
    ("david-moyes", "David_Moyes_2025.jpg"),
    ("frank-lampard", "Frank_Lampard_2019.jpg"),
    ("rafael-benitez", "Shahter-Reak_M_2015_(2).jpg"),
    ("ronald-koeman", "Матч_«Динамо»_-_«Барселона»_0-4._24_ноября_2020_года_—_1166990_(Ronald_Koeman).jpg"),
    ("walter-smith", "Walter_Smith_(cropped).jpg"),
    ("carlo-ancelotti", "Carlo_Ancelotti_Brazil_V_Morocco_13_June_2026-47.jpg"),
    ("mikel-arteta", "Arsenal_v_Everton_-_52223142689_(cropped).jpg"),
    ("sam-allardyce", "Big_Sam_Allardyce_signs_autographs_for_fans_October_2014.jpg"),
    ("john-houlding", "John_Houlding.jpg"),
    ("roberto-martinez", "Roberto_Martínez_USMNT_v_Portugal_Mar_31_2026-35.jpg"),
    ("sean-dyche", "Sean_Dyche_-_Toffee_TV_EFC.png"),
    ("farhad-moshiri", "Moshiribagnes.jpg"),
    ("dick-molyneux", "D_Molyneux.jpg"),
    ("marco-silva", "Marco_Silva_20042025_(2)_(cropped).jpg")
]

def get(url, tries=6):
    for i in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and i < tries - 1:
                wait = int(e.headers.get("Retry-After") or 0) or 5 * (i + 1)
                print(f"    Wikimedia asked us to slow down; waiting {wait}s")
                time.sleep(wait)
                continue
            raise

def text(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", h or ""))).strip()

os.makedirs("photos", exist_ok=True)
meta = {}
print("Looking up licences...")
for i in range(0, len(PEOPLE), 40):
    batch = PEOPLE[i:i + 40]
    titles = ["File:" + f.replace("_", " ") for _, f in batch]
    q = urllib.parse.urlencode({"action": "query", "format": "json", "formatversion": "2", "prop": "imageinfo",
                                "iiprop": "url|extmetadata", "iiurlwidth": "330",
                                "iiextmetadatafilter": "Artist|LicenseShortName", "titles": "|".join(titles)})
    data = json.loads(get(API + "?" + q))["query"]
    norm = {n["from"]: n["to"] for n in data.get("normalized", [])}
    pages = {p["title"]: p["imageinfo"][0] for p in data.get("pages", []) if p.get("imageinfo")}
    for (k, f), t in zip(batch, titles):
        ii = pages.get(norm.get(t, t))
        if ii:
            meta[k] = ii
    time.sleep(1)

credits, failed = {}, []
for n, (k, ii) in enumerate(meta.items(), 1):
    url = ii.get("thumburl") or ii["url"]
    ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
    ext = ".jpg" if ext in ("", ".jpeg") or ext not in (".jpg", ".png", ".webp", ".gif") else ext
    out = f"photos/{k}{ext}"
    try:
        if not os.path.exists(out):
            body = get(url)
            with open(out, "wb") as fh:
                fh.write(body)
            time.sleep(0.5)
        em = ii.get("extmetadata", {})
        artist = text(em.get("Artist", {}).get("value"))
        lic = text(em.get("LicenseShortName", {}).get("value"))
        credits[k] = {"img": out, "page": ii.get("descriptionurl", ""),
                      "credit": f"Photo: {artist or 'unknown author'}. {lic or 'Free licence'}, via Wikimedia Commons"[:200]}
        print(f"  [{n}/{len(meta)}] {k}")
    except Exception as e:
        failed.append(k)
        print(f"  [{n}/{len(meta)}] {k} FAILED: {e}")

with open("photos/credits.json", "w", encoding="utf-8") as fh:
    json.dump(credits, fh, ensure_ascii=False, indent=1)
print(f"\nDone: {len(credits)} photos saved in ./photos, {len(failed)} failed, {len(PEOPLE) - len(meta)} not found on Wikipedia.")
if failed:
    print("Re-run the script to retry the failures: " + ", ".join(failed))
