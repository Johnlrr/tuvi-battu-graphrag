# System Specification: Hệ Thống Hỏi Đáp Tử Vi / Bát Tự với Hybrid GraphRAG

**Version:** 6.0
**Date:** 2026-06-10
**Team size:** 4 người
**Budget:** $0 (MVP / free-tier first)

***

## Changelog v6.0

- Giữ nguyên toàn bộ nội dung v5.0.
- Bổ sung **Section 29: Ablation Study Framework** — thiết kế hệ thống thử nghiệm đa phương án toàn diện, bao gồm toggle kiến trúc và toggle cho từng chiều kỹ thuật: retrieval path, chunking strategy, fusion method, reranking, query rewriting, embedding model, generation model, entity extraction, và context assembly.
- Bổ sung **`ExperimentConfig`** — cấu trúc dữ liệu chuẩn để định nghĩa, lưu trữ, và tái hiện một experiment.
- Bổ sung **`AblationRunner`** — interface chạy ablation tự động trên golden dataset.
- Bổ sung bảng **pre-defined experiment matrix** gồm 20+ experiment được thiết kế có hệ thống.
- Bổ sung hướng dẫn **phân tích kết quả ablation** và cách ánh xạ từ metric sang quyết định kiến trúc.
- Cập nhật `RAGState` để mang theo `experiment_config` xuyên suốt pipeline.
- Cập nhật Section 19 (Evaluation plan) để tích hợp ablation với evaluation workflow.
- Cập nhật Section 27 (Official implementation decisions) để thêm quyết định liên quan đến ablation.

***

## 1. Mục tiêu hệ thống

Xây dựng một hệ thống hỏi đáp theo ngữ cảnh lá số dành cho **Tử Vi** và **Bát Tự**, trong đó người dùng có thể tạo chart, xem chart trực quan, và trò chuyện với hệ thống để nhận phần giải thích có trích dẫn nguồn.

MVP tập trung vào 3 khả năng chính:

1. Sinh chart từ thông tin ngày/giờ sinh, giới tính, và tên gọi.
2. Hiển thị chart trực quan trong giao diện web.
3. Hỏi đáp theo đúng chart hiện tại bằng hệ thống **Hybrid GraphRAG**, có dẫn nguồn và có kiểm soát hallucination.

Ngoài ra, dự án này có một mục tiêu thứ hai song song: **thử nghiệm có hệ thống nhiều phương án kỹ thuật** để xác định cấu hình tối ưu cho domain tử vi/bát tự thông qua ablation study kỹ lưỡng.

***

## 2. Phạm vi MVP

### 2.1 In-scope

- Đăng ký / đăng nhập bằng Supabase Auth.
- Tạo và lưu chart Tử Vi hoặc Bát Tự.
- Hiển thị chart trên giao diện web.
- Một chart có đúng một chat session đi kèm.
- Chat trả lời trong ngữ cảnh chart hiện tại.
- Retrieval dựa trên chart context + knowledge graph + vector + sparse retrieval.
- Trích dẫn nguồn theo chunk provenance.
- Theo dõi logs / traces bằng Langfuse.
- **Ablation study framework** cho phép chạy và so sánh nhiều cấu hình pipeline.

### 2.2 Out-of-scope

- Mobile app native.
- Hỗ trợ đa ngôn ngữ ngoài tiếng Việt.
- Enterprise scale / HA / multi-region.
- Hỗ trợ mọi trường phái luận đoán ngoài phạm vi nguồn dữ liệu đã ingest.
- Tối ưu latency ở mức very-low-latency production grade.
- LLM-based document grading đầy đủ trong mọi request ở giai đoạn MVP.

***

## 3. Engines

### 3.1 Tử Vi Engine – `doanguyen/lasotuvi` (Python)

```text
github.com/doanguyen/lasotuvi | MIT License | Python
```

Tích hợp trực tiếp vào FastAPI backend. Phụ thuộc `pyvnlunar` cho đổi lịch âm.

> ⚠️ Bắt buộc unit test bằng cách so sánh output với ít nhất 2 phần mềm tử vi đáng tin cậy trước khi go-live, ví dụ yeutuvi.com và tuvilyso.net.

### 3.2 Bát Tự Engine – `alvamind/bazi-calculator-by-alvamind` (TypeScript)

```text
github.com/alvamind/bazi-calculator-by-alvamind | MIT | npm package
```

Bát Tự được tính trong **Next.js API Route** `/api/battu/calculate` để giữ logic tính toán ở server-side và không phụ thuộc FastAPI.

#### Lý do giữ cách này trong v6

- Khớp với kiến trúc frontend-centric cho chart generation.
- Tránh subprocess giữa Python và Node.
- Tối ưu triển khai trên Vercel.
- Giữ FastAPI tập trung cho RAG orchestration, ingestion, retrieval, và generation.

```typescript
import { BaziCalculator } from 'bazi-calculator-by-alvamind';

export default function handler(req, res) {
  const { year, month, day, hour, gender } = req.body;
  const calc = new BaziCalculator(year, month, day, hour, gender);
  res.json(calc.getCompleteAnalysis());
}
```

***

## 4. Technical stack

### 4.1 Frontend

```text
Framework: Next.js 14 + TypeScript
Styling: Tailwind CSS + shadcn/ui
Visualizer: D3.js (SVG, 12 cung) hoặc plain SVG nếu cần giảm complexity implementation
State: Zustand
Auth: Supabase Auth
Deploy: Vercel Hobby
```

### 4.2 Backend

```text
Framework: FastAPI (Python 3.11)
RAG orchestration: LangGraph
LLM SDK: google-generativeai
Graph driver: neo4j Python driver
Observability: Langfuse
Deploy: Render Free
```

### 4.3 Databases / storage

```text
Graph + Vector + Fulltext: Neo4j AuraDB Free
Relational app data: Supabase PostgreSQL
Trace / auth / sessions: Supabase + Langfuse
```

### 4.4 Đánh giá tính phù hợp của stack

Stack này phù hợp cho MVP vì:

