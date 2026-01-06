"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Mail, Grid3x3, ArrowLeft } from "lucide-react";
import { useAuthStore } from "../../stores/authStore";
import { toast } from "sonner";

export default function ResendVerificationPage() {
  const router = useRouter();
  const { resendVerification, resendVerificationLoading } = useAuthStore();

  const [email, setEmail] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();

    if (!email) {
      toast.error("Please enter your email address.");
      return;
    }

    try {
      await resendVerification(email);
      toast.success("Verification email sent! Please check your inbox.");
      router.push("/login");
    } catch (err) {
      toast.error(err.message || "Failed to send verification email. Please try again.");
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="max-w-md w-full mx-4">
        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
            <Mail className="w-8 h-8 text-primary" />
          </div>

          <h1 className="text-2xl font-semibold text-foreground mb-4">
            Resend Verification Email
          </h1>

          <p className="text-muted-foreground">
            Enter your email address to receive a new verification link.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-foreground mb-2">
              Email Address
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full h-11 px-3 bg-background border border-border rounded-md text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="Enter your email"
              required
            />
          </div>

          <button
            type="submit"
            disabled={resendVerificationLoading}
            className="w-full h-11 bg-primary text-primary-foreground text-sm font-medium rounded-md hover:bg-primary/90 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {resendVerificationLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin"></div>
                Sending...
              </>
            ) : (
              <>
                <Mail className="w-4 h-4" />
                Send Verification Email
              </>
            )}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => router.push("/login")}
            className="text-sm text-muted-foreground hover:text-foreground transition flex items-center justify-center gap-1 mx-auto"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Login
          </button>
        </div>
      </div>
    </div>
  );
}
