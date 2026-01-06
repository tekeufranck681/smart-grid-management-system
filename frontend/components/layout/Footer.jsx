import Link from "next/link";

const FOOTER_LINKS = {
  product: [
    { label: "Features", href: "/#features" },
    { label: "Demo", href: "/demo" },
    { label: "API Docs", href: "/docs" },
  ],
  company: [
    { label: "About", href: "/#about" },
    { label: "Blog", href: "/blog" },
    { label: "Contact", href: "/contact" },
  ],
  legal: [
    { label: "Privacy", href: "/privacy" },
    { label: "Terms", href: "/terms" },
  ],
};

export default function Footer() {
  return (
    <footer className="border-t bg-background">
      <div className="mx-auto max-w-7xl px-4 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10">
          {/* Brand */}
          <div className="md:col-span-2">
            <div className="font-semibold text-lg">
              Smart<span className="text-primary">Grid</span>
            </div>
            <p className="mt-4 max-w-sm text-sm text-muted-foreground">
              Intelligent grid management solutions built for utility engineers
              and energy operators across Cameroon.
            </p>
          </div>

          {/* Links */}
          {Object.entries(FOOTER_LINKS).map(([title, links]) => (
            <div key={title}>
              <h4 className="mb-4 font-medium capitalize">{title}</h4>
              <ul className="space-y-3 text-sm">
                {links.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className="text-muted-foreground hover:text-foreground"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 border-t pt-6 text-sm text-muted-foreground flex flex-col md:flex-row items-center justify-between gap-4">
          <span>
            © {new Date().getFullYear()} SmartGrid. All rights reserved.
          </span>
          <span>Built for Africa’s energy future 🇨🇲</span>
        </div>
      </div>
    </footer>
  );
}
