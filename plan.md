# Kế Hoạch Công Việc: Hệ Thống Hỏi Đáp Tử Vi / Bát Tự với Hybrid GraphRAG
**Dựa trên:** Specification v5.0  
**Phiên bản:** 2.0  
**Ngày:** 2026-06-06  
**Thời gian thực hiện:** 7–8 tuần  
**Định dạng:** Các task được chia theo tuần, rất cụ thể, và không gán theo thành viên. Team tự phân công nội bộ.

***

## Cách đọc tài liệu này

- Mỗi task có mã duy nhất theo dạng `W[tuần]-[nhóm]-[số]`, ví dụ `W1-INFRA-01`.
- **When:** tuần hoặc khoảng thời gian cần làm task.
- **What to do:** các việc cần thực hiện cụ thể.
- **Deliverable:** kết quả đầu ra có thể kiểm tra được.
- **Depends on:** các task phải hoàn thành trước.
- **Done when:** tiêu chí hoàn thành rõ ràng, có thể xác minh.

> **Môi trường thực hiện:**  
> - 💻 **Local** = chạy trên laptop, không cần GPU  
> - ☁️ **Kaggle** = nên chạy trên Kaggle Free Tier cho job nặng  
> - 🌐 **Cloud** = chạy trên Render / Vercel / Supabase / Neo4j AuraDB

***

## Tuần 1 — Nền tảng và hạ tầng

Mục tiêu: Tất cả dịch vụ hạ tầng được tạo, skeleton project chạy local, và schema database được áp dụng.

***

### W1-INFRA-01 — Tạo tất cả dịch vụ cloud

**When:** Ngày 1–2  
**Môi trường:** 🌐 **Cloud**  
**What to do:**
- Tạo Supabase project ở free tier. Ghi lại project URL, anon key, và service key.
- Tạo Neo4j AuraDB Free instance. Ghi lại connection URI, username, password.
- Tạo project Vercel và kết nối với repo frontend. Cấu hình cho Next.js.
- Tạo service Render cho backend repo. Cấu hình môi trường Python 3.11.
- Tạo project Langfuse (cloud hoặc self-hosted). Ghi lại public key và secret key.
- Tạo file `.env.example` dùng chung, ghi đầy đủ toàn bộ biến môi trường cần thiết.

**Deliverable:** Tất cả dịch vụ hoạt động. File `.env.example` được commit vào repo.  
**Depends on:** —  
**Done when:** Team có thể kết nối tới từng dịch vụ từ máy local bằng biến môi trường.

***

### W1-INFRA-02 — Thiết lập cấu trúc repo

**When:** Ngày 1–2  
**Môi trường:** 💻 **Local**  
**What to do:**
- Quyết định và ghi rõ cấu trúc repo: monorepo (frontend + backend trong một repo) hoặc hai repo riêng.
- Khởi tạo project frontend: `npx create-next-app@14 --typescript`.
- Khởi tạo project backend: FastAPI với Python 3.11, dùng `pyproject.toml` hoặc `requirements.txt`.
- Thiết lập `.gitignore`, `README.md`, và chiến lược branch (ví dụ: `main`, `dev`, feature branches).
- Cấu hình chiến lược quản lý secrets và env cho cả dự án.

**Deliverable:** Repo được khởi tạo, `README.md` mô tả cách chạy, cả hai app chạy local bằng `npm run dev` và `uvicorn`.  
**Depends on:** W1-INFRA-01  
**Done when:** Bất kỳ thành viên nào cũng có thể clone repo và chạy cả hai app local trong vòng 10 phút theo README.

***

### W1-DB-01 — Áp dụng schema Supabase và RLS

**When:** Ngày 2–4  
**Môi trường:** 🌐 **Cloud** (Supabase dashboard + local SQL client)  
**What to do:**
- Viết migration SQL cho đủ 4 bảng: `profiles`, `la_so`, `chat_sessions`, `source_chunks`.
- Thêm constraint `UNIQUE (la_so_id)` trên `chat_sessions` để đảm bảo mỗi chart chỉ có một chat session.
- Thêm `CHECK (chart_system IN ('TUVI', 'BATU', 'TUVI_BATU'))` trên `la_so`.
- Thêm toàn bộ index theo schema đã định.
- Viết và áp dụng toàn bộ policy RLS cho `profiles`, `la_so`, `chat_sessions`.
- Thêm extension `moddatetime` và trigger tự động cập nhật `updated_at` cho cả 3 bảng.
- Viết script seed SQL tạo một test user + một `la_so` test + một `chat_sessions` test để dùng trong local dev.

**Deliverable:** File migration Supabase được áp dụng và commit. Seed script được commit. RLS được test thủ công để xác nhận user không đọc được data của user khác.  
**Depends on:** W1-INFRA-01  
**Done when:** Các bảng xuất hiện đúng trong Supabase dashboard. RLS chặn được truy cập chéo giữa user.

***

### W1-DB-02 — Khởi tạo schema và index Neo4j

**When:** Ngày 3–5  
**Môi trường:** 🌐 **Cloud** (Neo4j AuraDB + local Cypher client)  
**What to do:**
- Kết nối tới Neo4j AuraDB và chạy script setup Cypher.
- Tạo uniqueness constraint cho các node canonical: `Sao`, `Cung`, `ThienCan`, `DiaChi`, `NguHanh`, `Chunk`.
- Tạo vector index cho embedding chunk:
  ```cypher
  CREATE VECTOR INDEX chunkVector IF NOT EXISTS
  FOR (c:Chunk) ON (c.embedding)
  OPTIONS {indexConfig: {`vector.dimensions`: 768, `vector.similarity_function`: 'cosine'}}
  ```
- Tạo fulltext index cho sparse/BM25 retrieval:
  ```cypher
  CREATE FULLTEXT INDEX chunkFulltext IF NOT EXISTS
  FOR (c:Chunk) ON EACH [c.text, c.title, c.keywords]
  ```
- Commit toàn bộ Cypher setup vào repo trong `/infra/neo4j/`.

**Deliverable:** Neo4j có đầy đủ constraint và index. Script setup được commit.  
**Depends on:** W1-INFRA-01  
**Done when:** Cypher chạy không lỗi. `SHOW INDEXES` xác nhận vector index và fulltext index đã online.

***

### W1-AUTH-01 — Tích hợp Supabase Auth trong Next.js

**When:** Ngày 3–5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Cài `@supabase/supabase-js` và `@supabase/auth-helpers-nextjs`.
- Tạo `/app/(auth)/login/page.tsx` có form đăng nhập email/password.
- Tạo `/app/(auth)/register/page.tsx` có form đăng ký.
- Cài session handling ở server bằng `createServerComponentClient`.
- Tạo `lib/supabase.ts` cho client-side Supabase instance.
- Tạo middleware bảo vệ route: redirect user chưa đăng nhập về `/login`.
- Tạo chức năng logout.

**Deliverable:** Có trang login và register chạy được. Protected routes redirect đúng. Session tồn tại sau refresh trang.  
**Depends on:** W1-DB-01, W1-INFRA-02  
**Done when:** Thành viên có thể đăng ký, đăng nhập, vào trang protected, và đăng xuất. Truy cập dashboard khi chưa đăng nhập bị redirect về login.

***

### W1-API-01 — Tạo skeleton FastAPI và health endpoint

**When:** Ngày 3–5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Thiết lập FastAPI app với cấu trúc router:
  - `/health` — GET, trả về `{status: "ok"}`
  - `/chart/tuvi` — POST placeholder (tạm thời trả 501)
  - `/chat` — POST placeholder (tạm thời trả 501)
- Cấu hình CORS cho Vercel frontend và `localhost:3000`.
- Thêm stub tích hợp Langfuse SDK (khởi tạo client, chưa trace).
- Cấu hình đọc biến môi trường bằng `pydantic-settings`.
- Viết `Dockerfile` hoặc `render.yaml` cho deploy Render.

**Deliverable:** FastAPI chạy local. `/health` trả 200. Config deploy Render được commit.  
**Depends on:** W1-INFRA-01, W1-INFRA-02  
**Done when:** `curl http://localhost:8000/health` trả về `{"status":"ok"}`.