- Đủ rẻ để chạy free-tier.
- Không phân mảnh quá nhiều services.
- Next.js + FastAPI là cặp stack dễ chia việc cho team 4 người.
- Neo4j có thể chứa cả graph retrieval, vector index, và fulltext search trong cùng một nơi.
- LangGraph phù hợp cho flow có nhiều node retrieval và state theo `chart_id`.

Lưu ý thực dụng:

- D3.js là lựa chọn tốt nếu visualizer cần tương tác cao; nếu visualizer chủ yếu là hiển thị 12 cung với tương tác đơn giản thì plain SVG/React cũng có thể đủ cho MVP.
- Render free tier có cold start, vì vậy frontend cần loading state rõ ràng.

***

## 5. Kiến trúc hệ thống

```text
┌─────────────────────────────────────────────────────┐
│                Vercel – Next.js 14                  │
│                                                     │
│  /app/chart/[id]                                    │
│     ├── TuViBoard / BatuBoard                       │
│     └── ChatInterface                               │
│                                                     │
│  /api/battu/calculate  ←── alvamind (npm)           │
│  /api/chat             ──► FastAPI (proxy)          │
└────────────────────┬────────────────────────────────┘
                     │ REST
┌────────────────────▼────────────────────────────────┐
│                  Render – FastAPI                   │
│                                                     │
│  /chart/tuvi    ←── doanguyen/lasotuvi              │
│  /chat          ←── LangGraph Hybrid GraphRAG       │
│     ├── Query rewrite (Gemini Flash-Lite)           │
│     ├── Entity extraction                           │
│     ├── Graph retrieval (Neo4j Cypher)              │
│     ├── Hybrid retrieval                            │
│     │    ├── Dense vector retrieval                 │
│     │    └── Sparse BM25/fulltext retrieval         │
│     ├── RRF fusion                                  │
│     ├── Cross-encoder rerank                        │
│     ├── Context assembly                            │
│     └── Generation (Gemini Flash)                   │
└───────────────┬───────────────────────┬─────────────┘
                │                       │
        ┌───────▼────────┐      ┌───────▼─────────┐
        │ Neo4j AuraDB   │      │ Supabase Free   │
        │ - Knowledge KG │      │ - profiles      │
        │ - Vector index │      │ - la_so         │
        │ - Fulltext idx │      │ - chat_sessions │
        │ - Domain tags  │      │ - source_chunks │
        └────────────────┘      └─────────────────┘
```

### 5.1 Architectural principles

- Một chart là trung tâm của toàn bộ trải nghiệm.
- Chat phải luôn gắn với `chart_id` hiện tại.
- Retrieval phải vừa hiểu quan hệ khái niệm (graph) vừa bắt đúng thuật ngữ chuyên ngành (sparse/BM25) vừa giữ semantic recall (dense embeddings).
- MVP ưu tiên độ đúng và khả năng kiểm tra nguồn hơn là latency tối thiểu.
- Tử Vi và Bát Tự dùng chung hạ tầng graph/vector, nhưng có **phân tách logic theo domain metadata**.
- **Mọi thành phần có thể thay thế được trong pipeline đều phải có toggle tương ứng** để phục vụ ablation study.

***

## 6. Luồng dữ liệu chính

```text
User nhập ngày/giờ sinh
    │
    ├──► /api/battu/calculate (Next.js) → alvamind → Bát Tự JSON
    │
    └──► FastAPI /chart/tuvi → lasotuvi → Tử Vi JSON
              │
              └──► Lưu Supabase (la_so)
                        │
                        ▼
                User mở chart/[id]
                        │
                        ▼
                ChatInterface gửi câu hỏi
                        │
                        ▼
                Next.js /api/chat → FastAPI /chat
                        │
                        ▼
                LangGraph Hybrid GraphRAG
                [ExperimentConfig được load tại đây]
                [query rewrite nhẹ – nếu bật]
                        │
                ┌───────┴────────────────────────────┐
                │                                    │
      [graph retrieval path]              [hybrid retrieval path]
      Neo4j Cypher                        dense + BM25/fulltext
      (nếu bật)                           (mỗi path có toggle riêng)
                │                                    │
                └──────────────┬─────────────────────┘
                               │
                    [fusion method – RRF hoặc khác]
                               │
                    [reranker – nếu bật]
                               │
                    [document grading – nếu bật]
                               │
                    [context assembly strategy]
                               │
                    [generation model được chọn]
                               │
                  Response + citations + traces
                  + experiment_id được log vào Langfuse
```

***

## 7. RAG orchestration

### 7.1 LangGraph

Giữ LangGraph làm orchestration layer vì hệ thống cần:

- Multi-step retrieval.
- Branching/parallel retrieval.
- State theo `chart_id`.
- Dễ thêm cache, reranking, observability, fallback logic.
- **Dễ swap node theo `ExperimentConfig` mà không cần sửa graph topology.**

### 7.2 State đề xuất (cập nhật v6)

```python
from typing import TypedDict, Dict, Any, List, Optional

class RAGState(TypedDict, total=False):
    # Core
    query: str
    rewritten_query: str
    query_complexity: str
    chart_id: str
    chart_type: str
    chart_data: Dict[str, Any]
    user_id: str
    domain_filter: str

    # Retrieval
    entities: List[str]
    graph_candidates: List[Dict[str, Any]]
    dense_candidates: List[Dict[str, Any]]
    sparse_candidates: List[Dict[str, Any]]
    fused_candidates: List[Dict[str, Any]]
    reranked_candidates: List[Dict[str, Any]]
    graded_candidates: List[Dict[str, Any]]   # dùng khi document grading bật
    final_context: str
    retrieval_mode: str

    # Output
    answer: str
    sources: List[Dict[str, Any]]
    cache_key: str

    # Ablation (v6 mới)
    experiment_config: "ExperimentConfig"     # config của lần chạy này
    experiment_id: str                        # UUID của experiment run
    retrieval_trace: Dict[str, Any]           # chi tiết từng path để phân tích
```

### 7.3 Node graph đề xuất

