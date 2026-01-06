"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Eye, EyeOff, Mail, Lock, Grid3x3 } from "lucide-react";
import { useAuthStore } from "../../../stores/authStore";
import { toast } from "sonner";

export default function RegisterPage() {
  const router = useRouter();
  const { register, registerLoading, registerMessage, clearError } = useAuthStore();

  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [showPassword, setShowPassword] = useState(false);

  function updateField(e) {
    const { name, value } = e.target;
    setForm(prev => ({
      ...prev,
      [name]: value,
    }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    clearError();

    try {
      await register(form);
      toast.success(registerMessage || "Registration successful! Please verify your email.");
      router.push("/verify-email-pending");
    } catch (err) {
      toast.error(err.message || "Registration failed. Please try again.");
    }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Left */}
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
              Create your account
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Join thousands of utilities managing their grids
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
                  placeholder="you@company.com"
                  className="w-full h-11 pl-10 pr-3 border border-input bg-background rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input
                  name="password"
                  type={showPassword ? "text" : "password"}
                  required
                  value={form.password}
                  onChange={updateField}
                  placeholder="••••••••"
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
              disabled={registerLoading}
              className="w-full h-11 bg-primary text-primary-foreground text-sm font-medium rounded-md hover:bg-primary/90 transition disabled:opacity-60"
            >
              {registerLoading ? "Creating account…" : "Create account"}
            </button>
          </form>

          <p className="mt-8 text-center text-sm text-muted-foreground">
            Already have an account?{" "}
            <Link href="/login" className="font-medium text-primary hover:text-primary/80 underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>

      {/* Right */}
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
            Power your grid
            <br /> with intelligence
          </h2>
          <p className="mt-4 text-muted-foreground">
            Join leading utilities in Cameroon and beyond with our comprehensive grid management platform.
          </p>
          <div className="mt-8 grid grid-cols-2 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-primary">50+</div>
              <div className="text-xs text-muted-foreground">Utilities</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-primary">2M+</div>
              <div className="text-xs text-muted-foreground">Data Points</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