***

### W1-FE-01 — Tạo app shell và routing cho Next.js

**When:** Ngày 3–5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Tạo cấu trúc route:
  - `/` — landing hoặc redirect sang dashboard nếu đã đăng nhập.
  - `/dashboard` — protected, hiển thị danh sách chart.
  - `/chart/[id]` — protected, hiển thị chi tiết chart và chat.
- Cài và cấu hình Tailwind CSS và shadcn/ui.
- Cài và cấu hình Zustand cho global state.
- Tạo các component placeholder: `TuViBoard.tsx`, `BatuBoard.tsx`, `ChatInterface.tsx`, `ChartSummaryCard.tsx`.
- Tạo Next.js API route stub:
  - `/api/chat` — proxy tới FastAPI (tạm mock).
  - `/api/battu/calculate` — stub (tạm trả 501).

**Deliverable:** App shell có thể điều hướng. Route tồn tại và render placeholder content. Tailwind và shadcn/ui hoạt động.  
**Depends on:** W1-AUTH-01, W1-INFRA-02  
**Done when:** Vào `/dashboard` sau khi login thấy một trang hợp lệ. Không có route nào bị 404.

***

## Tuần 2 — Engine và visualizer

Mục tiêu: Tử Vi và Bát Tự engine được tích hợp và kiểm chứng. Visualizer hiển thị dữ liệu thật.

***

### W2-ENGINE-01 — Tích hợp engine Tử Vi (`lasotuvi`)

**When:** Tuần 2, ngày 1–3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Thêm `doanguyen/lasotuvi` và `pyvnlunar` vào backend dependencies.
- Implement endpoint `POST /chart/tuvi` trong FastAPI:
  - Nhận `{birth_date, birth_time, gender, label}`
  - Trả về full Tử Vi chart JSON.
- Chuẩn hóa output của engine thành internal schema ổn định.
- Xử lý các case lỗi: ngày không hợp lệ, giờ không hỗ trợ, thiếu field.

**Deliverable:** `POST /chart/tuvi` trả về chart JSON hợp lệ cho test birth date.  
**Depends on:** W1-API-01  
**Done when:** Endpoint được test với ít nhất 3 input khác nhau. Schema response được ghi trong `/docs/chart-schema.md`.

***

### W2-ENGINE-02 — Unit test độ chính xác engine Tử Vi

**When:** Tuần 2, ngày 2–4  
**Môi trường:** 💻 **Local**  
**What to do:**
- Chọn ít nhất 5 ngày sinh thật có chart Tử Vi đã được xác minh bằng tay từ yeutuvi.com và tuvilyso.net.
- Viết unit test so sánh output của engine với reference đã kiểm chứng, cả theo sao và cung.
- Ghi lại mọi sai lệch nếu có, đánh dấu là chấp nhận được hoặc cần sửa.

**Deliverable:** File test `tests/test_tuvi_engine.py` có ít nhất 5 case. Có test report ghi rõ pass/fail và deviation nếu có.  
**Depends on:** W2-ENGINE-01  
**Done when:** Cả 5 test case đều pass phần star placement (Chính Tinh). Nếu fail case nào thì phải có giải thích.

***

### W2-ENGINE-03 — Tích hợp engine Bát Tự (`alvamind`)

**When:** Tuần 2, ngày 1–3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Thêm package `bazi-calculator-by-alvamind` vào project Next.js.
- Implement Next.js API Route `POST /api/battu/calculate`:
  - Nhận `{year, month, day, hour, gender}`
  - Trả về Bát Tự JSON từ `calc.getCompleteAnalysis()`
- Chuẩn hóa output thành internal schema ổn định.
- Xử lý input lỗi: ngày/giờ không hợp lệ, tham số thiếu.

**Deliverable:** `POST /api/battu/calculate` trả về Bát Tự JSON hợp lệ.  
**Depends on:** W1-FE-01  
**Done when:** API route được test với ít nhất 3 bộ input. Schema response được ghi lại.

***

### W2-ENGINE-04 — Luồng tạo và lưu chart end-to-end

**When:** Tuần 2, ngày 3–5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Xây dựng form “Create new chart” trong Next.js:
  - Fields: label, birth date, birth time, gender, chart type (Tử Vi / Bát Tự / Both).
- Khi submit:
  - Gọi engine tương ứng.
  - Lưu chart JSON và metadata vào bảng `la_so` qua Supabase.
  - Redirect sang `/chart/[new_id]`.
- Xử lý loading state và error state.

**Deliverable:** Người dùng tạo chart được từ form và chart được lưu vào Supabase. Redirect sang chart page hoạt động.  
**Depends on:** W2-ENGINE-01, W2-ENGINE-03, W1-DB-01  
**Done when:** Tạo chart từ form sinh ra đúng một row trong `la_so` và redirect đúng.

***

### W2-VIZ-01 — Bảng Tử Vi 12 cung (SVG/D3 skeleton)

**When:** Tuần 2, ngày 3–5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement component `TuViBoard.tsx`:
  - Render layout 12 cung dạng SVG.
  - Mỗi ô cung hiển thị tên cung và danh sách sao.
  - Nhận chart JSON qua props.
- Ưu tiên plain SVG trước, D3 transitions chỉ thêm nếu còn thời gian.
- Style bằng Tailwind khi phù hợp.

**Deliverable:** `TuViBoard.tsx` render đúng 12 cung từ chart data thật trên `/chart/[id]`.  
**Depends on:** W2-ENGINE-04  
**Done when:** Lưới hiển thị sao đúng ở đúng cung cho một chart test đã kiểm chứng.

***

### W2-VIZ-02 — Bảng Bát Tự cơ bản

**When:** Tuần 2, ngày 4–5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement component `BatuBoard.tsx`:
  - Hiển thị bốn trụ (Năm, Tháng, Ngày, Giờ) theo layout 4 cột.
  - Hiển thị Thiên Can, Địa Chi, và Nạp Âm của từng trụ.
  - Nhận Bát Tự JSON qua props.

**Deliverable:** `BatuBoard.tsx` render đúng từ dữ liệu Bát Tự thật.  
**Depends on:** W2-ENGINE-04  
**Done when:** Bốn trụ hiển thị đúng cho một test birth date. Đã kiểm chứng với reference.

***

### W2-DASH-01 — Dashboard: danh sách chart

**When:** Tuần 2, ngày 4–5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement trang `/dashboard`:
  - Lấy toàn bộ row `la_so` của user hiện tại.
  - Hiển thị mỗi chart bằng `ChartSummaryCard`: label, birth date, chart type, ngày tạo.
  - Bấm vào card thì đi tới `/chart/[id]`.
  - Có nút “Create new chart”.

**Deliverable:** Dashboard hiển thị danh sách chart đã lưu. Điều hướng tới chart detail và trang tạo mới hoạt động.  
**Depends on:** W2-ENGINE-04, W1-AUTH-01  
**Done when:** Sau khi đăng nhập, user thấy chart của mình. Empty state được xử lý tử tế.

***

## Tuần 3 — Ingestion pipeline

Mục tiêu: Ít nhất 3–4 sách nguồn đầu tiên được ingest vào Neo4j dưới dạng graph có cấu trúc + vector + fulltext.

***

### W3-INGEST-01 — Script extract và normalize PDF

**When:** Tuần 3, ngày 1–2  
**Môi trường:** 💻 **Local**  
**What to do:**
- Viết Python script `scripts/extract_pdf.py`:
  - Nhận đường dẫn PDF qua argument.
  - Detect text-based hay scanned bằng `pdfplumber`.
  - Extract text từ PDF text-based bằng `pdfplumber` hoặc `pymupdf`.
  - Normalize output: Unicode NFC, bỏ header/footer/page number, xóa khoảng trắng thừa.
  - Output ra danh sách `{page, text}` cho từng trang.
- Xử lý trường hợp text extraction ra dưới 50 ký tự mỗi trang thì đánh dấu “needs OCR”.