1. Load chart context.
2. Load `ExperimentConfig` và gắn vào state.
3. Normalize query.
4. Query complexity classify.
5. Query rewrite bằng Flash-Lite *(nếu `config.query_rewrite_enabled`)*
6. Extract entities *(nếu `config.graph_retrieval_enabled`)*
7. Chạy song song theo config:
   - Graph retrieval path *(nếu `config.graph_retrieval_enabled`)*
   - Dense retrieval path *(nếu `config.dense_retrieval_enabled`)*
   - Sparse/BM25 retrieval path *(nếu `config.sparse_retrieval_enabled`)*
8. Fusion bằng method được chỉ định trong `config.fusion_method`.
9. Rerank *(nếu `config.reranker_enabled`)* với model từ `config.reranker_model`.
10. Document grading *(nếu `config.document_grading_enabled`)*
11. Context assembly theo `config.context_assembly_strategy`.
12. Final generation bằng model từ `config.generation_model`.
13. Citation map + trace log + ghi `experiment_id` vào Langfuse.

### 7.4 Những gì **không bắt buộc** trong MVP production

- LLM-based document grading sau retrieval *(nhưng bắt buộc có toggle để chạy ablation)*.
- Query decomposition phức tạp theo nhiều sub-question.
- Agentic planner nhiều bước trước retrieval.

***

## 8. Retrieval design (official v6)

### 8.1 Nguyên tắc chung

Retrieval stage trong v6 **không còn là graph trước rồi vector sau** như cách hiểu tuần tự đơn giản. Thay vào đó, retrieval chính thức của hệ thống gồm **2 nhánh lớn chạy song song**:

1. **Graph retrieval path** – dùng entity extraction + Cypher để đi theo quan hệ trong knowledge graph.
2. **Hybrid retrieval path** – gồm dense retrieval + sparse/BM25 retrieval chạy song song, sau đó fuse lại.

Cuối cùng, toàn bộ ứng viên từ cả 2 nhánh được trộn, rerank, rồi đưa vào generation.

**Bổ sung v6:** Mỗi path và mỗi method đều có toggle riêng trong `ExperimentConfig`. Cấu hình production mặc định bật tất cả, còn ablation có thể tắt từng phần để đo đóng góp riêng lẻ.

### 8.2 Graph retrieval path

Dùng khi câu hỏi liên quan đến:

- Các sao / cung / tổ hợp sao cụ thể.
- Các mối quan hệ dạng "sao nào ở cung nào", "tổ hợp này ảnh hưởng gì", "đại hạn – tài lộc – cung mệnh liên hệ ra sao".
- Multi-hop reasoning dựa trên liên kết giữa các khái niệm.

Graph retrieval path gồm:

- Extract entities từ câu hỏi + chart context.
- Chuẩn hóa entity names theo taxonomy nội bộ.
- Query Neo4j bằng Cypher với domain filter và chart-aware constraints.
- Trả về node/edge/chunk references liên quan.

**Ablation dimension:** `graph_retrieval_enabled` (true/false) + `graph_hop_depth` (1 hoặc 2 hop).

### 8.3 Hybrid retrieval path

Hybrid retrieval path gồm 2 retrieval method chạy song song:

- **Dense retrieval**: dùng `gemini-embedding-001` để tìm semantic similarity.
- **Sparse retrieval**: dùng Neo4j fulltext index (Lucene/BM25) để bắt đúng keyword/thuật ngữ chuyên ngành.

Dense retrieval mạnh khi người dùng hỏi diễn đạt tự nhiên.
Sparse retrieval mạnh khi câu hỏi chứa thuật ngữ tử vi/bát tự cụ thể, tên sao, tên cung, hoặc cụm khái niệm chuyên ngành.

**Ablation dimension:** `dense_retrieval_enabled` và `sparse_retrieval_enabled` là hai toggle độc lập.

### 8.4 Fusion và reranking

Sau khi có kết quả từ 3 nguồn:

- graph path
- dense path
- sparse path

Hệ thống thực hiện:

1. **Fusion** theo `config.fusion_method` — mặc định là RRF, có thể thay bằng score normalization + weighted sum.
2. **Cross-encoder reranker** để xếp hạng lại top candidates — nếu `config.reranker_enabled`.
3. Cắt top-k theo token budget để đưa vào prompt generation.

**Ablation dimension:** `fusion_method` (`rrf` / `weighted_sum` / `graph_first`) + `reranker_enabled` + `reranker_model`.

### 8.5 Vì sao thiết kế này là phù hợp nhất cho MVP

- Graph path giúp reasoning theo khái niệm tốt hơn vector-only.
- BM25 giúp bắt thuật ngữ chuyên ngành tiếng Việt tốt hơn dense-only.
- Dense retrieval giúp không bỏ sót các diễn đạt tự nhiên.
- Reranker mang lại lợi ích lớn hơn document grading trong khi chi phí latency thấp hơn.
- Kiến trúc này vẫn nằm trong khả năng vận hành của free-tier do Neo4j hỗ trợ cả vector index lẫn fulltext index.

### 8.6 Latency policy cho MVP

- Query rewrite: **bật mặc định**, dùng Flash-Lite, mục tiêu thêm latency nhỏ nhưng tăng recall rõ rệt.
- Reranker: **bật mặc định**.
- Document grading bằng LLM: **tắt mặc định ở MVP production**, **bật được để chạy ablation**.
- Cache retrieval/generation theo `chart_id + normalized_query` cho các câu hỏi lặp lại.

***

## 9. Query rewriting policy

### 9.1 Mục tiêu

Query rewriting nhằm giải quyết các câu hỏi:

- mơ hồ,
- quá ngắn,
- dùng ngôn ngữ đời thường,
- hoặc chưa nêu rõ đối tượng trong chart.

Ví dụ:

- "nghề gì hợp tôi"
- "tài lộc dạo này sao"
- "mệnh này có gì cần lưu ý"

### 9.2 Cách áp dụng trong MVP

- Dùng **Gemini Flash-Lite**.
- Rewriting phải ngắn, không thêm ý suy diễn ngoài chart context.
- Chỉ rewrite để làm rõ entity / house / term / intent cho retrieval.
- Không dùng query rewriting để tạo câu trả lời cuối.

