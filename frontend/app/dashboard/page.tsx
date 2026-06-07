"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "../../lib/supabaseClient";

export default function DashboardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [userEmail, setUserEmail] = useState<string | null>(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      if (!data.session) {
        router.push("/login");
        return;
      }
      setUserEmail(data.session.user.email || null);
      setLoading(false);
    });
  }, [router]);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.push("/login");
  };

  if (loading) {
    return <main>Đang tải dữ liệu người dùng...</main>;
  }

  return (
    <main>
      <h1>Dashboard</h1>
      <p>Xin chào, {userEmail ?? "Người dùng"}.</p>
      <button onClick={handleLogout}>Đăng xuất</button>
      <div>
        <h2>Chart sample</h2>
        <p>Trang chart cơ bản chưa có nội dung đầy đủ.</p>
        <a href="/chart/00000000-0000-0000-0000-000000000010">Xem chart ví dụ</a>
      </div>
    </main>
  );
}
