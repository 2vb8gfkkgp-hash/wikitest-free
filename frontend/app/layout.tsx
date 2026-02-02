import type { Metadata } from "next";
import "./globals.css";
import ServiceWorker from "../components/ServiceWorker";

export const metadata: Metadata = {
  title: "NewsroomKit",
  description: "Ethical newsroom assistant for student journalists.",
  manifest: "/manifest.json",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <ServiceWorker />
        {children}
      </body>
    </html>
  );
}