**Ablation dimension:** `query_rewrite_enabled` (true/false) + `query_rewrite_model` (`flash_lite` / `flash`).

### 9.3 Guardrails

- Không chèn thêm claim không tồn tại trong chart.
- Không mở rộng vượt domain hiện tại (`TUVI` hoặc `BATU`).
- Không sinh nhiều query decomposition trừ khi hậu MVP cần thiết.

***

## 10. Reranking and document grading policy

### 10.1 MVP decision

Ở v6, hệ thống **bắt buộc có reranker trong production**, nhưng **chưa bắt buộc có LLM document grading trong production**. Tuy nhiên, **cả hai phải có toggle để chạy ablation study**.

### 10.2 Lý do

- Reranker tăng precision tốt trong khi latency thấp hơn gọi thêm LLM grading cho mỗi batch retrieval.
- Với quy mô corpus MVP, reranker là điểm cân bằng tốt nhất giữa chất lượng và tốc độ.
- Ablation study sẽ cho biết liệu document grading có đáng thêm vào production hay không, dựa trên metric thực tế trên golden dataset của dự án này.

### 10.3 Cơ chế triển khai

- Lấy top-k ứng viên sau fusion.
- Chạy cross-encoder reranker trên top-k đó.
- Loại bỏ chunk có score thấp dưới ngưỡng.
- Chỉ giữ số chunk cần thiết theo token budget.

**Ablation dimension:** `reranker_enabled` + `reranker_model` + `reranker_threshold` + `document_grading_enabled` + `document_grading_model`.

***

## 11. Embedding, sparse retrieval, and indexing

### 11.1 Embedding model

Dùng `gemini-embedding-001` cho cả ingestion và runtime retrieval làm mặc định.

**Ablation dimension:** `embedding_model` — có thể thử `gemini-embedding-001` vs các model nhỏ hơn để đo quality/cost trade-off.

### 11.2 Sparse retrieval

Dùng **Neo4j fulltext index** để thực hiện keyword/sparse retrieval thay vì thêm Elasticsearch hay OpenSearch ở giai đoạn MVP.

Ví dụ fulltext index:

```cypher
CREATE FULLTEXT INDEX chunkFulltext IF NOT EXISTS
FOR (c:Chunk) ON EACH [c.text, c.title, c.keywords]
```

### 11.3 Lý do giữ mọi thứ trong Neo4j

- Giảm complexity vận hành.
- Không phát sinh thêm service mới.
- Vẫn đủ để chạy graph + dense + sparse retrieval trong một hệ thống thống nhất.

***

## 12. Domain modeling: Tử Vi vs Bát Tự

### 12.1 Quyết định kiến trúc

**Không tách Tử Vi và Bát Tự thành hai database riêng** ở giai đoạn MVP.

Thay vào đó, dùng **một Neo4j graph duy nhất** với chiến lược **soft separation theo domain metadata**.

### 12.2 Domain tagging

Mỗi node/chunk/relation cần có trường `domain`:

- `TUVI`
- `BATU`
- `SHARED`

Ví dụ:

```cypher
CREATE (n:Sao {name: 'Tử Vi', domain: 'TUVI'})
CREATE (n:ThienCan {name: 'Giáp', domain: 'SHARED'})
CREATE (n:NguHanh {name: 'Hỏa', domain: 'SHARED'})
```

### 12.3 Lý do không tách thành hai graph

- Free tier AuraDB chỉ có 1 instance.
- Nhiều khái niệm cốt lõi là shared: Thiên Can, Địa Chi, Ngũ Hành.
- Dễ maintain hơn.
- Cho phép tương lai hỗ trợ cross-domain reasoning nếu cần.

### 12.4 Quy tắc retrieval theo domain

- Với chart Tử Vi: mặc định filter `domain IN ['TUVI', 'SHARED']`.
- Với chart Bát Tự: mặc định filter `domain IN ['BATU', 'SHARED']`.
- Không lấy chéo domain đặc thù trừ khi có rule rõ ràng.

***

## 13. Data model and auth

### 13.1 Business rule chính thức

- Một user có thể có nhiều chart.
- Một chart chỉ có đúng **một chat session**.
- Một chat session chỉ thuộc về đúng **một chart**.
- Toàn bộ hội thoại phải xoay quanh chart hiện tại.

### 13.2 Supabase schema đề xuất

```sql
CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  display_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE la_so (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  label TEXT NOT NULL,
  birth_date DATE NOT NULL,
  birth_time TEXT NOT NULL,
  gender TEXT NOT NULL,
  chart_system TEXT NOT NULL CHECK (chart_system IN ('TUVI', 'BATU', 'TUVI_BATU')),
  chart_data JSONB NOT NULL,
  chart_version TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE chat_sessions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  la_so_id UUID NOT NULL UNIQUE REFERENCES la_so(id) ON DELETE CASCADE,
  title TEXT,
  summary TEXT,
  messages JSONB NOT NULL DEFAULT '[]',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE source_chunks (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  source_name TEXT NOT NULL,
  source_type TEXT NOT NULL,
  source_url TEXT,
  domain TEXT NOT NULL,
  source_page INT,
  title TEXT,
  chunk_text TEXT NOT NULL,
  chunk_hash TEXT UNIQUE NOT NULL,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Bảng mới trong v6: lưu experiment run results
CREATE TABLE experiment_runs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  experiment_id TEXT NOT NULL,         -- tên experiment, ví dụ "EXP-001"
  config JSONB NOT NULL,               -- ExperimentConfig được serialize
  dataset_version TEXT NOT NULL,       -- phiên bản golden dataset dùng
  metrics JSONB NOT NULL DEFAULT '{}', -- kết quả metric tổng hợp
  run_at TIMESTAMPTZ DEFAULT NOW(),
  notes TEXT
);

CREATE INDEX idx_la_so_user_id ON la_so(user_id);
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_source_chunks_hash ON source_chunks(chunk_hash);
CREATE INDEX idx_source_chunks_domain ON source_chunks(domain);
CREATE INDEX idx_experiment_runs_id ON experiment_runs(experiment_id);
```

