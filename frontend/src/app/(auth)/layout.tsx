import { Toaster } from "@/components/ui/sonner";

export default function AuthGroupLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
      <Toaster richColors position="top-right" />
    </>
  );
}
