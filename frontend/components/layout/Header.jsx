"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, X, Grid3x3 } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/cn";

const NAV_ITEMS = [
  { label: "Home", href: "/" },
  { label: "Features", href: "/#features" },
  { label: "About", href: "/#about" },
  { label: "Demo", href: "/demo" },
];

export default function Header() {
  const pathname = usePathname();
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 16);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={cn(
        "fixed top-0 inset-x-0 z-50 transition-all",
        scrolled
          ? "bg-background/80 backdrop-blur border-b"
          : "bg-transparent"
      )}
    >
      <div className="mx-auto max-w-7xl px-4 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 font-semibold tracking-tight">
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            whileHover={{ scale: 1.1, rotate: 5 }}
            className="p-1 rounded-md bg-primary/10"
          >
            <Grid3x3 className="h-6 w-6 text-primary" />
          </motion.div>
          <span>
            Smart<span className="text-primary">Grid</span>
          </span>
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden md:flex gap-6 text-sm">
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="relative px-3 py-2 rounded-md transition-all text-muted-foreground hover:text-foreground group"
            >
              {item.label}
              <span className="absolute bottom-0 left-0 h-0.5 bg-primary transition-all duration-300 ease-out w-0 group-hover:w-full" />
            </Link>
          ))}
        </nav>

        {/* Actions */}
        <div className="hidden md:flex items-center gap-4">
          <Link
            href="/login"
            className="rounded-md border border-border px-4 py-2 text-sm text-foreground hover:bg-muted hover:border-primary/50 transition-colors"
          >
            Sign in
          </Link>
          <Link
            href="/signup"
            className="rounded-md bg-gradient-to-r from-primary to-primary/90 px-4 py-2 text-sm text-primary-foreground hover:from-primary/90 hover:to-primary/80 shadow-sm hover:shadow-md transition-all"
          >
            Get started
          </Link>
        </div>

        {/* Mobile Toggle */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="md:hidden"
          aria-label="Toggle menu"
        >
          {mobileOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile Menu */}
      {mobileOpen && (
        <div className="md:hidden border-t bg-background">
          <nav className="flex flex-col gap-4 px-4 py-6 text-sm">
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileOpen(false)}
                className="text-muted-foreground hover:text-foreground"
              >
                {item.label}
              </Link>
            ))}
            <Link href="/login" onClick={() => setMobileOpen(false)} className="rounded-md border border-border py-2 text-center text-foreground hover:bg-muted hover:border-primary/50 transition-colors">
              Sign in
            </Link>
            <Link
              href="/signup"
              onClick={() => setMobileOpen(false)}
              className="rounded-md bg-gradient-to-r from-primary to-primary/90 py-2 text-center text-primary-foreground  hover:from-primary/90 hover:to-primary/80 shadow-sm hover:shadow-md transition-all"
            >
              Get started
            </Link>
          </nav>
        </div>
      )}
    </header>
  );
}