**Deliverable:** `scripts/extract_pdf.py` chạy được với PDF test và tạo ra text theo từng trang đã làm sạch. Output lưu dưới JSON.  
**Depends on:** —  
**Done when:** Script được test trên ít nhất 2 file PDF, một text-based và một borderline. Output sạch và chuẩn Unicode.

***

### W3-INGEST-02 — Parser cấu trúc và chunking parent-child

**When:** Tuần 3, ngày 1–3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Viết Python script `scripts/chunk_text.py`:
  - Nhận text đã normalize theo trang.
  - Detect heading/section/paragraph bằng heuristic (độ dài dòng, chữ hoa, pattern đánh số).
  - Tách thành parent chunk: 400–512 tokens, overlap 60–100 tokens.
  - Với mỗi parent chunk, tạo child chunk: 120–180 tokens, overlap nhỏ.
  - Ép rule: không tách giữa câu nếu câu có chứa tên sao hoặc tên cung.
  - Thêm metadata cho mỗi chunk: `source_name`, `source_page`, `parent_id`, `chunk_type` (parent/child), `domain`, `chunk_hash`.
- Danh sách tên sao và tên cung cần được hard-code hoặc load từ config để tránh cắt ngang.

**Deliverable:** `scripts/chunk_text.py` tạo được cặp parent-child chunk với đầy đủ metadata. Output lưu dưới JSON. Ít nhất 1 sách thật được xử lý end-to-end.  
**Depends on:** W3-INGEST-01  
**Done when:** Chunk output được review bằng tay cho hơn 50 chunk. Không có tên sao hoặc tên cung nào bị cắt ngang. Kích thước chunk nằm trong vùng target.

***

### W3-INGEST-03 — Trích xuất entity từ chunk

**When:** Tuần 3, ngày 2–4  
**Môi trường:** ☁️ **Kaggle**  
**What to do:**
- Viết Python script `scripts/extract_entities.py`:
  - Nhận danh sách chunk.
  - Với mỗi chunk, gọi Gemini Flash-Lite bằng prompt có cấu trúc để trích:
    - Entity types: `Sao`, `Cung`, `ToHop`, `KhaiNiem`, `LuanGiai`, `ThienCan`, `DiaChi`, `NguHanh`
    - Relation giữa các entity trong chunk
    - Phân loại `domain`: `TUVI`, `BATU`, hoặc `SHARED`
  - Chuẩn hóa tên entity theo lookup table (ví dụ `"tử vi"` → `"Tử Vi"`).
  - Output: danh sách `{entities, relations, domain}` cho mỗi chunk.
- Viết prompt template cho entity extraction và commit vào `/prompts/entity_extraction.txt`.
- Thêm rate limiting cơ bản để phù hợp với RPM của Gemini Flash-Lite.

**Deliverable:** `scripts/extract_entities.py` tạo được output entity/relation có cấu trúc cho toàn bộ chunk của ít nhất 1 sách. Prompt template và lookup table được commit.  
**Depends on:** W3-INGEST-02  
**Done when:** Output entity được review bằng tay cho hơn 30 chunk. Entity được type đúng và canonical name được dùng nhất quán.

***

### W3-INGEST-04 — Ghi graph vào Neo4j

**When:** Tuần 3, ngày 3–5  
**Môi trường:** ☁️ **Kaggle**  
**What to do:**
- Viết Python script `scripts/write_graph.py`:
  - Nhận output entity/relation từ W3-INGEST-03.
  - Với mỗi entity: dùng `MERGE` để tạo hoặc cập nhật node với key duy nhất `canonical_name + domain + entity_type`.
  - Với mỗi relation: dùng `MERGE` để tạo relationship.
  - Với mỗi chunk (parent và child): tạo node `Chunk`, link tới entity bằng `MENTIONS`, link tới `Source` bằng `HAS_CHUNK`.
  - Gán property `domain` cho toàn bộ node.
  - Ghi log số node được tạo và số node được merge để theo dõi dedup.

**Deliverable:** Ít nhất 1 sách được ghi đầy đủ vào Neo4j graph. Có log thống kê số node và edge.  
**Depends on:** W3-INGEST-03, W1-DB-02  
**Done when:** Neo4j browser xác nhận đúng node và edge. Kiểm tra ngẫu nhiên 5 node sao để xác nhận domain và relation đúng.

***

### W3-INGEST-05 — Tạo và lưu embedding

**When:** Tuần 3, ngày 4–5  
**Môi trường:** ☁️ **Kaggle**  
**What to do:**
- Viết Python script `scripts/embed_chunks.py`:
  - Nhận danh sách parent và child chunk.
  - Gọi `gemini-embedding-001` để tạo embedding cho text của từng chunk.
  - Ghi vector embedding vào property `embedding` của node `Chunk` trong Neo4j.
  - Batch processing và rate limiting cho Gemini Embedding API.

**Deliverable:** Tất cả node `Chunk` trong Neo4j có property `embedding`. Vector index hoạt động.  
**Depends on:** W3-INGEST-04  
**Done when:** `SHOW INDEXES` trong Neo4j cho thấy vector index đang ONLINE. Query similarity thử ra kết quả.

***

### W3-INGEST-06 — Lưu provenance vào Supabase `source_chunks`

**When:** Tuần 3, ngày 4–5  
**Môi trường:** ☁️ **Kaggle**  
**What to do:**
- Mở rộng pipeline để ghi provenance vào bảng `source_chunks` của Supabase.
- Mỗi row `source_chunks` phải có: `source_name`, `source_type`, `domain`, `source_page`, `chunk_text`, `chunk_hash`, `metadata` (bao gồm `parent_id`, `chunk_type`).
- Dùng `chunk_hash` để dedup: nếu hash đã tồn tại thì bỏ qua insert.
- Cross-reference: mỗi node `Chunk` trong Neo4j phải lưu `chunk_id` khớp với UUID trong `source_chunks`.

**Deliverable:** Bảng `source_chunks` trong Supabase được populate bằng toàn bộ chunk đã ingest. Cross-reference giữa Neo4j node và Supabase row được verify cho ít nhất 5 mẫu.  
**Depends on:** W3-INGEST-04  
**Done when:** Mỗi chunk ingested đều có row tương ứng trong `source_chunks` với `chunk_hash` khớp. Không có duplicate row.

***

### W3-INGEST-07 — Ingest 3–4 sách ưu tiên đầu tiên

**When:** Tuần 3, ngày 3–5 (chạy song song với W3-INGEST-04 đến W3-INGEST-06 khi xử lý từng sách)  
**Môi trường:** ☁️ **Kaggle**  
**What to do:**
- Chọn 3–4 đầu sách ưu tiên nhất cho MVP (khuyến nghị: 2 Tử Vi, 2 Bát Tự từ danh sách nguồn trong spec).
- Chạy toàn bộ pipeline cho từng sách: extract → chunk → entity extract → graph write → embed → provenance.
- Với mỗi sách, ghi lại:
  - Tổng số trang extract được.
  - Tổng số chunk tạo ra.
  - Tổng số entity/node tạo ra.
  - Tổng số edge tạo ra.
  - Các vấn đề extraction hoặc trang bị bỏ qua.

**Deliverable:** 3–4 sách được ingest đầy đủ. Báo cáo ingestion cho từng sách được commit trong `/docs/ingestion-reports/`.  
**Depends on:** W3-INGEST-01 đến W3-INGEST-06  
**Done when:** Neo4j chứa dữ liệu của cả 3–4 sách. Số node/edge nằm trong phạm vi dự kiến theo Section 16 của spec. Provenance có mặt trong Supabase.

***

### W3-INGEST-08 — Hỗ trợ incremental ingestion

**When:** Tuần 3, ngày 5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Mở rộng pipeline để hỗ trợ chạy lại incremental:
  - Trước khi insert chunk, kiểm tra `chunk_hash` trong `source_chunks`. Nếu đã tồn tại, skip.
  - Trước khi tạo node trong Neo4j, dùng `MERGE` như đã áp dụng ở W3-INGEST-04.
  - Ghi log số chunk được skip và số chunk mới được insert mỗi lần chạy.

