import Link from "next/link";
import { ArrowRight, Building2, Layers, Shield, Workflow } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const features = [
  {
    icon: Layers,
    title: "Metadata-Driven Hierarchy",
    description: "Configure unlimited org levels without code changes. Your structure, your rules.",
  },
  {
    icon: Shield,
    title: "RBAC + ABAC Permissions",
    description: "Hierarchy-scoped roles and fine-grained access control across every module.",
  },
  {
    icon: Workflow,
    title: "Reusable Platform Services",
    description: "Auth, workflows, notifications, and audit—built once, consumed by all modules.",
  },
  {
    icon: Building2,
    title: "Multi-Tenant by Design",
    description: "Strict tenant isolation from day one. Scale from startup to enterprise.",
  },
];

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b bg-card/80 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <span className="text-xl font-bold text-primary">EnterpriseOS</span>
          <div className="flex gap-3">
            <Link href="/login">
              <Button variant="ghost">Sign in</Button>
            </Link>
            <Link href="/register">
              <Button>
                Get started
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <section className="mx-auto max-w-6xl flex-1 px-6 py-20 text-center">
        <h1 className="text-5xl font-bold tracking-tight sm:text-6xl">
          Your Enterprise
          <span className="text-primary"> Operating System</span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
          A configurable, metadata-driven platform where HR is just one module. Build your
          organization, define workflows, and run every business process on a unified foundation.
        </p>
        <div className="mt-10 flex justify-center gap-4">
          <Link href="/register">
            <Button size="lg">Start free trial</Button>
          </Link>
          <Link href="/login">
            <Button size="lg" variant="outline">Sign in</Button>
          </Link>
        </div>
      </section>

      <section className="border-t bg-muted/30 py-20">
        <div className="mx-auto grid max-w-6xl gap-6 px-6 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Card key={feature.title}>
                <CardHeader>
                  <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                    <Icon className="h-5 w-5 text-primary" />
                  </div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                  <CardDescription>{feature.description}</CardDescription>
                </CardHeader>
              </Card>
            );
          })}
        </div>
      </section>

      <footer className="border-t py-8 text-center text-sm text-muted-foreground">
        EnterpriseOS — Build the platform once. Build business modules on top.
      </footer>
    </div>
  );
}
