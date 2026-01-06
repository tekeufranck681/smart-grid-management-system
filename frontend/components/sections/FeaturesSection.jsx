import {
  LayoutGrid,
  Activity,
  BarChart3,
  Zap,
  Database,
  Shield,
  Globe,
  Workflow,
} from "lucide-react";

const FEATURES = [
  {
    icon: LayoutGrid,
    title: "Workspace Management",
    description:
      "Organize grid configurations and teams with clear access control.",
  },
  {
    icon: Workflow,
    title: "Visual Grid Editor",
    description:
      "Model grid topology visually with intuitive drag-and-drop tools.",
  },
  {
    icon: Activity,
    title: "Real-time Monitoring",
    description:
      "Live metrics, alerts, and automated incident detection.",
  },
  {
    icon: BarChart3,
    title: "Advanced Analytics",
    description:
      "Dashboards with KPIs, demand forecasting, and insights.",
  },
  {
    icon: Zap,
    title: "Simulation Engine",
    description:
      "Test failure scenarios and stress-test grid resilience.",
  },
  {
    icon: Database,
    title: "Scenario Comparison",
    description:
      "Compare multiple simulations to guide infrastructure decisions.",
  },
  {
    icon: Shield,
    title: "Enterprise Security",
    description:
      "Encryption, SSO, audit logs, and compliance-ready architecture.",
  },
  {
    icon: Globe,
    title: "Bilingual Support",
    description:
      "English and French interfaces for national-scale adoption.",
  },
];

export default function FeaturesSection() {
  return (
    <section id="features" className="py-24">
      <div className="mx-auto max-w-7xl px-4">
        <div className="mb-16 max-w-3xl">
          <h2 className="text-3xl md:text-5xl font-bold">
            Everything you need to
            <span className="text-primary"> manage your grid</span>
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            A complete toolset designed with utility engineers and energy
            operators in mind.
          </p>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map((feature) => (
            <div key={feature.title} className="rounded-lg border p-6 transition-all duration-300 hover:scale-105 hover:shadow-lg hover:border-primary/50 bg-card hover:bg-card/80">
              <feature.icon className="mb-4 h-6 w-6 text-primary" />
              <h3 className="mb-2 font-semibold">{feature.title}</h3>
              <p className="text-sm text-muted-foreground">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