**Deliverable:** Chạy pipeline 2 lần trên cùng một sách thì không tạo duplicate node/chunk. Log xác nhận việc skip.  
**Depends on:** W3-INGEST-06  
**Done when:** Chạy lại pipeline trên sách đã ingest trước đó cho ra 0 insert mới và 0 duplicate node.

***

## Tuần 4 — Core RAG pipeline

Mục tiêu: Toàn bộ LangGraph Hybrid GraphRAG chạy end-to-end từ câu hỏi đến câu trả lời.

***

### W4-RAG-01 — State và skeleton node cho LangGraph

**When:** Tuần 4, ngày 1–2  
**Môi trường:** 💻 **Local**  
**What to do:**
- Định nghĩa `RAGState` TypedDict như trong Section 7.2 của spec.
- Định nghĩa toàn bộ node của LangGraph dưới dạng Python function (trước mắt chỉ stub):
  - `load_chart_context`
  - `normalize_query`
  - `classify_query_complexity`
  - `rewrite_query`
  - `extract_entities`
  - `graph_retrieval`
  - `dense_retrieval`
  - `sparse_retrieval`
  - `rrf_fusion`
  - `rerank`
  - `assemble_context`
  - `generate`
  - `map_citations`
- Định nghĩa edges và conditional routing của graph.
- Viết test để khởi tạo graph và chạy với mock state (chưa gọi API thật).

**Deliverable:** LangGraph graph được định nghĩa. Tất cả node có mặt. Graph compile và chạy không lỗi trên mock input.  
**Depends on:** W1-API-01  
**Done when:** `graph.invoke(mock_state)` chạy xong không exception. Graph visualization hiển thị topology đúng.

***

### W4-RAG-02 — Node rewrite query

**When:** Tuần 4, ngày 1–2  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement node `rewrite_query`:
  - Đọc mức độ phức tạp query từ state.
  - Nếu complexity là `high` hoặc query ngắn hơn 10 từ, rewrite bằng Gemini Flash-Lite.
  - Dùng prompt từ `/prompts/query_rewrite.txt`:
    - Chèn original query, chart type, key stars và houses từ `chart_data`.
    - Chỉ dẫn: làm rõ entity reference, không thêm claim không có cơ sở.
  - Lưu kết quả vào `state.rewritten_query`.
  - Nếu query `low` và đủ dài thì giữ nguyên.
- Viết prompt template và commit vào `/prompts/query_rewrite.txt`.

**Deliverable:** Node `rewrite_query` hoạt động. Ít nhất 5 lần rewrite được chạy và review bằng tay.  
**Depends on:** W4-RAG-01  
**Done when:** Node tạo ra query rõ hơn hoặc giữ nguyên hợp lý. Rewrite không thêm claim không có trong input.

***

### W4-RAG-03 — Node trích xuất entity khi runtime

**When:** Tuần 4, ngày 1–3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement node `extract_entities`:
  - Gọi Gemini Flash-Lite với prompt trích xuất entity.
  - Prompt phải bao gồm chart context và taxonomy entity types.
  - Chuẩn hóa tên entity theo cùng lookup table với ingestion pipeline.
  - Lưu kết quả vào `state.entities`.
- Tái sử dụng prompt template logic từ ingestion (W3-INGEST-03) nếu phù hợp.

**Deliverable:** Node `extract_entities` trả về danh sách entity canonical từ query thật + chart context thật.  
**Depends on:** W4-RAG-01, W3-INGEST-03  
**Done when:** Node được test với 5 query mẫu. Entity trích xuất khớp với sao/cung mong đợi.

***

### W4-RAG-04 — Node graph retrieval

**When:** Tuần 4, ngày 2–3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement node `graph_retrieval`:
  - Nhận entity từ `state.entities`.
  - Áp dụng domain filter theo `state.chart_type` (ví dụ `domain IN ['TUVI', 'SHARED']`).
  - Chạy Cypher query để tìm node khớp entity và traversal 1–2 hop.
  - Lấy các node `Chunk` liên quan.
  - Trả về danh sách chunk và score trong `state.graph_candidates`.
- Viết ít nhất 2 template Cypher khác nhau và test trước trong Neo4j browser.

**Deliverable:** Node `graph_retrieval` trả về ranked chunk candidate từ Neo4j cho query thật.  
**Depends on:** W4-RAG-01, W4-RAG-03, W3-INGEST-07  
**Done when:** Node được test với 5 query. Trả về kết quả không rỗng với câu hỏi liên quan tới sao/cung đã ingest.

***

### W4-RAG-05 — Node dense retrieval

**When:** Tuần 4, ngày 2–3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement node `dense_retrieval`:
  - Embed `state.rewritten_query` bằng `gemini-embedding-001`.
  - Chạy similarity search trên Neo4j vector index.
  - Filter theo `domain` khớp `state.domain_filter`.
  - Trả về top-k kết quả trong `state.dense_candidates`.

**Deliverable:** Node `dense_retrieval` trả về top-k chunk có độ tương tự ngữ nghĩa cao cho query thật.  
**Depends on:** W4-RAG-01, W3-INGEST-05  
**Done when:** Node test với 5 query. Kết quả hợp ngữ nghĩa khi review bằng tay.

***

### W4-RAG-06 — Node sparse retrieval (BM25/fulltext)

**When:** Tuần 4, ngày 2–3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement node `sparse_retrieval`:
  - Tạo keyword query từ `state.rewritten_query` hoặc top entities.
  - Chạy `CALL db.index.fulltext.queryNodes('chunkFulltext', ...)` trên Neo4j fulltext index.
  - Áp dụng domain filter.
  - Lưu kết quả vào `state.sparse_candidates`.

**Deliverable:** Node `sparse_retrieval` trả về chunk khớp keyword.  
**Depends on:** W4-RAG-01, W1-DB-02  
**Done when:** Node test với 5 query chứa tên sao/cung cụ thể. Trả về đúng chunk có term đó.

***

### W4-RAG-07 — Node RRF fusion

**When:** Tuần 4, ngày 3–4  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement node `rrf_fusion`:
  - Nhận `state.graph_candidates`, `state.dense_candidates`, `state.sparse_candidates`.
  - Áp dụng công thức Reciprocal Rank Fusion: `score(d) = sum(1 / (k + rank_i(d)))` với `k=60`.
  - Merge và dedup chunk theo `chunk_id`.
  - Sắp xếp kết quả theo fused RRF score giảm dần.
  - Lưu vào `state.fused_candidates`.

**Deliverable:** Node `rrf_fusion` merge được 3 danh sách candidate thành một list đã xếp hạng.  
**Depends on:** W4-RAG-04, W4-RAG-05, W4-RAG-06  
**Done when:** Node test với output thật từ cả 3 retrieval path. Ranking sau fusion cho thấy có sự phối hợp từ nhiều nguồn.

***

### W4-RAG-08 — Node rerank bằng cross-encoder

**When:** Tuần 4, ngày 3–4  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement node `rerank`:
  - Nhận top-k candidate từ `state.fused_candidates` (ví dụ top 20).
  - Dùng cross-encoder model để chấm lại từng cặp (query, chunk).
  - Khuyến nghị model nhẹ local như `cross-encoder/ms-marco-MiniLM-L-6-v2` qua `sentence-transformers`.
  - Loại candidate có score dưới ngưỡng (ví dụ 0.1).
  - Lưu top-k sau rerank (ví dụ top 5–8) vào `state.reranked_candidates`.
- Ghi lại model reranker đã chọn trong note tài liệu phụ.

**Deliverable:** Node `rerank` chấm lại và lọc candidate. Tên reranker model được ghi trong `/docs/model-choices.md`.  
**Depends on:** W4-RAG-07  
**Done when:** Node chạy end-to-end. Thứ tự sau rerank khác với RRF ở một số query, chứng minh reranker có tác dụng.

***

### W4-RAG-09 — Node assemble context và token budget

