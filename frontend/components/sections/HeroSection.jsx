"use client";

import Link from "next/link";
import { ArrowRight, Play, Shield, Network, Database, TrendingDown } from "lucide-react";
import CountUp from "react-countup";

export default function HeroSection() {
  return (
    <section className="relative pt-32 pb-24">
      <div className="mx-auto max-w-5xl px-4 text-center">
        <span className="inline-block mb-6 rounded-full bg-primary/10 px-4 py-1 text-sm font-medium text-primary">
          Next-generation grid management for Cameroon
        </span>

        <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
          Intelligent Power Grid
          <br />
          <span className="text-primary">Management Platform</span>
        </h1>

        <p className="mt-6 max-w-2xl mx-auto text-lg text-muted-foreground">
          Monitor, analyze, and optimize power distribution using real-time
          data, predictive analytics, and simulation tools built for modern
          utilities.
        </p>

        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            href="/signup"
            className="inline-flex items-center gap-2 rounded-md bg-primary px-6 py-3 text-primary-foreground hover:bg-primary/90"
          >
            Start free trial
            <ArrowRight size={18} />
          </Link>

          <Link
            href="/demo"
            className="inline-flex items-center gap-2 rounded-md border px-6 py-3 text-foreground hover:bg-muted"
          >
            <Play size={18} />
            Watch demo
          </Link>
        </div>

        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-6">
          {[
            { end: 99.9, suffix: "%", label: "Uptime", icon: Shield, color: "text-primary" },
            { end: 50, suffix: "+", label: "Networks", icon: Network, color: "text-primary" },
            { end: 2, suffix: "M+", label: "Data points/day", icon: Database, color: "text-primary" },
            { end: 40, suffix: "%", label: "Cost reduction", icon: TrendingDown, color: "text-primary" },
          ].map((item) => (
            <div key={item.label} className="group relative overflow-hidden rounded-xl border bg-gradient-to-br from-card to-card/50 p-6 shadow-sm transition-all duration-300 hover:shadow-lg hover:scale-105 hover:border-primary/50">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <div className="relative">
                <item.icon className={`mb-3 h-8 w-8 ${item.color}`} />
                <div className="text-3xl font-bold text-foreground">
                  <CountUp
                    end={item.end}
                    duration={2.5}
                    suffix={item.suffix}
                    prefix={item.prefix}
                    decimals={item.end % 1 !== 0 ? 1 : 0}
                    separator=","
                  />
                </div>
                <div className="text-sm text-muted-foreground font-medium">
                  {item.label}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