### 13.3 RLS policies

```sql
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE la_so ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Profiles are self-owned"
ON profiles FOR ALL
USING (auth.uid() = id) WITH CHECK (auth.uid() = id);

CREATE POLICY "Charts are self-owned"
ON la_so FOR ALL
USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Chat sessions are self-owned"
ON chat_sessions FOR ALL
USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
```

### 13.4 Context windowing policy

Vì mỗi chart có một chat dài hạn, cần giới hạn prompt history:

- Dùng **20 messages gần nhất** làm live context window.
- Các đoạn hội thoại cũ hơn được tóm tắt vào `chat_sessions.summary`.
- Summary được cập nhật định kỳ khi số message vượt ngưỡng.

### 13.5 Timestamp maintenance

Nên bổ sung trigger auto-update `updated_at` cho `profiles`, `la_so`, và `chat_sessions`.

***

## 14. Ingestion pipeline

### 14.1 Mục tiêu

Pipeline ingestion phải tạo được corpus sạch, có provenance, có graph entities, và có vector/fulltext index để phục vụ Hybrid GraphRAG.

**Bổ sung v6:** Pipeline ingestion phải **hỗ trợ nhiều chunking strategy** để có thể ingest cùng một bộ sách dưới nhiều cấu hình khác nhau, phục vụ ablation study chunking.

### 14.2 Nguồn dữ liệu ưu tiên

1. PDF text-based extract tốt.
2. PDF scan nhưng OCR ra text chấp nhận được.
3. Forum / website text có kiểm duyệt thủ công.

### 14.3 Offline pipeline chính thức

```text
Source documents
    ↓
Detect text-based PDF
    ↓
If scanned: OCR only when necessary
    ↓
Normalize text
    - remove headers/footers/page artifacts
    - normalize Unicode tiếng Việt (NFC)
    - clean duplicated line breaks
    ↓
Structure parse
    - heading / section / paragraph / sentence
    ↓
Chunking  ← ABLATION POINT: chunking_strategy
    - strategy A: structure-first recursive + parent-child (default)
    - strategy B: fixed-size sliding window
    - strategy C: sentence-based với dynamic merge
    - strategy D: semantic chunking bằng embedding similarity
    ↓
Metadata tagging
    - source, page, chapter, topic, language, domain
    - chunk_strategy_id (để trace lại khi so sánh)
    ↓
Entity extraction  ← ABLATION POINT: entity_extraction_model
    ↓
Canonicalization / dedup preparation
    ↓
Build graph objects
    ↓
Embed chunks  ← ABLATION POINT: embedding_model
    ↓
Create/update fulltext index entries
    ↓
Store in Neo4j + provenance in Supabase
```

### 14.4 Critical design choices

- **Không OCR toàn bộ trước**; chỉ OCR khi cần.
- **Normalize Unicode tiếng Việt rõ ràng**; dùng NFC làm chuẩn.
- **Entity extraction trước embedding** để graph-first modeling sạch hơn.
- **Dedup logic** là bắt buộc ở bước graph write để tránh nổ số lượng node giống nhau.
- **Incremental ingestion** phải được hỗ trợ dựa trên `chunk_hash`.
- **Bổ sung v6:** `chunk_hash` phải bao gồm cả `chunking_strategy_id` để các strategy khác nhau không dedup lẫn nhau.

### 14.5 Chunking strategies (Ablation — v6)

Đây là một trong những dimension quan trọng nhất của ablation study trong dự án này. Tài liệu tử vi/bát tự có cấu trúc độc đáo — chia theo sao, cung, tổ hợp, luận giải — nên không có cơ sở chắc chắn trước rằng strategy nào tốt nhất. Cần đo.

#### Strategy A — Structure-first recursive + parent-child (default v6)

- Tách theo thứ tự ưu tiên: heading → section → paragraph → sentence.
- **Parent chunk**: 400–512 tokens.
- **Child chunk**: 120–180 tokens, overlap nhỏ.
- Overlap parent: 60–100 tokens.
- Không tách giữa một đơn vị khái niệm hoàn chỉnh.
- Retrieve bằng child, trả context bằng parent.

#### Strategy B — Fixed-size sliding window

- Chunk kích thước cố định: thử 3 sub-variant: 256 / 512 / 1024 tokens.
- Overlap cố định: 10–15% kích thước chunk.
- Không có cấu trúc parent-child.
- Đơn giản nhất để implement, dùng làm baseline.

#### Strategy C — Sentence-based với dynamic merge

- Tách theo câu bằng regex hoặc rule đơn giản.
- Gộp các câu liên tiếp cho đến khi đạt target token range (200–400 tokens).
- Không gộp qua ranh giới heading/section.
- Không có parent-child.

#### Strategy D — Semantic chunking bằng embedding similarity

- Tách theo câu trước.
- Dùng embedding similarity để phát hiện điểm ngắt ngữ nghĩa: khi cosine similarity giữa câu liên tiếp giảm mạnh thì ngắt chunk mới.
- Target chunk: 300–500 tokens.
- Tốn Gemini Embedding quota hơn khi ingest; cần chạy trên Kaggle.

#### So sánh strategies

| Strategy | Tên | Tách theo | Parent-child | Ablation tag |
|---|---|---|---|---|
| A | Structure-first recursive | Cấu trúc tài liệu | Có | `chunk_structure_parent_child` |
| B1 | Fixed-size 256 | Token count | Không | `chunk_fixed_256` |
| B2 | Fixed-size 512 | Token count | Không | `chunk_fixed_512` |
| B3 | Fixed-size 1024 | Token count | Không | `chunk_fixed_1024` |
| C | Sentence-merge | Câu + dynamic merge | Không | `chunk_sentence_merge` |
| D | Semantic | Embedding similarity | Không | `chunk_semantic` |

### 14.6 Workflow chi tiết