**When:** Tuần 4, ngày 4  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement node `assemble_context`:
  - Lấy `state.reranked_candidates` (child chunk → fetch parent chunk tương ứng).
  - Ghép các parent chunk thành final context string.
  - Giới hạn token budget: đếm token và cắt nếu vượt threshold (ví dụ 8,000 tokens cho MVP).
  - Đưa chart context summary lên đầu context đã ghép.
  - Lưu vào `state.final_context`.

**Deliverable:** Node `assemble_context` tạo được context đã trim, có liên quan chart, và nằm trong giới hạn token.  
**Depends on:** W4-RAG-08  
**Done when:** Node được test. Output không vượt token budget. Chart context luôn có mặt trong final context.

***

### W4-RAG-10 — Node generation

**When:** Tuần 4, ngày 4–5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement node `generate`:
  - Chọn model theo logic `route_model()` dựa trên `query_complexity`.
  - Gọi Gemini Flash hoặc Flash-Lite với generation prompt.
  - Prompt generation (commit vào `/prompts/generation.txt`) phải:
    - Bao gồm chart context.
    - Bao gồm retrieval context đã assemble.
    - Bao gồm history hội thoại (20 message gần nhất).
    - Chỉ dẫn: trả lời bằng tiếng Việt, cite chunk, nói “không đủ dữ liệu” nếu context chưa đủ.
  - Parse response từ LLM và lưu vào `state.answer`.
- Tích hợp Langfuse tracing: log toàn bộ LLM call (prompt, response, model, latency).

**Deliverable:** Node `generate` trả về câu trả lời tiếng Việt grounded với trace trong Langfuse.  
**Depends on:** W4-RAG-09  
**Done when:** Test end-to-end với query thật + chart thật cho ra câu trả lời hợp lý. Trace xuất hiện trong Langfuse dashboard.

***

### W4-RAG-11 — Node map citations

**When:** Tuần 4, ngày 5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement node `map_citations`:
  - Map từng chunk ID được cite trong answer sang `source_name` và `source_page` từ bảng `source_chunks` trong Supabase.
  - Tạo `state.sources` dưới dạng list `{chunk_id, source_name, source_page, chunk_text_preview}`.

**Deliverable:** Node `map_citations` tạo ra danh sách citation liên kết tới record nguồn thật.  
**Depends on:** W4-RAG-10, W3-INGEST-06  
**Done when:** Danh sách citation của một answer test map đúng với row `source_chunks` trong Supabase.

***

### W4-RAG-12 — FastAPI `/chat` với LangGraph

**When:** Tuần 4, ngày 5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement `POST /chat` trong FastAPI:
  - Nhận `{chart_id, user_id, query, messages}`.
  - Load chart data từ `chart_id` qua Supabase.
  - Khởi tạo RAGState và invoke LangGraph graph.
  - Trả về `{answer, sources, rewritten_query}`.
- Implement `POST /chart/tuvi` để vừa save chart vào Supabase vừa trả `chart_id`.
- Thêm cache: dùng in-memory dict key theo `hash(chart_id + normalized_query)` cho MVP.

**Deliverable:** `POST /chat` trả về đầy đủ answer và citations cho một query thật + chart thật.  
**Depends on:** W4-RAG-11  
**Done when:** `curl -X POST /chat` với chart_id thật và câu hỏi thật trả về JSON đầy đủ có answer và sources.

***

## Tuần 5 — Tích hợp frontend và chat UI

Mục tiêu: Frontend kết nối đầy đủ với backend. Người dùng có thể chat với chart và xem citations.

***

### W5-FE-01 — Kết nối proxy Next.js `/api/chat` tới FastAPI

**When:** Tuần 5, ngày 1–2  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement Next.js API route `/api/chat` như proxy đúng nghĩa tới FastAPI:
  - Đính kèm session token.
  - Forward `chart_id`, `query`, `messages`.
  - Handle lỗi từ FastAPI và trả structured error response cho frontend.
- Xử lý Render cold start: retry sau 3 giây nếu request đầu tiên timeout.
- Thêm loading state vào `ChatInterface.tsx`.

**Deliverable:** `/api/chat` của Next.js proxy được tới FastAPI và trả answer + sources.  
**Depends on:** W4-RAG-12, W1-FE-01  
**Done when:** Gõ message trong browser sẽ kích hoạt toàn bộ RAG pipeline và hiển thị phản hồi.

***

### W5-FE-02 — Chat UI đầy đủ

**When:** Tuần 5, ngày 1–3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement `ChatInterface.tsx`:
  - Danh sách message cho user và assistant.
  - Input text + nút gửi.
  - Hiển thị full-response cho MVP hoặc streaming nếu kịp.
  - Loading indicator khi chờ phản hồi.
  - Hiển thị “System warming up…” và retry khi cold start timeout.
  - Lưu lịch sử chat vào `chat_sessions.messages` sau mỗi lần tương tác.
  - Load message cũ khi mở trang.

**Deliverable:** Chat UI hoàn chỉnh. Message được lưu và load lại từ Supabase.  
**Depends on:** W5-FE-01, W1-DB-01  
**Done when:** User gửi message, nhận phản hồi, refresh trang và vẫn thấy toàn bộ lịch sử chat.

***

### W5-FE-03 — Citation panel

**When:** Tuần 5, ngày 2–3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement `SourceCitationPanel.tsx`:
  - Hiển thị danh sách citation cho assistant response gần nhất.
  - Mỗi citation hiển thị: tên sách nguồn, số trang, và đoạn preview ngắn.
  - Có thể collapse/expand.
  - Tự cập nhật khi có response mới.

**Deliverable:** Citation hiển thị trong UI sau mỗi câu trả lời. Citation khớp dữ liệu trong `source_chunks`.  
**Depends on:** W5-FE-02, W4-RAG-11  
**Done when:** Ít nhất một answer test hiển thị 2+ citation với đúng tên nguồn và page.

***

### W5-FE-04 — Ghép đầy đủ trang chi tiết chart

**When:** Tuần 5, ngày 3–4  
**Môi trường:** 💻 **Local**  
**What to do:**
- Ghép trang `/chart/[id]` với các component:
  - `ChartSummaryCard.tsx` ở đầu: hiển thị label, thông tin sinh, chart system.
  - `TuViBoard.tsx` hoặc `BatuBoard.tsx` theo `chart_system`.
  - `ChatInterface.tsx` đặt cạnh hoặc dưới board.
  - `SourceCitationPanel.tsx` gắn cùng chat hoặc bên cạnh.
- Bảo đảm render đúng theo `chart_system`.
- Xử lý data thiếu hoặc đang load.

**Deliverable:** Trang `/chart/[id]` hiển thị đầy đủ trải nghiệm: chart board + chat + citations.  
**Depends on:** W2-VIZ-01, W2-VIZ-02, W5-FE-02, W5-FE-03  
**Done when:** Trang full render được với data thật. Cả 3 vùng chính hiển thị đúng.

***

### W5-FE-05 — Tự tạo chat session khi mở chart lần đầu

**When:** Tuần 5, ngày 3–4  
**Môi trường:** 💻 **Local**  
**What to do:**
- Khi load `/chart/[id]`:
  - Query Supabase để xem có row `chat_sessions` nào với `la_so_id = chart_id` không.
  - Nếu chưa có, tự tạo mới (title = label chart, messages = []).
  - Load message hiện có vào `ChatInterface`.
- Bảo đảm một chart chỉ có một chat session: không bao giờ tạo session thứ hai cho cùng chart.

**Deliverable:** Chat session được tự tạo khi mở chart lần đầu. Lần sau load lại đúng session cũ.  
**Depends on:** W5-FE-02, W1-DB-01  
**Done when:** Lần đầu mở chart mới chỉ tạo đúng 1 row trong `chat_sessions`. Lần sau load đúng session đó. Constraint `UNIQUE (la_so_id)` không bao giờ bị vi phạm.

***

### W5-FE-06 — Context windowing: rolling history

**When:** Tuần 5, ngày 4–5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Implement windowing ở frontend:
  - Chỉ gửi 20 message gần nhất trong payload tới `/api/chat`.
  - Nếu message > 20 thì trim phần cũ hơn khi gửi request, nhưng vẫn lưu đủ trong Supabase.
