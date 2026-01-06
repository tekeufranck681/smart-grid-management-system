import Link from "next/link";
import { Users, Target, Lightbulb, Award, ArrowRight } from "lucide-react";

const VALUES = [
  {
    icon: Target,
    title: "Mission-driven",
    description:
      "Focused on modernizing Cameroon’s energy infrastructure.",
  },
  {
    icon: Users,
    title: "Built for professionals",
    description:
      "Designed with real utility engineers and operators.",
  },
  {
    icon: Lightbulb,
    title: "Innovation first",
    description:
      "AI-powered insights and predictive simulations.",
  },
  {
    icon: Award,
    title: "Local expertise",
    description:
      "Deep understanding of regional energy challenges.",
  },
];

export default function AboutSection() {
  return (
    <section id="about" className="py-24 bg-muted/40">
      <div className="mx-auto max-w-7xl px-4 grid lg:grid-cols-2 gap-16 items-center">
        <div>
          <span className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1 text-sm text-primary mb-6">
            <Users size={14} />
            About us
          </span>

          <h2 className="text-3xl md:text-5xl font-bold">
            Powering Cameroon’s
            <span className="text-primary"> energy future</span>
          </h2>

          <p className="mt-6 text-lg text-muted-foreground">
            SmartGrid Management delivers world-class grid monitoring and
            simulation tools tailored for the realities of Cameroon’s
            infrastructure.
          </p>

          <p className="mt-4 text-lg text-muted-foreground">
            Our platform helps utilities improve reliability, reduce losses,
            and plan confidently for growth.
          </p>

          <Link
            href="/contact"
            className="mt-8 inline-flex items-center gap-2 rounded-md bg-primary px-6 py-3 text-primary-foreground hover:bg-primary/90"
          >
            Get in touch
            <ArrowRight size={18} />
          </Link>
        </div>

        <div className="grid sm:grid-cols-2 gap-6">
          {VALUES.map((value) => (
            <div key={value.title} className="rounded-lg border p-6 transition-all duration-300 hover:scale-105 hover:shadow-lg hover:border-primary/50 bg-card hover:bg-card/80">
              <value.icon className="mb-4 h-6 w-6 text-primary" />
              <h3 className="mb-2 font-semibold">{value.title}</h3>
              <p className="text-sm text-muted-foreground">
                {value.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
