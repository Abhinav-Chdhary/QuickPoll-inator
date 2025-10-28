// src/app/poll/page.tsx
"use client";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { motion } from "framer-motion";
// Components
import ProtectedRoute from "@/components/ProtectedRoutes";

export default function Poll() {
  const router = useRouter();

  // Effect to check authentication
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) router.push("/login");
  }, [router]);

  return (
    <ProtectedRoute>
      <div className="flex items-center justify-center min-h-screen bg-background p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          Poll page
        </motion.div>
      </div>
    </ProtectedRoute>
  );
}