1. Upload hoặc khai báo danh sách nguồn.
2. Kiểm tra file text-based.
3. Extract text bằng `pdfplumber` hoặc `pymupdf`.
4. Nếu cần thì OCR.
5. Normalize Unicode tiếng Việt và clean artifacts.
6. Parse cấu trúc tài liệu.
7. Tạo chunks theo `chunking_strategy` được chỉ định.
8. Gắn metadata và domain, bao gồm `chunk_strategy_id`.
9. Trích entity + relation bằng Flash-Lite.
10. Canonicalize / dedup trước khi ghi graph.
11. Ghi node/edge/chunk vào Neo4j (namespace riêng theo strategy nếu cần).
12. Ghi provenance vào Supabase với `chunk_strategy_id`.
13. Tạo embeddings và fulltext index.
14. Chạy sample QA review sau ingestion.

### 14.7 Canonicalization / dedup rules

- Dùng tên canonical cho sao, cung, thiên can, địa chi, ngũ hành.
- `MERGE` node theo `canonical_name + domain + entity_type`.
- Không tạo node mới nếu chỉ khác cách viết hoa, dấu cách, hoặc alias phổ biến.
- Lưu alias ở metadata nếu cần.
- **Bổ sung v6:** Node `Chunk` dùng `MERGE` theo `chunk_hash` (bao gồm strategy_id), nên nhiều strategy sẽ tạo ra các node chunk riêng biệt trong graph — không merge lẫn nhau.

***

## 15. Knowledge graph schema

### 15.1 Node types (MVP)

- `Chart`
- `Chunk`
- `Source`
- `Sao`
- `Cung`
- `ToHop`
- `KhaiNiem`
- `LuanGiai`
- `ThienCan`
- `DiaChi`
- `NguHanh`
- `VanHan` / `DaiHan` (nếu cần ở MVP)

### 15.2 Relation types (MVP)

- `THUOC_CUNG`
- `LIEN_KE`
- `GIAI_THICH`
- `DOI_CHIEU`
- `LUU_Y`
- `HAS_SOURCE`
- `HAS_CHUNK`
- `MENTIONS`
- `APPLIES_TO`
- `RELATED_TO`

### 15.3 Graph scope control

Chỉ giữ các relation thực sự có giá trị retrieval. Không nên bơm mọi quan hệ suy diễn vào graph ở MVP vì sẽ làm schema khó maintain và khó debug.

***

## 16. Neo4j free-tier capacity estimate

### 16.1 Assumption sơ bộ

Từ danh sách nguồn hiện tại:

- Khoảng 12 đầu sách chính cho MVP early corpus.
- Tổng chunk ước lượng khoảng **3,000–4,000 chunks** nếu chunk 400–512 tokens (strategy A).
- Với entity extraction mức vừa phải, tổng graph node có thể nằm khoảng **15,000–20,000 nodes**.
- Tổng relations có thể nằm khoảng **45,000–60,000 relations**.

**Bổ sung v6 — ablation overhead:** Nếu chạy ablation với 6 chunking strategy trên cùng 4 sách ban đầu, số chunk node có thể tăng lên ~6× so với một strategy. Tuy nhiên, các knowledge node (`Sao`, `Cung`, v.v.) vẫn được merge, nên tổng node sẽ không tăng 6×. Ước tính tổng node vẫn nằm dưới **80,000–100,000** — an toàn trong free tier.

### 16.2 Kết luận

Giới hạn Neo4j AuraDB Free hiện tại:

- 200,000 nodes
- 400,000 relationships

=> Với phạm vi sách hiện tại và ablation overhead, hệ thống **vẫn nằm an toàn trong free tier** cho MVP.

### 16.3 Khi nào cần lo vượt giới hạn

- Khi ingest hàng chục đến hàng trăm đầu sách mới.
- Khi chạy ablation trên toàn bộ 12 sách với tất cả strategy song song.
- Khi entity extraction quá granular và tạo quá nhiều node trùng lặp.

### 16.4 Quy tắc kiểm soát tăng trưởng

- Chỉ ingest 3–4 sách trọng tâm trong sprint MVP đầu tiên.
- Theo dõi số node/relation sau mỗi batch ingestion.
- Bắt buộc dedup trước graph write.
- Chỉ mở rộng corpus sau khi evaluation chứng minh retrieval đã ổn.
- **Bổ sung v6:** Khi chạy ablation chunking, chỉ ingest 1–2 sách đại diện để tránh vượt capacity.

***

## 17. Model routing

### 17.1 Mục tiêu

Model routing phải giữ chất lượng đủ tốt trong khi tôn trọng free-tier quota và latency budget.

### 17.2 Routing policy

```python
def classify_query_complexity(query: str) -> str:
    q = query.lower()
    if len(q) > 160:
        return "high"
    multi_hop_markers = ["và", "so với", "ảnh hưởng", "đồng thời", "liên quan", "trong khi"]
    if any(m in q for m in multi_hop_markers):
        return "high"
    return "low"

def route_model(task_type: str, query_complexity: str, config: "ExperimentConfig") -> str:
    # Trong ablation, config có thể override model mặc định
    if config.generation_model_override:
        if task_type == "generation":
            return config.generation_model_override
    if config.entity_extraction_model_override:
        if task_type == "entity_extraction":
            return config.entity_extraction_model_override

    # Default routing
    if task_type == "query_rewrite":
        return "gemini-2.0-flash-lite"
    if task_type == "entity_extraction":
        return "gemini-2.0-flash-lite"
    if task_type == "ingestion_annotation":
        return "gemini-2.0-flash-lite"
    if task_type == "retrieval_summary":
        return "gemini-2.0-flash-lite"
    if task_type == "simple_factual" and query_complexity == "low":
        return "gemini-2.0-flash-lite"
    return "gemini-2.5-flash"
```

### 17.3 Cache policy

- Cache key: `hash(chart_id + normalized_query + top_context_ids)` hoặc đơn giản hơn `hash(chart_id + normalized_query)` cho MVP.
- Cache retrieval/result cho câu hỏi lặp lại.
- Chỉ dùng cache nếu chart context không đổi.
- **Bổ sung v6:** Trong ablation run, **không dùng cache** vì mỗi config cần được đo độc lập. `AblationRunner` tự động disable cache khi chạy.

