// app/providers.jsx
"use client";

import { useEffect } from "react";
import { Toaster } from "sonner";
import { useAuthStore } from "@/stores/authStore";

export default function Providers({ children }) {
  const checkAuth = useAuthStore((s) => s.checkAuth);

  useEffect(() => {
    checkAuth(); // silent auth + refresh on first load
  }, [checkAuth]);

  return (
    <>
      {children}
      <Toaster />
    </>
  );
}
