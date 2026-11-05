# All-Temple Research Coverage — Resumable Checkpoint

Generated: 2026-11-05T16:43:13.922852+00:00

> **Incomplete.** This checkpoint does not meet the all-217 source-research completion condition. It records only source pages actually opened and read, with source relationships kept temple-specific.

## Verified state

- Catalogue: **217 records** (217 unique IDs). No records were added or removed.
- Curated knowledge documents: **391**.
- Persistent `temple_heritage` collection: **529 chunks** at `temple_heritage`.
- Actually inspected source URLs recorded across the queue history: **68 unique URLs**; 67 were linked to specific temple records, while general-purpose pages are tracked separately.
- Catalogue temples with at least one recorded source page inspected: **89 / 217**. All 89 remain partial and have outstanding topic gaps.
- Catalogue temples without a relevant source page inspected in this operation: **128 / 217**. This includes 18 with source-attributed corpus documents whose actual source pages were not confirmed inspected here.
- Queue status: source_inspected=41, enriched=49, not_started=108, source_gap=1, evidence_extracted=18.
- New source-attributed documents added in this operation: **65**, linked to **47** temples. New documents are `pending_human_review`; no document was marked verified.
- Documents modified after their first index: **8**. Source registry permissions were unchanged; no automated collection was run.

The source-gate workflow was respected. Research used identified government, UNESCO, ASI, state-tourism and institutional pages that were opened individually. The Himachal Tourism page returned HTTP 200 and its temple-specific text was read; the web extractor timed out, so the page was inspected through a direct single-page request. A source that named a similarly named temple at a conflicting locality was not attached as evidence.

## Coverage snapshot

Aggregate heuristic classes (not factual completeness):

- Partial profile: **8**
- Limited profile: **5**
- Broadly documented: **2**
- Several topics documented: **11**
- Basic / substantial gaps: **191**

Category statuses (heuristic corpus evidence, not verified facts):

- `historical_background`: Limited 33, Detailed 3, Good 12, Missing 129, Basic 40
- `architecture`: Limited 36, Detailed 4, Good 8, Missing 141, Basic 28
- `religious_cultural_significance`: Limited 27, Good 10, Detailed 7, Missing 139, Basic 34
- `festivals_rituals`: Missing 200, Basic 12, Good 1, Detailed 1, Limited 3
- `inscriptions_historical_evidence`: Limited 1, Missing 203, Basic 13
- `heritage_conservation`: Limited 20, Detailed 9, Missing 166, Basic 15, Good 7
- `visitor_information`: Missing 195, Limited 6, Basic 16

## Retrieval evaluation

- Name queries: **216 / 217** passed.
- Topic retrieval queries: **1519**; evidence-available queries passed **346 / 346**.
- Unsupported-topic queries: **1173**; potential unrelated context admitted: **1**.
- Source URL metadata matched the local document record in **3800 / 3800** checks. This validates metadata linkage, not whether a generated answer is factually supported by that page.
- Follow-up scope: **217 / 217**. Similar-name resolution: **30 / 30**; metadata scope checks passed **30 / 30**.
- External LLM called: **False**. Retrieval evaluation does not establish generated-answer accuracy.

Name-query failures: Champavati Temple (What is Champavati Temple and where is it located?)
Expected-topic retrieval mismatches: none.

## Incremental indexing and validation

- Curated document validation: **0 catalogue changes**, catalog remains 217; final document validation reported no errors and no duplicate content before indexing.
- Current collection: **529 chunks**. This operation added **65 documents**. After first indexing, **8 documents** were tightened to avoid caveat text being misread as evidence.
- Latest two dry runs agreed: 0 chunk updates, 0 metadata-only updates and 0 obsolete chunks from those modified document versions removed. No unrelated chunks were deleted.
- The Chroma collection was not reset. All document additions remain pending human review.

## Sources actually inspected

