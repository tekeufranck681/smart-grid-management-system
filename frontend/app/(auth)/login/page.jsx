"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Eye, EyeOff, Mail, Lock, Grid3x3 } from "lucide-react";
import { useAuthStore } from "../../../stores/authStore";
import { toast } from "sonner";

export default function LoginPage() {
  const router = useRouter();
  const { login, loginLoading, error, clearError } = useAuthStore();

  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [showPassword, setShowPassword] = useState(false);

  function updateField(e) {
    const { name, value, type, checked } = e.target;
    setForm(prev => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    clearError();

    try {
      const user = await login(form);
      toast.success("Login successful, Welcome to SmartGrid!");
      if (user.email_verified) {
        router.push("/dashboard");
      } else {
        router.push("/verify-email-pending");
      }
    } catch (err) {
      if (err.status === 403) {
        router.push("/resend-verification");
      } else {
        toast.error(err.message || "Login failed. Please check your credentials.");
      }
    }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Left - Info */}
      <div className="hidden lg:flex items-center justify-center bg-gradient-to-br from-primary/5 via-primary/10 to-accent/5 relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute top-10 left-10 w-32 h-32 bg-primary/10 rounded-full blur-xl"></div>
          <div className="absolute bottom-10 right-10 w-40 h-40 bg-accent/10 rounded-full blur-xl"></div>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-primary/5 rounded-full blur-2xl"></div>
        </div>
        <div className="relative max-w-md text-center px-10">
          <div className="w-20 h-20 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <Grid3x3 className="w-10 h-10 text-primary" />
          </div>
          <h2 className="text-3xl font-semibold text-foreground">
            Smart grid operations,
            <br /> simplified
          </h2>
          <p className="mt-4 text-muted-foreground">
            Real-time monitoring, forecasting, and optimization — built for scale.
          </p>
          <div className="mt-8 grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-primary">99.9%</div>
              <div className="text-xs text-muted-foreground">Uptime</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-primary">24/7</div>
              <div className="text-xs text-muted-foreground">Monitoring</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-primary">1.2s</div>
              <div className="text-xs text-muted-foreground">Response</div>
            </div>
          </div>
        </div>
      </div>

      {/* Right - Form */}
      <div className="flex items-center justify-center px-6">
        <div className="w-full max-w-sm">
          <header className="mb-10">
            <Link href="/" className="flex items-center text-lg font-semibold tracking-tight">
              <div className="w-8 h-8 rounded-md bg-primary/10 flex items-center justify-center">
                <Grid3x3 className="w-5 h-5 text-primary" />
              </div>
              Smart<span className="text-primary">Grid</span>
            </Link>

            <h1 className="mt-6 text-2xl font-semibold text-foreground">
              Sign in to your account
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Manage and monitor your grid infrastructure
            </p>
          </header>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input
                  name="email"
                  type="email"
                  required
                  value={form.email}
                  onChange={updateField}
                  className="w-full h-11 pl-10 pr-3 border border-input bg-background rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <div className="flex justify-between mb-1">
                <label className="text-sm font-medium text-foreground">Password</label>
                <Link
                  href="/forgot-password"
                  className="text-xs text-primary hover:text-primary/80 hover:underline"
                >
                  Forgot?
                </Link>
              </div>

              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input
                  name="password"
                  type={showPassword ? "text" : "password"}
                  required
                  value={form.password}
                  onChange={updateField}
                  className="w-full h-11 pl-10 pr-10 border border-input bg-background rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(v => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loginLoading}
              className="w-full h-11 bg-primary text-primary-foreground text-sm font-medium rounded-md hover:bg-primary/90 transition disabled:opacity-60"
            >
              {loginLoading ? "Signing in…" : "Sign in"}
            </button>
          </form>

          <div className="mt-4 text-center">
            <Link href="/forgot-password" className="text-sm text-muted-foreground hover:text-foreground underline">
              Forgot your password?
            </Link>
          </div>

          <p className="mt-8 text-center text-sm text-muted-foreground">
            No account?{" "}
            <Link href="/register" className="font-medium text-primary hover:text-primary/80 underline">
              Create one
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