***

## 18. Prompting principles

### 18.1 Generation prompt requirements

Prompt generation phải:

- Bám chart hiện tại.
- Ưu tiên context được retrieve.
- Không suy diễn khi context không đủ.
- Trả lời bằng tiếng Việt.
- Gắn citations theo chunk/source map.
- Nếu thiếu bằng chứng, phải nói rõ là chưa đủ dữ liệu.

**Ablation dimension:** `prompt_template` — có thể thử nhiều phiên bản prompt template để đo ảnh hưởng lên Faithfulness và Answer Relevancy độc lập với retrieval config.

### 18.2 Entity extraction prompt requirements

Prompt extraction phải nêu rõ:

- taxonomy entity,
- domain (`TUVI` / `BATU` / `SHARED`),
- alias phổ biến,
- rule canonicalization,
- yêu cầu không suy diễn vượt văn bản gốc.

***

## 19. Evaluation plan (cập nhật v6)

### 19.1 Mục tiêu đánh giá

Đánh giá xem hệ thống có:

- bám chart context,
- retrieve đúng,
- không hallucinate,
- citation đúng,
- và giữ latency chấp nhận được cho MVP.

**Bổ sung v6:** Evaluation còn có mục tiêu so sánh có hệ thống giữa các cấu hình pipeline thông qua ablation study để xác định cấu hình tối ưu cho domain.

### 19.2 Golden dataset

MVP có thể bắt đầu với **50–100 Q&A pairs**, chia:

- 40% factual
- 40% interpretive
- 20% multi-hop

Mỗi mẫu nên có:

- `question`
- `question_type`
- `chart_id` hoặc chart context
- `expected_answer_summary`
- `required_sources`
- `gold_context`
- `difficulty`

Dataset được version hóa (ví dụ `golden_v1.jsonl`) để đảm bảo kết quả ablation có thể so sánh với nhau qua các lần chạy khác nhau.

### 19.3 Metrics

| Metric | Ý nghĩa | Target MVP |
|--------|---------|------------|
| Faithfulness | Câu trả lời có bám context hay không | >= 0.80 |
| Answer Relevancy | Câu trả lời có trực tiếp trả lời câu hỏi hay không | >= 0.75 |
| Context Recall | Retrieval có lấy đủ thông tin cần thiết hay không | >= 0.70 |
| Graph Hit Rate (custom) | Retrieval graph có chạm đúng node/edge quan trọng hay không | >= 0.65 |
| Citation Coverage (custom) | Tỷ lệ câu trả lời có nguồn trích dẫn hợp lệ | >= 0.90 |
| p95 End-to-End Latency | Thời gian phản hồi tổng thể | <= 8s |
| Retrieval p95 | Thời gian retrieval + rerank | <= 3s |

### 19.4 Evaluation workflow

1. Chuẩn bị 50–100 câu hỏi đại diện.
2. Gắn mỗi câu với chart context cụ thể.
3. Chạy system và lưu retrieval traces.
4. Tính metrics.
5. Phân loại lỗi thành:
   - retrieval miss
   - rerank miss
   - hallucination
   - source mismatch
   - weak multi-hop reasoning
6. **Bổ sung v6:** Chạy `AblationRunner` để sweep qua các experiment trong experiment matrix.
7. **Bổ sung v6:** So sánh metric giữa các experiment và ánh xạ sang quyết định kiến trúc.
8. Tinh chỉnh chunking / prompt / retrieval theo loại lỗi và kết quả ablation.

### 19.5 Adversarial tests

Bổ sung một nhóm câu hỏi ngoài domain hoặc không có trong nguồn để test khả năng từ chối trả lời khi context không đủ.

***

## 20. Latency, caching, and performance policy

### 20.1 Latency trade-off chính thức

Hệ thống chấp nhận một mức tăng latency hợp lý để đổi lấy retrieval quality tốt hơn.

Ưu tiên chất lượng theo thứ tự:

1. Query rewrite nhẹ
2. Parallel retrieval
3. Rerank
4. Generation

Document grading bằng LLM chưa bật ở MVP vì chưa xứng đáng với latency cost — nhưng ablation sẽ kiểm chứng điều này.

### 20.2 Caching

Áp dụng cache cho:

- normalized query rewrite,
- retrieval result theo `chart_id`,
- final answer nếu cùng query và cùng chart context.

**Bổ sung v6:** Cache bị vô hiệu hóa tự động khi request mang `experiment_id`.

### 20.3 Frontend UX cho latency

- Hiển thị loading state rõ ràng.
- Nếu gặp cold start Render, frontend phải hiển thị thông báo kiểu "Hệ thống đang khởi động, vui lòng đợi vài giây".
- Có retry nhẹ cho request đầu tiên nếu timeout mềm.

***

## 21. Risk table

| Rủi ro | Tác động | Mitigation |
|-------|----------|------------|
| Gemini Flash quota bị vượt | Request fail hoặc giảm chất lượng | Dùng Flash-Lite cho rewrite/extraction/query đơn giản, cache, giới hạn request |
| Render free tier cold start | Latency tăng mạnh ở request đầu tiên | Loading state rõ ràng, health ping nếu cần, tối ưu startup |
| Neo4j schema quá phức tạp | Khó maintain/debug | Giữ graph schema tối giản, only high-value entities/relations |
| OCR làm nhiễu dữ liệu | Retrieval quality giảm | Ưu tiên PDF text-based, OCR only when needed, sample review |
| Supabase RLS sai | Lộ dữ liệu người dùng | Test policy kỹ trước deploy |
| Query multi-hop thiếu ngữ cảnh | Trả lời nông | Chạy parallel graph + hybrid retrieval, rerank, chart-aware context |
| Citation mapping không ổn định | Người dùng khó kiểm tra nguồn | Lưu provenance per chunk + stable chunk hash |
| Dữ liệu graph bị duplicate | Tăng node/edge vô ích, retrieval nhiễu | Canonicalization + `MERGE` + chunk hash + alias control |
| Chat history quá dài | Prompt phình to, tốn quota | Rolling window + summary field |
| Team timeline bị trượt | Chậm demo / release | Giảm corpus MVP xuống 3–4 sách trọng tâm, chia sprint song song |
| **Ablation tốn quá nhiều quota** | **Vượt Gemini free-tier RPD** | **Chạy ablation vào buổi tối/ngày khác, batch nhỏ, dùng Flash-Lite cho các node không cần thiết phải Flash** |
| **Nhiều chunking strategy làm Neo4j gần đầy** | **Vượt free-tier node limit** | **Chỉ ingest 1–2 sách đại diện khi so sánh chunking, xóa chunk node của strategy cũ sau khi có kết quả** |