- Implement windowing ở backend:
  - FastAPI `/chat` chỉ dùng 20 message gần nhất từ payload.
- Khi `len(messages) > 30`, dùng Gemini Flash-Lite để tạo summary và lưu vào `chat_sessions.summary`.

**Deliverable:** Prompt history không vượt quá 20 message. Summary được tạo cho chat dài.  
**Depends on:** W5-FE-02, W4-RAG-12  
**Done when:** Test với 30+ message: prompt gửi lên Gemini chỉ có 20 message cuối. Cột summary được cập nhật trong Supabase sau khi vượt ngưỡng.

***

### W5-FE-07 — Error handling và fallback states

**When:** Tuần 5, ngày 5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Định nghĩa và implement các error state:
  - Neo4j không truy cập được: trả message fallback chung, log lỗi vào Langfuse.
  - Gemini vượt quota: trả “Hệ thống đang bận, vui lòng thử lại sau”.
  - Supabase write fail khi lưu chat: retry một lần, sau đó log âm thầm (không chặn UI).
  - Retrieval rỗng: model vẫn phải trả “không đủ dữ liệu trong nguồn hiện tại”.
- Thêm rate limiting cho `/api/chat`: tối đa 10 request/phút cho mỗi `user_id`.

**Deliverable:** Tất cả error state được xử lý. Có rate limiter. Error message thân thiện bằng tiếng Việt.  
**Depends on:** W5-FE-01, W4-RAG-12  
**Done when:** Simulate Neo4j outage thì UI trả message graceful. Gửi 11 request trong 1 phút thì request thứ 11 nhận HTTP 429.

***

## Tuần 6 — Tích hợp, đánh giá và tinh chỉnh

Mục tiêu: Hệ thống được đánh giá bằng golden dataset. Retrieval, chunking, và prompt được tinh chỉnh theo kết quả.

***

### W6-EVAL-01 — Tạo bộ dữ liệu đánh giá

**When:** Tuần 6, ngày 1–3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Tạo 50–100 cặp Q&A để đánh giá.
- Phân bổ: 40% factual, 40% interpretive, 20% multi-hop.
- Với mỗi Q&A:
  - Viết `question`, `question_type`, `difficulty`.
  - Gắn `chart_id` thật hoặc chart context test.
  - Viết `expected_answer_summary` (không cần nguyên văn, chỉ key points).
  - Liệt kê `required_sources` (sách/section nào cần được cite).
  - Viết `gold_context` (đoạn thật trả lời câu hỏi).
- Thêm 5–10 câu adversarial ngoài corpus, yêu cầu hệ thống phải từ chối bằng “không đủ dữ liệu”.
- Lưu dataset vào `evaluation/golden_dataset.json`.

**Deliverable:** `evaluation/golden_dataset.json` có 50–100 entry theo schema đã ghi.  
**Depends on:** W3-INGEST-07  
**Done when:** Dataset được ít nhất 2 thành viên review và xác nhận đúng.

***

### W6-EVAL-02 — Viết evaluation runner tự động

**When:** Tuần 6, ngày 2–3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Viết `evaluation/run_eval.py`:
  - Duyệt qua toàn bộ dataset.
  - Với mỗi entry, gọi FastAPI `/chat` với question và chart context.
  - Lưu response hệ thống (answer, sources, rewritten_query, retrieved context).
  - Tính RAGAS metrics bằng thư viện `ragas`:
    - Faithfulness
    - Answer Relevancy
    - Context Recall
  - Tính custom metrics:
    - Graph Hit Rate: kiểm tra overlap giữa retrieved source và `required_sources`
    - Citation Coverage: tỷ lệ answer có ít nhất 1 citation hợp lệ
  - Xuất kết quả thành `evaluation/results/run_[timestamp].json` và summary CSV.

**Deliverable:** Evaluation runner tạo được results JSON và summary CSV với đủ 7 metrics.  
**Depends on:** W6-EVAL-01, W4-RAG-12  
**Done when:** Runner chạy hết 50+ entry không crash. Output metrics đọc được.

***

### W6-EVAL-03 — Chạy đánh giá và phân tích kết quả

**When:** Tuần 6, ngày 3–4  
**Môi trường:** ☁️ **Kaggle**  
**What to do:**
- Chạy `run_eval.py` trên system hiện tại.
- So sánh kết quả với các ngưỡng target trong spec Section 19.3.
- Phân loại lỗi theo nhóm:
  - Retrieval miss
  - Reranking miss
  - Hallucination
  - Source mismatch
  - Weak multi-hop
- Ghi kết quả vào `evaluation/report_v1.md`.

**Deliverable:** `evaluation/report_v1.md` có metric score, phân tích lỗi, và danh sách ưu tiên cải tiến.  
**Depends on:** W6-EVAL-02  
**Done when:** Báo cáo được viết và chia sẻ cho team. Từng metric được ghi rõ pass/fail theo target.

***

### W6-EVAL-04 — Tuning sprint dựa trên kết quả đánh giá

**When:** Tuần 6, ngày 4–5  
**Môi trường:** 💻 **Local** + ☁️ **Kaggle**  
**What to do:**
Dựa trên kết quả W6-EVAL-03, thực hiện các fix có mục tiêu. Các tình huống phổ biến:

- **Context Recall thấp** → chỉnh chunk overlap, chunk size, hoặc trọng số hybrid retrieval.
- **Faithfulness thấp / hallucination** → siết prompt generation, thêm chỉ dẫn “Chỉ sử dụng thông tin có trong context”.
- **Graph Hit Rate thấp** → xem lại chất lượng entity extraction, bảng canonicalization, hoặc độ sâu traversal Cypher.
- **Citation Coverage thấp** → kiểm tra node `map_citations` có lấy đúng chunk ID hay không.
- **Multi-hop thất bại** → tăng số hop graph traversal hoặc đưa chart context vào initial state rõ hơn.

Sau khi sửa, chạy lại `run_eval.py` và so sánh với baseline.

**Deliverable:** Hoàn thành ít nhất một vòng tuning. Kết quả evaluation lần 2 được commit vào `evaluation/results/run_[timestamp]_v2.json`. Có ghi lại delta so với baseline.  
**Depends on:** W6-EVAL-03  
**Done when:** Ít nhất 3 trong 7 metrics đạt hoặc vượt target sau tuning.

***

### W6-INT-01 — Integration test end-to-end

**When:** Tuần 6, ngày 5  
**Môi trường:** 💻 **Local**  
**What to do:**
- Chạy toàn bộ user journey từ đầu đến cuối:
  1. Đăng ký user mới.
  2. Tạo chart Tử Vi.
  3. Mở `/chart/[id]`.
  4. Hỏi 5 câu khác nhau.
  5. Kiểm tra câu trả lời có citation.
  6. Làm lại cho chart Bát Tự.
- Ghi lại bug hoặc luồng bị hỏng thành GitHub Issue.

**Deliverable:** Báo cáo integration test liệt kê từng bước, pass/fail, và issue tìm thấy.  
**Depends on:** Toàn bộ W4 và W5  
**Done when:** Tất cả 10 bước pass không có lỗi nghiêm trọng. Mọi bug được mở issue.

***

## Tuần 7 — Deploy, monitoring và QA

Mục tiêu: Hệ thống được deploy lên Vercel và Render. Langfuse monitoring hoạt động. Mọi bug nghiêm trọng đã được xử lý.

***

### W7-DEPLOY-01 — Deploy backend FastAPI lên Render

**When:** Tuần 7, ngày 1–2  
**Môi trường:** 🌐 **Cloud**  
**What to do:**
- Cấu hình `render.yaml` hoặc Render dashboard:
  - Build command: `pip install -r requirements.txt`
  - Start command: `uvicorn main:app --host 0.0.0.0 --port 8000`
  - Set toàn bộ environment variables (Neo4j URI, Gemini key, Supabase keys, Langfuse keys)
- Deploy và verify `/health` trả 200 từ URL của Render.
- Verify CORS cho phép frontend Vercel.
- Test cold start: đo thời gian request đầu sau idle.

