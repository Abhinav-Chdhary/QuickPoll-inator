// src/app/page.tsx
"use client";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Heart, Loader2 } from "lucide-react";
// Helpers
import { API_URL } from "@/components/helpers/constants";
import { PollResponse } from "@/components/helpers/types/Poll";
// Components
import ProtectedRoute from "@/components/ProtectedRoutes";
import PollCard from "@/components/ui/02_molecules/pollCard";

export default function Home() {
  const [polls, setPolls] = useState<PollResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch polls on page load
  useEffect(() => {
    const fetchPolls = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const res = await fetch(`${API_URL}/polls/`);

        if (!res.ok) {
          const errData = await res.json();
          throw new Error(errData.detail || "Failed to fetch polls");
        }

        const data: PollResponse[] = await res.json();
        setPolls(data);
      } catch (error: any) {
        setError(error.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPolls();
  }, []);

  // Render content based on state
  const renderContent = () => {
    // Loading state
    if (isLoading) {
      return (
        <div className="flex justify-center items-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          <p className="ml-2">Loading polls...</p>
        </div>
      );
    }

    // Error state
    if (error) {
      return (
        <div className="text-center py-20 text-destructive">
          <p>Error: {error}</p>
          <p>Could not load polls. Please try again later.</p>
        </div>
      );
    }

    // No polls found state
    if (polls.length === 0) {
      return (
        <div className="text-center py-20 text-muted-foreground">
          <p>No polls found.</p>
          <p>Why not be the first to create one?</p>
          {/* You could add a <Button> to create a poll here */}
        </div>
      );
    }

    // Polls found state
    return (
      <div className="flex flex-col space-y-4">
        {polls.map((poll) => (
          <PollCard key={poll._id} poll={poll} />
        ))}
      </div>
    );
  };

  return (
    <ProtectedRoute>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="container mx-auto max-w-2xl py-10 px-4" // Centered layout
      >
        <div className="mb-8">
          {/* Title */}
          <h1 className="text-3xl font-bold tracking-tight">Home Feed</h1>

          {/* Description */}
          <p className="text-muted-foreground">
            See what the community is polling about.
          </p>
        </div>

        {renderContent()}
      </motion.div>
    </ProtectedRoute>
  );
}
