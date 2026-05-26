import "./globals.css";

export const metadata = {
  title: "AI Website Workflow",
  description:
    "End-to-End Playbook für Website-Erstellung mit KI: Setup, Akquise, Briefing, Umsetzung, Abschluss.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="de">
      <body className="antialiased">{children}</body>
    </html>
  );
}