**Deliverable:** FastAPI live trên Render. `/health` truy cập được từ browser.  
**Depends on:** W4-RAG-12  
**Done when:** `curl https://[render-url]/health` trả về `{"status":"ok"}`. Có ghi lại độ trễ cold start.

***

### W7-DEPLOY-02 — Deploy frontend Next.js lên Vercel

**When:** Tuần 7, ngày 1–2  
**Môi trường:** 🌐 **Cloud**  
**What to do:**
- Kết nối project Vercel với repo frontend.
- Set toàn bộ environment variables trong Vercel: Supabase URL/keys, FastAPI URL, Langfuse public key.
- Deploy và verify app load được ở URL Vercel.
- Cấu hình redirect URL Supabase Auth cho production domain.
- Test login, tạo chart, và chat từ URL live.

**Deliverable:** Next.js app live trên Vercel. Full user flow chạy được từ production URL.  
**Depends on:** W7-DEPLOY-01, W5-FE-04  
**Done when:** Full user journey (đăng ký → tạo chart → chat) chạy được từ URL Vercel.

***

### W7-OBS-01 — Theo dõi Langfuse cho toàn pipeline

**When:** Tuần 7, ngày 2–3  
**Môi trường:** 🌐 **Cloud**  
**What to do:**
- Bảo đảm Langfuse trace được phát ra cho mọi request chat:
  - Root trace: toàn bộ `/chat`
  - Spans: query_rewrite, entity_extraction, graph_retrieval, dense_retrieval, sparse_retrieval, rrf_fusion, rerank, generation
  - Mỗi span phải log: input, output, model dùng (nếu có), latency.
- Kiểm tra trace hiển thị trong Langfuse dashboard.
- Tạo dashboard cơ bản cho: RPD usage, average latency, error rate.

**Deliverable:** Langfuse dashboard hiển thị trace cho tất cả request chat. Mọi pipeline span chính đều có mặt.  
**Depends on:** W7-DEPLOY-01, W4-RAG-10  
**Done when:** Gửi 3 query test từ UI production tạo ra 3 trace đầy đủ trong Langfuse.

***

### W7-OBS-02 — Đo p95 latency

**When:** Tuần 7, ngày 3  
**Môi trường:** 🌐 **Cloud**  
**What to do:**
- Gửi 20 query test qua production system (mix simple và complex).
- Ghi lại end-to-end latency của từng request.
- Tính p95 latency.
- So sánh với target: p95 end-to-end <= 8s, p95 retrieval <= 3s.
- Nếu p95 > 8s, phân tích span chậm nhất trong Langfuse và tối ưu.

**Deliverable:** Báo cáo latency: p95 end-to-end và p95 retrieval được ghi rõ. Nếu vượt target thì đã có tối ưu đầu tiên.  
**Depends on:** W7-OBS-01  
**Done when:** p95 end-to-end được đo và ghi lại. Nếu vượt ngưỡng thì có ít nhất một tối ưu đã thử.

***

### W7-QA-01 — Sprint fix bug

**When:** Tuần 7, ngày 3–5  
**Môi trường:** 💻 **Local** / 🌐 **Cloud**  
**What to do:**
- Review toàn bộ GitHub Issue mở từ W6-INT-01 và các issue phát sinh khi deploy.
- Ưu tiên: P0 (chặn core user journey), P1 (làm yếu feature chính), P2 (cosmetic/minor).
- Fix toàn bộ bug P0 và P1.
- Test lại các bug đã fix.

**Deliverable:** Tất cả bug P0 và P1 đã được fix và xác nhận. Bug P2 được ghi lại cho post-MVP backlog.  
**Depends on:** W6-INT-01, W7-DEPLOY-01, W7-DEPLOY-02  
**Done when:** Không còn P0 hoặc P1 nào mở. P2 được ghi vào “Post-MVP backlog”.

***

### W7-QA-02 — Kiểm tra cross-browser và mobile responsive

**When:** Tuần 7, ngày 4  
**Môi trường:** 🌐 **Cloud**  
**What to do:**
- Test app trên:
  - Chrome (latest)
  - Safari (latest)
  - Mobile browser (iOS Safari hoặc Android Chrome)
- Kiểm tra: layout, chart board, chat input, citation panel.
- Ghi lại mọi lỗi hiển thị.

**Deliverable:** Báo cáo test theo browser/device.  
**Depends on:** W7-DEPLOY-02  
**Done when:** App sử dụng được trên các browser đã test. Lỗi layout nghiêm trọng được mở P1 issue.

***

### W7-SEC-01 — Checklist review bảo mật

**When:** Tuần 7, ngày 4–5  
**Môi trường:** 🌐 **Cloud**  
**What to do:**
- Xác nhận RLS Supabase chặn truy cập chéo user (lặp lại test từ W1-DB-01 trên production).
- Xác nhận toàn bộ env variables được lưu trong Vercel/Render secrets, không hardcode.
- Xác nhận rate limiter FastAPI (10 req/phút) hoạt động trên production.
- Xác nhận frontend không nhận raw stack trace khi lỗi.
- Xác nhận Supabase anon key không bị dùng sai cho operation server-side (server dùng service key).

**Deliverable:** Checklist bảo mật được hoàn thành và sign off. Mọi fail phải được fix trước demo.  
**Depends on:** W7-DEPLOY-01, W7-DEPLOY-02  
**Done when:** Cả 5 mục trong checklist đều pass.

***

## Tuần 8 — Buffer, polish và chuẩn bị demo

Mục tiêu: Hệ thống ổn định, được polish, và sẵn sàng demo. Mọi work critical còn lại từ tuần 7 được hoàn thành.

***

### W8-POLISH-01 — Polish UX

**When:** Tuần 8, ngày 1–2  
**Môi trường:** 💻 **Local**  
**What to do:**
- Cải thiện empty state: dashboard không có chart, chart chưa có chat history.
- Cải thiện error message: chuyển sang tiếng Việt dễ hiểu.
- Thêm feedback thành công khi tạo chart (toast hoặc redirect message).
- Cải thiện loading state cho tất cả async actions.
- Sửa các lỗi visual nhỏ phát hiện ở W7-QA-02.

**Deliverable:** App cảm giác hoàn chỉnh và chỉn chu. Không còn rough edge ở luồng chính.  
**Depends on:** W7-QA-01  
**Done when:** Team review xác nhận UX đủ chuẩn demo.

***

### W8-DOCS-01 — Viết tài liệu cho developer

**When:** Tuần 8, ngày 1–3  
**Môi trường:** 💻 **Local**  
**What to do:**
- Viết hoặc hoàn thiện:
  - `README.md`: tổng quan dự án, cách chạy local, biến môi trường.
  - `docs/architecture.md`: mô tả kiến trúc hệ thống kèm ASCII diagram từ spec.
  - `docs/ingestion-guide.md`: cách thêm sách nguồn mới.
  - `docs/model-choices.md`: model reranker, embedding, LLM dùng trong hệ thống.
  - `docs/evaluation-guide.md`: cách chạy evaluation, cách thêm Q&A mới.

**Deliverable:** Tất cả docs được commit vào repo. README đủ để một developer mới onboard trong dưới 30 phút.  
**Depends on:** —  
**Done when:** Một thành viên không viết tài liệu đó vẫn có thể đọc và làm theo thành công.

***

### W8-EVAL-01 — Chạy evaluation cuối cùng

**When:** Tuần 8, ngày 2–3  
**Môi trường:** ☁️ **Kaggle**  
**What to do:**
- Chạy `run_eval.py` lần cuối trên production system.
- So sánh với target trong spec Section 19.3.
- Ghi lại final metric score.
- Tạo `evaluation/report_final.md`.

**Deliverable:** `evaluation/report_final.md` với metric cuối cùng cho cả 7 target.  
**Depends on:** W6-EVAL-02, W7-DEPLOY-01  
**Done when:** Report có kết quả cho toàn bộ metric. Ít nhất 5/7 metric đạt hoặc vượt target.

***

### W8-DEMO-01 — Chuẩn bị demo

