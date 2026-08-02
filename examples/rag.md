# tokenminning with RAG Systems

Retrieval-Augmented Generation (RAG) systems exist because models need access to relevant external information without requiring all available information to be included in every request.

The challenge is not retrieving more information.

The challenge is retrieving the right information.

---

## Problem

A common failure mode in RAG systems is assuming:

> More retrieved information creates better answers.

However, irrelevant or low-value information can create noise and reduce the model's ability to identify what matters.

---

## tokenmaxxing approach

Retrieve large amounts of context without sufficient prioritization:

- More documents regardless of relevance
- More chunks without quality filtering
- Larger context windows without information selection
- More retrieved passages without ranking

The system prioritizes quantity over information value.

---

## tokenminning approach

Optimize the information pipeline:

```
Query
 ↓
Retrieve candidates
 ↓
Rank by relevance
 ↓
Filter noise
 ↓
Provide focused context
 ↓
Generate answer
```

The amount of retrieved information should match the complexity of the task.

---

## Examples

### tokenmaxxing

Retrieve:

```
50 documents
10,000 tokens
```

Send everything directly to the model without ranking or filtering.

---

### tokenminning

Retrieve:

```
50 documents

↓

Rerank

↓

5 highest-value passages

↓

2,000 high-value tokens
```

---

## Beyond retrieval size

Tokenminning considers:

- Retrieval quality
- Chunk quality
- Metadata
- Ranking
- Context placement
- Information freshness
- Context compression

---

## Principle

The best RAG systems are not the ones that retrieve the most.

They are the ones that retrieve the most useful information.
