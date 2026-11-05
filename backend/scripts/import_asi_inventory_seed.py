"""Idempotently import a manually checked subset of ASI's public monument inventory.

The seed is intentionally limited to source-listed identity/location facts. It does
not infer deity, date, coordinates, architecture, rituals, or visitor information.
Run from backend with: python scripts/import_asi_inventory_seed.py
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
CATALOGUE_PATH = DATA / "catalogue.json"
DOCUMENTS_PATH = DATA / "raw" / "temple_sources.json"
ASI_URL = "https://asi.nic.in/pdf/CPM_List.pdf"
ASI_TITLE = "Centrally Protected Monuments/Sites: State-wise and Circle-wise"
PUBLISHER = "Archaeological Survey of India"
CHECKED = "2026-11-04"

# State | district | locality | exact entry/name from the ASI inventory.
ROWS = r"""
Andhra Pradesh|Anantapuramu|Gorantla|Madhavaraya temple (Old Vishnu temple)
Andhra Pradesh|Anantapuramu|Hemavati|Group of old temples
Andhra Pradesh|Anantapuramu|Kambaduru|Mallikarjuna (Siva) temple
Andhra Pradesh|Anantapuramu|Lepakashi|Veerabhadra temple
Andhra Pradesh|Anantapuramu|Lepakashi|Basavannah temple
Andhra Pradesh|Anantapuramu|Rayadurg|Palace and two temples of Rama and Krishna
Andhra Pradesh|Anantapuramu|Tadpatri|Chintalarayaswami temple
Andhra Pradesh|Anantapuramu|Tadpatri|Rameswaraswami temple
Andhra Pradesh|Chittoor|Gudimallam|Parasuramesvara temple
Andhra Pradesh|Chittoor|Kalakada|Palliswara mudaya Mahadeva temple
Andhra Pradesh|Chittoor|Mangapuram (Hamlet of Mittapalam)|Venkateswara Vishnu temple
Andhra Pradesh|Chittoor|Sompalle|Chennakeswaraswami temple
Andhra Pradesh|East Godavari|Biccavolu|Gollingeswara group of temples
Andhra Pradesh|East Godavari|Biccavolu|Nakkalagudi
Andhra Pradesh|East Godavari|Biccavolu|Veerabhadra temple
Andhra Pradesh|Vizianagaram|Sarapalli (Sarapalle)|The old temple (Dibbesvarasvami temple)
Assam|Biswanath|Biswanathghat|Bordole temple
Assam|Biswanath|Dhandi (Gohpur)|Dhandi temple
Assam|Cachar|Khaspur|The temple of Ranachandi
Assam|Goalpara|Sri Suryapahar|Shri Surya Pahar Ruins, Dasabhaja Devasthan
Assam|Golaghat|Negheriting|Sivadol
Assam|Kamrup|Hajo|Shri Shri Hayagriva Madhava temple
Assam|Kamrup|Hajo|Shri Shri Kedar temple
Assam|Kamrup|Hajo|Shri Shri Ganesh temple
Assam|Kamrup|Hajo|Shri Shri Kameshwar temple
Assam|Sivasagar|Gaurisagar|Bisdol (Bishnudol)
Assam|Sivasagar|Gaurisagar|Devidol
Assam|Sivasagar|Gaurisagar|Sivadol
Assam|Sivasagar|Joysagar|Bisdol (Bishnudol)
Assam|Sivasagar|Joysagar|Devidol
Assam|Sivasagar|Joysagar|Ranganath dole
Assam|Sivasagar|Joysagar|Sivadol
Assam|Sivasagar|Sibsagar|Bishnu dole
Assam|Sivasagar|Sibsagar|Debi dole
Assam|Sivasagar|Sibsagar|Siva dole
Assam|Sonitpur|Tezpur|The mound and ruins of the stone temple at Parbatiya
Himachal Pradesh|Chamba|Bharmaur|Ganesh Temple Bharmaur
Himachal Pradesh|Chamba|Bharmaur|Laxmi (Lakhan) Devi Temple Bharmaur
Himachal Pradesh|Chamba|Bharmaur|Mani Mahesh Temple Bharmaur
Himachal Pradesh|Chamba|Bharmaur|Narsingh Temple Bharmaur
Himachal Pradesh|Chamba|Chamba|Champavati Temple
Himachal Pradesh|Chamba|Chamba|Shri Bajreshwari Temple, Bhardiath
Himachal Pradesh|Chamba|Chamba|Shri Bansi Gopal Temple
Himachal Pradesh|Chamba|Chamba|Shri Chamunda Devi Temple
Himachal Pradesh|Chamba|Chamba|Shri Hari Rai Temple
Himachal Pradesh|Chamba|Chamba|Shri Lakshmi Narayan group of Temples, Muhalla Hattnala
Himachal Pradesh|Chamba|Chamba|Shri Sita Ram Temple Muhalla Bangotu
Himachal Pradesh|Chamba|Chhatrari|Sri Shakti Devi Temple
Himachal Pradesh|Kangra|Ashapuri|Temple at Asapuri
Himachal Pradesh|Kangra|Baijnath|Temple of Baijnath
Himachal Pradesh|Kangra|Baijnath|Temple of Sidhnath
Himachal Pradesh|Kangra|Masroor|Monolithic Temples at Masrur with sculptures lying in and outside them
Himachal Pradesh|Kullu|Bajaura|Temple of Basheshar Mahadeo at Hat
Himachal Pradesh|Kullu|Dassal|Temple of Gaurishankar with sculptures
Himachal Pradesh|Kullu|Jagatsukh|A Miniature stone Saiva Temple at Jagat Sukh
Himachal Pradesh|Kullu|Manali|Hidimba Devi Temple
Himachal Pradesh|Kullu|Naggar|Temple of Gaurishankar with its sculptures
Himachal Pradesh|Lahaul & Spiti|Udaipur (Lahaul)|Mirkula Devi Temple
Himachal Pradesh|Mandi|Mandi|Panchvaktra Temple
Himachal Pradesh|Mandi|Mandi|Temple of Trillokinath
Jammu and Kashmir|Anantnag|Ranbelpur / Ranbirsinghpur|Ancient temple of Martand
Jammu and Kashmir|Baramulla|Bandi|Detha Mandir
Jammu and Kashmir|Baramulla|Pattan|Sankaragaurisvara temple
Jammu and Kashmir|Baramulla|Pattan|Sugandesha Temple
Jammu and Kashmir|Baramulla|Tapparwaripora|Partapswami temple with four Subsidiary shrines
Karnataka|Chamarajanagar|Gundlupet|Vijayanarayana Temple
Karnataka|Chamarajanagar|Hale Alur|Arkesvara Temple
Karnataka|Chamarajanagar|Narasamangala|Ramesvara Temple
Karnataka|Chamarajanagar|Yelandur|Gaurisvara Temple
Karnataka|Chikkaballapur|Nandi|Bhoganandisvara Temple
Karnataka|Chikkamagaluru|Amrithapura|Amritesvara Temple
Karnataka|Chikkamagaluru|Belavadi|Viranarayana Temple
Karnataka|Chikkamagaluru|Sringeri|Vidyasankara Temple
Karnataka|Chitradurga|Ramesvara Hill|Inscription and Jatingi Rameswar Temple
Karnataka|Chitradurga|Siddepura|Akka Tangi Temple
Karnataka|Davangere|Harihar|Hariharesvara Temple
Karnataka|Hassan|Arakere|Channakesva Temple
Karnataka|Hassan|Arsikere|Isvara Temple
Karnataka|Hassan|Belur|Kesava Temple and Inscriptions
Karnataka|Hassan|Doddgaddavalli|Lakshmi devi Temple
Karnataka|Hassan|Halebidu|Hoysalesvara Temple
Karnataka|Mysuru|Somanathapura|Keshava Temple
Karnataka|Bagalkot|Pattadakal|Virupaksha Temple
Karnataka|Bagalkot|Pattadakal|Mallikarjuna Temple
Karnataka|Bagalkot|Pattadakal|Papanatha Temple
Karnataka|Bagalkot|Aihole|Durga Temple
Karnataka|Bagalkot|Aihole|Lad Khan Temple
Karnataka|Bagalkot|Badami|Cave Temples
Kerala|Palakkad|Pattambi|Siva temple at Netrimangalam
Kerala|Thiruvananthapuram|Tiruvallam|Temples of Parasurama, Brahma, Siva and Matsya
Kerala|Thrissur|Kadavallur|Vishnu Temple at Kadavallur
Kerala|Thrissur|Peruvanam|Siva Temple complex, Peruvanam
Kerala|Thrissur|Triprayar|Sriramaswami temple
Madhya Pradesh|Ashok Nagar|Budhichanderi|Jain Temples 1 to 5
Madhya Pradesh|Ashok Nagar|Kadwaha|Temples 2 to 7
Madhya Pradesh|Ashok Nagar|Thoban|Andhakuan Group of Temples
Madhya Pradesh|Ashok Nagar|Thoban|Gargaj and Mahadev Ghat Group of Temples
Madhya Pradesh|Ashok Nagar|Thoban|Hanuman Marhi Group of Temples
Madhya Pradesh|Ashok Nagar|Thoban|Sitamarhi Group of Temples
Madhya Pradesh|Burhanpur|Asirgarh|Mahadeo Temple with its compound near the inspection Bunglow
Madhya Pradesh|Bhind|Kherat|Brick Temples (two)
Madhya Pradesh|Gwalior|Gwalior|Sas Bahu Temples
Maharashtra|Ahmednagar|Bemini|Hemadpanthi Temple
Maharashtra|Ahmednagar|Bhingar Cantonment|Jain Temple
Maharashtra|Yeotmal|Tapona|Hemadpanthi Temple of Shree Mahadev (Taponeshwar)
Maharashtra|Kolhapur|Kopeshwar|Kopeshwar Temple
Odisha|Bolangir|Jharial|Chausatti Jogini temple together with three minor shrines
Odisha|Bolangir|Ranipur-Jharial|Group of Temples
Odisha|Boudh|Gandharadhi|Temples of Nilamadhava and Siddheswara
Odisha|Boudh|Boudh Town|Paschima-Somanatha and Kapilesvara Temples
Odisha|Gajapati|Mahendragiri|Bhima Temple
Odisha|Gajapati|Mahendragiri|Kunti Temple
Odisha|Gajapati|Mahendragiri|Yudhishthira Temple
Odisha|Ganjam|Kottakolla (Buddha Khol)|Monuments of Gangadhara Swami
Odisha|Ganjam|Kottakolla (Buddha Khol)|Jagadeswara Swami
Odisha|Khurda|Bhubaneswar|Bhaskareswar Temple
Odisha|Khurda|Bhubaneswar|Brahmeswar Temple with minor shrines
Odisha|Khurda|Bhubaneswar|Ananta Basudeva Temple
Odisha|Khurda|Bhubaneswar|Baitala Temple
Odisha|Khurda|Bhubaneswar|Chitrakarini Temple
Odisha|Khurda|Bhubaneswar|Jameswar Temple
Odisha|Khurda|Bhubaneswar|Lingaraj Temple
Odisha|Khurda|Bhubaneswar|Maitreswar Temple
Odisha|Khurda|Bhubaneswar|Makareswar Temple
Odisha|Khurda|Bhubaneswar|Markandeswar Temple
Odisha|Khurda|Bhubaneswar|Mukteswar Temple
Odisha|Khurda|Bhubaneswar|Parsurameswar Temple
Odisha|Khurda|Bhubaneswar|Siddheswar Temple
Odisha|Khurda|Bhubaneswar|Kapileswar Temple
Odisha|Puri|Konark|Sun Temple
Tamil Nadu|Villupuram|Gingee|Venketaramana Temple
Tamil Nadu|Villupuram|Narasingarayanpettai|Pattabirama Temple
Tamil Nadu|Villupuram|Dalavanur|Rock cut Pallava Temple
Tamil Nadu|Villupuram|Kilmavilangai|Pallava rock cut shrine
Tamil Nadu|Villupuram|Mandagapattu|Rock cut Pallava temple
Tamil Nadu|Villupuram|Panamalai|Talagiriswara temple
Tamil Nadu|Villupuram|Ennayiram|Sri Azhagiya Narasimma perumal temple
Tamil Nadu|Villupuram|Brahmadesam|Sri Pataleswara Temple
Tamil Nadu|Villupuram|Brahmadesam|Sri Brahmapuriswara Temple
Tamil Nadu|Villupuram|Sendamangalam|Sri Apathsahayeswara Temple
Tamil Nadu|Kanchipuram|Kanchipuram|Vaikuntaperumal temple
Tamil Nadu|Kanchipuram|Kanchipuram|Kailasanatha temple
Tamil Nadu|Kanchipuram|Kanchipuram|Piravathanesvara temple
Tamil Nadu|Kanchipuram|Kanchipuram|Iravathanesvara temple
Tamil Nadu|Kanchipuram|Kanchipuram|Jvarahesvara temple
Tamil Nadu|Kanchipuram|Kanchipuram|Mathangesvara temple
Tamil Nadu|Kanchipuram|Kanchipuram|Muktesvara temple
Tamil Nadu|Kanchipuram|Tiruvidanthai|Nithya kalyanaswami Temple
Tamil Nadu|Kanchipuram|Vayalur|Tirupuleswarar Temple
Tamil Nadu|Namakkal|Namakkal|Ranganathaswamy temple
Tamil Nadu|Namakkal|Namakkal|Narasimhaswamy temple
Tamil Nadu|Coimbatore|Tirumuruganpoondi|Muruganatha temple
Tamil Nadu|Dharmapuri|Adiyamankottai|Chennarayaperumal temple
Tamil Nadu|Karur|Srinivasanallur|Korangunatha temple
Tamil Nadu|Ariyalur|Gangaikondacholapuram|Brihadisvara Temple
Tamil Nadu|Thanjavur|Darasuram|Airavatesvara Temple
Rajasthan|Alwar|Neelkanth|Siva temple
Rajasthan|Baran|Atru or Ganesh Ganj|Ruins of Temples
Rajasthan|Baran|Baran|Temple (12 century)
Rajasthan|Bharatpur|Bayana|Usha Mandir
Rajasthan|Bharatpur|Kaman|Chaurasi Khamba temple
Rajasthan|Bhilwara|Bijolia|Mahakal and two other temples
Rajasthan|Chittorgarh|Badoli|Temple of Shiv, Ganesh and adjoining Kund
Telangana|Jagulamba Gadwal|Alampur|Alampur Temples
Telangana|Mulugu|Palampet|Ramappa temple
Telangana|Warangal-Urban|Hanamkonda|Thousand Pillared temple
Gujarat|Mehsana|Modhera|Sun temple, Surya kind with adjoining other temples and loose sculptures
Gujarat|Kheda|Sarnal|Temple of Galteshwar
Gujarat|Mehsana|Asoda|Jasmalnathji Mahadev temple
Gujarat|Mehsana|Khandosan|Hingloji Mata temple
Gujarat|Mehsana|Palodar|Malai Mata temple
Gujarat|Mehsana|Piludara|Sitamata temple
Gujarat|Mehsana|Piludara|Torana with a Surya Temple
Gujarat|Mehsana|Sunak|Nilkantheswar Mahadev temple
Gujarat|Mehsana|Sunak|Sivai Mata temple
Uttarakhand|Almora|Dwarahat|Gujardeo Temple
Uttarakhand|Almora|Dwarahat|Badrinath group of Temples
Uttarakhand|Almora|Dwarahat|Bandeo Temple
Uttarakhand|Almora|Dwarahat|Kacheri group of Temple
Uttarakhand|Almora|Dwarahat|Kutumbari Temple
Uttarakhand|Almora|Dwarahat|Maniyan group of Temples
Uttarakhand|Almora|Katarmal|Surya Temple
Uttarakhand|Almora|Jageshwar|Dandeshwar Temple
Uttarakhand|Almora|Jageshwar|Jageshwar Temple
Uttarakhand|Almora|Jageshwar|Kuber Temple
Uttarakhand|Almora|Jageshwar|Mritunjaya Temple
Uttarakhand|Almora|Jageshwar|Nanda Devi or Nau Durga
Uttarakhand|Bageshwar|Baijnath or Vaidyanath|Group of ancient temples, main shrine of Siva and subsidiary shrines
Uttarakhand|Bageshwar|Talli Hat, Mound Katyur|Lakshmi Narayan, Rakshas Deval and Satya Narayan Temples
Uttarakhand|Chamoli|Adibadri|Remains of sixteen temples
Uttarakhand|Chamoli|Gopeshwar|Rudranath temple
Uttarakhand|Chamoli|Pandukeshwar|Two Temple
Uttarakhand|Champawat|Champawat|Group of Baleshwar Temples
Uttarakhand|Dehradun|Hanol|Temple sacred to Mahasu
West Bengal|Bankura|Bahulara|Ancient Temple
West Bengal|Bankura|Birsingha|Brindaban Chandra Temple
West Bengal|Bankura|Birsingha|Radha Damodar Temple
West Bengal|Purulia|Banda|Old Temple at Banda
West Bengal|Midanapur|Pathra|Dharmaraj Temple
West Bengal|Midanapur|Pathra|Temples of Bandyopadhyay Family
West Bengal|Midanapur|Pathra|Sitala Temples
West Bengal|Midanapur|Pathra|Nava Ratna Temple Complex
West Bengal|Nadia|Palpara|Temple
West Bengal|North 24 Parganas|Barrakpore-Khardah|26 Shiva Temples
"""

def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")

def stable_temple_id(state: str, district: str, locality: str, name: str) -> str:
    identity = "|".join((state.casefold(), district.casefold(), locality.casefold(), name.casefold()))
    return f"asi_{slug(state)[:12]}_{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:16]}"

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def save(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def meaningful_name_tokens(value: str) -> set[str]:
    stop = {"temple", "the", "at", "of", "and", "group", "site", "monuments"}
    return {token for token in re.findall(r"[a-z0-9]+", value.casefold()) if token not in stop}

def main() -> None:
    catalogue = load(CATALOGUE_PATH)
    documents = load(DOCUMENTS_PATH)
    initial_catalogue_count, initial_document_count = len(catalogue), len(documents)
    by_id = {item["id"]: item for item in catalogue}
    by_fingerprint = {
        (name.casefold(), str(item.get("state", "")).casefold(), str(item.get("district", "")).casefold(), str(item.get("area", "")).casefold())
        for item in catalogue for name in item.get("names", [])
    }
    document_ids = {item.get("document_id") for item in documents}
    added = []
    rich_added = []
    rich_records_added = []
    duplicates = []
    duplicate_cleanup = False
    for line in ROWS.strip().splitlines():
        state, district, locality, official_name = (part.strip() for part in line.split("|", 3))
        temple_id = stable_temple_id(state, district, locality, official_name)
        fingerprint = (official_name.casefold(), state.casefold(), district.casefold(), locality.casefold())
        same_site = next((item for item in catalogue if
            item.get("id") != temple_id
            and
            str(item.get("state") or "").casefold() == state.casefold()
            and str(item.get("district") or "").casefold() == district.casefold()
            and str(item.get("area") or item.get("city") or "").casefold() == locality.casefold()
            and any(
                len(candidate_tokens) >= 1 and candidate_tokens <= meaningful_name_tokens(str(name))
                for name in (item.get("names") or [])
                for candidate_tokens in [meaningful_name_tokens(official_name)]
            )), None)
        if same_site:
            # Remove an earlier run's duplicate inventory row, if this seed was
            # already imported before stronger same-site alias matching existed.
            stale_seed = by_id.get(temple_id)
            if stale_seed:
                catalogue.remove(stale_seed)
                by_id.pop(temple_id, None)
                stale_document_ids = set(stale_seed.get("document_ids") or [])
                documents[:] = [doc for doc in documents if doc.get("document_id") not in stale_document_ids]
                document_ids.difference_update(stale_document_ids)
                duplicate_cleanup = True
            duplicates.append(official_name)
            continue
        if temple_id in by_id or fingerprint in by_fingerprint:
            duplicates.append(official_name)
            continue
        record = {
            "id": temple_id,
            "canonical_name": official_name,
            "names": [official_name],
            "alternate_names": [],
            "state": state,
            "district": district,
            "city": locality,
            "area": locality,
            "coordinates": None,
            "deities": None,
            "architectural_style": None,
            "historical_period": None,
            "important_festivals": None,
            "official_website_url": None,
            "description": f"Listed by the Archaeological Survey of India as a centrally protected monument/site. The ASI inventory records the locality as {locality} and district as {district}; this entry does not provide further historical or visitor details.",
            "sources": [{"title": ASI_TITLE, "url": ASI_URL, "publisher": PUBLISHER}],
            "document_ids": [],
            "verification_status": "source_listed_needs_review",
            "last_verified": None,
            "source_checked_at": CHECKED,
        }
        catalogue.append(record)
        by_id[temple_id] = record
        by_fingerprint.add(fingerprint)
        document_id = f"asi_inventory_{temple_id}"
        text = (
            f"The Archaeological Survey of India (ASI) Centrally Protected Monuments/Sites inventory records "
            f"{official_name} in {locality}, {district} district, {state}. This source supports the listed monument name, "
            f"place and inclusion in the ASI inventory. The inventory entry does not state a construction date, deity, "
            f"architectural style, festival, or visitor information, so those details remain unknown pending a more "
            f"specific authoritative source."
        )
        content_hash = hashlib.sha256(" ".join(text.split()).encode("utf-8")).hexdigest()
        doc = {
            "document_id": document_id,
            "temple_id": temple_id,
            "temple_name": official_name,
            "state": state,
            "district": district,
            "topic": "asi_inventory_listing",
            "source_title": ASI_TITLE,
            "source_url": ASI_URL,
            "publisher": PUBLISHER,
            "source_type": "official_inventory_paraphrase",
            "language": "en",
            "retrieval_date": CHECKED,
            "verification_status": "source_listed_needs_review",
            "content_hash": content_hash,
            "text": text,
        }
        documents.append(doc)
        record["document_ids"].append(document_id)
        document_ids.add(document_id)
        added.append(temple_id)

    def add_rich_record(state: str, district: str | None, locality: str, name: str, url: str, title: str, text: str, description: str):
        temple_id = f"whc_{hashlib.sha256('|'.join((state, district or '', locality, name)).casefold().encode('utf-8')).hexdigest()[:20]}"
        fingerprint = (name.casefold(), state.casefold(), (district or '').casefold(), locality.casefold())
        if temple_id in by_id or fingerprint in by_fingerprint:
            return None
        identifier = f"whc_{hashlib.sha256(f'{temple_id}|{url}|{title}'.encode('utf-8')).hexdigest()[:24]}"
        record = {
            "id": temple_id, "canonical_name": name, "names": [name], "alternate_names": [],
            "state": state, "district": district, "city": locality, "area": locality,
            "coordinates": None, "deities": None, "architectural_style": None,
            "historical_period": None, "important_festivals": None, "official_website_url": None,
            "description": description,
            "sources": [{"title": title, "url": url, "publisher": "UNESCO World Heritage Centre"}],
            "document_ids": [identifier], "verification_status": "source_reviewed_needs_review",
            "last_verified": None, "source_checked_at": CHECKED,
        }
        catalogue.append(record)
        by_id[temple_id] = record
        by_fingerprint.add(fingerprint)
        rich_records_added.append(temple_id)
        document = {
            "document_id": identifier, "temple_id": temple_id, "temple_name": name,
            "state": state, "district": district, "topic": "history_and_architecture",
            "source_title": title, "source_url": url, "publisher": "UNESCO World Heritage Centre",
            "source_type": "institutional_paraphrase", "language": "en", "retrieval_date": CHECKED,
            "verification_status": "source_reviewed_needs_review", "is_paraphrase": True, "text": text,
        }
        document["content_hash"] = hashlib.sha256(" ".join(text.split()).encode("utf-8")).hexdigest()
        documents.append(document)
        document_ids.add(identifier)
        rich_added.append(temple_id)
        return record

    rich_specs = [
        ("Madhya Pradesh", "Chhatarpur", "Khajuraho", "Khajuraho Group of Monuments", "https://whc.unesco.org/en/list/240/", "Khajuraho Group of Monuments", "UNESCO states that Khajuraho's group of temples represents a culmination of northern Indian temple art and architecture associated with the Chandella dynasty, which ruled the region in the 10th and 11th centuries CE. The source describes the group and period; it does not assign an individual construction date to every temple.", "UNESCO describes the Khajuraho temple group as a major expression of 10th–11th century Chandella-period northern Indian temple art and architecture."),
        ("Bihar", "Gaya", "Bodh Gaya", "Mahabodhi Temple Complex", "https://whc.unesco.org/en/list/1056/", "Mahabodhi Temple Complex at Bodh Gaya", "UNESCO identifies Mahabodhi as one of the four holy sites associated with the Buddha's life, particularly his enlightenment. It describes the present temple as dating to the 5th–6th centuries CE and as one of India's earliest surviving brick temples; an earlier temple at the site is attributed to Emperor Ashoka in the 3rd century BCE.", "UNESCO describes the complex as a Buddhist sacred site associated with the Buddha's enlightenment and early brick architecture."),
    ]
    for state, district, locality, name, url, title, text, description in rich_specs:
        add_rich_record(state, district, locality, name, url, title, text, description)

    hampi_names = ("Virupaksha Temple", "Vitthala Temple Complex", "Krishna Temple Complex", "Achyutaraya Temple Complex", "Pattabhirama Temple Complex", "Hemakuta Group of Temples")
    for name in hampi_names:
        description = f"UNESCO identifies {name} as part of the Hampi heritage property; site-specific details are limited in the UNESCO summary."
        text = (
            f"UNESCO identifies the {name} as a sacred component of the Group of Monuments at Hampi. UNESCO describes Hampi as the former capital of the Vijayanagara Empire, "
            "with most surviving remains dating from the 14th to 16th centuries, and the property includes sacred, royal and urban remains in the Tungabhadra basin. "
            "The UNESCO summary names this temple complex but does not provide a separate construction date or detailed architectural description for it."
        )
        if name == "Vitthala Temple Complex":
            text = (
                "UNESCO identifies the Vitthala Temple Complex as part of the Group of Monuments at Hampi. Its account highlights the complex's Garuda shrine shaped as a granite ratha, "
                "along with mandapas, a bazaar street and a stepped tank. UNESCO describes Hampi as the former capital of the Vijayanagara Empire, with most surviving remains dating "
                "from the 14th to 16th centuries; it does not assign a separate construction date to this complex in the summary."
            )
        record = add_rich_record("Karnataka", "Bellary", "Hampi", name, "https://whc.unesco.org/en/list/241/", "Group of Monuments at Hampi", text, description)
        if record is None:
            record = next((item for item in catalogue if item.get("state") == "Karnataka" and item.get("area") == "Hampi" and name.casefold() in str(item.get("canonical_name", "")).casefold()), None)
        if record:
            linked = next((doc for doc in documents if doc.get("temple_id") == record.get("id") and doc.get("source_url") == "https://whc.unesco.org/en/list/241/"), None)
            if linked and linked.get("text") != text:
                linked["text"] = text
                linked["content_hash"] = hashlib.sha256(" ".join(text.split()).encode("utf-8")).hexdigest()
                duplicate_cleanup = True

    # Add detailed UNESCO documents to matching inventory records without making
    # unsupported claims about protected status or changing their existing IDs.
    detailed_specs = [
        ("Karnataka", "Belur", "Channakeshava Temple", "Sacred Ensembles of the Hoysalas", "https://whc.unesco.org/en/list/1670/", "The Channakeshava Temple at Belur is a component of UNESCO's Sacred Ensembles of the Hoysalas, a serial property of 12th- and 13th-century temple complexes. UNESCO describes Hoysala features including stellate plans, circumambulatory platforms, sculptural galleries, tiered friezes and carved chloritic schist. Belur is identified as a living temple with continuing rituals and festivals."),
        ("Karnataka", "Halebidu", "Hoysalesvara Temple", "Sacred Ensembles of the Hoysalas", "https://whc.unesco.org/en/list/1670/", "The Hoysalesvara Temple at Halebidu is one of the three components of UNESCO's 12th- and 13th-century Sacred Ensembles of the Hoysalas. The UNESCO record describes the ensemble's stellate plans, circumambulatory platforms, sculptural galleries, multi-tiered friezes and carved chloritic schist. It notes this temple as a component of a serial heritage property."),
        ("Karnataka", "Somanathapura", "Keshava Temple", "Sacred Ensembles of the Hoysalas", "https://whc.unesco.org/en/list/1670/", "The Keshava Temple at Somanathapura is one component of UNESCO's Sacred Ensembles of the Hoysalas, a serial property dating from the 12th to 13th centuries. UNESCO describes Hoysala architectural characteristics such as stellate plans, sculptural galleries, circumambulatory platforms, multi-tiered friezes and carved chloritic schist."),
        ("Tamil Nadu", "Gangaikondacholapuram", "Brihadisvara Temple", "Great Living Chola Temples", "https://whc.unesco.org/en/list/250", "UNESCO states that the Brihadisvara Temple at Gangaikondacholisvaram was built by Rajendra I and completed in 1035. Its vimana is described as 53 metres high. The temple belongs to the Great Living Chola Temples property, whose temples show the development of Chola architecture and art."),
        ("Tamil Nadu", "Darasuram", "Airavatesvara Temple", "Great Living Chola Temples", "https://whc.unesco.org/en/list/250", "UNESCO describes the Airavatesvara Temple at Darasuram as a Chola temple built by Rajaraja II. Its 24-metre vimana and ornate chariot-like front mandapa are noted in the UNESCO account, along with sculptures associated with Chola art and Saivism. It is one of the three temples in the Great Living Chola Temples property."),
        ("Telangana", "Palampet", "Ramappa temple", "Kakatiya Rudreshwara (Ramappa) Temple, Telangana", "https://whc.unesco.org/en/list/1570", "UNESCO describes the Kakatiya Rudreshwara (Ramappa) Temple at Palampet as a 13th-century Kakatiyan temple. Its account highlights the sandbox foundation, lightweight porous bricks in the roof structure, carved stone sculpture and the relation between temple, landscape, ritual and dance traditions. The temple continues ceremonial use."),
        ("Karnataka", "Pattadakal", "Virupaksha Temple", "Group of Monuments at Pattadakal", "https://whc.unesco.org/en/list/239", "UNESCO describes Pattadakal as a 7th- and 8th-century Chalukya site where northern and southern Indian architectural forms were brought together. The group contains nine Hindu temples and a Jain sanctuary. The Virupaksha Temple, built around 740 by Queen Lokamahadevi, is highlighted as a major monument in the group."),
    ]
    for state, locality, match_name, title, url, text in detailed_specs:
        record = next((item for item in catalogue if item.get("state") == state and item.get("area") == locality and (match_name.casefold() in str(item.get("canonical_name", "")).casefold() or match_name.casefold() in " ".join(item.get("names", [])).casefold() or (match_name == "Channakeshava Temple" and locality == "Belur"))), None)
        if not record:
            continue
        identifier = "unesco_" + hashlib.sha256(f"{record['id']}|{url}|{text}".encode("utf-8")).hexdigest()[:24]
        if identifier in document_ids:
            continue
        document = {
            "document_id": identifier, "temple_id": record["id"], "temple_name": record.get("canonical_name") or (record.get("names") or [None])[0],
            "state": state, "district": record.get("district"), "topic": "history_and_architecture",
            "source_title": title, "source_url": url, "publisher": "UNESCO World Heritage Centre",
            "source_type": "institutional_paraphrase", "language": "en", "retrieval_date": CHECKED,
            "verification_status": "source_reviewed_needs_review", "is_paraphrase": True, "text": text,
        }
        document["content_hash"] = hashlib.sha256(" ".join(text.split()).encode("utf-8")).hexdigest()
        documents.append(document)
        record.setdefault("sources", []).append({"title": title, "url": url, "publisher": "UNESCO World Heritage Centre"})
        record.setdefault("document_ids", []).append(identifier)
        document_ids.add(identifier)
        rich_added.append(identifier)

    # Repeated official monument names may refer to separate sites. Keep each
    # real record, but qualify its display name by locality so discovery and
    # citations do not collapse distinct temples into one ambiguous label.
    by_canonical: dict[tuple[str, str], list[dict]] = {}
    for item in catalogue:
        key = (str(item.get("state") or "").casefold(), str(item.get("canonical_name") or "").casefold())
        if key[1]:
            by_canonical.setdefault(key, []).append(item)
    names_changed = False
    for (_state, _name), matches in by_canonical.items():
        if len(matches) < 2:
            continue
        for item in matches:
            old_name = item["canonical_name"]
            locality = item.get("area") or item.get("city") or item.get("district")
            if not locality:
                continue
            qualified = f"{old_name} ({locality})"
            aliases = item.setdefault("alternate_names", [])
            if old_name not in aliases:
                aliases.append(old_name)
            item["canonical_name"] = qualified
            prior_names = item.get("names") or [old_name]
            item["names"] = list(dict.fromkeys([qualified, *prior_names, old_name]))
            for document in documents:
                if document.get("temple_id") == item.get("id"):
                    document["temple_name"] = qualified
            names_changed = True

    if added or rich_added or names_changed or duplicate_cleanup:
        save(CATALOGUE_PATH, catalogue)
        save(DOCUMENTS_PATH, documents)
    print(json.dumps({"catalogue_records_added": len(catalogue) - initial_catalogue_count, "knowledge_documents_added": len(documents) - initial_document_count, "asi_inventory_records_added": len(added), "unesco_records_added": len(rich_records_added), "duplicate_candidates_skipped": len(duplicates), "catalogue_total": len(catalogue), "documents_total": len(documents), "added_ids": added + rich_records_added, "additional_knowledge_document_ids": rich_added}, indent=2))

if __name__ == "__main__":
    main()