**When:** Tuần 8, ngày 3–5  
**Môi trường:** 🌐 **Cloud**  
**What to do:**
- Chuẩn bị demo script cho toàn bộ user journey:
  1. Đăng ký và đăng nhập.
  2. Tạo chart Tử Vi.
  3. Xem bảng 12 cung.
  4. Hỏi 3 câu demo (1 factual, 1 interpretive, 1 multi-hop).
  5. Hiển thị citation panel.
  6. Tạo chart Bát Tự và hỏi lại một câu.
- Chạy thử demo script ít nhất 2 lần từ đầu đến cuối.
- Chuẩn bị 2–3 câu hỏi dự phòng nếu query live bị lỗi.
- Đảm bảo demo account đã có sẵn chart để tránh phụ thuộc vào việc tạo chart live.

**Deliverable:** Demo script được ghi lại. Demo account có chart sẵn. Team đã rehearsal ít nhất một lần.  
**Depends on:** W8-POLISH-01  
**Done when:** Demo hoàn chỉnh chạy được end-to-end trong một lần dry run mà không lỗi.

***

## Danh sách deliverables

| ID | Deliverable | Tuần |
|----|-------------|------|
| D-01 | Tất cả cloud services được provision, `.env.example` được commit | W1 |
| D-02 | Supabase schema, RLS, và seed script được áp dụng | W1 |
| D-03 | Neo4j constraint, vector index, fulltext index được tạo | W1 |
| D-04 | Supabase Auth hoạt động trong Next.js | W1 |
| D-05 | FastAPI skeleton chạy với cấu hình Render | W1 |
| D-06 | Next.js app shell với đầy đủ routes và placeholder components | W1 |
| D-07 | Tử Vi engine được tích hợp và test | W2 |
| D-08 | Bát Tự engine được tích hợp | W2 |
| D-09 | Luồng tạo và lưu chart end-to-end | W2 |
| D-10 | TuViBoard và BatuBoard hiển thị dữ liệu thật | W2 |
| D-11 | Dashboard hiển thị chart đã lưu | W2 |
| D-12 | PDF extraction và normalization script | W3 |
| D-13 | Chunking parent-child có metadata | W3 |
| D-14 | Entity extraction script và prompt template | W3 |
| D-15 | Script ghi graph (dedup + MERGE) | W3 |
| D-16 | Embedding pipeline + vector index được populate | W3 |
| D-17 | Provenance lưu trong Supabase `source_chunks` | W3 |
| D-18 | 3–4 sách được ingest đầy đủ, có ingestion report | W3 |
| D-19 | Incremental ingestion hoạt động | W3 |
| D-20 | LangGraph node graph được compile | W4 |
| D-21 | Query rewrite node + prompt template | W4 |
| D-22 | Entity extraction node runtime | W4 |
| D-23 | Graph retrieval node (Cypher) | W4 |
| D-24 | Dense retrieval node (vector) | W4 |
| D-25 | Sparse retrieval node (BM25/fulltext) | W4 |
| D-26 | RRF fusion node | W4 |
| D-27 | Cross-encoder reranker node | W4 |
| D-28 | Context assembly với token budget | W4 |
| D-29 | Generation node + Langfuse trace | W4 |
| D-30 | Citation mapping node | W4 |
| D-31 | FastAPI `/chat` endpoint hoàn chỉnh | W4 |
| D-32 | Next.js chat proxy nối tới FastAPI | W5 |
| D-33 | Chat UI đầy đủ với lưu lịch sử | W5 |
| D-34 | Citation panel trong UI | W5 |
| D-35 | Trang chi tiết chart hoàn chỉnh | W5 |
| D-36 | Auto-create chat session khi mở chart lần đầu | W5 |
| D-37 | Context windowing + summary generation | W5 |
| D-38 | Error handling + rate limiting | W5 |
| D-39 | Golden evaluation dataset (50–100 entry) | W6 |
| D-40 | Evaluation runner script + kết quả | W6 |
| D-41 | Evaluation report v1 với phân tích lỗi | W6 |
| D-42 | Vòng tuning và metric được cải thiện | W6 |
| D-43 | Integration test report end-to-end | W6 |
| D-44 | Backend FastAPI deploy lên Render | W7 |
| D-45 | Frontend Next.js deploy lên Vercel | W7 |
| D-46 | Langfuse trace live cho mọi request | W7 |
| D-47 | p95 latency được đo và ghi lại | W7 |
| D-48 | Tất cả bug P0/P1 được fix | W7 |
| D-49 | Checklist bảo mật hoàn tất | W7 |
| D-50 | UX polish hoàn tất | W8 |
| D-51 | Tài liệu developer hoàn tất | W8 |
| D-52 | Báo cáo evaluation cuối cùng | W8 |
| D-53 | Demo script và rehearsal demo | W8 |

## Cách chạy hệ thống

### Chạy local trên laptop

Dùng cách này cho toàn bộ phần phát triển thường ngày: frontend, backend, auth, chart engine, và RAG graph. Máy không cần GPU, vì các model lớn đều gọi qua API ngoài, còn cross-encoder reranker có thể chạy CPU trong quá trình dev. [sbert](https://sbert.net/docs/cross_encoder/usage/efficiency.html)

1. Khởi động các dịch vụ cloud trước: Supabase, Neo4j AuraDB, Langfuse, Render, và Vercel theo biến môi trường trong `.env.example`.
2. Chạy backend FastAPI local bằng `uvicorn`.
3. Chạy frontend Next.js local bằng `npm run dev`.
4. Kiểm tra `/health`, đăng nhập, tạo chart, rồi vào `/chart/[id]` để test chat.
5. Nếu cần test ingestion nhỏ, chạy từng script local trên một file PDF mẫu trước khi đưa lên Kaggle.

### Chạy trên Kaggle Free Tier

Dùng Kaggle cho các công việc nặng, đặc biệt là ingest hàng loạt và evaluation nhiều mẫu. Kaggle Free Tier hiện có T4 GPU, 29GB RAM và 4 CPU cores, phù hợp để tăng tốc embedding, rerank, và chạy batch pipeline. [lilys](https://lilys.ai/notes/en/google-tpu-20251128/free-kaggle-gpu-29gb-4-cpu-update)

1. Chỉ đẩy các task nặng lên Kaggle: `W3-INGEST-03` đến `W3-INGEST-07`, `W6-EVAL-03`, `W6-EVAL-04`, và `W8-EVAL-01`.
2. Chuẩn bị sẵn file input từ local: chunk JSON, entity JSON, hoặc evaluation dataset JSON.
3. Chạy notebook Kaggle theo từng bước của pipeline, rồi ghi kết quả về Neo4j và Supabase qua secret keys.
4. Sau khi ingest xong, quay lại local để chạy app và xác minh dữ liệu đã có thể truy vấn được.
5. Không dùng Kaggle để host app hay database; Kaggle chỉ nên là nơi xử lý batch, không phải nơi chạy hệ thống live. [reddit](https://www.reddit.com/r/LocalLLaMA/comments/17bhwtj/kaggle_upgraded_their_free_tier_to_t4_with_29gb/)

### Cách phối hợp giữa local và Kaggle

- Local là nơi viết code, test nhanh, và nối frontend-backend.
- Kaggle là nơi xử lý batch nặng, rồi đẩy kết quả về cloud DB.
- Supabase và Neo4j phải là nơi lưu trữ trung tâm để cả local lẫn Kaggle cùng đọc/ghi được.
- Sau mỗi lần chạy Kaggle, hãy sync lại state vào Neo4j/Supabase rồi kiểm tra lại bằng app local.
- Khi deploy xong, production vẫn chạy trên Render + Vercel; Kaggle chỉ còn dùng cho ingestion hoặc evaluation lại khi cần. [lilys](https://lilys.ai/notes/en/google-tpu-20251128/free-kaggle-gpu-29gb-4-cpu-update)

### Quy trình khuyến nghị

1. Xây và test code local.
2. Chạy ingestion nhỏ local để kiểm tra logic.
3. Chuyển batch lớn sang Kaggle.
4. Đồng bộ kết quả vào Neo4j và Supabase.
5. Chạy lại app local để xác minh.
6. Deploy production lên Render và Vercel.