- [Martand Sun Temple](https://anantnag.nic.in/tourist-place/martand-sun-temple/) — inspected for: asi_jammu_and_ka_1f8a290d8729fbea
- [General (1920–1935): archival index](https://archives.assam.gov.in/sites/default/files/swf_utility_folder/departments/archives_webcomindia_org_oid_3/portlet/level_1/files/General%20%281920-1935%29_0.pdf) — inspected for: asi_assam_68e3d36ac845c504
- [Centrally Protected Monuments/Sites: State-wise and Circle-wise](https://asi.nic.in/pdf/CPM_List.pdf) — inspected for: asi_karnataka_20e758c06d541bd9, asi_karnataka_39c8b5453cc604ec, asi_karnataka_43d31d5b7b909f6e, asi_karnataka_df9d7ed1a005d4a6, asi_karnataka_e7e3292346518668
- [https://asichennai.gov.in/monuments_full_list.html](https://asichennai.gov.in/monuments_full_list.html) — inspected for: asi_tamil_nadu_476eb8cc97fb84ef, asi_tamil_nadu_8efa92f0aa42a214, asi_tamil_nadu_9ff95b5f3937c27a, asi_tamil_nadu_c4c0740aa244e2f1, asi_tamil_nadu_dfe60f19c80a4e44
- [Bordol Temple (Biswanath), ASI Guwahati Circle profile](https://asiguwahaticircle.gov.in/bordol.html) — inspected for: asi_assam_4bf398fbc498bf4d
- [Dhandi Temple, N.C. Kamadayal (Gohpur Mouza)](https://asiguwahaticircle.gov.in/dhandi.html) — inspected for: asi_assam_24dc8f3855351f21
- [Shri Shri Kedar Temple, Hajo](https://asiguwahaticircle.gov.in/kedar%20temple.html) — inspected for: asi_assam_6bca1547cfa3d7cc
- [Activities of Archaeological Survey of India, Guwahati Circle during 2010 & 2011](https://asiguwahaticircle.gov.in/paw.pdf) — inspected for: asi_assam_24dc8f3855351f21, asi_assam_6bca1547cfa3d7cc, asi_assam_73c2196bfdf2df7a, asi_assam_dbf0ecb97451eb87
- [Hayagriva Madhava Temple](https://assamtourism.gov.in/Hayagriva-Madhava-Temple.php) — inspected for: asi_assam_0aecea616e14afa3
- [Historical Monuments](https://directortourism.assam.gov.in/portlet-sub-innerpage/historical-monuments) — inspected for: asi_assam_68e3d36ac845c504
- [Sri Golingeswara Swami Vari Temple, Biccavolu](https://eastgodavari.ap.gov.in/temples/sri-golingeswara-swami-vari-temple-biccavolu/) — inspected for: asi_andhra_prade_d219a5f1c4c7fc35
- [Hindu Pilgrimage](https://himachal.nic.in/Content/HtmlPage?qs=LdEF+AuYkB4Dve235DK9HQ%3D%3D) — inspected for: asi_himachal_pra_29892a543f8e7863, asi_himachal_pra_a6a66c91268cdcdf
- [Temples](https://himachaltourism.gov.in/destination/temples/) — inspected for: asi_himachal_pra_2d93808a25e7f773, asi_himachal_pra_3e34b97076b4e1a3, asi_himachal_pra_56b348db7df5aa99, asi_himachal_pra_7509a21fdaa8af22, asi_himachal_pra_a1ef8ff6339c407d, asi_himachal_pra_a6a66c91268cdcdf, asi_himachal_pra_aac4a2248ad925db, asi_himachal_pra_d0cbd9e9b4b403a2
- [Manimahesh Yatra](https://hpchamba.nic.in/manimahesh-yatra/) — inspected for: asi_himachal_pra_7509a21fdaa8af22
- [Kangra Pilgrimage](https://hpkangra.nic.in/kangra-pilgrimage/) — inspected for: asi_himachal_pra_d0cbd9e9b4b403a2
- [Archaeological Survey of India Annual Report 1902-03: Chennakesavami Temple at Sompalle](https://ignca.gov.in/Asi_data/13956.pdf) — inspected for: asi_andhra_prade_ba65914fa7b7de40
- [100 Temples of Baijnath and Sidhnath (Baijnath)](https://ignca.gov.in/Asi_data/84884.pdf) — inspected for: asi_himachal_pra_d0cbd9e9b4b403a2
- [Nandi Hills — Karnataka Tourism](https://karnatakatourism.org/en/experiences/nandi-hills-bengaluru/) — inspected for: asi_karnataka_1544f0a56a8c103b
- [Temples Trust: List of Acquired Temples](https://lac.hp.gov.in/temples-trust/) — inspected for: asi_himachal_pra_7509a21fdaa8af22, asi_himachal_pra_a6a66c91268cdcdf
- [Adopt a Heritage / Apni Dharohar Apni Pehchaan and Aaj Purani Rahon Se: Himachal Pradesh](https://lac.hp.gov.in/wp-content/themes/capital/pdf/APURSA-converted.pdf) — inspected for: asi_himachal_pra_3e34b97076b4e1a3, asi_himachal_pra_4a3a5f31aa66c811, asi_himachal_pra_7509a21fdaa8af22, asi_himachal_pra_a1ef8ff6339c407d, asi_himachal_pra_c5706cddb70077f6
- [Festivals and Events](https://madurai.nic.in/festivals-and-events/) — inspected for: meenakshi
- [Sri Meenakshi - Sundareswarar Temple](https://madurai.nic.in/tourist-place/sri-meenakshi-sundareswarar-temple/) — inspected for: meenakshi
- [Monuments of Himachal Pradesh under Shimla Circle](https://ncf.nic.in/assets/images/Himachal%20under%20Shimal%20Circle.pdf) — inspected for: asi_himachal_pra_29892a543f8e7863, asi_himachal_pra_2cd9e34ca0dd4e17, asi_himachal_pra_2d93808a25e7f773, asi_himachal_pra_53211815add81171, asi_himachal_pra_9681bf3ab0a6c3f8, asi_himachal_pra_a6a66c91268cdcdf, asi_himachal_pra_aac4a2248ad925db
- [Amaravati Circle Joint Hand: Andhra Pradesh](https://ncf.nic.in/joint-hand/andhra_pradesh_amravati_circle) — inspected for: asi_andhra_prade_4902522d216f33d7, asi_andhra_prade_63f2355eafb0759e, asi_andhra_prade_78f1c41f21c933de, asi_andhra_prade_d219a5f1c4c7fc35
- [Indian Archaeology 2012–13: A Review](https://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%20%202012%20-%202013%20%20A%20Review.pdf) — inspected for: asi_andhra_prade_4824bbb04f702849, asi_andhra_prade_ba65914fa7b7de40, asi_andhra_prade_e429b0544ae6aaa7
- [Indian Archaeology 1956-57: A Review](https://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%201956-57%20A%20Review.pdf) — inspected for: asi_andhra_prade_34fdc7ad2433488f, asi_andhra_prade_4824bbb04f702849, asi_andhra_prade_5509b425f6edbf42, asi_andhra_prade_bead535e8e3f76eb
- [Indian Archaeology 1975–76: A Review — Panamalai report](https://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%201975-76%20A%20Review.pdf) — inspected for: asi_tamil_nadu_c4c0740aa244e2f1
- [Indian Archaeology 2000–01: A Review](https://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%202000-2001%20A%20Review.pdf) — inspected for: asi_assam_150626777a56d77d, asi_assam_3176178449463d6c
- [Shree Jagannath Temple](https://odishatourism.gov.in/en/places/shree-jagannath-temple) — inspected for: jagannath
- [Puri Ratha Jatra 2026 & Chariot Festival](https://odishatourism.gov.in/en/ratha-jatra-2026) — inspected for: jagannath
- [Assam Tourism Coffee Table Book](https://publications.assamtourism.gov.in/publications/files/Assam_Tourism_Coffee_Table_Book.pdf) — inspected for: asi_assam_68e3d36ac845c504
- [Rajya Sabha Unstarred Question 162: Centrally protected monuments in Andhra Pradesh](https://rsdebate.nic.in/bitstream/123456789/35430/1/PQ_210_27022007_U162_p55_p61.pdf) — inspected for: asi_andhra_prade_34fdc7ad2433488f, asi_andhra_prade_4824bbb04f702849, asi_andhra_prade_5509b425f6edbf42, asi_andhra_prade_994f268937105045, asi_andhra_prade_bead535e8e3f76eb, asi_andhra_prade_e74ff866d54d0cc2
- [Rajya Sabha Unstarred Question No. 2421: List of Centrally Protected Monuments/Sites under ASI in Andhra Pradesh](https://rsdebate.nic.in/bitstream/123456789/725884/1/PQ_256_24032022_U2421_p152_p159.pdf) — inspected for: asi_andhra_prade_24e5a8c78a3f68e5, asi_andhra_prade_34fdc7ad2433488f, asi_andhra_prade_4824bbb04f702849, asi_andhra_prade_4902522d216f33d7, asi_andhra_prade_5509b425f6edbf42, asi_andhra_prade_78f1c41f21c933de, asi_andhra_prade_85900195bd76980b, asi_andhra_prade_994f268937105045, asi_andhra_prade_ba65914fa7b7de40, asi_andhra_prade_bead535e8e3f76eb, asi_andhra_prade_d219a5f1c4c7fc35, asi_andhra_prade_e429b0544ae6aaa7, asi_andhra_prade_e74ff866d54d0cc2
- [The Uttar Pradesh Sri Kashi Vishwanath Temple Act, 1983 (officially hosted PDF)](https://shrikashivishwanath.org/files/adhiniyam_merged.pdf) — inspected for: kashi_vishwanath
- [Sivasagar Tank and Temples](https://sivasagar.assam.gov.in/index.php/tourist-place-detail/275) — inspected for: asi_assam_087d550e6d805059, asi_assam_53f3d143b7f21899, asi_assam_6324da2158eb30bc
- [Joysagar Tank and Temples](https://sivasagar.assam.gov.in/tourist-place-detail/329) — inspected for: asi_assam_6f13d020bbaf4068, asi_assam_80af7f930eb9cfb5, asi_assam_fcd74543096308a5
- [Ranganath Temple and Fakua Doul](https://sivasagar.assam.gov.in/tourist-place-detail/331) — inspected for: asi_assam_888093ddb8ea0098
- [Gaurisagar Tank and Doul](https://sivasagar.assam.gov.in/tourist-place-detail/333) — inspected for: asi_assam_d296790c660bb3b9
- [Da Parbatia Gate](https://sonitpur.assam.gov.in/tourist-place-detail/272) — inspected for: asi_assam_68e3d36ac845c504
- [Shree Kashi Vishvanath Temple](https://varanasi.nic.in/tourist-place/shri-kashi-vishwanath-temple/) — inspected for: kashi_vishwanath
- [Venkataramana Temple, Gingee — Viluppuram District Administration](https://viluppuram.nic.in/tourism/place-of-interest/) — inspected for: asi_tamil_nadu_228792b71860b713, asi_tamil_nadu_476eb8cc97fb84ef, asi_tamil_nadu_8efa92f0aa42a214, asi_tamil_nadu_94ef770652db64a5, asi_tamil_nadu_b8864915b92941b5
- [Section II: Periodic Report on the State of Conservation of the Group of Monuments at Hampi, India, 2003](https://whc.unesco.org/document/162842) — inspected for: whc_0550440746a0ab1b40e6, whc_0601b84399076df5f6eb, whc_57e81c99363e3334087c, whc_5a482f12eb769406674c, whc_b5eaf9ee03e0215d1573, whc_ffb69144fee941fb01a9
- [World Heritage Site Nomination Dossier: Sacred Ensembles of the Hoysalas (Supplementary Information)](https://whc.unesco.org/document/198086) — inspected for: asi_karnataka_03633ec3263fe299, asi_karnataka_2afd54b8e1b183a7, asi_karnataka_4e9044ce27267cfb, asi_karnataka_e1c13713806e44d6
- [Decision 45 COM 8B.38 — Sacred Ensembles of the Hoysalas](https://whc.unesco.org/en/decisions/8419) — inspected for: asi_karnataka_d5d33227e0a3a92f, asi_karnataka_f29968094d7b92b1
- [Decision 47 COM 7B.73 — Sacred Ensembles of the Hoysalas](https://whc.unesco.org/en/decisions/8797) — inspected for: asi_karnataka_d5d33227e0a3a92f, asi_karnataka_f29968094d7b92b1
- [Mahabodhi Temple Complex at Bodh Gaya](https://whc.unesco.org/en/list/1056/) — inspected for: whc_b64d0b1bb2989639c1f1
- [Kakatiya Rudreshwara (Ramappa) Temple, Telangana](https://whc.unesco.org/en/list/1570) — inspected for: asi_telangana_f3a7458053e48f24
- [UNESCO World Heritage Centre](https://whc.unesco.org/en/list/1570/) — inspected for: asi_telangana_f3a7458053e48f24
- [Group of Monuments at Pattadakal](https://whc.unesco.org/en/list/239) — inspected for: asi_karnataka_7c32bc783d1664dc
- [Khajuraho Group of Monuments](https://whc.unesco.org/en/list/240/) — inspected for: whc_798b3d431ca45563a0f8
- [Group of Monuments at Hampi](https://whc.unesco.org/en/list/241/) — inspected for: whc_0601b84399076df5f6eb, whc_ffb69144fee941fb01a9
- [Sun Temple, Konârak](https://whc.unesco.org/en/list/246) — inspected for: konark
- [Sun Temple, Konârak](https://whc.unesco.org/en/list/246/) — inspected for: konark
- [Group of Monuments at Mahabalipuram](https://whc.unesco.org/en/list/249/) — inspected for: shore
- [Great Living Chola Temples](https://whc.unesco.org/en/list/250/) — inspected for: asi_tamil_nadu_64f350d8e3dc3e9c, asi_tamil_nadu_9b2980bb768b7c42, brihadeeswarar
- [Temples of Kanchipuram](https://whc.unesco.org/en/tentativelists/6528) — inspected for: asi_tamil_nadu_e53edf8ca8494828
- [Sri Veerabhadra Temple and Monolithic Bull (Nandi), Lepakshi (The Vijayanagara Sculpture and Painting Art Tradition)](https://whc.unesco.org/en/tentativelists/6607/) — inspected for: asi_andhra_prade_bead535e8e3f76eb
- [Sun Temple, Modhera and its adjoining monuments](https://whc.unesco.org/en/tentativelists/6627) — inspected for: asi_gujarat_fd7e0734b68a92df
- [30. Vishnudol, Gaurisagar](https://www.asiguwahaticircle.gov.in/Bishnudol%20Gaurisagar.html) — inspected for: asi_assam_3176178449463d6c
- [31. Sivadol, Gaurisagar](https://www.asiguwahaticircle.gov.in/Sivadol%20Gaurisagar.html) — inspected for: asi_assam_150626777a56d77d
- [Shri Shri Ganesh Temple, Hajo, ASI Guwahati Circle profile](https://www.asiguwahaticircle.gov.in/ganesh%20temple.html) — inspected for: asi_assam_08eedbf158fc288a
- [The Temple of Ranachandi](https://www.asiguwahaticircle.gov.in/ranachandi.html) — inspected for: asi_assam_641483ffa47752ae
- [Martand Temple (National Monuments Authority meeting record, 254th meeting)](https://www.nma.gov.in/showfile.php?lang=2&level=1&lid=535&ls_id=416&nma_type=0) — inspected for: asi_jammu_and_ka_1f8a290d8729fbea
- [FAQ — Shri Kashi Vishwanath Temple](https://www.shrikashivishwanath.org/pdffile/FAQ_SHRI_KASHI_VISHWANTH_TEMPLE_2_0_pdf.pdf) — inspected for: kashi_vishwanath
- [Sri Vidyashankara Temple — Sringeri Sharada Peetham](https://www.srisharadapeetham.org/temples/sri-vidyashankara) — inspected for: asi_karnataka_80d2910c86f3032b
- [TTD Board Resolution Item 269: Proposal concerning Sri Parasurameswara Swamy Temple, Gudimallam](https://www.tirumala.org/BoardResolutions/74_1834.pdf) — inspected for: asi_andhra_prade_24e5a8c78a3f68e5
- [Tirupati Urban Development Authority Master Plan and Zonal Development Plans 2040, Part A](https://www.tudaap.in/Admintuda254tuda124ttda/assets/ZDPR%20Part-A.pdf) — inspected for: asi_andhra_prade_24e5a8c78a3f68e5

## Temples still needing an inspected source page

These 128 IDs have not yet had a relevant external page inspected in this operation (18 have source-attributed corpus documents whose original pages were not confirmed inspected here; the list is exact and resumable):

- `asi_andhra_prade_0eae7591ae183981` — **Palace and two temples of Rama and Krishna** (Anantapuramu, Andhra Pradesh) — status: `not_started`
- `asi_andhra_prade_f5896e760114c743` — **The old temple (Dibbesvarasvami temple)** (Vizianagaram, Andhra Pradesh) — status: `not_started`
- `asi_assam_21748e5141ece6d2` — **Shri Surya Pahar Ruins, Dasabhaja Devasthan** (Goalpara, Assam) — status: `enriched`
- `asi_himachal_pra_f2a74ffbd1613f95` — **Champavati Temple** (Chamba, Himachal Pradesh) — status: `not_started`
- `asi_himachal_pra_196b8a9e201023ce` — **Shri Bajreshwari Temple, Bhardiath** (Chamba, Himachal Pradesh) — status: `not_started`
- `asi_himachal_pra_f001bee4a9b9a47e` — **Shri Bansi Gopal Temple** (Chamba, Himachal Pradesh) — status: `not_started`
- `asi_himachal_pra_749dc6854c0ca88f` — **Shri Sita Ram Temple Muhalla Bangotu** (Chamba, Himachal Pradesh) — status: `not_started`
- `asi_himachal_pra_261e3e311cc68a99` — **Temple at Asapuri** (Kangra, Himachal Pradesh) — status: `not_started`
- `asi_himachal_pra_45d89c71bc32c153` — **Temple of Sidhnath** (Kangra, Himachal Pradesh) — status: `not_started`
- `asi_himachal_pra_c1e0c007c90d08b5` — **A Miniature stone Saiva Temple at Jagat Sukh** (Kullu, Himachal Pradesh) — status: `not_started`
- `asi_himachal_pra_b5aa2390218f7fa8` — **Mirkula Devi Temple** (Lahaul & Spiti, Himachal Pradesh) — status: `not_started`
- `asi_himachal_pra_14fdecc910252f5f` — **Panchvaktra Temple** (Mandi, Himachal Pradesh) — status: `not_started`
- `asi_himachal_pra_dddb6f1b1b3e3ef2` — **Temple of Trillokinath** (Mandi, Himachal Pradesh) — status: `source_gap`
- `asi_jammu_and_ka_f0c72405cfee5ce7` — **Detha Mandir** (Baramulla, Jammu and Kashmir) — status: `not_started`
- `asi_jammu_and_ka_5832eda4c7e777ea` — **Sankaragaurisvara temple** (Baramulla, Jammu and Kashmir) — status: `not_started`
- `asi_jammu_and_ka_32fcec810cd23272` — **Sugandesha Temple** (Baramulla, Jammu and Kashmir) — status: `not_started`
- `asi_jammu_and_ka_1c06e277029d8ad6` — **Partapswami temple with four Subsidiary shrines** (Baramulla, Jammu and Kashmir) — status: `not_started`
- `asi_karnataka_4a69d324a639a65c` — **Inscription and Jatingi Rameswar Temple** (Chitradurga, Karnataka) — status: `not_started`
- `asi_karnataka_3853d41ca24309c8` — **Akka Tangi Temple** (Chitradurga, Karnataka) — status: `not_started`
- `asi_karnataka_fe399f2c6fb88366` — **Channakesva Temple** (Hassan, Karnataka) — status: `not_started`
- `asi_karnataka_27cd1e0038517009` — **Kesava Temple and Inscriptions** (Hassan, Karnataka) — status: `evidence_extracted`
- `asi_karnataka_ac180b0d6288c76f` — **Mallikarjuna Temple** (Bagalkot, Karnataka) — status: `evidence_extracted`
- `asi_karnataka_2854d2a42446f401` — **Papanatha Temple** (Bagalkot, Karnataka) — status: `evidence_extracted`
- `asi_karnataka_2494fc98f5e2568d` — **Durga Temple** (Bagalkot, Karnataka) — status: `evidence_extracted`
- `asi_karnataka_87e1e40d23b47df2` — **Lad Khan Temple** (Bagalkot, Karnataka) — status: `evidence_extracted`
- `asi_karnataka_a0dee297d7802db0` — **Cave Temples** (Bagalkot, Karnataka) — status: `evidence_extracted`
- `asi_kerala_e6e99bfd98bd5070` — **Siva temple at Netrimangalam** (Palakkad, Kerala) — status: `not_started`
- `asi_kerala_96f43aa8f34c86f4` — **Temples of Parasurama, Brahma, Siva and Matsya** (Thiruvananthapuram, Kerala) — status: `not_started`
- `asi_kerala_72944ced12e189e0` — **Vishnu Temple at Kadavallur** (Thrissur, Kerala) — status: `not_started`
- `asi_kerala_e815fe3f10fdd760` — **Siva Temple complex, Peruvanam** (Thrissur, Kerala) — status: `not_started`
- `asi_kerala_ecb9c135966535b1` — **Sriramaswami temple** (Thrissur, Kerala) — status: `not_started`
- `asi_madhya_prade_3be4b3cfd9e31141` — **Jain Temples 1 to 5** (Ashok Nagar, Madhya Pradesh) — status: `not_started`
- `asi_madhya_prade_8a70b2ed617f5dee` — **Temples 2 to 7** (Ashok Nagar, Madhya Pradesh) — status: `not_started`
- `asi_madhya_prade_39f87ba33fbc0dff` — **Andhakuan Group of Temples** (Ashok Nagar, Madhya Pradesh) — status: `not_started`
- `asi_madhya_prade_9ebdb8af62835385` — **Gargaj and Mahadev Ghat Group of Temples** (Ashok Nagar, Madhya Pradesh) — status: `not_started`
- `asi_madhya_prade_730baf46b521ee24` — **Hanuman Marhi Group of Temples** (Ashok Nagar, Madhya Pradesh) — status: `not_started`
- `asi_madhya_prade_9cc250591e94d31e` — **Sitamarhi Group of Temples** (Ashok Nagar, Madhya Pradesh) — status: `not_started`
- `asi_madhya_prade_e69aa82e756a5d9a` — **Mahadeo Temple with its compound near the inspection Bunglow** (Burhanpur, Madhya Pradesh) — status: `not_started`
- `asi_madhya_prade_02029e9c2d8d1670` — **Brick Temples (two)** (Bhind, Madhya Pradesh) — status: `not_started`
- `asi_madhya_prade_ea71d0bc499fc609` — **Sas Bahu Temples** (Gwalior, Madhya Pradesh) — status: `evidence_extracted`
- `asi_maharashtra_751d30fc81cbcd46` — **Hemadpanthi Temple** (Ahmednagar, Maharashtra) — status: `not_started`
- `asi_maharashtra_c1a7e8d462e133f0` — **Jain Temple** (Ahmednagar, Maharashtra) — status: `not_started`
- `asi_maharashtra_c8f2dfebe1308e89` — **Hemadpanthi Temple of Shree Mahadev (Taponeshwar)** (Yeotmal, Maharashtra) — status: `not_started`
- `asi_maharashtra_96d11a89fd351641` — **Kopeshwar Temple** (Kolhapur, Maharashtra) — status: `not_started`
- `asi_odisha_a99e7488945c8296` — **Chausatti Jogini temple together with three minor shrines** (Bolangir, Odisha) — status: `not_started`
- `asi_odisha_20cdc50e15a57135` — **Group of Temples** (Bolangir, Odisha) — status: `not_started`
- `asi_odisha_22c609400a8e68dd` — **Temples of Nilamadhava and Siddheswara** (Boudh, Odisha) — status: `not_started`
- `asi_odisha_f9799c0f052ff1eb` — **Paschima-Somanatha and Kapilesvara Temples** (Boudh, Odisha) — status: `not_started`
- `asi_odisha_5328f8745ffc1d9c` — **Bhima Temple** (Gajapati, Odisha) — status: `not_started`
- `asi_odisha_8381056230321b2b` — **Kunti Temple** (Gajapati, Odisha) — status: `not_started`
- `asi_odisha_477f232bcad1ceb5` — **Yudhishthira Temple** (Gajapati, Odisha) — status: `not_started`
- `asi_odisha_ec436988567c52b2` — **Monuments of Gangadhara Swami** (Ganjam, Odisha) — status: `not_started`
- `asi_odisha_df77a3c4a87c5deb` — **Jagadeswara Swami** (Ganjam, Odisha) — status: `not_started`
- `asi_odisha_4e2ff9dbfa31c9c4` — **Bhaskareswar Temple** (Khurda, Odisha) — status: `evidence_extracted`
- `asi_odisha_9b7d1946270be4a0` — **Brahmeswar Temple with minor shrines** (Khurda, Odisha) — status: `evidence_extracted`
- `asi_odisha_f4c379be270f3526` — **Ananta Basudeva Temple** (Khurda, Odisha) — status: `evidence_extracted`
- `asi_odisha_224c8e9b9c4d99fd` — **Baitala Temple** (Khurda, Odisha) — status: `evidence_extracted`
- `asi_odisha_db2df3391ab83241` — **Chitrakarini Temple** (Khurda, Odisha) — status: `not_started`
- `asi_odisha_7af4bfe1534010f1` — **Jameswar Temple** (Khurda, Odisha) — status: `not_started`
- `asi_odisha_871ae670bd5d4d3d` — **Lingaraj Temple** (Khurda, Odisha) — status: `evidence_extracted`
- `asi_odisha_03c187b9f1d681a5` — **Maitreswar Temple** (Khurda, Odisha) — status: `not_started`
- `asi_odisha_a16934ba2669f290` — **Makareswar Temple** (Khurda, Odisha) — status: `not_started`
- `asi_odisha_f2a6072b85b7702d` — **Markandeswar Temple** (Khurda, Odisha) — status: `not_started`
- `asi_odisha_a534d4ada83fa69c` — **Mukteswar Temple** (Khurda, Odisha) — status: `evidence_extracted`
- `asi_odisha_9a65411c4e7a8720` — **Parsurameswar Temple** (Khurda, Odisha) — status: `evidence_extracted`
- `asi_odisha_b33605c4fe242dbb` — **Siddheswar Temple** (Khurda, Odisha) — status: `not_started`
- `asi_odisha_f3ef7830ee3d5a70` — **Kapileswar Temple** (Khurda, Odisha) — status: `not_started`
- `asi_tamil_nadu_391fcec2d80aafc7` — **Sri Pataleswara Temple** (Villupuram, Tamil Nadu) — status: `not_started`
- `asi_tamil_nadu_e61d14dae331b5c6` — **Sri Brahmapuriswara Temple** (Villupuram, Tamil Nadu) — status: `not_started`
- `asi_tamil_nadu_4c1f14f2232e8d73` — **Kailasanatha temple** (Kanchipuram, Tamil Nadu) — status: `evidence_extracted`
- `asi_tamil_nadu_7f9b8196b0215b46` — **Piravathanesvara temple** (Kanchipuram, Tamil Nadu) — status: `not_started`
- `asi_tamil_nadu_02e99fdbd7948315` — **Iravathanesvara temple** (Kanchipuram, Tamil Nadu) — status: `not_started`
- `asi_tamil_nadu_9749a48a5fe7189c` — **Jvarahesvara temple** (Kanchipuram, Tamil Nadu) — status: `not_started`
- `asi_tamil_nadu_22c217c323d0a7d5` — **Mathangesvara temple** (Kanchipuram, Tamil Nadu) — status: `not_started`
- `asi_tamil_nadu_a080ae14b6ea9152` — **Muktesvara temple** (Kanchipuram, Tamil Nadu) — status: `not_started`
- `asi_tamil_nadu_3d38b8ffebe20845` — **Nithya kalyanaswami Temple** (Kanchipuram, Tamil Nadu) — status: `not_started`
- `asi_tamil_nadu_c70316ee1074960c` — **Tirupuleswarar Temple** (Kanchipuram, Tamil Nadu) — status: `not_started`
- `asi_tamil_nadu_6b95918b411d34a5` — **Ranganathaswamy temple** (Namakkal, Tamil Nadu) — status: `not_started`
- `asi_tamil_nadu_45cdbc557dc243f5` — **Narasimhaswamy temple** (Namakkal, Tamil Nadu) — status: `not_started`
- `asi_tamil_nadu_ad4715a221a1521c` — **Muruganatha temple** (Coimbatore, Tamil Nadu) — status: `not_started`
- `asi_tamil_nadu_327b4fca42edb96e` — **Chennarayaperumal temple** (Dharmapuri, Tamil Nadu) — status: `not_started`
- `asi_tamil_nadu_f4f02026c173d091` — **Korangunatha temple** (Karur, Tamil Nadu) — status: `evidence_extracted`
- `asi_rajasthan_f0ba506b3db47dae` — **Siva temple** (Alwar, Rajasthan) — status: `not_started`
- `asi_rajasthan_5f25a885fee268fd` — **Ruins of Temples** (Baran, Rajasthan) — status: `not_started`
- `asi_rajasthan_2721058d5e165985` — **Temple (12 century)** (Baran, Rajasthan) — status: `not_started`
- `asi_rajasthan_2dd827c13c7e541a` — **Usha Mandir** (Bharatpur, Rajasthan) — status: `not_started`
- `asi_rajasthan_31737518a207a194` — **Chaurasi Khamba temple** (Bharatpur, Rajasthan) — status: `not_started`
- `asi_rajasthan_3528d7534d1b4939` — **Mahakal and two other temples** (Bhilwara, Rajasthan) — status: `not_started`
- `asi_rajasthan_13e5aee2c374e844` — **Temple of Shiv, Ganesh and adjoining Kund** (Chittorgarh, Rajasthan) — status: `not_started`
- `asi_telangana_39f3f37fca8287ca` — **Alampur Temples** (Jagulamba Gadwal, Telangana) — status: `evidence_extracted`
- `asi_telangana_cc77c673d026d843` — **Thousand Pillared temple** (Warangal-Urban, Telangana) — status: `evidence_extracted`
- `asi_gujarat_6267ab451be02ce3` — **Temple of Galteshwar** (Kheda, Gujarat) — status: `not_started`
- `asi_gujarat_996f3029d0c5f44f` — **Jasmalnathji Mahadev temple** (Mehsana, Gujarat) — status: `not_started`
- `asi_gujarat_a5a107387b925508` — **Hingloji Mata temple** (Mehsana, Gujarat) — status: `not_started`
- `asi_gujarat_fd44e3f30d745a6c` — **Malai Mata temple** (Mehsana, Gujarat) — status: `not_started`
- `asi_gujarat_8f67b8724590e5e7` — **Sitamata temple** (Mehsana, Gujarat) — status: `not_started`
- `asi_gujarat_26a0e24bc3f63029` — **Torana with a Surya Temple** (Mehsana, Gujarat) — status: `not_started`
- `asi_gujarat_44e195418584abce` — **Nilkantheswar Mahadev temple** (Mehsana, Gujarat) — status: `not_started`
- `asi_gujarat_17fd66842c6141ff` — **Sivai Mata temple** (Mehsana, Gujarat) — status: `not_started`
- `asi_uttarakhand_2d8956bf44158d84` — **Gujardeo Temple** (Almora, Uttarakhand) — status: `not_started`
- `asi_uttarakhand_14ba3ed9412c2289` — **Badrinath group of Temples** (Almora, Uttarakhand) — status: `not_started`
- `asi_uttarakhand_7a35c895a84fabbb` — **Bandeo Temple** (Almora, Uttarakhand) — status: `not_started`
- `asi_uttarakhand_6723226d57c01cf2` — **Kacheri group of Temple** (Almora, Uttarakhand) — status: `not_started`
- `asi_uttarakhand_5ab9fee964329668` — **Kutumbari Temple** (Almora, Uttarakhand) — status: `not_started`
- `asi_uttarakhand_2e56b83a4ba9bc45` — **Maniyan group of Temples** (Almora, Uttarakhand) — status: `not_started`
- `asi_uttarakhand_0747aeef9d6d49bd` — **Surya Temple** (Almora, Uttarakhand) — status: `not_started`
- `asi_uttarakhand_35b0da4b7733f1c2` — **Dandeshwar Temple** (Almora, Uttarakhand) — status: `not_started`
- `asi_uttarakhand_04515971b1f81327` — **Jageshwar Temple** (Almora, Uttarakhand) — status: `not_started`
- `asi_uttarakhand_0f29234748b59280` — **Kuber Temple** (Almora, Uttarakhand) — status: `not_started`
- `asi_uttarakhand_8ab8a87bbf5957ac` — **Mritunjaya Temple** (Almora, Uttarakhand) — status: `not_started`
- `asi_uttarakhand_81847ed76c1dc2f9` — **Nanda Devi or Nau Durga** (Almora, Uttarakhand) — status: `not_started`
- `asi_uttarakhand_749c98c406b1c2c0` — **Group of ancient temples, main shrine of Siva and subsidiary shrines** (Bageshwar, Uttarakhand) — status: `not_started`
- `asi_uttarakhand_c0260c03af3b545b` — **Lakshmi Narayan, Rakshas Deval and Satya Narayan Temples** (Bageshwar, Uttarakhand) — status: `not_started`
- `asi_uttarakhand_5ab1fdf713889f62` — **Remains of sixteen temples** (Chamoli, Uttarakhand) — status: `not_started`
- `asi_uttarakhand_84fff101928cc2fc` — **Rudranath temple** (Chamoli, Uttarakhand) — status: `not_started`
- `asi_uttarakhand_fcbe014224f39483` — **Two Temple** (Chamoli, Uttarakhand) — status: `not_started`
- `asi_uttarakhand_1d25a82cc5f91d46` — **Group of Baleshwar Temples** (Champawat, Uttarakhand) — status: `not_started`
- `asi_uttarakhand_a03db0d2ca2f253a` — **Temple sacred to Mahasu** (Dehradun, Uttarakhand) — status: `not_started`
- `asi_west_bengal_39fc2872e6818bc1` — **Ancient Temple** (Bankura, West Bengal) — status: `not_started`
- `asi_west_bengal_23eb0de7e9cf942e` — **Brindaban Chandra Temple** (Bankura, West Bengal) — status: `not_started`
- `asi_west_bengal_ac3d3194de07c169` — **Radha Damodar Temple** (Bankura, West Bengal) — status: `not_started`
- `asi_west_bengal_e756fa05949d5297` — **Old Temple at Banda** (Purulia, West Bengal) — status: `not_started`
- `asi_west_bengal_537a9276da8ba940` — **Dharmaraj Temple** (Midanapur, West Bengal) — status: `not_started`
- `asi_west_bengal_fc6f7b005a338966` — **Temples of Bandyopadhyay Family** (Midanapur, West Bengal) — status: `not_started`
- `asi_west_bengal_8a31f276999645d4` — **Sitala Temples** (Midanapur, West Bengal) — status: `not_started`
- `asi_west_bengal_4639dc1c20a6d5a3` — **Nava Ratna Temple Complex** (Midanapur, West Bengal) — status: `not_started`
- `asi_west_bengal_7fa4da47836e015d` — **Temple** (Nadia, West Bengal) — status: `not_started`
- `asi_west_bengal_251d1e7bbd6e7117` — **26 Shiva Temples** (North 24 Parganas, West Bengal) — status: `not_started`

## Partially researched temples and remaining gaps

The following temples have at least one inspected source page, but none has a complete seven-topic research profile. Their exact outstanding category gaps are recorded below.

- `brihadeeswarar` — **Brihadisvara Temple (Thanjavur)** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `shore` — **Shore Temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `konark` — **Sun Temple at Konark** — gaps: festivals_traditions, inscriptions_historical_evidence, visitor_information
- `meenakshi` — **Meenakshi Amman Temple** — gaps: festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `jagannath` — **Jagannath Temple in Puri** — gaps: festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `kashi_vishwanath` — **Kashi Vishwanath Temple** — gaps: historical_background, architecture, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_andhra_prade_4824bbb04f702849` — **Madhavaraya temple (Old Vishnu temple)** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, visitor_information
- `asi_andhra_prade_63f2355eafb0759e` — **Group of old temples** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_andhra_prade_5509b425f6edbf42` — **Mallikarjuna (Siva) temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_andhra_prade_bead535e8e3f76eb` — **Veerabhadra temple (Lepakashi)** — gaps: religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, visitor_information
- `asi_andhra_prade_34fdc7ad2433488f` — **Basavannah temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_andhra_prade_994f268937105045` — **Chintalarayaswami temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_andhra_prade_e74ff866d54d0cc2` — **Rameswaraswami temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_andhra_prade_24e5a8c78a3f68e5` — **Parasuramesvara temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_andhra_prade_85900195bd76980b` — **Palliswara mudaya Mahadeva temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_andhra_prade_e429b0544ae6aaa7` — **Venkateswara Vishnu temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_andhra_prade_ba65914fa7b7de40` — **Chennakeswaraswami temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_andhra_prade_d219a5f1c4c7fc35` — **Gollingeswara group of temples** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_andhra_prade_4902522d216f33d7` — **Nakkalagudi** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_andhra_prade_78f1c41f21c933de` — **Veerabhadra temple (Biccavolu)** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_assam_4bf398fbc498bf4d` — **Bordole temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_assam_24dc8f3855351f21` — **Dhandi temple** — gaps: architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, visitor_information
- `asi_assam_641483ffa47752ae` — **The temple of Ranachandi** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_assam_dbf0ecb97451eb87` — **Sivadol (Negheriting)** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_assam_0aecea616e14afa3` — **Shri Shri Hayagriva Madhava temple** — gaps: historical_background, architecture, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_assam_6bca1547cfa3d7cc` — **Shri Shri Kedar temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_assam_08eedbf158fc288a` — **Shri Shri Ganesh temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_assam_73c2196bfdf2df7a` — **Shri Shri Kameshwar temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_assam_3176178449463d6c` — **Bisdol (Bishnudol) (Gaurisagar)** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, visitor_information
- `asi_assam_d296790c660bb3b9` — **Devidol (Gaurisagar)** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_assam_150626777a56d77d` — **Sivadol (Gaurisagar)** — gaps: historical_background, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, visitor_information
- `asi_assam_80af7f930eb9cfb5` — **Bisdol (Bishnudol) (Joysagar)** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_assam_6f13d020bbaf4068` — **Devidol (Joysagar)** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_assam_888093ddb8ea0098` — **Ranganath dole** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_assam_fcd74543096308a5` — **Sivadol (Joysagar)** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_assam_087d550e6d805059` — **Bishnu dole** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_assam_6324da2158eb30bc` — **Debi dole** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_assam_53f3d143b7f21899` — **Siva dole** — gaps: historical_background, architecture, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_assam_68e3d36ac845c504` — **The mound and ruins of the stone temple at Parbatiya** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_himachal_pra_c5706cddb70077f6` — **Ganesh Temple Bharmaur** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_himachal_pra_3e34b97076b4e1a3` — **Laxmi (Lakhan) Devi Temple Bharmaur** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_himachal_pra_7509a21fdaa8af22` — **Mani Mahesh Temple Bharmaur** — gaps: architecture, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_himachal_pra_4a3a5f31aa66c811` — **Narsingh Temple Bharmaur** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_himachal_pra_2cd9e34ca0dd4e17` — **Shri Chamunda Devi Temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_himachal_pra_56b348db7df5aa99` — **Shri Hari Rai Temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_himachal_pra_a6a66c91268cdcdf` — **Shri Lakshmi Narayan group of Temples, Muhalla Hattnala** — gaps: festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_himachal_pra_29892a543f8e7863` — **Sri Shakti Devi Temple** — gaps: festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_himachal_pra_d0cbd9e9b4b403a2` — **Temple of Baijnath** — gaps: historical_background, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_himachal_pra_a1ef8ff6339c407d` — **Monolithic Temples at Masrur with sculptures lying in and outside them** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_himachal_pra_2d93808a25e7f773` — **Temple of Basheshar Mahadeo at Hat** — gaps: architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_himachal_pra_9681bf3ab0a6c3f8` — **Temple of Gaurishankar with sculptures** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_himachal_pra_aac4a2248ad925db` — **Hidimba Devi Temple** — gaps: festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_himachal_pra_53211815add81171` — **Temple of Gaurishankar with its sculptures** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_jammu_and_ka_1f8a290d8729fbea` — **Ancient temple of Martand** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_karnataka_39c8b5453cc604ec` — **Vijayanarayana Temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_karnataka_df9d7ed1a005d4a6` — **Arkesvara Temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_karnataka_20e758c06d541bd9` — **Ramesvara Temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_karnataka_e7e3292346518668` — **Gaurisvara Temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_karnataka_1544f0a56a8c103b` — **Bhoganandisvara Temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_karnataka_43d31d5b7b909f6e` — **Amritesvara Temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_karnataka_4e9044ce27267cfb` — **Viranarayana Temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_karnataka_80d2910c86f3032b` — **Vidyasankara Temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_karnataka_2afd54b8e1b183a7` — **Hariharesvara Temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_karnataka_e1c13713806e44d6` — **Isvara Temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_karnataka_03633ec3263fe299` — **Lakshmi devi Temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_karnataka_d5d33227e0a3a92f` — **Hoysalesvara Temple** — gaps: historical_background, festivals_traditions, inscriptions_historical_evidence, visitor_information
- `asi_karnataka_f29968094d7b92b1` — **Keshava Temple** — gaps: historical_background, architecture, festivals_traditions, inscriptions_historical_evidence, visitor_information
- `asi_karnataka_7c32bc783d1664dc` — **Virupaksha Temple (Pattadakal)** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_tamil_nadu_228792b71860b713` — **Venketaramana Temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_tamil_nadu_b8864915b92941b5` — **Pattabirama Temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_tamil_nadu_8efa92f0aa42a214` — **Rock cut Pallava Temple (Dalavanur)** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_tamil_nadu_476eb8cc97fb84ef` — **Pallava rock cut shrine** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_tamil_nadu_94ef770652db64a5` — **Rock cut Pallava temple (Mandagapattu)** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_tamil_nadu_c4c0740aa244e2f1` — **Talagiriswara temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_tamil_nadu_dfe60f19c80a4e44` — **Sri Azhagiya Narasimma perumal temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_tamil_nadu_9ff95b5f3937c27a` — **Sri Apathsahayeswara Temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_tamil_nadu_e53edf8ca8494828` — **Vaikuntaperumal temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_tamil_nadu_9b2980bb768b7c42` — **Brihadisvara Temple (Gangaikondacholapuram)** — gaps: historical_background, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, visitor_information
- `asi_tamil_nadu_64f350d8e3dc3e9c` — **Airavatesvara Temple** — gaps: religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, visitor_information
- `asi_telangana_f3a7458053e48f24` — **Ramappa temple** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `asi_gujarat_fd7e0734b68a92df` — **Sun temple, Surya kind with adjoining other temples and loose sculptures** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `whc_798b3d431ca45563a0f8` — **Khajuraho Group of Monuments** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `whc_b64d0b1bb2989639c1f1` — **Mahabodhi Temple Complex** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, heritage_conservation, visitor_information
- `whc_ffb69144fee941fb01a9` — **Virupaksha Temple (Hampi)** — gaps: architecture, festivals_traditions, inscriptions_historical_evidence, visitor_information
- `whc_0601b84399076df5f6eb` — **Vitthala Temple Complex** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, visitor_information
- `whc_b5eaf9ee03e0215d1573` — **Krishna Temple Complex** — gaps: architecture, festivals_traditions, inscriptions_historical_evidence, visitor_information
- `whc_57e81c99363e3334087c` — **Achyutaraya Temple Complex** — gaps: historical_background, architecture, religious_cultural_significance, festivals_traditions, inscriptions_historical_evidence, visitor_information
- `whc_5a482f12eb769406674c` — **Pattabhirama Temple Complex** — gaps: architecture, festivals_traditions, inscriptions_historical_evidence, visitor_information
- `whc_0550440746a0ab1b40e6` — **Hemakuta Group of Temples** — gaps: architecture, festivals_traditions, inscriptions_historical_evidence, visitor_information

## Verification and known limitations

- New source claims are paraphrases pending human review. Opened pages and source metadata were checked; this does not constitute independent historical verification.
- Conflicting chronology for Chamba's Lakshmi Narayan complex (state government pilgrimage page: broad 8th-century group date; state tourism page: main Vishnu shrine attributed to Sahil Varman in the 10th century) is preserved in the documents for review.
- The 2019 Masroor project profile and Himachal Tourism page differ on the number of rock-cut temples (19 versus 15); both accounts are disclosed in the document.
- The official Himachal Tourism Trilokinath entry describes an Udaipur, Lahaul-Spiti shrine, whereas the catalogue record is localized to Mandi. It was not attached; the mismatch is in the research plan.
- Retrieval context admission is evaluated locally. The latest report records 1 potentially unrelated contexts among 1173 unsupported-topic queries. A previous one-off name-query miss for Debi dole did not repeat on the latest full run (name-query success: 216/217).
- A candidate Assam Directorate of Archaeology protected-sites page returned HTTP 404 on direct access; the search result was not used as evidence and the failed attempt is recorded in the research plan.
- Source pages for festival dates, visitor timings, fees and access were not assumed current unless explicitly dated by the page. No OpenRouter call was made.

## Test and command record

- `python -m app.ingestion validate`: passed for 391 curated documents and 217 catalogue records; pending human-review warnings are expected.
- `python -m app.ingestion index --dry-run`: latest consecutive dry runs matched; 7 documents / 13 chunks to add, with 529 existing chunks unchanged.
- `python -m app.ingestion index`: completed incrementally; latest collection count is 529.
- `python scripts/evaluate_retrieval_all_temples.py`: local retrieval only; 216/217 name queries, 346/346 evidence-available topic queries, 3800/3800 citation metadata matches. No OpenRouter call was made.
- Backend pytest and Python compilation results are recorded in the current work log; frontend files were not changed.

## Resume instructions

Use `research_plan_all_217.json` as the authoritative queue. Continue first with rows whose `sources_inspected` list is empty, then re-research the inspected rows' `missing_categories`. Verify any candidate page before adding its URL to `source_checks_this_operation`; do not treat corpus citations or a source URL alone as inspected evidence. Save a backup and checkpoint after every small group.