***

## 22. MVP success boundary

MVP được coi là đạt nếu thỏa toàn bộ điều kiện sau:

1. Người dùng có thể tạo chart từ ngày/giờ sinh, giới tính, và tên gọi.
2. Người dùng có thể xem chart trực quan trên web.
3. Mỗi chart có đúng một chat session và chat đó hoạt động ổn định.
4. Hệ thống trả lời trong phạm vi chart hiện tại, có diễn giải, có nguồn trích dẫn.
5. Retrieval hoạt động theo kiến trúc hybrid graph + dense + sparse.
6. Evaluation đạt gần hoặc đạt các ngưỡng metric đã đặt ra.
7. **Bổ sung v6:** Ít nhất 10 experiment từ ablation matrix đã được chạy và kết quả được ghi lại.
8. **Bổ sung v6:** Cấu hình production cuối cùng được chọn dựa trên bằng chứng từ ablation, không phải giả định.

***

## 23. User flow

```text
Đăng ký / đăng nhập
    ↓
Dashboard: danh sách chart đã lưu
    ↓
Tạo chart mới
    ↓
Xem chart/[id]
    ↓
Nếu chart chưa có chat_session → hệ thống tạo đúng 1 chat_session
    ↓
Người dùng hỏi đáp trong chat của chart đó
    ↓
Hệ thống trả lời bằng Hybrid GraphRAG + citations
```

### 23.1 UI modules

- `TuViBoard.tsx`
- `BatuBoard.tsx`
- `ChatInterface.tsx`
- `SourceCitationPanel.tsx` (nên có ở MVP nếu kịp)
- `ChartSummaryCard.tsx`

***

## 24. Free-tier update (working assumptions)

| Service | Limit thực tế | Ghi chú |
|---------|--------------|---------|
| Gemini Flash | 1,500 RPD, 10 RPM | Final generation |
| Gemini Flash-Lite | 1,500 RPD, 15 RPM | Rewrite, extraction, simple tasks |
| Gemini Embedding | 10M TPM free | Ingestion + runtime embeddings |
| Neo4j AuraDB | 200k nodes, 400k rel | 1 instance, đủ cho MVP + ablation chunking vừa phải |
| Supabase | 500MB DB, 50k MAU | Đủ cho MVP + experiment_runs table |
| Vercel | Hobby | Frontend |
| Render | 750h/month | FastAPI, có cold start |

***

## 25. Delivery roadmap (7–8 weeks)

### 25.1 Team split suggestion

- **Dev A**: FastAPI + LangGraph + Neo4j
- **Dev B**: Ingestion pipeline + evaluation dataset + ablation runner
- **Dev C**: Next.js UI + chart visualizer
- **Dev D**: Supabase auth/data + integration + QA/observability

### 25.2 Roadmap

| Week | Backend / Data | Frontend / Product |
|------|----------------|---------------------|
| W1 | Supabase schema (incl. experiment_runs) + RLS + FastAPI skeleton | Next.js auth skeleton + routing |
| W2 | Tử Vi engine verify + unit tests + ExperimentConfig schema | Bát Tự API route + chart page shell |
| W3 | Ingestion pipeline v1 + strategy A (default) + 1–2 sách đầu tiên | D3/SVG visualizer v1 + chat UI |
| W4 | Neo4j graph + vector + fulltext indexing + AblationRunner skeleton | Dashboard + chart detail integration |
| W5 | LangGraph với ExperimentConfig toggle + query rewrite + rerank | Citation UI + loading/error states |
| W6 | Ablation run v1 (retrieval paths + reranker) + chunking strategy comparison | End-to-end integration + polish |
| W7 | Ablation run v2 (generation model + prompt template) + chọn config production | QA, UX polish, demo prep |
| W8 | Buffer: mở rộng corpus, thêm experiment nếu kịp | Buffer / stretch goals |

### 25.3 Scope rule để giữ timeline

Nếu cần giữ đúng 7–8 tuần, bắt buộc:

- chỉ ingest 3–4 sách quan trọng ban đầu,
- chưa bật LLM document grading trong production,
- chưa tối ưu cross-domain reasoning,
- ưu tiên chất lượng retrieval cho các câu hỏi thường gặp nhất,
- **ablation được giới hạn trong danh sách experiment matrix đã định**, không tự do thêm mới vô hạn trong sprint.

***

## 26. Final stack summary

```text
FRONTEND (Vercel)
  Next.js 14 + TypeScript + Tailwind + shadcn/ui
  D3.js hoặc plain SVG cho chart visualizer
  Zustand
  Supabase JS
  alvamind (Bát Tự, Next.js API Route)

BACKEND (Render)
  FastAPI (Python 3.11)
  doanguyen/lasotuvi (Tử Vi engine)
  LangGraph (Hybrid GraphRAG orchestration + ExperimentConfig-aware)
  google-generativeai SDK
  neo4j Python driver
  reranker component
  AblationRunner (offline, chạy trên Kaggle)

DATABASES
  Neo4j AuraDB Free
    - Knowledge graph
    - Vector index
    - Fulltext/BM25 index
    - Domain metadata (TUVI / BATU / SHARED)
    - Chunk nodes có chunk_strategy_id

  Supabase PostgreSQL
    - profiles
    - la_so
    - chat_sessions
    - source_chunks (có chunk_strategy_id)
    - experiment_runs