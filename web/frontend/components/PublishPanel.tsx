"use client";

import { useEffect, useRef, useState } from "react";
import {
  LoginChallenge,
  PlatformStatus,
  getPlatforms,
  loginStatus,
  logoutPlatform,
  publishTo,
  startLogin,
} from "@/lib/api";

// 任务成稿后的「发布到各平台」面板。
export default function PublishPanel({ jobId }: { jobId: string }) {
  const [platforms, setPlatforms] = useState<PlatformStatus[]>([]);
  const [qr, setQr] = useState<{ platform: string; ch: LoginChallenge } | null>(null);
  const [busy, setBusy] = useState<string>("");
  const [msg, setMsg] = useState<Record<string, string>>({});
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  async function refresh() {
    try {
      setPlatforms(await getPlatforms());
    } catch {
      /* ignore */
    }
  }
  useEffect(() => {
    refresh();
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  function setPlatMsg(id: string, text: string) {
    setMsg((m) => ({ ...m, [id]: text }));
  }

  async function onLogin(platform: string) {
    setBusy(platform);
    setPlatMsg(platform, "");
    try {
      const ch = await startLogin(platform);
      setQr({ platform, ch });
      // 轮询登录状态
      if (pollRef.current) clearInterval(pollRef.current);
      pollRef.current = setInterval(async () => {
        try {
          const st = await loginStatus(platform);
          if (st.logged_in) {
            if (pollRef.current) clearInterval(pollRef.current);
            setQr(null);
            setPlatMsg(platform, `已登录${st.user_name ? "：" + st.user_name : ""} ✓`);
            refresh();
          }
        } catch {
          /* keep polling */
        }
      }, 2500);
    } catch (e) {
      setPlatMsg(platform, "登录失败：" + String(e));
    } finally {
      setBusy("");
    }
  }

  async function onLogout(platform: string) {
    await logoutPlatform(platform);
    setPlatMsg(platform, "已登出");
    refresh();
  }

  async function onPublish(platform: string) {
    setBusy(platform);
    setPlatMsg(platform, "");
    try {
      const r = await publishTo(platform, { job_id: jobId });
      setPlatMsg(
        platform,
        r.ok ? `发布成功 ✓ ${r.url || ""}` : `发布失败：${r.detail}`
      );
    } catch (e) {
      setPlatMsg(platform, "发布失败：" + String(e));
    } finally {
      setBusy("");
    }
  }

  return (
    <div style={{ marginTop: 18, borderTop: "1px solid var(--border)", paddingTop: 16 }}>
      <h2 style={{ marginBottom: 12 }}>发布到平台</h2>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {platforms.map((p) => (
          <div
            key={p.id}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              flexWrap: "wrap",
              background: "var(--panel-2)",
              border: "1px solid var(--border)",
              borderRadius: 8,
              padding: "10px 14px",
            }}
          >
            <strong style={{ minWidth: 90 }}>{p.label}</strong>
            {!p.available ? (
              <span className="badge">未开放</span>
            ) : p.logged_in ? (
              <span className="badge done">
                已登录{p.user_name ? "：" + p.user_name : ""}
              </span>
            ) : (
              <span className="badge">未登录</span>
            )}

            <span style={{ flex: 1, color: "var(--muted)", fontSize: 12 }}>
              {msg[p.id] || p.note}
            </span>

            {p.available && p.login_kind === "qrcode" && !p.logged_in && (
              <button
                className="btn secondary"
                disabled={busy === p.id}
                onClick={() => onLogin(p.id)}
              >
                {busy === p.id ? "…" : "扫码登录"}
              </button>
            )}
            {p.available && p.logged_in && p.login_kind === "qrcode" && (
              <button className="btn danger" onClick={() => onLogout(p.id)}>
                登出
              </button>
            )}
            {p.available && p.id !== "wechat" && (
              <button
                className="btn"
                disabled={busy === p.id || !p.logged_in}
                onClick={() => onPublish(p.id)}
              >
                发布
              </button>
            )}
            {p.id === "wechat" && (
              <span style={{ fontSize: 12, color: "var(--muted)" }}>
                （创建任务时勾选「推送草稿箱」由管道发布）
              </span>
            )}
          </div>
        ))}
      </div>

      {qr && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.6)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 50,
          }}
          onClick={() => setQr(null)}
        >
          <div
            className="panel"
            style={{ maxWidth: 320, textAlign: "center" }}
            onClick={(e) => e.stopPropagation()}
          >
            <h2>扫码登录 · {qr.platform}</h2>
            {qr.ch.qrcode_image ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={qr.ch.qrcode_image}
                alt="二维码"
                style={{ width: 220, height: 220, background: "#fff", borderRadius: 8 }}
              />
            ) : (
              <p className="hint">未返回二维码：{qr.ch.detail}</p>
            )}
            <p className="hint">{qr.ch.detail}</p>
            <button className="btn secondary" onClick={() => setQr(null)}>
              关闭
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
