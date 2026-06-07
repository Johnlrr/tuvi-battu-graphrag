import Link from "next/link";

export default function Home() {
  return (
    <main>
      <h1>TuVi / BaTu GraphRAG</h1>
      <p>Chào mừng bạn đến với hệ thống MVP tư vấn Tử Vi và Bát Tự.</p>
      <p>
        <Link href="/login">Đăng nhập</Link> hoặc <Link href="/register">Đăng ký</Link> để tiếp tục.
      </p>
    </main>
  );
}
