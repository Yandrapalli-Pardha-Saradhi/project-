"""Prepare a reviewed-source, pending-review enrichment batch without crawling.

Run from backend: python scripts/prepare_enrichment_batch_02.py
This script only adds curated draft documents and a manifest. It does not index.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE_PATH = ROOT / "data" / "catalogue.json"
DOCUMENTS_PATH = ROOT / "data" / "raw" / "temple_sources.json"
MANIFEST_PATH = ROOT / "data" / "enrichment_manifest_batch_02.json"
TODAY = date.today().isoformat()

# These are manually researched, narrowly scoped drafts. No source fetches or
# registry changes are performed by this script. All documents remain pending review.
RESEARCH: list[dict[str, Any]] = [
    {"id":"jagannath","url":"https://puri.odisha.gov.in/en/tourism/tourist-places/shree-jagannath-temple","title":"Shree Jagannath Temple","publisher":"Puri District Administration","source_type":"official_district_tourism","topic":"history_culture","text":"The Puri district administration describes the Shree Jagannath Temple as a major place of worship in Puri dedicated to Jagannath, with Balabhadra and Subhadra also central to its worship tradition. The temple is associated with the Eastern Ganga ruler Anantavarman Chodaganga and the 12th-century development of the shrine. Its Kalinga temple complex is closely connected to the annual Rath Yatra, when the deities are carried in processional chariots; the district page also identifies related observances including Snana Yatra and Bahuda Yatra. These notes summarize the administration's visitor information and should be checked against the temple's current ritual calendar before reuse."},
    {"id":"asi_odisha_871ae670bd5d4d3d","url":"https://odishatourism.gov.in/en/places/lingaraj-temple","title":"Lingaraj Temple","publisher":"Odisha Tourism","source_type":"official_state_tourism","topic":"history_architecture_culture","text":"Odisha Tourism presents Lingaraj as an important Bhubaneswar shrine dedicated to Shiva in the Harihara form. Its account places the principal temple in the 11th century and describes a sandstone structure whose tower rises to nearly 180 feet. The complex illustrates the region's Kalinga temple vocabulary, with the principal sanctuary and attached halls forming a large temple precinct. The source notes the self-manifested linga tradition and identifies Maha Shivaratri and Rukuna Ratha Jatra among the temple's important observances. This document records the tourism department's summary; details of construction phases and ritual practice merit specialist review."},
    {"id":"asi_odisha_a534d4ada83fa69c","url":"https://odishatourism.gov.in/en/places/mukteswara-temple","title":"Mukteswara Temple","publisher":"Odisha Tourism","source_type":"official_state_tourism","topic":"history_architecture","text":"Odisha Tourism dates Mukteswara Temple in Bhubaneswar to around the 10th century and associates it with the Somavamsi ruler Jajati I. The temple is a compact example of Kalinga architecture, organized around a deula (sanctuary tower) and jagamohana (assembly hall). The department highlights the carved arched gateway, sculpted surfaces and perforated lattice windows as distinctive features. The source describes the monument as an important stage in the development of Odisha temple architecture. Its concise account does not establish every attribution or date independently, so those details remain subject to human source review."},
    {"id":"asi_odisha_9a65411c4e7a8720","url":"https://apps.odishatourism.gov.in/blog-detail/parsurameswar-temple-bhubaneswar","title":"Parsurameswar Temple, Bhubaneswar","publisher":"Odisha Tourism","source_type":"official_state_tourism_article","topic":"history_architecture","text":"Odisha Tourism's account identifies Parsurameswar Temple as an early Bhubaneswar monument, generally placed in the 7th century, and dedicated to Shiva. The compact Kalinga shrine combines a sanctuary with an assembly space and is noted for carved figures and panels, including depictions associated with the Saptamatrikas. The temple is useful for understanding early forms of Odisha's stone temple architecture. The date and interpretation here follow the tourism article's summary and should be treated as attributed rather than as a new independent archaeological assessment."},
    {"id":"asi_odisha_f4c379be270f3526","url":"https://odishatourism.gov.in/en/places/ananta-basudeva-temple","title":"Ananta Basudeva Temple","publisher":"Odisha Tourism","source_type":"official_state_tourism","topic":"history_architecture_culture","text":"Odisha Tourism describes Ananta Basudeva Temple in Bhubaneswar as a 13th-century Vaishnava shrine associated with Queen Chandrika Devi of the Eastern Ganga period. Its worship tradition centers on Krishna (Basudeva), with the source also identifying Balarama (Ananta) and Subhadra. The department outlines a multi-part temple complex with a sanctuary, assembly and offering halls. It also notes the temple's association with the preparation and offering of the Mahaprasad tradition known as Abadha. These points are drawn from the tourism authority's overview; ritual details and historical attribution remain pending review."},
    {"id":"asi_odisha_4e2ff9dbfa31c9c4","url":"https://nma.gov.in/showfile.php?lang=1&level=1&lid=85&ls_id=142&nma_type=0","title":"Bhaskareswar Temple: monument description","publisher":"National Monuments Authority, Government of India","source_type":"official_archaeological_document","topic":"architecture_history","text":"The National Monuments Authority's monument description identifies Bhaskareswar as a west-facing Shiva temple with a two-tiered structure and a notably large linga, reported there at about 2.74 metres. The description records a pancharatha ground plan and sculpted niches with figures including Parvati, Kartikeya and Ganesha. It also relays a scholarly proposal that the linga may incorporate a fragment of an Ashokan pillar; this is presented as an attributed hypothesis, not an established fact. The architectural observations in this document are limited to the NMA description and should be checked against the protected-monument record."},
    {"id":"asi_odisha_9b7d1946270be4a0","url":"https://ignca.gov.in/Asi_data/73821.pdf","title":"Living Architecture: Indian Temples","publisher":"Indira Gandhi National Centre for the Arts (digitized copy from ASI Central Archaeological Library) — Andreas Volwahsen","source_type":"institutional_architecture_monograph","topic":"architecture","text":"The architectural monograph Living Architecture: Indian Temples discusses the Brahmeswar temple at Bhubaneswar as a Shaiva sanctuary with an assembly hall and four subsidiary shrines in its precinct. Its plates and description show the sanctuary and hall as a coordinated composition, with the hall's pyramidal roof built in receding tiers. The publication illustrates the monument within the mature stone-temple architecture of Odisha. This summary follows the digitized monograph held in the Archaeological Survey of India's Central Archaeological Library; precise construction chronology is not asserted here because the cited excerpt does not establish it."},
    {"id":"asi_odisha_224c8e9b9c4d99fd","url":"https://magazines.odisha.gov.in/Orissareview/2018/May/engpdf/may_or_2018.pdf","title":"Baitala Temple and the Khakhara tradition","publisher":"Odisha Review, Government of Odisha (Sujata Routray) ","source_type":"state_publication_research_article","topic":"architecture_deity","text":"An Odisha Review article by Sujata Routray describes Baitala Deula in Bhubaneswar as an 8th-century monument associated with Chamunda worship and the Khakhara form of Kalinga architecture. It distinguishes the sanctuary's elongated, semi-cylindrical roof profile from the more familiar curvilinear temple tower and discusses its sculptural program and tantric associations. These are the article author's historical and architectural interpretations, recorded here with explicit attribution rather than treated as an independent verification. The source is a state-published research article, not a current temple administration page."},
    {"id":"asi_telangana_39f3f37fca8287ca","url":"https://gadwal.telangana.gov.in/places-of-interest/","title":"Alampur Nava Brahma Temples","publisher":"Jogulamba Gadwal District Administration, Government of Telangana","source_type":"official_district_tourism","topic":"history_architecture_deity","text":"The Jogulamba Gadwal district administration presents Alampur's Nava Brahma group as nine Shiva shrines associated with the Badami Chalukya period, broadly the 6th–7th centuries. The temples are distinguished by individual names and architectural forms within a shared sacred landscape; the district source identifies Bala Brahma as the principal shrine and notes its continuing worship. The complex demonstrates early Deccan temple building and the region's historical connections. The administration page includes dates and local traditions that require monument-level corroboration; this draft retains only its group-level account and does not assign the same detailed history to every shrine."},
    {"id":"asi_telangana_cc77c673d026d843","url":"https://tourism.telangana.gov.in/attractions/thousand-pillars-temple","title":"Thousand Pillars Temple","publisher":"Telangana Tourism","source_type":"official_state_tourism","topic":"history_architecture_deity","text":"Telangana Tourism dates the Thousand Pillars Temple at Hanamkonda to 1163 and associates its construction with Kakatiya ruler Rudra Deva. The department describes a shrine tradition honoring Shiva, Vishnu and Surya and highlights the star-shaped plan, carved pillars and monolithic Nandi. The building is presented as an example of Kakatiya-era craftsmanship, with the sculpted stone supports giving the monument its familiar name. These claims follow the state tourism page; architectural dating and conservation status should be checked against the responsible archaeology authority before being treated as fully verified."},
    {"id":"asi_andhra_prade_bead535e8e3f76eb","url":"https://srisathyasai.ap.gov.in/tourism/","title":"Lepakshi Veerabhadra Temple","publisher":"Sri Sathya Sai District Administration, Government of Andhra Pradesh","source_type":"official_district_tourism","topic":"architecture_history_deity","text":"The Sri Sathya Sai district tourism page identifies the Veerabhadra Temple at Lepakshi as a Vijayanagara-period complex and points visitors to its sculptural and architectural features, including the celebrated hanging pillar. The complex includes shrines associated with Veerabhadra and other Hindu deities. The district account also preserves the local association of the site with the Vijayanagara official Virupanna; this is recorded as the administration's account, not expanded into unsupported legend. The page is a general tourism overview, so individual construction dates, mural descriptions and conservation interventions require stronger monument-specific sourcing."},
    {"id":"asi_andhra_prade_994f268937105045","url":"https://ananthapuramu.ap.gov.in/chintala-venkataramana-swamy-temple/","title":"Chintala Venkataramana Swamy Temple","publisher":"Ananthapuramu District Administration, Government of Andhra Pradesh","source_type":"official_district_tourism","topic":"history_architecture_deity_festivals","text":"The Ananthapuramu district administration identifies the Tadipatri shrine as Chintala Venkataramana Swamy Temple, also called Chintalarayaswami, and describes it as a temple to Vishnu in the Venkateswara form. Its page associates construction in the 16th century with Pemmasani Timmanayudu II under Vijayanagara rule, and notes the gopuram and carved mandapa. Vaikuntha Ekadashi and Brahmotsavam are listed among its observances. These details are transcribed in paraphrase from the district's temple page; current festival schedules and the exact chronology remain for review."},
    {"id":"asi_andhra_prade_4824bbb04f702849","url":"https://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%20%202012%20-%202013%20%20A%20Review.pdf","title":"Indian Archaeology 2012–13: A Review","publisher":"Archaeological Survey of India, National Mission on Monuments and Antiquities digital archive","source_type":"official_archaeological_report","topic":"conservation","text":"The Archaeological Survey of India's 2012–13 annual review records conservation work at the Madhavaraya temple in Gorantla: exposed flooring members were addressed with granite flooring laid over lime concrete, with slopes and drainage channels provided. This is a specific conservation record for the reported work period, not a description of the temple's complete history or its present condition. No further historical or architectural claims are included because this source excerpt is focused on conservation."},
    {"id":"asi_madhya_prade_ea71d0bc499fc609","url":"https://www.incredibleindia.gov.in/en/madhya-pradesh/gwalior","title":"Gwalior","publisher":"Incredible India, Ministry of Tourism, Government of India","source_type":"official_national_tourism","topic":"history_architecture_deity","text":"The Government of India's Incredible India Gwalior guide describes the Sas Bahu temples within Gwalior Fort as a pair of historic shrines, one associated with Vishnu and the other with Shiva, and highlights their carved stone surfaces. The twin monuments are commonly dated to the 11th century in the guide's historical overview. Their contrasting scale and detailed exterior carving make them notable examples of the region's medieval temple architecture. This draft deliberately follows the national tourism summary and does not expand the popular name into an unsupported personal story."},
    {"id":"asi_tamil_nadu_64f350d8e3dc3e9c","url":"https://whc.unesco.org/en/list/250/","title":"Great Living Chola Temples","publisher":"UNESCO World Heritage Centre","source_type":"unesco_world_heritage","topic":"heritage_history_conservation","text":"UNESCO's Great Living Chola Temples property includes Airavatesvara Temple at Darasuram alongside the major Chola temples at Thanjavur and Gangaikondacholapuram. UNESCO describes Airavatesvara as a 12th-century monument commissioned under Rajaraja II, notable for its sculpted stone architecture and a chariot-form mandapa. The property is recognized for its outstanding Chola temple architecture and continuing religious use. UNESCO's page identifies the Archaeological Survey of India as responsible for protection and conservation of the centrally protected monuments, while worship and temple administration involve the relevant local authority. This is a property-level heritage summary, not a detailed conservation-condition assessment of Airavatesvara alone."},
    {"id":"asi_karnataka_87e1e40d23b47df2","url":"https://www.prod.incredibleindia.gov.in/content/incredible-india-v2/en/destinations/vijayapura-bijapur/aihole.html","title":"Aihole","publisher":"Incredible India, Ministry of Tourism, Government of India","source_type":"official_national_tourism","topic":"architecture_deity","text":"The Government of India's Aihole guide describes Lad Khan Temple as an early Chalukya-period monument with a hall-like, panchayat-style plan and a shrine dedicated to Shiva. Its form differs from the later, more familiar towering temple compositions and is useful for tracing experiments in early Deccan temple architecture. The guide explains that the name Lad Khan is connected to a later occupant rather than the original temple dedication. This account is attributed to the tourism source; the monument's more precise date and construction sequence are not asserted here."},
    {"id":"asi_karnataka_ac180b0d6288c76f","url":"https://karnatakatourism.org/en/attractions/mallikarjuna-temple/","title":"Mallikarjuna Temple, Pattadakal","publisher":"Karnataka Tourism","source_type":"official_state_tourism","topic":"history_architecture_deity","text":"Karnataka Tourism associates the Mallikarjuna Temple at Pattadakal with Queen Trailokyamahadevi and the 8th-century Chalukya period, linking its construction to the political context of Vikramaditya II's campaigns against the Pallavas. The temple is dedicated to Shiva and is described with a southern-style pyramidal tower, pillared mandapa and sculptural panels drawing on epic narratives. It stands within Pattadakal, the UNESCO-listed group of Chalukya monuments. This document distinguishes the state tourism account's historical interpretation from independently reviewed epigraphic evidence."},
    {"id":"asi_karnataka_2854d2a42446f401","url":"https://kstdc.co/wp-content/uploads/2024/09/Tourist-Guide.pdf","title":"Karnataka Tourist Guide","publisher":"Karnataka State Tourism Development Corporation","source_type":"official_state_tourism_publication","topic":"architecture_heritage","text":"The Karnataka State Tourism Development Corporation guide places Papanatha Temple within the UNESCO World Heritage monuments of Pattadakal. It draws attention to the temple's richly carved surfaces, decorated ceilings and a substantial pillared main hall. These features form part of the mixed architectural landscape at Pattadakal, where temple forms reflect the Chalukya period's interaction of northern and southern design vocabularies. This short document is limited to architectural details given in the tourism guide; it does not add a precise construction date or deity claim beyond what is established in the existing catalogue."},
    {"id":"asi_karnataka_d5d33227e0a3a92f","url":"https://whc.unesco.org/document/205738","title":"Hoysala Temples of Belur, Halebidu and Somnathapura: ICOMOS evaluation","publisher":"ICOMOS / UNESCO World Heritage Centre","source_type":"unesco_advisory_evaluation","topic":"history_architecture_heritage_conservation","text":"The ICOMOS evaluation dossier for the Hoysala temples describes the Halebidu Hoysalesvara monument as a double-shrine temple dedicated to Shiva, with paired sanctums, associated Nandi pavilions, star-shaped plans and an extensive narrative sculptural frieze around the platform. The dossier discusses the site within the Hoysala architectural tradition and records its role in the historic Hoysala capital. Its conservation discussion describes the protected monument and preservation context. These details come from the advisory evaluation for UNESCO nomination and should be cited as an institutional assessment, not as a current conservation inspection."},
    {"id":"asi_karnataka_f29968094d7b92b1","url":"https://whc.unesco.org/document/205738","title":"Hoysala Temples of Belur, Halebidu and Somnathapura: ICOMOS evaluation","publisher":"ICOMOS / UNESCO World Heritage Centre","source_type":"unesco_advisory_evaluation","topic":"history_architecture_heritage","text":"The ICOMOS evaluation describes the Keshava Temple at Somanathapura as a late major Hoysala temple, consecrated in 1268 under the patronage of Somanatha Dandanayaka. Its plan has three sanctums arranged around a shared hall, with stellate outlines and sculpted exterior bands; the three shrines are associated with forms of Vishnu. The dossier also documents the temple's inclusion in the Hoysala temple serial property inscribed on the UNESCO World Heritage List in 2023. These claims follow the UNESCO nomination evaluation and are kept specific to the Somanathapura monument."},
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def main() -> None:
    catalogue = read_json(CATALOGUE_PATH)
    documents = read_json(DOCUMENTS_PATH)
    by_id = {item["id"]: item for item in catalogue}
    if len(by_id) != len(catalogue):
        raise SystemExit("Catalogue has duplicate IDs; refusing to prepare batch")
    existing_doc_ids = {doc.get("document_id") for doc in documents}
    if len(existing_doc_ids) != len(documents):
        raise SystemExit("Knowledge documents have duplicate IDs; refusing to prepare batch")
    if len({entry["id"] for entry in RESEARCH}) != 20:
        raise SystemExit("Batch definition must contain exactly 20 unique temple IDs")
    missing = [entry["id"] for entry in RESEARCH if entry["id"] not in by_id]
    if missing:
        raise SystemExit(f"Selected IDs are not present in catalogue: {missing}")

    new_documents: list[dict[str, Any]] = []
    manifest_rows: list[dict[str, Any]] = []
    for entry in RESEARCH:
        temple = by_id[entry["id"]]
        document_id = f"enrich_batch02_{entry['id']}"
        clean_text = " ".join(entry["text"].split())
        content_hash = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()
        doc = {
            "document_id": document_id,
            "temple_id": temple["id"],
            "temple_name": temple.get("canonical_name") or temple.get("names", [temple["id"]])[0],
            "state": temple.get("state"),
            "district": temple.get("district"),
            "source_title": entry["title"],
            "source_url": entry["url"],
            "publisher": entry["publisher"].strip(),
            "source_type": entry["source_type"],
            "topic": entry["topic"],
            "language": "en",
            "publication_date": None,
            "retrieval_date": TODAY,
            "verification_status": "source_review_pending",
            "review_status": "pending_human_review",
            "is_paraphrase": True,
            "content_hash": content_hash,
            "text": clean_text,
        }
        if document_id in existing_doc_ids:
            current = next(doc_item for doc_item in documents if doc_item.get("document_id") == document_id)
            if current.get("content_hash") != content_hash or current.get("text") != clean_text:
                raise SystemExit(f"Existing batch document differs; refusing overwrite: {document_id}")
        else:
            new_documents.append(doc)

        temple_doc_ids = list(temple.get("document_ids") or [])
        if document_id not in temple_doc_ids:
            temple_doc_ids.append(document_id)
            temple["document_ids"] = temple_doc_ids
        temple_sources = list(temple.get("sources") or [])
        if not any(source.get("url") == entry["url"] for source in temple_sources if isinstance(source, dict)):
            temple_sources.append({"title": entry["title"], "url": entry["url"], "publisher": entry["publisher"].strip()})
            temple["sources"] = temple_sources

        prior = [d for d in documents if d.get("temple_id") == temple["id"]]
        current_topics = sorted({d.get("topic", "general") for d in prior})
        missing_topics = [topic for topic in ("history", "architecture", "festivals/culture", "heritage/conservation") if not any(topic.split("/")[0] in str(t).lower() for t in current_topics)]
        manifest_rows.append({
            "temple_id": temple["id"],
            "name": doc["temple_name"],
            "state": temple.get("state"),
            "district": temple.get("district"),
            "current_document_coverage": current_topics,
            "missing_topics_before_batch": missing_topics,
            "candidate_authoritative_sources": [{"title": entry["title"], "url": entry["url"], "publisher": entry["publisher"].strip()}],
            "enrichment_status": "pending_human_review" if document_id not in existing_doc_ids else "prepared_pending_human_review",
            "draft_document_id": document_id,
            "claims_scope": entry["topic"],
        })

    for doc in new_documents:
        documents.append(doc)
    manifest = {
        "batch_id": "2026-11-05-batch-02",
        "created_date": TODAY,
        "scope": "20 existing catalogue temples; no catalogue records created; one source-attributed draft per temple",
        "source_collection": "Manual source checks only; no automated source collection; source registry and approval gates unchanged",
        "counts": {"temples_in_batch": 20, "draft_documents_added": len(new_documents), "pending_human_review": 20, "automated_collection_runs": 0},
        "temples": manifest_rows,
    }
    atomic_json(DOCUMENTS_PATH, documents)
    atomic_json(CATALOGUE_PATH, catalogue)
    atomic_json(MANIFEST_PATH, manifest)
    print(json.dumps({"temples": 20, "new_documents": len(new_documents), "documents_total": len(documents), "manifest": str(MANIFEST_PATH)}, indent=2))


if __name__ == "__main__":
    main()
