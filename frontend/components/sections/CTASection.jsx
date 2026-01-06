import Link from "next/link";
import { ArrowRight, CheckCircle2 } from "lucide-react";

const BENEFITS = [
  "14-day free trial",
  "Full feature access",
  "Onboarding support",
  "Cancel anytime",
];

export default function CTASection() {
  return (
    <section className="py-24 border-t">
      <div className="mx-auto max-w-4xl px-4 text-center">
        <h2 className="text-3xl md:text-5xl font-bold">
          Ready to modernize your
          <span className="text-primary"> grid operations</span>?
        </h2>

        <p className="mt-6 text-lg text-muted-foreground">
          Join utility teams already improving reliability and reducing
          operational costs with SmartGrid.
        </p>

        <div className="mt-8 flex flex-wrap justify-center gap-4">
          {BENEFITS.map((item) => (
            <div
              key={item}
              className="flex items-center gap-2 rounded-md border px-4 py-2 text-sm"
            >
              <CheckCircle2 size={16} className="text-primary" />
              {item}
            </div>
          ))}
        </div>

        <div className="mt-10 flex flex-col sm:flex-row justify-center gap-4">
          <Link
            href="/signup"
            className="inline-flex items-center gap-2 rounded-md bg-primary px-6 py-3 text-primary-foreground hover:bg-primary/90"
          >
            Start trial
            <ArrowRight size={18} />
          </Link>

          <Link
            href="/register"
            className="inline-flex items-center rounded-md border px-6 py-3 hover:bg-muted"
          >
            New to SmartGrid
          </Link>
        </div>
      </div>
    </section>
  );
}
