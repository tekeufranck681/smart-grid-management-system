"use client";

import { useRouter } from "next/navigation";
import {  Mail, Home, LogIn } from "lucide-react";

export default function VerifyEmailPendingPage() {
  const router = useRouter();



  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="max-w-md w-full mx-4">
        <div className="text-center">
          <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
            <Mail className="w-8 h-8 text-primary" />
          </div>

          <h1 className="text-2xl font-semibold text-foreground mb-4">
            Email Verification Required
          </h1>

          <p className="text-muted-foreground mb-6">
            We&apos;ve sent a verification link to your email address. Please check your inbox and click the link to verify your account before accessing the dashboard.
          </p>

          <div className="space-y-3">
            <button
              onClick={() => router.push("/")}
              className="w-full h-11 bg-secondary text-secondary-foreground text-sm font-medium rounded-md hover:bg-secondary/80 transition flex items-center justify-center gap-2"
            >
              <Home className="w-4 h-4" />
              Go to Home
            </button>

            <button
              onClick={() => router.push("/login")}
              className="w-full h-11 bg-primary text-primary-foreground text-sm font-medium rounded-md hover:bg-primary/90 transition flex items-center justify-center gap-2"
            >
              <LogIn className="w-4 h-4" />
              Login
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
