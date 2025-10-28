import { motion } from "framer-motion";
// Components
import ProtectedRoute from "@/components/ProtectedRoutes";

export default function Home() {
  return (
    <ProtectedRoute>
      <div className="flex items-center justify-center min-h-screen bg-background p-4">
        Home page
      </div>
    </ProtectedRoute>
  );
}
