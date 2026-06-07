"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { supabase } from "../../../lib/supabaseClient";

export default function ChartDetailPage() {
  const params = useParams();
  const chartId = params?.id ?? "";
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [sessionEmail, setSessionEmail] = useState<string | null>(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      if (!data.session) {
        router.push("/login");
        return;
      }
      setSessionEmail(data.session.user.email || null);
      setLoading(false);
    });
  }, [router]);

  if (loading) {
    return <main>Đang tải chart...</main>;
  }

  return (
    <main>
      <h1>Chart Detail</h1>
      <p>Chart ID: {chartId}</p>
      <p>Người dùng: {sessionEmail}</p>
      <p>Phần giao diện chart và chat sẽ được bổ sung tiếp theo.</p>
    </main>
  );
}
