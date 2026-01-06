/* eslint-disable react-hooks/exhaustive-deps */
"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuthStore } from "../../stores/authStore";
import { toast } from "sonner";
import { Grid3x3, CheckCircle, XCircle, Loader2 } from "lucide-react";

export default function VerifyEmailPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { verifyEmail, verifyEmailMessage, checkAuth } = useAuthStore();

  const token = searchParams.get("token");
  const [status, setStatus] = useState(token ? "loading" : "error");

  useEffect(() => {
    if (!token) {
      toast.error("Invalid verification link. No token provided.");
      return;
    }

    const performVerification = async () => {
      try {
        await verifyEmail(token);
        setStatus("success");
        toast.success(verifyEmailMessage || "Email verified successfully! Redirecting to dashboard.");
        // Check auth to set user state
        await checkAuth();
        // Redirect to dashboard
        setTimeout(() => {
          router.push("/dashboard");
        }, 3000);
      } catch (err) {
        setStatus("error");
        toast.error(err.message || "Email verification failed. Please try again.");
      }
    };

    performVerification();
  }, [token, verifyEmail, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="max-w-md w-full mx-4">
        <div className="text-center">
          <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
            <Grid3x3 className="w-8 h-8 text-primary" />
          </div>

          <h1 className="text-2xl font-semibold text-foreground mb-4">
            Email Verification
          </h1>

          {status === "loading" && (
            <div className="space-y-4">
              <Loader2 className="w-8 h-8 animate-spin mx-auto text-primary" />
              <p className="text-muted-foreground">
                Verifying your email address...
              </p>
            </div>
          )}

          {status === "success" && (
            <div className="space-y-4">
              <CheckCircle className="w-12 h-12 text-green-500 mx-auto" />
              <div>
                <h2 className="text-lg font-medium text-foreground mb-2">
                  Email Verified!
                </h2>
                <p className="text-muted-foreground">
                  Your email has been successfully verified. You will be redirected to the dashboard shortly.
                </p>
              </div>
            </div>
          )}

          {status === "error" && (
            <div className="space-y-4">
              <XCircle className="w-12 h-12 text-destructive mx-auto" />
              <div>
                <h2 className="text-lg font-medium text-foreground mb-2">
                  Verification Failed
                </h2>
                <p className="text-muted-foreground mb-4">
                  We could not verify your email. The link may be expired or invalid.
                </p>
                <button
                  onClick={() => router.push("/login")}
                  className="w-full h-11 bg-primary text-primary-foreground text-sm font-medium rounded-md hover:bg-primary/90 transition"
                >
                  Go to Login
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
