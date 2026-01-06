"use client";

import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";

export default function ProtectedRoute({ children }: any) {
  const { token } = useAuth();
  const router = useRouter();

  if (!token) {
    router.push("/login");
    return null;
  }

  return children;
}
