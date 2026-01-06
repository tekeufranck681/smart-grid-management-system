"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Lock, Grid3x3, Eye, EyeOff } from "lucide-react";
import { useAuthStore } from "../../stores/authStore";
import { toast } from "sonner";

export default function ResetPasswordPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { resetPassword, resetPasswordLoading } = useAuthStore();

  const [form, setForm] = useState({
    token: "",
    new_password: "",
    confirm_password: "",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  useEffect(() => {
    const token = searchParams.get("token");
    if (token) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setForm(prev => ({ ...prev, token }));
    } else {
      toast.error("Invalid reset link. No token provided.");
      router.push("/login");
    }
  }, [searchParams, router]);

  function updateField(e) {
    const { name, value } = e.target;
    setForm(prev => ({
      ...prev,
      [name]: value,
    }));
  }

  async function handleSubmit(e) {
    e.preventDefault();

    if (!form.new_password || !form.confirm_password) {
      toast.error("Please fill in all fields.");
      return;
    }

    if (form.new_password !== form.confirm_password) {
      toast.error("Passwords do not match.");
      return;
    }

    if (form.new_password.length < 6) {
      toast.error("Password must be at least 6 characters.");
      return;
    }

    try {
      await resetPassword({ token: form.token, new_password: form.new_password });
      toast.success("Password reset successful! You can now log in.");
      router.push("/login");
    } catch (err) {
      toast.error(err.message || "Failed to reset password. Please try again.");
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="max-w-md w-full mx-4">
        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
            <Lock className="w-8 h-8 text-primary" />
          </div>

          <h1 className="text-2xl font-semibold text-foreground mb-4">
            Reset Password
          </h1>

          <p className="text-muted-foreground">
            Enter your new password below.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="new_password" className="block text-sm font-medium text-foreground mb-2">
              New Password
            </label>
            <div className="relative">
              <input
                id="new_password"
                name="new_password"
                type={showPassword ? "text" : "password"}
                value={form.new_password}
                onChange={updateField}
                className="w-full h-11 px-3 pr-10 bg-background border border-border rounded-md text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                placeholder="Enter new password"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <div>
            <label htmlFor="confirm_password" className="block text-sm font-medium text-foreground mb-2">
              Confirm New Password
            </label>
            <div className="relative">
              <input
                id="confirm_password"
                name="confirm_password"
                type={showConfirmPassword ? "text" : "password"}
                value={form.confirm_password}
                onChange={updateField}
                className="w-full h-11 px-3 pr-10 bg-background border border-border rounded-md text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                placeholder="Confirm new password"
                required
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={resetPasswordLoading}
            className="w-full h-11 bg-primary text-primary-foreground text-sm font-medium rounded-md hover:bg-primary/90 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {resetPasswordLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin"></div>
                Resetting...
              </>
            ) : (
              <>
                <Lock className="w-4 h-4" />
                Reset Password
              </>
            )}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => router.push("/login")}
            className="text-sm text-muted-foreground hover:text-foreground transition"
          >
            Back to Login
          </button>
        </div>
      </div>
    </div>
  );
}
