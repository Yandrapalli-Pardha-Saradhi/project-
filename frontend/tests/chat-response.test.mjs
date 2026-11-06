import test from "node:test";
import assert from "node:assert/strict";
import { normalizeChatResponse } from "../src/services/chatResponse.ts";

const citation = {
  source_id: "doc-1",
  source_title: "Temple history",
  source_url: "https://example.org/temple",
  publisher: "Heritage Archive",
  excerpt: "Supporting passage.",
};

function response(answer, overrides = {}) {
  return {
    answer,
    citations: [],
    language: "en",
    insufficient_evidence: false,
    generation_disabled: false,
    ...overrides,
  };
}

test("keeps an ordinary generated answer unchanged", () => {
  const answer = "The temple developed over several historical periods.";
  assert.equal(normalizeChatResponse(response(answer)).answer, answer);
});

test("extracts a structured JSON answer once and preserves API citations", () => {
  const result = normalizeChatResponse(response(JSON.stringify({
    answer: "The evidence does not identify one original builder.",
    cited_chunk_ids: ["chunk-1"],
  }), { citations: [citation] }));
  assert.equal(result.answer, "The evidence does not identify one original builder.");
  assert.deepEqual(result.citations, [citation]);
});

test("does not mistake citation-bearing natural language for a JSON wrapper", () => {
  const answer = "The inscription records a later renovation [chunk-1].";
  const result = normalizeChatResponse(response(answer, { citations: [citation] }));
  assert.equal(result.answer, answer);
  assert.equal(result.citations[0].source_url, citation.source_url);
});

test("keeps insufficient-evidence responses as natural language", () => {
  const answer = "I could not find sufficient reliable evidence to answer that.";
  const result = normalizeChatResponse(response(answer, { insufficient_evidence: true }));
  assert.equal(result.answer, answer);
  assert.equal(result.insufficient_evidence, true);
});

test("rejects malformed and unexpected structured answers", () => {
  assert.throws(() => normalizeChatResponse(response('{"answer":')), /malformed structured answer/);
  assert.throws(() => normalizeChatResponse(response('{"message":"unexpected"}')), /unexpected structured answer/);
  assert.throws(() => normalizeChatResponse({ answer: {}, citations: [] }), /incomplete response/);
});
