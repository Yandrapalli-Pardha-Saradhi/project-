import React from "react";
import { checkHealth, getStates, getTemples, getTemple, getTempleFacets, sendChat } from "./services/api";
import type { Temple } from "./services/api";
import type { ChatResponse, ConversationMessage } from "./types/chat";
import { SUPPORTED_LANGUAGES } from "./types/chat";

type Message = { role: "user" | "assistant"; content: string; result?: ChatResponse };
const suggestions = ["What makes Dravidian temple architecture distinctive?", "Tell me about the Shore Temple's history", "How was the Konark Sun Temple designed?"];

function App() {
  const [path, setPath] = React.useState(location.pathname);
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const [temples, setTemples] = React.useState<Temple[]>([]);
  const [states, setStates] = React.useState<string[]>([]);
  const [districtOptions, setDistrictOptions] = React.useState<string[]>([]);
  const [templeOptions, setTempleOptions] = React.useState<Temple[]>([]);
  const [selectedTempleName, setSelectedTempleName] = React.useState("");
  const [total, setTotal] = React.useState(0);
  const [offset, setOffset] = React.useState(0);
  const [hasMore, setHasMore] = React.useState(false);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState("");
  const [query, setQuery] = React.useState("");
  const [state, setState] = React.useState("");
  const [district, setDistrict] = React.useState("");
  const [area, setArea] = React.useState("");
  const [selected, setSelected] = React.useState<Temple | null>(null);
  const [health, setHealth] = React.useState("checking");
  const [language, setLanguage] = React.useState("en");
  const [templeScope, setTempleScope] = React.useState<string | null>(null);
  const [messages, setMessages] = React.useState<Message[]>([]);
  const [draft, setDraft] = React.useState("");
  const [chatLoading, setChatLoading] = React.useState(false);
  const chatBusy = React.useRef(false);
  const chatSession = React.useRef(0);
  const chatAbort = React.useRef<AbortController | null>(null);
  const [chatError, setChatError] = React.useState("");
  const [chatInputError, setChatInputError] = React.useState("");
  const [detailsLoading, setDetailsLoading] = React.useState(false);
  const [detailsError, setDetailsError] = React.useState("");
  const [catalogueRefresh, setCatalogueRefresh] = React.useState(0);
  const [discoveryNotice, setDiscoveryNotice] = React.useState("");
  const detailsAbort = React.useRef<AbortController | null>(null);
  const listRef = React.useRef<HTMLElement>(null);
  const messagesEnd = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const onPop = () => { setPath(location.pathname); setMobileOpen(false); };
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);
  React.useEffect(() => { checkHealth().then(() => setHealth("online")).catch(() => setHealth("offline")); getStates().then(setStates).catch(() => setError("Temple catalogue could not be loaded.")); }, []);
  React.useEffect(() => {
    const controller = new AbortController();
    getTempleFacets({ state, district }, controller.signal).then(facets => {
      setDistrictOptions(facets.districts);
      setTempleOptions(facets.temples);
      if (district && !facets.districts.includes(district)) setDistrict("");
      if (selectedTempleName && !facets.temples.some(t => t.names[0] === selectedTempleName)) setSelectedTempleName("");
    }).catch(() => { if (!controller.signal.aborted) { setDistrictOptions([]); setTempleOptions([]); } });
    return () => controller.abort();
  }, [state, district]);
  React.useEffect(() => { setOffset(0); }, [query, state, district, area]);
  React.useEffect(() => {
    const controller = new AbortController();
    setLoading(true); setError("");
    getTemples({ query, state, district, area, limit: 12, offset }, controller.signal).then(page => {
      setTemples(current => offset ? [...current, ...page.items] : page.items);
      setTotal(page.total);
      setHasMore(offset + page.items.length < page.total);
    }).catch(err => { if (!controller.signal.aborted) setError(err instanceof Error ? err.message : "Could not load temples."); }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [query, state, district, area, offset, catalogueRefresh]);
  React.useEffect(() => { messagesEnd.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, chatLoading]);

  const navigate = (next: string) => {
    if (!next.startsWith("/temples/")) {
      detailsAbort.current?.abort();
      detailsAbort.current = null;
      setDetailsLoading(false);
    }
    history.pushState({}, "", next); setPath(next); setMobileOpen(false); window.scrollTo({ top: 0, behavior: "smooth" });
  };
  const openTemple = async (id: string) => {
    detailsAbort.current?.abort();
    const controller = new AbortController();
    detailsAbort.current = controller;
    navigate(`/temples/${id}`); setDetailsLoading(true); setDetailsError(""); setSelected(null);
    try { setSelected(await getTemple(id, controller.signal)); }
    catch (err) { if (!controller.signal.aborted) setDetailsError(err instanceof Error ? err.message : "Could not load temple details."); }
    finally { if (!controller.signal.aborted) { detailsAbort.current = null; setDetailsLoading(false); } }
  };
  const openChat = (id?: string) => {
    chatSession.current += 1;
    chatAbort.current?.abort();
    chatAbort.current = null;
    chatBusy.current = false;
    setChatLoading(false);
    setDraft("");
    setTempleScope(id || null); setMessages([]); setChatError(""); navigate("/ask");
  };
  const submitChat = async (text = draft) => {
    if (!text.trim() || chatLoading || chatBusy.current) return;
    const question = text.trim(); setDraft(""); setChatInputError(""); setChatError("");
    chatBusy.current = true;
    setMessages(current => {
      const last = current[current.length - 1];
      return last?.role === "user" && last.content === question ? current : [...current, { role: "user", content: question }];
    });
    const completedHistory: ConversationMessage[] = [];
    for (let index = 0; index + 1 < messages.length; index += 1) {
      if (messages[index].role === "user" && messages[index + 1].role === "assistant") {
        completedHistory.push({ ...messages[index], content: messages[index].content.slice(0, 1000) }, {
          ...messages[index + 1],
          content: messages[index + 1].content.slice(0, 1000),
          context_temple_id: messages[index + 1].result?.context_temple_id ?? null,
        });
        index += 1;
      }
    }
    setChatLoading(true);
    const currentSession = chatSession.current;
    const controller = new AbortController();
    chatAbort.current = controller;
    try {
      const result = await sendChat(
        { question, language, temple_id: templeScope, history: completedHistory.slice(-8) },
        controller.signal,
      );
      if (currentSession !== chatSession.current) return;
      setMessages(current => [...current, { role: "assistant", content: result.answer, result }]);
      setTempleScope(result.context_temple_id || null);
    } catch (err) {
      if (currentSession === chatSession.current && !controller.signal.aborted) {
        setChatError(err instanceof Error ? err.message : "The assistant could not respond.");
        setDraft(question);
      }
    } finally {
      if (currentSession === chatSession.current) {
        chatAbort.current = null;
        chatBusy.current = false;
        setChatLoading(false);
      }
    }
  };
  const clearFilters = () => { setQuery(""); setSelectedTempleName(""); setState(""); setDistrict(""); setArea(""); };
  const findAPlace = async () => {
    setDiscoveryNotice("");
    if (loading) { setDiscoveryNotice("The collection is still loading. Choose a place as soon as it appears."); listRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }); return; }
    if (!error && temples[0]) { await openTemple(temples[0].id); return; }
    listRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    try {
      const firstPage = await getTemples({});
      if (firstPage.items[0]) await openTemple(firstPage.items[0].id);
      else setDiscoveryNotice("The temple catalogue is currently empty.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "The temple catalogue could not be loaded.");
    }
  };
  const locationText = (t: Temple) => [t.area, t.district, t.state].filter(Boolean).join(", ");
  const detailId = path.startsWith("/temples/") ? path.split("/")[2] : "";
  React.useEffect(() => { if (detailId && selected?.id !== detailId && !detailsLoading) void openTemple(detailId); }, [detailId]);

  return <div className="site-shell">
    <header className="site-header"><a className="brand" href="/" onClick={e => { e.preventDefault(); navigate("/"); }}><span className="brand-mark">TH</span><span><strong>Temple & Heritage</strong><small>INFORMATION ASSISTANT</small></span></a>
      <button className="menu-toggle" aria-label="Toggle navigation" aria-expanded={mobileOpen} onClick={() => setMobileOpen(!mobileOpen)}>{mobileOpen ? "×" : "☰"}</button>
      <nav className={mobileOpen ? "main-nav open" : "main-nav"}><a className={path === "/" || path.startsWith("/temples") ? "active" : ""} href="/" onClick={e => { e.preventDefault(); navigate("/"); }}>Explore temples</a><a className={path === "/ask" ? "active" : ""} href="/ask" onClick={e => { e.preventDefault(); openChat(); }}>Ask AI</a><span className={`api-status ${health}`}><i />{health === "online" ? "Assistant online" : health === "offline" ? "Service unavailable" : "Connecting"}</span></nav>
    </header>
    {path === "/ask" ? <main className="chat-page"><div className="chat-intro"><span className="eyebrow">A conversation with heritage</span><h1>Ask with curiosity.</h1><p>Explore the stories, architecture and traditions held in our curated sources.</p>{templeScope && <div className="scope-chip">About {(selected?.id === templeScope ? selected.names[0] : temples.find(temple => temple.id === templeScope)?.names[0]) || templeScope}<button onClick={() => openChat()} aria-label="Start a new conversation without temple context">×</button></div>}</div>
      <div className="chat-workspace"><section className="conversation" aria-label="Conversation"><div className="messages">
        {messages.length === 0 && <div className="chat-empty"><span className="assistant-seal">✳</span><h2>Where shall we begin?</h2><p>Ask a question, or try one of these prompts.</p><div className="suggestions">{suggestions.map(s => <button key={s} onClick={() => void submitChat(s)}>{s}<span>↗</span></button>)}</div></div>}
        {messages.map((m, i) => <article className={`message ${m.role}`} key={`${i}-${m.content.slice(0, 12)}`}><span className="message-label">{m.role === "user" ? "YOU" : "HERITAGE ASSISTANT"}</span><div className="message-body">{m.content}</div>{m.result && <>{m.result.insufficient_evidence && <p className="evidence-note">The collection did not find enough reliable evidence to answer this question.</p>}{m.result.generation_disabled && <p className="evidence-note">Showing retrieved evidence. AI generation is not configured.</p>}{m.result.citations.length > 0 && <div className="chat-sources"><b>Sources</b>{m.result.citations.map(c => <a key={c.source_id} href={c.source_url} target="_blank" rel="noreferrer">{c.source_title}<span>↗</span></a>)}</div>}</>}</article>)}
        {chatLoading && <div className="message assistant"><span className="message-label">HERITAGE ASSISTANT</span><div className="typing"><i/><i/><i/> Searching sources and preparing a response</div></div>}
        {chatError && <div className="chat-error" role="alert"><span>{chatError}</span><button onClick={() => void submitChat()}>Retry</button></div>}<div ref={messagesEnd}/>
      </div><form className="composer" onSubmit={e => { e.preventDefault(); void submitChat(); }}><label className="sr-only" htmlFor="chat-prompt">Your question</label><textarea id="chat-prompt" value={draft} maxLength={1000} onChange={e => { setDraft(e.target.value); setChatInputError(""); }} onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); void submitChat(); } }} placeholder="Ask about a temple, its history, or architecture…" rows={2} disabled={chatLoading}/><div className="composer-footer"><select aria-label="Answer language" value={language} onChange={e => setLanguage(e.target.value)}>{SUPPORTED_LANGUAGES.map(l => <option key={l.code} value={l.code}>{l.label}</option>)}</select><span>Enter to send · Shift + Enter for a new line</span><button type="submit" disabled={!draft.trim() || chatLoading}>Send <span>↑</span></button></div>{chatInputError && <p className="field-error">{chatInputError}</p>}</form></section><aside className="chat-aside"><span className="eyebrow">Grounded in sources</span><h3>Knowledge, with context.</h3><p>Answers draw on the curated heritage collection and include links to their sources.</p><div className="aside-rule"/><div className="aside-stat"><strong>Curated</strong><span>heritage source documents</span></div><button className="text-link" onClick={() => navigate("/")}>Browse the temple catalogue <span>→</span></button></aside></div>
    </main> : detailId ? <main className="detail-page"><button className="back-link" onClick={() => { navigate("/"); setSelected(null); }}>← Back to discovery</button>{detailsLoading ? <div className="state-panel">Loading temple details…</div> : detailsError ? <div className="state-panel error-state"><h2>Details unavailable</h2><p>{detailsError}</p><button onClick={() => void openTemple(detailId)}>Try again</button></div> : selected && <><div className="detail-hero"><div><span className="eyebrow">A place in the living heritage</span><h1>{selected.names[0]}</h1>{locationText(selected) && <p className="detail-location">⌖ &nbsp;{locationText(selected)}</p>}</div><button className="button button-dark" onClick={() => openChat(selected.id)}>Ask AI about this temple <span>↗</span></button></div><div className="detail-columns"><article className="detail-story"><span className="section-kicker">THE STORY</span><h2>History & heritage</h2><p>{selected.description}</p>{selected.history && <p>{selected.history}</p>}<button className="button button-gold" onClick={() => openChat(selected.id)}>Continue exploring with AI <span>→</span></button></article><aside className="detail-facts"><span className="section-kicker">AT A GLANCE</span>{selected.area && <div><small>LOCATION</small><strong>{locationText(selected)}</strong></div>}{selected.state && <div><small>STATE</small><strong>{selected.state}</strong></div>}<div className="source-list"><small>CURATED SOURCES</small>{[...selected.sources, ...(selected.location_source ? [selected.location_source] : [])].map((s, i) => <a href={s.url} key={`${s.url}-${i}`} target="_blank" rel="noreferrer">{s.title}<span>↗</span>{s.publisher && <small>{s.publisher}</small>}</a>)}</div></aside></div></>}</main> : <main>
      <section className="hero"><div className="hero-content"><span className="eyebrow">A living archive of sacred places</span><h1>India’s heritage,<br/><em>closer than ever.</em></h1><p>Discover the histories, artistry and enduring traditions of India’s temples, grounded in a collection of trusted sources.</p><form className="hero-search" onSubmit={e => { e.preventDefault(); listRef.current?.scrollIntoView({ behavior: "smooth" }); }}><span className="search-icon">⌕</span><label className="sr-only" htmlFor="hero-query">Search temples</label><input id="hero-query" value={query} onChange={e => { setQuery(e.target.value); setSelectedTempleName(""); }} placeholder="Search temples or places…"/><button type="submit" aria-label="Search temples">→</button></form><button className="hero-link" onClick={() => listRef.current?.scrollIntoView({ behavior: "smooth" })}>Explore the collection <span>↓</span></button></div><div className="hero-art" aria-label="Illustration of a traditional Indian temple"><div className="sun-disc"/><div className="temple-drawing"><div className="shikhara"><i/><i/><i/><i/><i/></div><div className="temple-crown"/><div className="temple-roof"/><div className="temple-body"><div className="temple-door"/><div className="pillar p1"/><div className="pillar p2"/></div><div className="temple-base"/></div><div className="art-caption">ARCHITECTURE · MEMORY · DEVOTION</div></div><div className="hero-index"><span>01</span><i/> A JOURNEY THROUGH TIME</div></section>
      <section className="collection" ref={listRef}><div className="section-heading"><div><span className="eyebrow">The curated collection</span><h2><button className="collection-start" onClick={() => void findAPlace()}>Find a place to begin.</button></h2></div><span className="result-count">{loading ? "Updating collection…" : `${total} ${total === 1 ? "place" : "places"}`}</span></div>
        <div className="filter-bar"><div className="filter-search"><span>⌕</span><label className="sr-only" htmlFor="catalog-search">Search by temple name</label><input id="catalog-search" placeholder="Temple or alternate name" value={query} onChange={e => { setQuery(e.target.value); setSelectedTempleName(""); }}/></div><label className="sr-only" htmlFor="state-filter">Filter by state or union territory</label><select id="state-filter" value={state} onChange={e => { setState(e.target.value); setDistrict(""); setQuery(""); setSelectedTempleName(""); }}><option value="">All states &amp; union territories</option>{states.map(s => <option key={s} value={s}>{s}</option>)}</select><label className="sr-only" htmlFor="district-filter">Filter by district</label><select id="district-filter" value={district} disabled={!state || !districtOptions.length} onChange={e => { setDistrict(e.target.value); setQuery(""); setSelectedTempleName(""); }}><option value="">{state ? districtOptions.length ? "All districts" : "No district data" : "Select a state first"}</option>{districtOptions.map(d => <option key={d} value={d}>{d}</option>)}</select><label className="sr-only" htmlFor="temple-filter">Choose a temple</label><select id="temple-filter" value={selectedTempleName} onChange={e => { const name = e.target.value; setSelectedTempleName(name); setQuery(name); }}><option value="">All temples</option>{templeOptions.map(t => <option key={t.id} value={t.names[0]}>{t.names[0]}</option>)}</select><label className="sr-only" htmlFor="area-filter">Filter by area or location</label><input id="area-filter" placeholder="Area / location" value={area} onChange={e => setArea(e.target.value)}/><button className="clear-filters" onClick={clearFilters}>Clear filters</button></div>
        {discoveryNotice && <p className="discovery-notice" role="status">{discoveryNotice}</p>}
        {error ? <div className="state-panel error-state"><h3>We couldn’t reach the collection.</h3><p>{error}</p><button onClick={() => setCatalogueRefresh(n => n + 1)}>Try again</button></div> : loading && !temples.length ? <div className="state-panel">Loading the heritage collection…</div> : temples.length === 0 ? <div className="state-panel"><span className="empty-mark">⌕</span><h3>No temples match those filters.</h3><p>Try another name or clear the selected filters.</p><button onClick={clearFilters}>Clear all filters</button></div> : <div className="temple-grid">{temples.map((t, i) => <article className="temple-card" key={t.id}><div className={`card-art card-art-${i % 3}`}><span className="card-number">{String(i + 1).padStart(2, "0")}</span><span className="card-art-mark">{t.state?.toUpperCase()}</span><div className="mini-temple"><i/><i/><i/><i/><i/><b/></div></div><div className="card-content">{locationText(t) && <span className="card-location">{locationText(t)}</span>}<h3>{t.names[0]}</h3><p>{t.description}</p><button onClick={() => void openTemple(t.id)}>Explore details <span>→</span></button></div></article>)}</div>}
        {hasMore && !error && <div className="pagination"><button className="button button-gold" onClick={() => setOffset(value => value + 12)} disabled={loading}>{loading ? "Loading…" : "Load more places"}</button><span>Showing {temples.length} of {total} matching places</span></div>}
      </section><section className="closing-note"><span className="closing-symbol">✳</span><div><span className="eyebrow">The stories continue</span><h2>Curiosity is a kind of pilgrimage.</h2><p>Ask a question and explore what the sources reveal.</p></div><button className="button button-dark" onClick={() => openChat()}>Ask the heritage assistant <span>↗</span></button></section>
    </main>}
    <footer className="site-footer"><a className="footer-brand" href="/" onClick={e => {e.preventDefault(); navigate("/");}}>TEMPLE & HERITAGE</a><span>Knowledge grounded in curated heritage sources.</span><span>Built for the preservation of memory.</span></footer>
  </div>;
}
export default App;
