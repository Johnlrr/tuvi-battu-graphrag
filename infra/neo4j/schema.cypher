// Neo4j schema setup for TuVi/BatTu GraphRAG

CREATE CONSTRAINT chunk_hash_unique IF NOT EXISTS
FOR (c:Chunk)
REQUIRE c.chunk_hash IS UNIQUE;

CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS
FOR (c:Chunk)
REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT sao_canonical_unique IF NOT EXISTS
FOR (s:Sao)
REQUIRE s.canonical_name IS UNIQUE;

CREATE CONSTRAINT cung_canonical_unique IF NOT EXISTS
FOR (c:Cung)
REQUIRE c.canonical_name IS UNIQUE;

CREATE CONSTRAINT thien_can_canonical_unique IF NOT EXISTS
FOR (t:ThienCan)
REQUIRE t.canonical_name IS UNIQUE;

CREATE CONSTRAINT dia_chi_canonical_unique IF NOT EXISTS
FOR (d:DiaChi)
REQUIRE d.canonical_name IS UNIQUE;

CREATE CONSTRAINT ngu_hanh_canonical_unique IF NOT EXISTS
FOR (n:NguHanh)
REQUIRE n.canonical_name IS UNIQUE;

CREATE VECTOR INDEX chunkVector IF NOT EXISTS
FOR (c:Chunk) ON (c.embedding)
OPTIONS {indexConfig: {`vector.dimensions`: 768, `vector.similarity_function`: 'cosine'}};

CREATE FULLTEXT INDEX chunkFulltext IF NOT EXISTS
FOR (c:Chunk) ON EACH [c.text, c.title, c.keywords];
